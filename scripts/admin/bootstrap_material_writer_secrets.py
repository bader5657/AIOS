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
import fcntl
import os
import re
import secrets
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

_ASSIGNMENT = re.compile(rb"^([A-Za-z_][A-Za-z0-9_]*)=")
_ENCODED_SECRET = re.compile(rb"^[A-Za-z0-9_-]{43}$")


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


def validate_filesystem(policy: FilesystemPolicy) -> None:
    """Validate every object with lstat so symlinks are never followed."""
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
    def __init__(self, path: Path):
        self.path = path
        self.fd: int | None = None

    def __enter__(self) -> "ExclusiveLock":
        flags = os.O_RDWR | os.O_CREAT | os.O_CLOEXEC | os.O_NOFOLLOW
        try:
            self.fd = os.open(self.path, flags, 0o600)
            os.fchmod(self.fd, 0o600)
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            if self.fd is not None:
                os.close(self.fd)
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


def atomic_write(path: Path, content: bytes, uid: int, gid: int, mode: int = 0o640, timestamps_ns: tuple[int, int] | None = None) -> None:
    """Securely build and replace a file in its own directory."""
    fd = -1
    temp_name: str | None = None
    try:
        fd, temp_name = tempfile.mkstemp(prefix=".runtime.env.bootstrap.", dir=path.parent)
        os.fchmod(fd, 0o600)
        os.fchown(fd, uid, gid)
        with os.fdopen(fd, "wb", closefd=True) as stream:
            fd = -1
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
            os.fchmod(stream.fileno(), mode)
            os.fchown(stream.fileno(), uid, gid)
            if timestamps_ns is not None:
                os.utime(stream.fileno(), ns=timestamps_ns)
            final_meta = os.fstat(stream.fileno())
            if not stat.S_ISREG(final_meta.st_mode) or stat.S_IMODE(final_meta.st_mode) != mode:
                raise BootstrapError("temporary file invariant failed")
        os.replace(temp_name, path)
        temp_name = None
        _fsync_directory(path.parent)
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
SELECT current_setting('log_statement'),
       current_setting('log_min_duration_statement'),
       current_setting('log_duration'),
       CASE WHEN 'pgaudit' = ANY(regexp_split_to_array(current_setting('shared_preload_libraries'), '\\s*,\\s*'))
            THEN current_setting('pgaudit.log', true) ELSE '' END;
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
SET LOCAL log_statement = 'none';
SET LOCAL log_min_duration_statement = -1;
SET LOCAL log_duration = off;
CREATE ROLE {CANDIDATE_ROLE} NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE {POSTING_ROLE} NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE {CANDIDATE_LOGIN} LOGIN INHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD '{candidate._value.decode('ascii')}';
CREATE ROLE {POSTING_LOGIN} LOGIN INHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD '{posting._value.decode('ascii')}';
GRANT {CANDIDATE_ROLE} TO {CANDIDATE_LOGIN};
GRANT {POSTING_ROLE} TO {POSTING_LOGIN};
GRANT CONNECT ON DATABASE {DATABASE} TO {CANDIDATE_ROLE}, {POSTING_ROLE};
GRANT USAGE ON SCHEMA {SCHEMA} TO {CANDIDATE_ROLE}, {POSTING_ROLE};
GRANT SELECT ON TABLE material_receipts, material_receipt_items, material_stock TO {CANDIDATE_ROLE};
GRANT INSERT ({candidate_receipt_insert}) ON material_receipts TO {CANDIDATE_ROLE};
GRANT UPDATE ({candidate_receipt_update}) ON material_receipts TO {CANDIDATE_ROLE};
GRANT INSERT ({candidate_item_insert}) ON material_receipt_items TO {CANDIDATE_ROLE};
GRANT UPDATE ({candidate_item_update}) ON material_receipt_items TO {CANDIDATE_ROLE};
GRANT SELECT ON TABLE material_receipts, material_receipt_items, inventory_movements, material_stock TO {POSTING_ROLE};
GRANT UPDATE (status, updated_at) ON material_receipts TO {POSTING_ROLE};
GRANT UPDATE (status, updated_at) ON material_receipt_items TO {POSTING_ROLE};
GRANT INSERT ({movement_insert}) ON inventory_movements TO {POSTING_ROLE};
GRANT UPDATE (stock_qty, updated_at) ON material_stock TO {POSTING_ROLE};
{validation_sql()}
COMMIT;
"""
    return sql.encode("ascii")


def validation_sql() -> str:
    """Catalog/effective checks, including ACLs, membership and ownership."""
    return f"""\
DO $verify$
DECLARE bad boolean;
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
  IF NOT has_table_privilege('{CANDIDATE_ROLE}','material_receipts','SELECT')
     OR NOT has_table_privilege('{CANDIDATE_ROLE}','material_receipt_items','SELECT')
     OR NOT has_table_privilege('{CANDIDATE_ROLE}','material_stock','SELECT')
     OR has_table_privilege('{CANDIDATE_ROLE}','inventory_movements','SELECT')
     OR has_table_privilege('{CANDIDATE_ROLE}','inventory_movements','INSERT')
     OR has_table_privilege('{CANDIDATE_ROLE}','inventory_movements','UPDATE')
     OR has_table_privilege('{CANDIDATE_ROLE}','inventory_movements','DELETE')
     OR has_table_privilege('{CANDIDATE_ROLE}','inventory_movements','TRUNCATE')
     OR NOT has_table_privilege('{POSTING_ROLE}','inventory_movements','SELECT')
     OR has_table_privilege('{POSTING_ROLE}','inventory_movements','UPDATE')
     OR has_table_privilege('{POSTING_ROLE}','inventory_movements','DELETE')
     OR has_table_privilege('{POSTING_ROLE}','inventory_movements','TRUNCATE')
     OR has_table_privilege('{POSTING_ROLE}','material_stock','INSERT')
     OR has_table_privilege('{POSTING_ROLE}','material_stock','DELETE')
     OR has_table_privilege('{POSTING_ROLE}','material_stock','TRUNCATE')
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
  PERFORM 1 FROM pg_class c CROSS JOIN LATERAL aclexplode(coalesce(c.relacl, acldefault(CASE WHEN c.relkind='S' THEN 'S'::"char" ELSE 'r'::"char" END,c.relowner))) a
    WHERE c.relnamespace='public'::regnamespace LIMIT 1;
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


class Postgres:
    def __init__(self, runner: Runner = subprocess_runner):
        self.runner = runner

    def _admin(self, sql: bytes) -> ProcessResult:
        return self.runner(ADMIN_ARGV, sql, ADMIN_ENV, ())

    def preflight(self) -> None:
        logging_result = self._admin(logging_preflight_sql())
        if logging_result.returncode != 0:
            raise BootstrapError("PostgreSQL logging preflight failed")
        rows = [line.strip() for line in logging_result.stdout.splitlines() if b"|" in line]
        if rows != [b"none|-1|off|"]:
            raise BootstrapError("unsafe PostgreSQL logging posture")
        collision = self._admin(collision_preflight_sql())
        if collision.returncode != 0 or collision.stdout.strip():
            raise BootstrapError("database identity collision")

    def provision(self, candidate: Secret, posting: Secret) -> None:
        result = self._admin(provisioning_sql(candidate, posting))
        if result.returncode != 0:
            raise BootstrapError("database provisioning failed")

    def _probe(self, login: str, password: Secret) -> bool:
        read_fd, write_fd = os.pipe()
        try:
            os.set_inheritable(read_fd, True)
            line = b"localhost:5432:" + DATABASE.encode() + b":" + login.encode() + b":" + password._value + b"\n"
            os.write(write_fd, line)
            os.close(write_fd)
            write_fd = -1
            env = dict(ADMIN_ENV)
            env["PGPASSFILE"] = f"/proc/self/fd/{read_fd}"
            argv = ("/usr/bin/psql", "-X", "-v", "ON_ERROR_STOP=1", "-h", "localhost", "-p", "5432", "-U", login, "-d", DATABASE)
            sql = b"SELECT 1; SELECT count(*) FROM information_schema.tables WHERE table_schema='public';\n"
            return self.runner(argv, sql, env, (read_fd,)).returncode == 0
        finally:
            if write_fd >= 0:
                os.close(write_fd)
            os.close(read_fd)

    def authenticate(self, candidate: Secret, posting: Secret) -> bool:
        return self._probe(CANDIDATE_LOGIN, candidate) and self._probe(POSTING_LOGIN, posting)

    def compensate(self) -> None:
        sql = f"ALTER ROLE {CANDIDATE_LOGIN} NOLOGIN; ALTER ROLE {POSTING_LOGIN} NOLOGIN;\n".encode("ascii")
        result = self._admin(sql)
        if result.returncode != 0:
            raise BootstrapError("NOLOGIN compensation failed")

    def verify_disabled(self) -> None:
        sql = f"SELECT bool_and(NOT rolcanlogin) FROM pg_roles WHERE rolname IN ('{CANDIDATE_LOGIN}','{POSTING_LOGIN}');\n".encode("ascii")
        result = self._admin(sql)
        if result.returncode != 0 or result.stdout.strip() != b"t":
            raise BootstrapError("NOLOGIN compensation verification failed")


def bootstrap(policy: FilesystemPolicy, postgres: Postgres, generator: Callable[[], Secret] = generate_secret) -> None:
    """Run the full lifecycle.  Intended production entry uses only fixed policy."""
    with ExclusiveLock(policy.lock_file):
        validate_filesystem(policy)  # necessarily precedes generation
        original_meta = os.lstat(policy.env_file)
        original = policy.env_file.read_bytes()
        candidate, posting = generate_secret_pair(generator)
        replacement = replace_governed_assignments(original, {CANDIDATE_KEY: candidate, POSTING_KEY: posting})
        postgres.preflight()
        atomic_write(policy.env_file, replacement, policy.uid, policy.gid)
        committed = False
        try:
            postgres.provision(candidate, posting)
            committed = True
            if not postgres.authenticate(candidate, posting):
                compensation_failed = False
                try:
                    postgres.compensate()
                except BootstrapError:
                    compensation_failed = True
                try:
                    atomic_write(policy.env_file, original, original_meta.st_uid, original_meta.st_gid, stat.S_IMODE(original_meta.st_mode), (original_meta.st_atime_ns, original_meta.st_mtime_ns))
                except BootstrapError:
                    compensation_failed = True
                try:
                    postgres.verify_disabled()
                except BootstrapError:
                    compensation_failed = True
                if compensation_failed:
                    raise BootstrapError("authentication compensation failed closed")
                raise BootstrapError("authentication verification failed; identities disabled")
        except BootstrapError:
            if not committed:
                atomic_write(policy.env_file, original, original_meta.st_uid, original_meta.st_gid, stat.S_IMODE(original_meta.st_mode), (original_meta.st_atime_ns, original_meta.st_mtime_ns))
            raise


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
