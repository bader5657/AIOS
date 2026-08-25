#!/usr/bin/env python3
"""One-shot, fail-closed bootstrap for the two governed material writers.

Production execution is deliberately gated by ``--execute-production``.  With
no flag the program performs static self-description only.  The module is also
structured so tests can inject an isolated filesystem and a fake PostgreSQL
transport; the command-line production policy itself is not configurable.
"""

from __future__ import annotations

import argparse
import base64
import enum
import fcntl
import os
import re
import secrets
import signal
import stat
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence


ROOT = Path("/opt/aios")
RUNTIME = ROOT / "runtime"
CONFIG = RUNTIME / "config"
ENV_FILE = CONFIG / "runtime.env"
LOCK_FILE = CONFIG / ".runtime.env.writer-bootstrap.lock"
DOLLAR = chr(36)
DATABASE = "aios"
SCHEMA = "public"
ADMIN_ENV = {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"}
ADMIN_ARGV = (
    "/usr/bin/sudo", "-n", "-u", "postgres", "/usr/bin/psql", "-X", "-A", "-t", "-q",
    "-v", "ON_ERROR_STOP=1", "-h", "/var/run/postgresql", "-p", "5432", "-d", DATABASE,
)

CANDIDATE_KEY = "AIOS_MATERIAL_RECEIPT_CANDIDATE_DB_PASSWORD"
POSTING_KEY = "AIOS_MATERIAL_INVENTORY_POSTING_DB_PASSWORD"
GOVERNED_KEYS = (CANDIDATE_KEY, POSTING_KEY)
CANDIDATE_ROLE = "aios_material_receipt_candidate_writer"
CANDIDATE_LOGIN = "aios_material_receipt_candidate_runtime"
POSTING_ROLE = "aios_material_inventory_posting_writer"
POSTING_LOGIN = "aios_material_inventory_posting_runtime"
ROLES = (CANDIDATE_ROLE, CANDIDATE_LOGIN, POSTING_ROLE, POSTING_LOGIN)
GOVERNED_TABLES = ("material_receipts", "material_receipt_items", "inventory_movements", "material_stock")


_ASSIGNMENT = re.compile(rb"^([A-Za-z_][A-Za-z0-9_]*)=")
_ENCODED_SECRET = re.compile(rb"^[A-Za-z0-9_-]{43}$")


class LifecycleState(enum.Enum):
    PREPARED_ENV = "prepared_env"
    DB_OUTCOME_UNKNOWN = "db_outcome_unknown"
    DB_ROLLED_BACK = "db_rolled_back"
    DB_COMMITTED = "db_committed"
    AUTH_VALIDATED = "auth_validated"
    COMPENSATED_DISABLED = "compensated_disabled"


class BootstrapError(RuntimeError):
    """A deliberately message-only, non-secret operational failure."""


@dataclass(frozen=True, repr=False)
class Secret:
    _value: bytes

    def __repr__(self) -> str:
        return "Secret(<redacted>)"

    def __str__(self) -> str:
        return "<redacted>"

    def reveal_for_private_delivery(self) -> bytes:
        return self._value


@dataclass(frozen=True)
class PathRule:
    path: Path
    mode: int
    regular: bool = False


@dataclass(frozen=True)
class FilesystemPolicy:
    rules: tuple[PathRule, ...]
    uid: int
    gid: int
    env_file: Path
    lock_file: Path


def production_policy() -> FilesystemPolicy:
    if os.geteuid() != 0:
        raise BootstrapError("production bootstrap requires root")
    try:
        import grp

        gid = grp.getgrnam("aiosadmin").gr_gid
    except (KeyError, ImportError) as exc:
        raise BootstrapError("required production group is unavailable") from exc
    return FilesystemPolicy(
        rules=(
            PathRule(ROOT, 0o755),
            PathRule(RUNTIME, 0o755),
            PathRule(CONFIG, 0o750),
            PathRule(ENV_FILE, 0o640, regular=True),
        ),
        uid=0,
        gid=gid,
        env_file=ENV_FILE,
        lock_file=LOCK_FILE,
    )


def validate_filesystem(policy: FilesystemPolicy) -> tuple[os.stat_result, ...]:
    """Read-only validation of every governed component; never follows symlinks."""
    observed: list[os.stat_result] = []
    for rule in policy.rules:
        try:
            metadata = os.lstat(rule.path)
        except OSError as exc:
            raise BootstrapError("filesystem invariant failed") from exc
        kind_ok = stat.S_ISREG(metadata.st_mode) if rule.regular else stat.S_ISDIR(metadata.st_mode)
        if (
            not kind_ok
            or stat.S_ISLNK(metadata.st_mode)
            or metadata.st_uid != policy.uid
            or metadata.st_gid != policy.gid
            or stat.S_IMODE(metadata.st_mode) != rule.mode
        ):
            raise BootstrapError("filesystem invariant failed")
        observed.append(metadata)
    config_meta, env_meta = observed[-2], observed[-1]
    if config_meta.st_dev != env_meta.st_dev:
        raise BootstrapError("runtime environment is not on the config filesystem")
    return tuple(observed)


def generate_secret() -> Secret:
    # 32 bytes of CSPRNG input, encoded without '=', quotes, whitespace, or ':';
    # ':' is excluded so the same value is safe in the private pgpass pipe.
    raw = secrets.token_bytes(32)
    encoded = base64.urlsafe_b64encode(raw).rstrip(b"=")
    if not _ENCODED_SECRET.fullmatch(encoded):
        raise BootstrapError("secret generation failed")
    return Secret(encoded)


def generate_secret_pair(generator: Callable[[], Secret] = generate_secret) -> tuple[Secret, Secret]:
    first = generator()
    second = generator()
    if not secrets.compare_digest(first._value, second._value):
        return first, second
    raise BootstrapError("independent secret generation failed")


def replace_governed_assignments(original: bytes, replacements: Mapping[str, Secret]) -> bytes:
    """Replace governed assignments while preserving every unrelated byte.

    Missing keys are appended in governed order.  If the original lacks a
    trailing newline, exactly one ``\n`` is inserted before the first appended
    assignment.  An originally empty file needs no leading newline.  Appended
    assignments each end in ``\n``.  Existing assignments retain their exact
    line-ending bytes.
    """
    if set(replacements) != set(GOVERNED_KEYS):
        raise BootstrapError("replacement key set is invalid")
    lines = original.splitlines(keepends=True)
    counts = {key: 0 for key in GOVERNED_KEYS}
    output: list[bytes] = []
    for line in lines:
        body = line.rstrip(b"\r\n")
        ending = line[len(body) :]
        match = _ASSIGNMENT.match(body)
        key = match.group(1).decode("ascii") if match else None
        if key in counts:
            counts[key] += 1
            if counts[key] > 1:
                raise BootstrapError("duplicate governed key")
            output.append(key.encode("ascii") + b"=" + replacements[key]._value + ending)
        else:
            output.append(line)
    missing = [key for key in GOVERNED_KEYS if counts[key] == 0]
    result = b"".join(output)
    if missing and result and not result.endswith((b"\n", b"\r")):
        result += b"\n"
    for key in missing:
        result += key.encode("ascii") + b"=" + replacements[key]._value + b"\n"
    return result


class ExclusiveLock:
    """Fixed lock inode retained intentionally and revalidated on every run."""

    def __init__(self, policy: FilesystemPolicy):
        self.policy = policy
        self.path = policy.lock_file
        self.fd: int | None = None

    def _valid(self, metadata: os.stat_result) -> bool:
        return (
            stat.S_ISREG(metadata.st_mode)
            and not stat.S_ISLNK(metadata.st_mode)
            and metadata.st_uid == self.policy.uid
            and metadata.st_gid == self.policy.gid
            and stat.S_IMODE(metadata.st_mode) == 0o600
            and metadata.st_nlink == 1
        )

    def __enter__(self) -> "ExclusiveLock":
        flags = os.O_RDWR | os.O_CLOEXEC | os.O_NOFOLLOW
        created_here = False
        try:
            try:
                before = os.lstat(self.path)
            except FileNotFoundError:
                self.fd = os.open(self.path, flags | os.O_CREAT | os.O_EXCL, 0o600)
                created_here = True
                os.fchown(self.fd, self.policy.uid, self.policy.gid)
                os.fsync(self.fd)
                created = os.fstat(self.fd)
                if not self._valid(created):
                    raise BootstrapError("created lock invariant failed")
                _fsync_directory(self.path.parent)
            else:
                if not self._valid(before):
                    raise BootstrapError("existing lock invariant failed")
                self.fd = os.open(self.path, flags)
                opened = os.fstat(self.fd)
                if not self._valid(opened) or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
                    raise BootstrapError("existing lock changed during validation")
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BootstrapError:
            if self.fd is not None:
                os.close(self.fd)
                self.fd = None
            if created_here:
                try:
                    os.unlink(self.path)
                    _fsync_directory(self.path.parent)
                except OSError:
                    pass
                self.fd = None
            raise
        except OSError as exc:
            if self.fd is not None:
                os.close(self.fd)
                self.fd = None
            if created_here:
                try:
                    os.unlink(self.path)
                    _fsync_directory(self.path.parent)
                except OSError:
                    pass
                self.fd = None
            raise BootstrapError("bootstrap lock unavailable") from exc
        return self

    def __exit__(self, *_: object) -> None:
        if self.fd is not None:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
            os.close(self.fd)
            self.fd = None


def _fsync_directory(directory: Path) -> None:
    fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_write(
    path: Path, content: bytes, uid: int, gid: int, mode: int = 0o640,
    timestamps_ns: tuple[int, int] | None = None,
) -> None:
    """Durably replace and revalidate a governed file in its own directory."""
    fd = -1
    temp_name: str | None = None
    try:
        fd, temp_name = tempfile.mkstemp(prefix=".runtime.env.bootstrap.", dir=path.parent)
        initial = os.fstat(fd)
        if not stat.S_ISREG(initial.st_mode) or initial.st_uid != uid or stat.S_IMODE(initial.st_mode) != 0o600 or initial.st_nlink != 1:
            raise BootstrapError("temporary construction invariant failed")
        with os.fdopen(fd, "wb", closefd=True) as stream:
            fd = -1
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
            os.fchown(stream.fileno(), uid, gid)
            os.fchmod(stream.fileno(), mode)
            if timestamps_ns is not None:
                os.utime(stream.fileno(), ns=timestamps_ns)
            final_meta = os.fstat(stream.fileno())
            if (
                not stat.S_ISREG(final_meta.st_mode)
                or final_meta.st_uid != uid
                or final_meta.st_gid != gid
                or stat.S_IMODE(final_meta.st_mode) != mode
                or final_meta.st_nlink != 1
            ):
                raise BootstrapError("temporary file invariant failed")
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
        temp_name = None
        _fsync_directory(path.parent)
        verify_fd = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
        try:
            installed = os.fstat(verify_fd)
            if (
                not stat.S_ISREG(installed.st_mode)
                or installed.st_uid != uid
                or installed.st_gid != gid
                or stat.S_IMODE(installed.st_mode) != mode
                or installed.st_nlink != 1
            ):
                raise BootstrapError("installed environment invariant failed")
            with os.fdopen(verify_fd, "rb", closefd=False) as installed_stream:
                installed_bytes = installed_stream.read()
            if not secrets.compare_digest(installed_bytes, content):
                raise BootstrapError("installed environment content verification failed")
        finally:
            os.close(verify_fd)
    except BootstrapError:
        raise
    except OSError as exc:
        raise BootstrapError("atomic environment replacement failed") from exc
    finally:
        if fd >= 0:
            os.close(fd)
        if temp_name is not None:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass


def _sql_list(values: Iterable[str]) -> str:
    # All callers supply module constants, never external identifiers.
    return ", ".join(values)


def logging_preflight_sql() -> bytes:
    return b"""\
BEGIN;
SET LOCAL search_path = pg_catalog;
SET LOCAL log_statement = 'none';
SET LOCAL log_min_duration_statement = -1;
SET LOCAL log_duration = off;
SET LOCAL log_min_error_statement = panic;
SET LOCAL log_min_duration_sample = -1;
SET LOCAL log_statement_sample_rate = 0;
SET LOCAL log_transaction_sample_rate = 0;
SELECT current_setting('log_statement'),
       current_setting('log_min_duration_statement'),
       current_setting('log_duration'),
       current_setting('log_min_error_statement'),
       current_setting('log_min_duration_sample'),
       current_setting('log_statement_sample_rate'),
       current_setting('log_transaction_sample_rate'),
       current_setting('shared_preload_libraries'),
       current_setting('session_preload_libraries'),
       current_setting('local_preload_libraries'),
       coalesce((SELECT string_agg(extname, ', ' ORDER BY extname)
                 FROM pg_extension WHERE extname IN ('pgaudit', 'auto_explain', 'pg_stat_statements')), '');
ROLLBACK;
"""


def collision_preflight_sql() -> bytes:
    frozen = ", ".join("'%s'" % role for role in ROLES)
    return ("SELECT rolname FROM pg_roles WHERE rolname IN (" + frozen + ");\n").encode("ascii")


def provisioning_sql(candidate: Secret, posting: Secret) -> bytes:
    """Return the frozen transaction; secrets are safe alphabet-only literals."""
    for secret in (candidate, posting):
        if not _ENCODED_SECRET.fullmatch(secret._value):
            raise BootstrapError("secret encoding invariant failed")
    candidate_receipt_insert = _sql_list((
        "receipt_id", "supplier_name", "document_number", "document_date", "received_at", "source_asset_reference"
    ))
    candidate_receipt_update = _sql_list((
        "supplier_name", "document_number", "document_date", "received_at", "source_asset_reference", "status",
        "version", "confirmed_version", "confirmed_at", "confirmation_actor_reference", "updated_at"
    ))
    candidate_item_insert = _sql_list((
        "receipt_item_id", "receipt_id", "line_number", "candidate_material_description", "canonical_display_name",
        "size_description", "specification", "material_id", "full_colly_count", "qty_per_full_colly",
        "partial_qty", "total_qty", "unit"
    ))
    candidate_item_update = _sql_list((
        "line_number", "candidate_material_description", "canonical_display_name", "size_description",
        "specification", "material_id", "full_colly_count", "qty_per_full_colly", "partial_qty", "total_qty",
        "unit", "status", "updated_at"
    ))
    movement_insert = _sql_list((
        "movement_id", "material_id", "movement_type", "quantity_delta", "unit", "source_receipt_item_id",
        "occurred_at", "posting_actor_reference", "balance_before", "balance_after"
    ))
    sql = f"""\
BEGIN;
SET LOCAL search_path = pg_catalog;
SET LOCAL log_statement = 'none';
SET LOCAL log_min_duration_statement = -1;
SET LOCAL log_duration = off;
SET LOCAL log_min_error_statement = panic;
SET LOCAL log_min_duration_sample = -1;
SET LOCAL log_statement_sample_rate = 0;
SET LOCAL log_transaction_sample_rate = 0;
CREATE ROLE {CANDIDATE_ROLE} NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE {POSTING_ROLE} NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE {CANDIDATE_LOGIN} LOGIN INHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD '{candidate._value.decode('ascii')}';
CREATE ROLE {POSTING_LOGIN} LOGIN INHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD '{posting._value.decode('ascii')}';
GRANT {CANDIDATE_ROLE} TO {CANDIDATE_LOGIN};
GRANT {POSTING_ROLE} TO {POSTING_LOGIN};
GRANT CONNECT ON DATABASE {DATABASE} TO {CANDIDATE_ROLE}, {POSTING_ROLE};
GRANT USAGE ON SCHEMA {SCHEMA} TO {CANDIDATE_ROLE}, {POSTING_ROLE};
GRANT SELECT ON TABLE public.material_receipts, public.material_receipt_items, public.material_stock TO {CANDIDATE_ROLE};
GRANT INSERT ({candidate_receipt_insert}) ON public.material_receipts TO {CANDIDATE_ROLE};
GRANT UPDATE ({candidate_receipt_update}) ON public.material_receipts TO {CANDIDATE_ROLE};
GRANT INSERT ({candidate_item_insert}) ON public.material_receipt_items TO {CANDIDATE_ROLE};
GRANT UPDATE ({candidate_item_update}) ON public.material_receipt_items TO {CANDIDATE_ROLE};
GRANT SELECT ON TABLE public.material_receipts, public.material_receipt_items, public.inventory_movements, public.material_stock TO {POSTING_ROLE};
GRANT UPDATE (status, updated_at) ON public.material_receipts TO {POSTING_ROLE};
GRANT UPDATE (status, updated_at) ON public.material_receipt_items TO {POSTING_ROLE};
GRANT INSERT ({movement_insert}) ON public.inventory_movements TO {POSTING_ROLE};
GRANT UPDATE (stock_qty, updated_at) ON public.material_stock TO {POSTING_ROLE};
{validation_sql()}
COMMIT;
"""
    return sql.encode("ascii")


def validation_sql() -> str:
    """Catalog/effective checks, including ACLs, membership and ownership."""
    return f"""\
DO $verify$
DECLARE bad boolean;
DECLARE rec record;
DECLARE expected boolean;
DECLARE actual boolean;
BEGIN
  SELECT bool_or(rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls)
    OR bool_or(CASE WHEN rolname IN ('{CANDIDATE_ROLE}','{POSTING_ROLE}') THEN rolcanlogin ELSE NOT rolcanlogin END)
    INTO bad FROM pg_roles WHERE rolname IN ('{CANDIDATE_ROLE}','{POSTING_ROLE}','{CANDIDATE_LOGIN}','{POSTING_LOGIN}');
  IF bad OR (SELECT count(*) FROM pg_roles WHERE rolname IN ('{CANDIDATE_ROLE}','{POSTING_ROLE}','{CANDIDATE_LOGIN}','{POSTING_LOGIN}')) <> 4
  THEN RAISE EXCEPTION 'role attribute validation failed'; END IF;
  IF NOT has_database_privilege('{CANDIDATE_ROLE}','{DATABASE}','CONNECT')
     OR NOT has_database_privilege('{POSTING_ROLE}','{DATABASE}','CONNECT')
     OR NOT has_schema_privilege('{CANDIDATE_ROLE}','{SCHEMA}','USAGE')
     OR NOT has_schema_privilege('{POSTING_ROLE}','{SCHEMA}','USAGE')
  THEN RAISE EXCEPTION 'database/schema validation failed'; END IF;
  IF NOT has_table_privilege('{CANDIDATE_ROLE}','public.material_receipts','SELECT')
     OR NOT has_table_privilege('{CANDIDATE_ROLE}','public.material_receipt_items','SELECT')
     OR NOT has_table_privilege('{CANDIDATE_ROLE}','public.material_stock','SELECT')
     OR has_table_privilege('{CANDIDATE_ROLE}','public.inventory_movements','SELECT')
     OR has_table_privilege('{CANDIDATE_ROLE}','public.inventory_movements','INSERT')
     OR has_table_privilege('{CANDIDATE_ROLE}','public.inventory_movements','UPDATE')
     OR has_table_privilege('{CANDIDATE_ROLE}','public.inventory_movements','DELETE')
     OR has_table_privilege('{CANDIDATE_ROLE}','public.inventory_movements','TRUNCATE')
     OR NOT has_table_privilege('{POSTING_ROLE}','public.inventory_movements','SELECT')
     OR has_table_privilege('{POSTING_ROLE}','public.inventory_movements','UPDATE')
     OR has_table_privilege('{POSTING_ROLE}','public.inventory_movements','DELETE')
     OR has_table_privilege('{POSTING_ROLE}','public.inventory_movements','TRUNCATE')
     OR has_table_privilege('{POSTING_ROLE}','public.material_stock','INSERT')
     OR has_table_privilege('{POSTING_ROLE}','public.material_stock','DELETE')
     OR has_table_privilege('{POSTING_ROLE}','public.material_stock','TRUNCATE')
  THEN RAISE EXCEPTION 'table privilege validation failed'; END IF;
  IF EXISTS (
    SELECT 1 FROM information_schema.columns c
    WHERE c.table_schema='{SCHEMA}' AND c.table_name IN ('material_receipts','material_receipt_items','material_stock','inventory_movements')
      AND ((has_column_privilege('{CANDIDATE_ROLE}', format('%I.%I',c.table_schema,c.table_name), c.column_name, 'INSERT')
           OR has_column_privilege('{CANDIDATE_ROLE}', format('%I.%I',c.table_schema,c.table_name), c.column_name, 'UPDATE'))
           OR (has_column_privilege('{POSTING_ROLE}', format('%I.%I',c.table_schema,c.table_name), c.column_name, 'INSERT')
           OR has_column_privilege('{POSTING_ROLE}', format('%I.%I',c.table_schema,c.table_name), c.column_name, 'UPDATE')))
      AND NOT (
        ('{CANDIDATE_ROLE}' IS NOT NULL AND c.table_name='material_receipts' AND c.column_name IN ('receipt_id','supplier_name','document_number','document_date','received_at','source_asset_reference','status','version','confirmed_version','confirmed_at','confirmation_actor_reference','updated_at'))
        OR (c.table_name='material_receipt_items' AND c.column_name IN ('receipt_item_id','receipt_id','line_number','candidate_material_description','canonical_display_name','size_description','specification','material_id','full_colly_count','qty_per_full_colly','partial_qty','total_qty','unit','status','updated_at'))
        OR (c.table_name='inventory_movements' AND c.column_name IN ('movement_id','material_id','movement_type','quantity_delta','unit','source_receipt_item_id','occurred_at','posting_actor_reference','balance_before','balance_after'))
        OR (c.table_name='material_stock' AND c.column_name IN ('stock_qty','updated_at'))
      )) THEN RAISE EXCEPTION 'column ACL validation failed'; END IF;
  IF (SELECT count(*) FROM pg_auth_members m JOIN pg_roles member ON member.oid=m.member JOIN pg_roles parent ON parent.oid=m.roleid
      WHERE (member.rolname='{CANDIDATE_LOGIN}' AND parent.rolname='{CANDIDATE_ROLE}') OR (member.rolname='{POSTING_LOGIN}' AND parent.rolname='{POSTING_ROLE}')) <> 2
     OR EXISTS (SELECT 1 FROM pg_auth_members m JOIN pg_roles member ON member.oid=m.member
                WHERE member.rolname IN ('{CANDIDATE_LOGIN}','{POSTING_LOGIN}')
                  AND m.roleid NOT IN (SELECT oid FROM pg_roles WHERE rolname IN ('{CANDIDATE_ROLE}','{POSTING_ROLE}')))
  THEN RAISE EXCEPTION 'membership validation failed'; END IF;
  IF EXISTS (SELECT 1 FROM pg_class c JOIN pg_roles r ON r.oid=c.relowner WHERE r.rolname IN ('{CANDIDATE_ROLE}','{POSTING_ROLE}','{CANDIDATE_LOGIN}','{POSTING_LOGIN}'))
     OR EXISTS (SELECT 1 FROM pg_namespace n JOIN pg_roles r ON r.oid=n.nspowner WHERE r.rolname IN ('{CANDIDATE_ROLE}','{POSTING_ROLE}','{CANDIDATE_LOGIN}','{POSTING_LOGIN}'))
     OR EXISTS (SELECT 1 FROM pg_database d JOIN pg_roles r ON r.oid=d.datdba WHERE r.rolname IN ('{CANDIDATE_ROLE}','{POSTING_ROLE}','{CANDIDATE_LOGIN}','{POSTING_LOGIN}'))
  THEN RAISE EXCEPTION 'ownership validation failed'; END IF;
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname IN ('{CANDIDATE_LOGIN}','{POSTING_LOGIN}') AND NOT rolinherit) THEN RAISE EXCEPTION 'runtime inherit validation failed'; END IF;
  IF (SELECT count(*) FROM pg_auth_members m JOIN pg_roles member ON member.oid=m.member WHERE member.rolname IN ('{CANDIDATE_LOGIN}','{POSTING_LOGIN}')) <> 2
     OR EXISTS (SELECT 1 FROM pg_auth_members m JOIN pg_roles member ON member.oid=m.member JOIN pg_roles parent ON parent.oid=m.roleid WHERE member.rolname IN ('{CANDIDATE_LOGIN}','{POSTING_LOGIN}') AND (m.admin_option OR NOT ((member.rolname='{CANDIDATE_LOGIN}' AND parent.rolname='{CANDIDATE_ROLE}') OR (member.rolname='{POSTING_LOGIN}' AND parent.rolname='{POSTING_ROLE}'))))
  THEN RAISE EXCEPTION 'exact membership validation failed'; END IF;
  FOR rec IN SELECT r.role_name, r.policy, t.table_name, p.action FROM (VALUES ('{CANDIDATE_ROLE}','candidate'),('{CANDIDATE_LOGIN}','candidate'),('{POSTING_ROLE}','posting'),('{POSTING_LOGIN}','posting')) r(role_name,policy) CROSS JOIN (VALUES ('material_receipts'),('material_receipt_items'),('inventory_movements'),('material_stock')) t(table_name) CROSS JOIN (VALUES ('SELECT'),('INSERT'),('UPDATE'),('DELETE'),('TRUNCATE'),('REFERENCES'),('TRIGGER')) p(action)
  LOOP
    expected := rec.action='SELECT' AND ((rec.policy='candidate' AND rec.table_name IN ('material_receipts','material_receipt_items','material_stock')) OR rec.policy='posting');
    actual := has_table_privilege(rec.role_name, format('%I.%I','public',rec.table_name), rec.action);
    IF actual IS DISTINCT FROM expected THEN RAISE EXCEPTION 'exact table privilege validation failed'; END IF;
  END LOOP;
  FOR rec IN SELECT r.role_name, r.policy, c.table_name, c.column_name, p.action FROM (VALUES ('{CANDIDATE_ROLE}','candidate'),('{CANDIDATE_LOGIN}','candidate'),('{POSTING_ROLE}','posting'),('{POSTING_LOGIN}','posting')) r(role_name,policy) CROSS JOIN information_schema.columns c CROSS JOIN (VALUES ('INSERT'),('UPDATE')) p(action) WHERE c.table_schema='public' AND c.table_name IN ('material_receipts','material_receipt_items','inventory_movements','material_stock')
  LOOP
    expected := CASE
      WHEN rec.policy='candidate' AND rec.action='INSERT' AND rec.table_name='material_receipts' THEN rec.column_name IN ('receipt_id','supplier_name','document_number','document_date','received_at','source_asset_reference')
      WHEN rec.policy='candidate' AND rec.action='UPDATE' AND rec.table_name='material_receipts' THEN rec.column_name IN ('supplier_name','document_number','document_date','received_at','source_asset_reference','status','version','confirmed_version','confirmed_at','confirmation_actor_reference','updated_at')
      WHEN rec.policy='candidate' AND rec.action='INSERT' AND rec.table_name='material_receipt_items' THEN rec.column_name IN ('receipt_item_id','receipt_id','line_number','candidate_material_description','canonical_display_name','size_description','specification','material_id','full_colly_count','qty_per_full_colly','partial_qty','total_qty','unit')
      WHEN rec.policy='candidate' AND rec.action='UPDATE' AND rec.table_name='material_receipt_items' THEN rec.column_name IN ('line_number','candidate_material_description','canonical_display_name','size_description','specification','material_id','full_colly_count','qty_per_full_colly','partial_qty','total_qty','unit','status','updated_at')
      WHEN rec.policy='posting' AND rec.action='UPDATE' AND rec.table_name IN ('material_receipts','material_receipt_items') THEN rec.column_name IN ('status','updated_at')
      WHEN rec.policy='posting' AND rec.action='INSERT' AND rec.table_name='inventory_movements' THEN rec.column_name IN ('movement_id','material_id','movement_type','quantity_delta','unit','source_receipt_item_id','occurred_at','posting_actor_reference','balance_before','balance_after')
      WHEN rec.policy='posting' AND rec.action='UPDATE' AND rec.table_name='material_stock' THEN rec.column_name IN ('stock_qty','updated_at') ELSE false END;
    actual := has_column_privilege(rec.role_name, format('%I.%I','public',rec.table_name), rec.column_name, rec.action);
    IF actual IS DISTINCT FROM expected THEN RAISE EXCEPTION 'exact column privilege validation failed'; END IF;
  END LOOP;
  IF EXISTS (SELECT 1 FROM pg_class c, (VALUES ('{CANDIDATE_ROLE}'),('{CANDIDATE_LOGIN}'),('{POSTING_ROLE}'),('{POSTING_LOGIN}')) r(role_name), (VALUES ('SELECT'),('INSERT'),('UPDATE'),('DELETE'),('TRUNCATE'),('REFERENCES'),('TRIGGER')) p(action) WHERE c.relnamespace='public'::regnamespace AND c.relkind IN ('r','p','v','m','f') AND c.relname NOT IN ('material_receipts','material_receipt_items','inventory_movements','material_stock') AND has_table_privilege(r.role_name,c.oid,p.action)) THEN RAISE EXCEPTION 'unrelated relation privilege validation failed'; END IF;
  IF EXISTS (SELECT 1 FROM pg_shdepend d JOIN pg_roles r ON r.oid=d.refobjid WHERE d.refclassid='pg_authid'::regclass AND d.deptype='o' AND r.rolname IN ('{CANDIDATE_ROLE}','{CANDIDATE_LOGIN}','{POSTING_ROLE}','{POSTING_LOGIN}')) THEN RAISE EXCEPTION 'complete ownership validation failed'; END IF;
  IF EXISTS (SELECT 1 FROM pg_database d CROSS JOIN LATERAL aclexplode(d.datacl) a JOIN pg_roles r ON r.oid=a.grantee WHERE r.rolname IN ('{CANDIDATE_LOGIN}','{POSTING_LOGIN}')) OR EXISTS (SELECT 1 FROM pg_namespace n CROSS JOIN LATERAL aclexplode(n.nspacl) a JOIN pg_roles r ON r.oid=a.grantee WHERE r.rolname IN ('{CANDIDATE_LOGIN}','{POSTING_LOGIN}')) OR EXISTS (SELECT 1 FROM pg_class c CROSS JOIN LATERAL aclexplode(c.relacl) a JOIN pg_roles r ON r.oid=a.grantee WHERE r.rolname IN ('{CANDIDATE_LOGIN}','{POSTING_LOGIN}')) OR EXISTS (SELECT 1 FROM pg_attribute at CROSS JOIN LATERAL aclexplode(at.attacl) a JOIN pg_roles r ON r.oid=a.grantee WHERE r.rolname IN ('{CANDIDATE_LOGIN}','{POSTING_LOGIN}')) THEN RAISE EXCEPTION 'runtime direct ACL validation failed'; END IF;
  IF (SELECT count(*) FROM pg_database d CROSS JOIN LATERAL aclexplode(d.datacl) a JOIN pg_roles r ON r.oid=a.grantee WHERE d.datname='{DATABASE}' AND r.rolname IN ('{CANDIDATE_ROLE}','{POSTING_ROLE}') AND a.privilege_type='CONNECT' AND NOT a.is_grantable) <> 2 OR (SELECT count(*) FROM pg_namespace n CROSS JOIN LATERAL aclexplode(n.nspacl) a JOIN pg_roles r ON r.oid=a.grantee WHERE n.nspname='public' AND r.rolname IN ('{CANDIDATE_ROLE}','{POSTING_ROLE}') AND a.privilege_type='USAGE' AND NOT a.is_grantable) <> 2 OR EXISTS (SELECT 1 FROM pg_database d CROSS JOIN LATERAL aclexplode(d.datacl) a JOIN pg_roles r ON r.oid=a.grantee WHERE r.rolname IN ('{CANDIDATE_ROLE}','{POSTING_ROLE}') AND NOT (d.datname='{DATABASE}' AND a.privilege_type='CONNECT' AND NOT a.is_grantable)) OR EXISTS (SELECT 1 FROM pg_namespace n CROSS JOIN LATERAL aclexplode(n.nspacl) a JOIN pg_roles r ON r.oid=a.grantee WHERE r.rolname IN ('{CANDIDATE_ROLE}','{POSTING_ROLE}') AND NOT (n.nspname='public' AND a.privilege_type='USAGE' AND NOT a.is_grantable)) THEN RAISE EXCEPTION 'database/schema direct ACL validation failed'; END IF;
  IF (SELECT count(*) FROM pg_class c CROSS JOIN LATERAL aclexplode(c.relacl) a JOIN pg_roles r ON r.oid=a.grantee WHERE c.relnamespace='public'::regnamespace AND r.rolname IN ('{CANDIDATE_ROLE}','{POSTING_ROLE}')) <> 7 OR EXISTS (SELECT 1 FROM pg_class c CROSS JOIN LATERAL aclexplode(c.relacl) a JOIN pg_roles r ON r.oid=a.grantee WHERE c.relnamespace='public'::regnamespace AND r.rolname IN ('{CANDIDATE_ROLE}','{POSTING_ROLE}') AND NOT (a.privilege_type='SELECT' AND NOT a.is_grantable AND ((r.rolname='{CANDIDATE_ROLE}' AND c.relname IN ('material_receipts','material_receipt_items','material_stock')) OR (r.rolname='{POSTING_ROLE}' AND c.relname IN ('material_receipts','material_receipt_items','inventory_movements','material_stock'))))) THEN RAISE EXCEPTION 'table ACL assertion failed'; END IF;
  IF (SELECT count(*) FROM pg_attribute at JOIN pg_class c ON c.oid=at.attrelid CROSS JOIN LATERAL aclexplode(at.attacl) a JOIN pg_roles r ON r.oid=a.grantee WHERE c.relnamespace='public'::regnamespace AND r.rolname IN ('{CANDIDATE_ROLE}','{POSTING_ROLE}')) <> 59
     OR EXISTS (SELECT 1 FROM pg_attribute at JOIN pg_class c ON c.oid=at.attrelid CROSS JOIN LATERAL aclexplode(at.attacl) a JOIN pg_roles r ON r.oid=a.grantee WHERE c.relnamespace='public'::regnamespace AND r.rolname IN ('{CANDIDATE_ROLE}','{POSTING_ROLE}') AND (a.is_grantable OR NOT (
       (r.rolname='{CANDIDATE_ROLE}' AND c.relname='material_receipts' AND ((a.privilege_type='INSERT' AND at.attname IN ('receipt_id','supplier_name','document_number','document_date','received_at','source_asset_reference')) OR (a.privilege_type='UPDATE' AND at.attname IN ('supplier_name','document_number','document_date','received_at','source_asset_reference','status','version','confirmed_version','confirmed_at','confirmation_actor_reference','updated_at'))))
       OR (r.rolname='{CANDIDATE_ROLE}' AND c.relname='material_receipt_items' AND ((a.privilege_type='INSERT' AND at.attname IN ('receipt_item_id','receipt_id','line_number','candidate_material_description','canonical_display_name','size_description','specification','material_id','full_colly_count','qty_per_full_colly','partial_qty','total_qty','unit')) OR (a.privilege_type='UPDATE' AND at.attname IN ('line_number','candidate_material_description','canonical_display_name','size_description','specification','material_id','full_colly_count','qty_per_full_colly','partial_qty','total_qty','unit','status','updated_at'))))
       OR (r.rolname='{POSTING_ROLE}' AND c.relname IN ('material_receipts','material_receipt_items') AND a.privilege_type='UPDATE' AND at.attname IN ('status','updated_at'))
       OR (r.rolname='{POSTING_ROLE}' AND c.relname='inventory_movements' AND a.privilege_type='INSERT' AND at.attname IN ('movement_id','material_id','movement_type','quantity_delta','unit','source_receipt_item_id','occurred_at','posting_actor_reference','balance_before','balance_after'))
       OR (r.rolname='{POSTING_ROLE}' AND c.relname='material_stock' AND a.privilege_type='UPDATE' AND at.attname IN ('stock_qty','updated_at'))))) THEN RAISE EXCEPTION 'column ACL assertion failed'; END IF;
  IF EXISTS (SELECT 1 FROM (VALUES ('{CANDIDATE_ROLE}'),('{CANDIDATE_LOGIN}'),('{POSTING_ROLE}'),('{POSTING_LOGIN}')) r(role_name) WHERE has_schema_privilege(r.role_name,'public','CREATE')) THEN RAISE EXCEPTION 'schema CREATE privilege validation failed'; END IF;
END $verify$;
"""


@dataclass(frozen=True)
class ProcessResult:
    returncode: int
    stdout: bytes = b""


Runner = Callable[[Sequence[str], bytes, Mapping[str, str] | None, tuple[int, ...]], ProcessResult]


def subprocess_runner(argv: Sequence[str], stdin: bytes, env: Mapping[str, str] | None, pass_fds: tuple[int, ...]) -> ProcessResult:
    completed = subprocess.run(
        list(argv), input=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env=None if env is None else dict(env), pass_fds=pass_fds, check=False,
    )
    return ProcessResult(completed.returncode, completed.stdout)


def private_pgpass_probe(runner: Runner, argv: Sequence[str], host: str, port: str, database: str, login: str, password: Secret, sql: bytes) -> bool:
    """Deliver one testable pgpass record through a single inherited read descriptor."""
    read_fd, write_fd = os.pipe()
    try:
        os.set_inheritable(read_fd, True)
        line = host.encode("ascii") + b":" + port.encode("ascii") + b":" + database.encode("ascii") + b":" + login.encode("ascii") + b":" + password._value + bytes((10,))
        os.write(write_fd, line)
        os.close(write_fd)
        write_fd = -1
        env = dict(ADMIN_ENV)
        env["PGPASSFILE"] = f"/proc/self/fd/{read_fd}"
        return runner(argv, sql, env, (read_fd,)).returncode == 0
    finally:
        if write_fd >= 0:
            os.close(write_fd)
        os.close(read_fd)


class Postgres:
    def __init__(self, runner: Runner = subprocess_runner):
        self.runner = runner

    def _admin(self, sql: bytes) -> ProcessResult:
        try:
            return self.runner(ADMIN_ARGV, sql, ADMIN_ENV, ())
        except (OSError, subprocess.SubprocessError) as exc:
            raise BootstrapError("PostgreSQL client transport failed") from exc

    def preflight(self) -> None:
        logging_result = self._admin(logging_preflight_sql())
        if logging_result.returncode != 0:
            raise BootstrapError("PostgreSQL logging preflight failed")
        rows = [line.strip() for line in logging_result.stdout.splitlines() if b"|" in line]
        if rows != [b"none|-1|off|panic|-1|0|0||||"]:
            raise BootstrapError("unsafe PostgreSQL logging posture")
        collision = self._admin(collision_preflight_sql())
        if collision.returncode != 0 or collision.stdout.strip():
            raise BootstrapError("database identity collision")

    def provision(self, candidate: Secret, posting: Secret) -> bool:
        return self._admin(provisioning_sql(candidate, posting)).returncode == 0

    def reconcile(self) -> LifecycleState:
        identities = self._admin(collision_preflight_sql())
        if identities.returncode != 0:
            raise BootstrapError("database outcome reconciliation unavailable")
        found = {line.decode("ascii") for line in identities.stdout.splitlines() if line.strip()}
        if not found:
            return LifecycleState.DB_ROLLED_BACK
        if found != set(ROLES):
            raise BootstrapError("database outcome is partial or unexpected")
        validation = self._admin(validation_sql().encode("ascii"))
        if validation.returncode != 0:
            raise BootstrapError("committed database state failed exact reconciliation")
        return LifecycleState.DB_COMMITTED

    def _probe(self, login: str, password: Secret) -> bool:
        argv = ("/usr/bin/psql", "-X", "-v", "ON_ERROR_STOP=1", "-h", "localhost", "-p", "5432", "-U", login, "-d", DATABASE)
        sql = b"SELECT 1; SELECT count(*) FROM information_schema.tables WHERE table_schema='public';\n"
        return private_pgpass_probe(self.runner, argv, "localhost", "5432", DATABASE, login, password, sql)

    def authenticate(self, candidate: Secret, posting: Secret) -> bool:
        return self._probe(CANDIDATE_LOGIN, candidate) and self._probe(POSTING_LOGIN, posting)

    def compensate(self) -> None:
        sql = f"""\
BEGIN;
SET LOCAL search_path = pg_catalog;
ALTER ROLE {CANDIDATE_LOGIN} NOLOGIN;
ALTER ROLE {POSTING_LOGIN} NOLOGIN;
DO {DOLLAR}compensate{DOLLAR}
BEGIN
  IF (SELECT count(*) FROM pg_roles WHERE rolname IN ('{CANDIDATE_LOGIN}','{POSTING_LOGIN}')) <> 2
     OR EXISTS (SELECT 1 FROM pg_roles WHERE rolname IN ('{CANDIDATE_LOGIN}','{POSTING_LOGIN}') AND rolcanlogin)
  THEN RAISE EXCEPTION 'NOLOGIN compensation validation failed'; END IF;
END {DOLLAR}compensate{DOLLAR};
COMMIT;
""".encode("ascii")
        result = self._admin(sql)
        if result.returncode != 0 and not self.verify_disabled():
            raise BootstrapError("high-severity NOLOGIN compensation failure")
        if not self.verify_disabled():
            raise BootstrapError("high-severity NOLOGIN compensation verification failure")

    def verify_disabled(self) -> bool:
        sql = f"SELECT count(*), bool_and(NOT rolcanlogin) FROM pg_roles WHERE rolname IN ('{CANDIDATE_LOGIN}','{POSTING_LOGIN}');\n".encode("ascii")
        result = self._admin(sql)
        return result.returncode == 0 and result.stdout.strip() == b"2|t"


class SignalGuard:
    """Turn SIGINT/SIGTERM into normal fail-closed unwinding; SIGKILL remains unrecoverable."""

    def __init__(self):
        self.previous: dict[int, object] = {}
        self.interrupted = False

    def __enter__(self) -> "SignalGuard":
        for signum in (signal.SIGINT, signal.SIGTERM):
            self.previous[signum] = signal.getsignal(signum)
            signal.signal(signum, self._interrupt)
        return self

    def _interrupt(self, _signum: int, _frame: object) -> None:
        self.interrupted = True

    def check(self) -> None:
        if self.interrupted:
            raise BootstrapError("bootstrap interrupted; recovery required")

    def __exit__(self, *_: object) -> None:
        for signum, handler in self.previous.items():
            signal.signal(signum, handler)


def read_validated_environment(path: Path, expected: os.stat_result) -> bytes:
    fd = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        opened = os.fstat(fd)
        if (opened.st_dev, opened.st_ino) != (expected.st_dev, expected.st_ino) or not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
            raise BootstrapError("runtime environment changed during validation")
        with os.fdopen(fd, "rb", closefd=False) as stream:
            return stream.read()
    finally:
        os.close(fd)


def restore_environment(policy: FilesystemPolicy, original: bytes, metadata: os.stat_result) -> None:
    atomic_write(policy.env_file, original, metadata.st_uid, metadata.st_gid, stat.S_IMODE(metadata.st_mode), (metadata.st_atime_ns, metadata.st_mtime_ns))


def bootstrap(policy: FilesystemPolicy, postgres: Postgres, generator: Callable[[], Secret] = generate_secret) -> None:
    """Run the fixed lifecycle with authoritative DB-outcome reconciliation."""
    validate_filesystem(policy)  # read-only: no lock/temp mutation precedes trust
    with SignalGuard() as signals, ExclusiveLock(policy):
        observed = validate_filesystem(policy)
        signals.check()
        original_meta = observed[-1]
        original = read_validated_environment(policy.env_file, original_meta)
        candidate, posting = generate_secret_pair(generator)
        replacement = replace_governed_assignments(original, {CANDIDATE_KEY: candidate, POSTING_KEY: posting})
        postgres.preflight()
        signals.check()
        try:
            atomic_write(policy.env_file, replacement, policy.uid, policy.gid)
        except BootstrapError as exc:
            try:
                restore_environment(policy, original, original_meta)
            except BootstrapError as restore_exc:
                raise BootstrapError("environment preparation recovery failed closed") from restore_exc
            raise exc

        state = LifecycleState.PREPARED_ENV
        compensation_attempted = False
        try:
            signals.check()
            try:
                provisioned = postgres.provision(candidate, posting)
            except BootstrapError:
                provisioned = False
            if provisioned:
                state = LifecycleState.DB_COMMITTED
            else:
                state = LifecycleState.DB_OUTCOME_UNKNOWN
                state = postgres.reconcile()
                if state is LifecycleState.DB_ROLLED_BACK:
                    restore_environment(policy, original, original_meta)
                    raise BootstrapError("database provisioning rolled back")
            signals.check()

            try:
                authenticated = postgres.authenticate(candidate, posting)
            except BootstrapError:
                authenticated = False
            signals.check()
            if not authenticated:
                compensation_attempted = True
                postgres.compensate()
                state = LifecycleState.COMPENSATED_DISABLED
                restore_environment(policy, original, original_meta)
                raise BootstrapError("authentication verification failed; identities disabled")
            signals.check()
            state = LifecycleState.AUTH_VALIDATED
        except BootstrapError as exc:
            if state in (LifecycleState.PREPARED_ENV, LifecycleState.DB_OUTCOME_UNKNOWN):
                try:
                    state = postgres.reconcile()
                except BootstrapError as reconcile_exc:
                    raise BootstrapError("high-severity database outcome remains unknown; environment retained") from reconcile_exc
                if state is LifecycleState.DB_ROLLED_BACK:
                    restore_environment(policy, original, original_meta)
            if state is LifecycleState.DB_COMMITTED and not compensation_attempted:
                compensation_attempted = True
                postgres.compensate()
                state = LifecycleState.COMPENSATED_DISABLED
                restore_environment(policy, original, original_meta)
            raise exc



def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute-production", action="store_true", help="explicitly perform the fixed production bootstrap")
    args = parser.parse_args(argv)
    if not args.execute_production:
        print("Structural dry-run only: fixed production bootstrap is inactive.")
        return 0
    try:
        bootstrap(production_policy(), Postgres())
    except BootstrapError:
        print("Writer bootstrap failed closed; no secret details are available.", file=sys.stderr)
        return 1
    print("Writer bootstrap completed successfully; no secret values were emitted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
