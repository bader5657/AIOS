from __future__ import annotations

import contextlib
import fcntl
import importlib.util
import io
import json
import logging
import os
import stat
import subprocess
import signal
import sys
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).parents[3] / "scripts/admin/bootstrap_material_writer_secrets.py"
SPEC = importlib.util.spec_from_file_location("writer_bootstrap", MODULE_PATH)
assert SPEC and SPEC.loader
helper = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = helper
SPEC.loader.exec_module(helper)


def secret(byte: bytes) -> helper.Secret:
    # 32 deterministic bytes, encoded exactly as production does.
    import base64

    return helper.Secret(base64.urlsafe_b64encode(byte * 32).rstrip(b"="))


@pytest.fixture
def fixture_policy(tmp_path: Path) -> helper.FilesystemPolicy:
    root = tmp_path / "opt" / "aios"
    runtime = root / "runtime"
    config = runtime / "config"
    config.mkdir(parents=True)
    env_file = config / "runtime.env"
    env_file.write_bytes(b"UNCHANGED=yes\n")
    os.chmod(root, 0o755)
    os.chmod(runtime, 0o755)
    os.chmod(config, 0o750)
    os.chmod(env_file, 0o640)
    return helper.FilesystemPolicy(
        rules=(
            helper.PathRule(root, 0o755),
            helper.PathRule(runtime, 0o755),
            helper.PathRule(config, 0o750),
            helper.PathRule(env_file, 0o640, regular=True),
        ),
        uid=os.getuid(),
        gid=os.getgid(),
        env_file=env_file,
        lock_file=config / ".runtime.env.writer-bootstrap.lock",
    )


def test_parent_and_target_metadata_accepted(fixture_policy):
    helper.validate_filesystem(fixture_policy)


@pytest.mark.parametrize("index,mode", [(0, 0o775), (1, 0o777), (2, 0o770), (3, 0o600)])
def test_wrong_or_writable_mode_rejected(fixture_policy, index, mode):
    os.chmod(fixture_policy.rules[index].path, mode)
    with pytest.raises(helper.BootstrapError, match="filesystem invariant failed"):
        helper.validate_filesystem(fixture_policy)


def test_wrong_owner_or_group_rejected_without_chown(fixture_policy):
    bad = helper.FilesystemPolicy(
        fixture_policy.rules, fixture_policy.uid + 1, fixture_policy.gid + 1,
        fixture_policy.env_file, fixture_policy.lock_file,
    )
    with pytest.raises(helper.BootstrapError, match="filesystem invariant failed"):
        helper.validate_filesystem(bad)


def test_symlink_target_rejected(fixture_policy):
    target = fixture_policy.env_file
    real = target.with_name("real.env")
    target.rename(real)
    target.symlink_to(real)
    with pytest.raises(helper.BootstrapError):
        helper.validate_filesystem(fixture_policy)


def test_directory_target_rejected(fixture_policy):
    fixture_policy.env_file.unlink()
    fixture_policy.env_file.mkdir(mode=0o640)
    with pytest.raises(helper.BootstrapError):
        helper.validate_filesystem(fixture_policy)


def replacements():
    return {helper.CANDIDATE_KEY: secret(b"a"), helper.POSTING_KEY: secret(b"b")}


def test_env_preserves_unrelated_comments_blanks_order_and_line_endings():
    source = b"# comment\r\n\r\nA=1\n" + helper.CANDIDATE_KEY.encode() + b"=old\r\nB=$A literal\n"
    result = helper.replace_governed_assignments(source, replacements())
    assert result.startswith(b"# comment\r\n\r\nA=1\n")
    assert b"B=$A literal\n" in result
    assert result.index(b"A=1") < result.index(helper.CANDIDATE_KEY.encode()) < result.index(b"B=$A literal")
    assert helper.CANDIDATE_KEY.encode() + b"=" + secret(b"a")._value + b"\r\n" in result
    assert result.endswith(helper.POSTING_KEY.encode() + b"=" + secret(b"b")._value + b"\n")


def test_absent_keys_append_with_minimum_newline():
    result = helper.replace_governed_assignments(b"A=1", replacements())
    assert result.startswith(b"A=1\n" + helper.CANDIDATE_KEY.encode())
    assert not result.startswith(b"A=1\n\n")
    assert result.count(b"\n") == 3


def test_empty_file_has_no_leading_newline():
    result = helper.replace_governed_assignments(b"", replacements())
    assert result.startswith(helper.CANDIDATE_KEY.encode())
    assert result.endswith(b"\n")


def test_existing_keys_replaced_once_without_extra_newline():
    source = helper.CANDIDATE_KEY.encode() + b"=x\n" + helper.POSTING_KEY.encode() + b"=y"
    result = helper.replace_governed_assignments(source, replacements())
    assert result.count(helper.CANDIDATE_KEY.encode() + b"=") == 1
    assert result.count(helper.POSTING_KEY.encode() + b"=") == 1
    assert not result.endswith(b"\n")


@pytest.mark.parametrize("key", helper.GOVERNED_KEYS)
def test_duplicate_governed_key_fails_closed(key):
    source = key.encode() + b"=x\n" + key.encode() + b"=y\n"
    with pytest.raises(helper.BootstrapError, match="duplicate governed key"):
        helper.replace_governed_assignments(source, replacements())


def test_no_variable_expansion_or_shell_parsing():
    source = b"A=$(whoami)\nB=${HOME}\nexport C=untouched\n"
    result = helper.replace_governed_assignments(source, replacements())
    assert result.startswith(source)


def test_atomic_write_same_directory_final_mode_and_cleanup(fixture_policy, monkeypatch):
    seen = {}
    real_mkstemp = helper.tempfile.mkstemp

    def observe(*args, **kwargs):
        fd, name = real_mkstemp(*args, **kwargs)
        seen["dir"] = Path(name).parent
        seen["construction_mode"] = stat.S_IMODE(os.fstat(fd).st_mode)
        return fd, name

    monkeypatch.setattr(helper.tempfile, "mkstemp", observe)
    helper.atomic_write(fixture_policy.env_file, b"new\n", os.getuid(), os.getgid())
    assert fixture_policy.env_file.read_bytes() == b"new\n"
    assert seen == {"dir": fixture_policy.env_file.parent, "construction_mode": 0o600}
    assert stat.S_IMODE(fixture_policy.env_file.stat().st_mode) == 0o640
    assert not list(fixture_policy.env_file.parent.glob(".runtime.env.bootstrap.*"))


def test_atomic_write_failure_cleans_temp_and_preserves_target(fixture_policy, monkeypatch):
    original = fixture_policy.env_file.read_bytes()

    def fail_replace(*_):
        raise OSError("simulated")

    monkeypatch.setattr(helper.os, "replace", fail_replace)
    with pytest.raises(helper.BootstrapError, match="atomic environment replacement failed"):
        helper.atomic_write(fixture_policy.env_file, b"new", os.getuid(), os.getgid())
    assert fixture_policy.env_file.read_bytes() == original
    assert not list(fixture_policy.env_file.parent.glob(".runtime.env.bootstrap.*"))


def test_lock_contention_fails_closed(fixture_policy):
    with helper.ExclusiveLock(fixture_policy):
        with pytest.raises(helper.BootstrapError, match="bootstrap lock unavailable"):
            with helper.ExclusiveLock(fixture_policy):
                pass


def test_generator_uses_32_csprng_bytes_and_safe_encoding(monkeypatch):
    calls = []

    def fake(n):
        calls.append(n)
        return b"z" * n

    monkeypatch.setattr(helper.secrets, "token_bytes", fake)
    generated = helper.generate_secret()
    assert calls == [32]
    assert helper._ENCODED_SECRET.fullmatch(generated._value)
    assert b"=" not in generated._value and b":" not in generated._value


def test_pair_is_independent_and_different():
    values = iter((secret(b"a"), secret(b"b")))
    first, second = helper.generate_secret_pair(lambda: next(values))
    assert first._value != second._value


def test_equal_pair_fails_without_disclosure():
    value = secret(b"q")
    with pytest.raises(helper.BootstrapError, match="independent secret generation failed") as caught:
        helper.generate_secret_pair(lambda: value)
    assert value._value.decode() not in str(caught.value)
    assert value._value.decode() not in repr(caught.value)


def test_secret_repr_and_str_are_redacted():
    value = secret(b"s")
    assert value._value.decode() not in repr(value)
    assert value._value.decode() not in str(value)


def test_main_failure_never_outputs_secret(monkeypatch, capsys, caplog):
    value = secret(b"v")._value.decode()
    monkeypatch.setattr(helper, "production_policy", lambda: (_ for _ in ()).throw(helper.BootstrapError("sanitized")))
    caplog.set_level(logging.DEBUG)
    assert helper.main(["--execute-production"]) == 1
    captured = capsys.readouterr()
    assert value not in captured.out + captured.err + caplog.text


def hba_rule(number, *, rule_type="host", database=None, users=None,
             address="all", netmask=None, auth="scram-sha-256", error=None):
    return {
        "rule_number": number,
        "type": rule_type,
        "database": ["all"] if database is None else database,
        "user_name": ["all"] if users is None else users,
        "address": address,
        "netmask": netmask,
        "auth_method": auth,
        "error": error,
    }


def auth_output(rules=None, password_encryption="scram-sha-256"):
    payload = {
        "password_encryption": password_encryption,
        "rules": [hba_rule(1)] if rules is None else rules,
    }
    return json.dumps(payload, separators=(",", ":")).encode("utf-8")


class RecordingRunner:
    def __init__(self, replies=None):
        self.calls = []
        self.replies = iter(replies or [])

    def __call__(self, argv, stdin, env, pass_fds):
        self.calls.append((tuple(argv), stdin, env, pass_fds))
        if tuple(argv) == helper.CONTAINER_INSPECT_ARGV:
            output = f"/{helper.POSTGRES_CONTAINER}|true|healthy|{helper.POSTGRES_IMAGE}\n".encode()
            return helper.ProcessResult(0, output)
        if tuple(argv) == helper.RUNTIME_BINDING_INSPECT_ARGV:
            output = f'[{chr(123)}"HostIp":"{helper.RUNTIME_PROBE_HOST}","HostPort":"{helper.RUNTIME_PROBE_PORT}"{chr(125)}]\n'.encode()
            return helper.ProcessResult(0, output)
        if tuple(argv) == helper.RUNTIME_CONFIGURED_BINDING_INSPECT_ARGV:
            output = f'[{chr(123)}"HostIp":"{helper.RUNTIME_PROBE_HOST}","HostPort":"{helper.RUNTIME_PROBE_PORT}"{chr(125)}]\n'.encode()
            return helper.ProcessResult(0, output)
        if tuple(argv) == helper.RUNTIME_GATEWAY_INSPECT_ARGV:
            return helper.ProcessResult(0, b"172.16.2.1\n")
        if tuple(argv) == helper.RUNTIME_TCP_CHECK_ARGV:
            return helper.ProcessResult(0, b"")
        if stdin == helper.runtime_auth_preflight_sql("172.16.2.1"):
            return helper.ProcessResult(0, auth_output())
        if stdin == helper.admin_identity_preflight_sql():
            output = f"{helper.ADMIN_ROLE}|{helper.ADMIN_ROLE}|{helper.DATABASE}|17|{helper.ADMIN_PG_SOCKET}\nt|t|t\n1|0\n".encode()
            return helper.ProcessResult(0, output)
        try:
            return next(self.replies)
        except StopIteration:
            return helper.ProcessResult(0, b"")


def test_logging_preflight_safe_then_no_collision():
    runner = RecordingRunner([helper.ProcessResult(0, b"none|-1|off|panic|-1|0|0||||\n"), helper.ProcessResult(0, b""), helper.ProcessResult(0, b"4|0\n0\n")])
    helper.Postgres(runner).preflight()
    assert runner.calls[0][0] == helper.CONTAINER_INSPECT_ARGV
    assert runner.calls[1][0] == helper.ADMIN_ARGV
    assert b"current_user" in runner.calls[1][1]
    assert b"log_statement" in runner.calls[7][1]
    assert all(call[2] == helper.ADMIN_ENV for call in runner.calls)


def test_admin_command_is_exact_fixed_container_transport():
    assert helper.ADMIN_ARGV[:5] == ("/usr/bin/docker", "exec", "-i", "aios-postgres", "/usr/local/bin/psql")
    assert helper.ADMIN_ARGV[helper.ADMIN_ARGV.index("-U") + 1] == "aios"
    assert helper.ADMIN_ARGV[helper.ADMIN_ARGV.index("-d") + 1] == "aios"
    assert "sudo" not in " ".join(helper.ADMIN_ARGV)
    assert "postgres" not in helper.ADMIN_ARGV


@pytest.mark.parametrize("output", [b"", b"/aios-postgres|false|healthy|postgres:17-alpine\n", b"/aios-postgres|true|unhealthy|postgres:17-alpine\n", b"/aios-postgres|true|healthy|other\n"])
def test_container_identity_failure_blocks_before_sql(output):
    calls = []

    def runner(argv, stdin, env, pass_fds):
        calls.append((tuple(argv), stdin, env, pass_fds))
        return helper.ProcessResult(0, output)

    with pytest.raises(helper.BootstrapError, match="container identity preflight failed"):
        helper.Postgres(runner).preflight()
    assert len(calls) == 1


@pytest.mark.parametrize("identity", [b"", b"aios|aios|aios|17|/var/run/postgresql\nt|f|t\n1|0\n", b"aios|aios|other|17|/var/run/postgresql\nt|t|t\n1|0\n", b"aios|aios|aios|17|/var/run/postgresql\nt|t|t\n0|0\n"])
def test_admin_identity_or_auth_contract_failure_blocks(identity):
    def runner(argv, stdin, env, pass_fds):
        if tuple(argv) == helper.CONTAINER_INSPECT_ARGV:
            output = f"/{helper.POSTGRES_CONTAINER}|true|healthy|{helper.POSTGRES_IMAGE}\n".encode()
            return helper.ProcessResult(0, output)
        return helper.ProcessResult(0, identity)

    with pytest.raises(helper.BootstrapError, match="administrative identity preflight failed"):
        helper.Postgres(runner).preflight()


@pytest.mark.parametrize("posture", [b"all|-1|off|\n", b"none|0|off|\n", b"none|-1|on|\n", b"none|-1|off|write\n"])
def test_unsafe_logging_posture_blocks_before_collision(posture):
    runner = RecordingRunner([helper.ProcessResult(0, posture)])
    with pytest.raises(helper.BootstrapError, match="unsafe PostgreSQL logging posture"):
        helper.Postgres(runner).preflight()
    assert len(runner.calls) == 8


def test_role_collision_blocks():
    runner = RecordingRunner([helper.ProcessResult(0, b"none|-1|off|panic|-1|0|0||||\n"), helper.ProcessResult(0, b"existing\n")])
    with pytest.raises(helper.BootstrapError, match="database identity collision"):
        helper.Postgres(runner).preflight()


def test_sql_is_fixed_transaction_and_exact_contract():
    sql = helper.provisioning_sql(secret(b"a"), secret(b"b")).decode()
    assert sql.startswith("BEGIN;\n") and sql.endswith("COMMIT;\n")
    assert sql.index("SET LOCAL log_statement") < sql.index("CREATE ROLE") < sql.index("GRANT") < sql.index("DO $verify$") < sql.index("COMMIT")
    for identity in helper.ROLES:
        assert identity in sql
    for key_fragment in (
        "GRANT SELECT ON TABLE public.material_receipts, public.material_receipt_items, public.material_stock TO aios_material_receipt_candidate_writer",
        "GRANT UPDATE (status, updated_at) ON public.material_receipts TO aios_material_inventory_posting_writer",
        "GRANT UPDATE (stock_qty, updated_at) ON public.material_stock TO aios_material_inventory_posting_writer",
        "has_database_privilege", "has_schema_privilege", "has_table_privilege", "has_column_privilege",
        "pg_roles", "pg_auth_members", "pg_class", "aclexplode",
    ):
        assert key_fragment in sql
    assert "GRANT ALL" not in sql.upper()
    assert "ALTER TABLE" not in sql.upper()
    assert "INSERT INTO" not in sql.upper()


def test_provision_password_private_stdin_not_argv():
    candidate, posting = secret(b"a"), secret(b"b")
    runner = RecordingRunner()
    helper.Postgres(runner).provision(candidate, posting)
    argv, stdin, env, _ = runner.calls[0]
    assert candidate._value not in b" ".join(x.encode() for x in argv)
    assert posting._value not in b" ".join(x.encode() for x in argv)
    assert candidate._value in stdin and posting._value in stdin
    assert env == helper.ADMIN_ENV


def test_auth_password_uses_inherited_private_pipe_not_argv(monkeypatch):
    value = secret(b"a")
    observed = {}

    def runner(argv, stdin, env, pass_fds):
        observed.update(argv=argv, stdin=stdin, env=env, pass_fds=pass_fds)
        passfile = env["PGPASSFILE"]
        fd = int(passfile.rsplit("/", 1)[1])
        metadata = os.fstat(fd)
        observed["descriptor_regular"] = stat.S_ISREG(metadata.st_mode)
        observed["descriptor_mode"] = stat.S_IMODE(metadata.st_mode)
        observed["descriptor_links"] = metadata.st_nlink
        observed["seals"] = fcntl.fcntl(fd, fcntl.F_GET_SEALS)
        observed["pipe"] = os.read(fd, 4096)
        return helper.ProcessResult(0, b"")

    assert helper.Postgres(runner)._probe(helper.CANDIDATE_LOGIN, value)
    assert value._value not in b" ".join(x.encode() for x in observed["argv"])
    assert value._value not in observed["stdin"]
    assert tuple(observed["argv"][:-1]) == helper.RUNTIME_PROBE_ARGV
    assert observed["argv"][-1] == helper.CANDIDATE_LOGIN
    assert observed["stdin"] == helper.runtime_probe_program()
    assert helper.DOCKER not in observed["argv"]
    assert value._value in observed["pipe"]
    assert observed["pipe"].startswith(
        f"{helper.RUNTIME_PROBE_HOST}:{helper.RUNTIME_PROBE_PORT}:{helper.RUNTIME_PROBE_DATABASE}:{helper.CANDIDATE_LOGIN}:".encode("ascii")
    )
    assert observed["pass_fds"]
    assert observed["descriptor_regular"] and observed["descriptor_mode"] == 0o600
    assert observed["descriptor_links"] == 0
    assert observed["seals"] & fcntl.F_SEAL_WRITE
    with pytest.raises(OSError):
        os.fstat(observed["pass_fds"][0])


class FakePostgres:
    def __init__(self, *, provision_failure=False, auth=False, outcome=helper.LifecycleState.DB_ROLLED_BACK):
        self.events = []
        self.provision_failure = provision_failure
        self.auth = auth
        self.outcome = outcome

    def preflight(self):
        self.events.append("preflight")

    def provision(self, *_):
        self.events.append("provision")
        if self.provision_failure:
            raise helper.BootstrapError("database provisioning failed")
        return True

    def reconcile(self):
        self.events.append("reconcile")
        return self.outcome

    def revalidate_runtime_transport(self):
        self.events.append("revalidate")

    def authenticate(self, *_):
        self.events.append("authenticate")
        return self.auth

    def compensate(self):
        self.events.append("compensate")

    def verify_disabled(self):
        self.events.append("verify_disabled")


def deterministic_generator():
    values = iter((secret(b"a"), secret(b"b")))
    return lambda: next(values)


def test_db_transaction_failure_restores_original_and_cleans(fixture_policy):
    original = fixture_policy.env_file.read_bytes()
    postgres = FakePostgres(provision_failure=True)
    with pytest.raises(helper.BootstrapError, match="database provisioning rolled back"):
        helper.bootstrap(fixture_policy, postgres, deterministic_generator())
    assert fixture_policy.env_file.read_bytes() == original
    assert postgres.events == ["preflight", "preflight", "provision", "reconcile"]
    assert not list(fixture_policy.env_file.parent.glob(".runtime.env.bootstrap.*"))


def test_post_commit_auth_failure_disables_then_restores_and_verifies(fixture_policy):
    original = fixture_policy.env_file.read_bytes()
    postgres = FakePostgres(auth=False)
    with pytest.raises(helper.BootstrapError, match="identities disabled"):
        helper.bootstrap(fixture_policy, postgres, deterministic_generator())
    assert fixture_policy.env_file.read_bytes() == original
    assert postgres.events == ["preflight", "preflight", "provision", "revalidate", "authenticate", "compensate"]
    assert not list(fixture_policy.env_file.parent.glob(".runtime.env.bootstrap.*"))


def test_success_keeps_replacement_and_cleans(fixture_policy):
    postgres = FakePostgres(auth=True)
    helper.bootstrap(fixture_policy, postgres, deterministic_generator())
    content = fixture_policy.env_file.read_bytes()
    assert helper.CANDIDATE_KEY.encode() in content and helper.POSTING_KEY.encode() in content
    assert postgres.events == ["preflight", "preflight", "provision", "revalidate", "authenticate"]
    assert not list(fixture_policy.env_file.parent.glob(".runtime.env.bootstrap.*"))


def test_validation_occurs_before_generation(fixture_policy):
    os.chmod(fixture_policy.rules[2].path, 0o770)
    called = False

    def generator():
        nonlocal called
        called = True
        return secret(b"x")

    with pytest.raises(helper.BootstrapError):
        helper.bootstrap(fixture_policy, FakePostgres(), generator)
    assert not called


def test_dry_run_has_no_filesystem_or_database_side_effect(monkeypatch, capsys):
    monkeypatch.setattr(helper, "production_policy", lambda: pytest.fail("production policy called"))
    assert helper.main([]) == 0
    assert "inactive" in capsys.readouterr().out


def test_source_prohibited_patterns():
    source = MODULE_PATH.read_text()
    compact = source.replace(" ", "")
    assert "shell=True" not in compact
    assert "GRANT ALL" not in source.upper()
    assert "/tmp" not in source
    assert ".bak" not in source
    assert "NOPASSWD" not in source
    assert "chmod(0o660" not in compact
    assert "chmod(0o666" not in compact
    assert "chmod(0o777" not in compact
    assert "source runtime.env" not in source
    assert "print(secret" not in compact
    assert "logging." not in source
    assert "ALTER TABLE" not in source.upper()
    assert "INSERT INTO" not in source.upper()


def test_subprocess_runner_does_not_use_shell(monkeypatch):
    captured = {}

    def fake_run(*args, **kwargs):
        captured.update(kwargs)
        return subprocess.CompletedProcess(args[0], 0, b"", b"")

    monkeypatch.setattr(helper.subprocess, "run", fake_run)
    helper.subprocess_runner(("fixed",), b"sql", None, ())
    assert "shell" not in captured
    assert captured["input"] == b"sql"

def test_untrusted_ancestor_causes_zero_filesystem_mutation(fixture_policy):
    os.chmod(fixture_policy.rules[2].path, 0o770)
    before = set(fixture_policy.rules[2].path.iterdir())
    with pytest.raises(helper.BootstrapError):
        helper.bootstrap(fixture_policy, FakePostgres(), deterministic_generator())
    assert set(fixture_policy.rules[2].path.iterdir()) == before
    assert not fixture_policy.lock_file.exists()


@pytest.mark.parametrize("kind", ["symlink", "wrong_mode", "hardlink"])
def test_untrusted_preexisting_lock_rejected(fixture_policy, kind):
    lock = fixture_policy.lock_file
    if kind == "symlink":
        lock.symlink_to(fixture_policy.env_file)
    else:
        lock.write_bytes(b"")
        os.chmod(lock, 0o600 if kind == "hardlink" else 0o640)
        if kind == "hardlink":
            os.link(lock, lock.with_name("lock.link"))
    before = fixture_policy.env_file.read_bytes()
    with pytest.raises(helper.BootstrapError):
        with helper.ExclusiveLock(fixture_policy):
            pass
    assert fixture_policy.env_file.read_bytes() == before


def test_retained_lock_is_valid_and_reusable(fixture_policy):
    with helper.ExclusiveLock(fixture_policy):
        metadata = os.lstat(fixture_policy.lock_file)
        assert stat.S_ISREG(metadata.st_mode) and metadata.st_nlink == 1
        assert metadata.st_uid == fixture_policy.uid and metadata.st_gid == fixture_policy.gid
        assert stat.S_IMODE(metadata.st_mode) == 0o600
    with helper.ExclusiveLock(fixture_policy):
        pass

@pytest.mark.parametrize("operation", ["fchown", "fchmod", "fsync", "replace", "parent_fsync"])
def test_atomic_metadata_or_replace_failure_cleans(operation, fixture_policy, monkeypatch):
    original = fixture_policy.env_file.read_bytes()
    if operation == "parent_fsync":
        monkeypatch.setattr(helper, "_fsync_directory", lambda *_: (_ for _ in ()).throw(OSError("simulated")))
    else:
        monkeypatch.setattr(helper.os, operation, lambda *_: (_ for _ in ()).throw(OSError("simulated")))
    with pytest.raises(helper.BootstrapError):
        helper.atomic_write(fixture_policy.env_file, b"replacement\n", fixture_policy.uid, fixture_policy.gid)
    assert not list(fixture_policy.env_file.parent.glob(".runtime.env.bootstrap.*"))
    if operation != "parent_fsync":
        assert fixture_policy.env_file.read_bytes() == original


def test_atomic_metadata_mismatch_rejected_before_rename(fixture_policy, monkeypatch):
    original = fixture_policy.env_file.read_bytes()
    real_fstat = helper.os.fstat
    calls = 0
    def mismatching(fd):
        nonlocal calls
        calls += 1
        value = real_fstat(fd)
        if calls == 2:
            values = list(value)
            values[4] = value.st_uid + 1
            return os.stat_result(values)
        return value
    monkeypatch.setattr(helper.os, "fstat", mismatching)
    with pytest.raises(helper.BootstrapError, match="temporary file invariant failed"):
        helper.atomic_write(fixture_policy.env_file, b"new\n", fixture_policy.uid, fixture_policy.gid)
    assert fixture_policy.env_file.read_bytes() == original


def test_atomic_fsync_occurs_before_and_after_metadata(fixture_policy, monkeypatch):
    real_fsync = helper.os.fsync
    calls = []
    def observing(fd):
        calls.append(fd)
        return real_fsync(fd)
    monkeypatch.setattr(helper.os, "fsync", observing)
    helper.atomic_write(fixture_policy.env_file, b"durable\n", fixture_policy.uid, fixture_policy.gid)
    assert len(calls) >= 3

@pytest.mark.parametrize("unsafe", [
    b"all|-1|off|panic|-1|0|0||||\n",
    b"none|0|off|panic|-1|0|0||||\n",
    b"none|-1|on|panic|-1|0|0||||\n",
    b"none|-1|off|error|-1|0|0||||\n",
    b"none|-1|off|panic|0|0|0||||\n",
    b"none|-1|off|panic|-1|1|0||||\n",
    b"none|-1|off|panic|-1|0|1||||\n",
    b"none|-1|off|panic|-1|0|0|pg_stat_statements|||\n",
    b"none|-1|off|panic|-1|0|0||auto_explain||\n",
    b"none|-1|off|panic|-1|0|0||||pgaudit\n",
])
def test_every_known_unsafe_logging_state_blocks(unsafe):
    runner = RecordingRunner([helper.ProcessResult(0, unsafe)])
    with pytest.raises(helper.BootstrapError, match="unsafe PostgreSQL logging posture"):
        helper.Postgres(runner).preflight()
    assert len(runner.calls) == 8


def test_all_governed_relations_are_schema_qualified():
    sql = helper.provisioning_sql(secret(b"a"), secret(b"b")).decode()
    for table in helper.GOVERNED_TABLES:
        assert f"public.{table}" in sql
    assert "SET LOCAL search_path = pg_catalog" in sql
    for line in sql.splitlines():
        if line.startswith("GRANT") and " ON " in line:
            assert "public." in line or "DATABASE" in line or "SCHEMA" in line


def test_validator_has_independent_role_matrices_and_denials():
    sql = helper.validation_sql()
    assert f"('{helper.CANDIDATE_LOGIN}','candidate')" in sql
    assert f"('{helper.POSTING_LOGIN}','posting')" in sql
    assert "actual IS DISTINCT FROM expected" in sql
    assert "runtime direct ACL validation failed" in sql
    assert "table ACL assertion failed" in sql
    assert "column ACL assertion failed" in sql
    assert "unrelated relation privilege validation failed" in sql
    assert "m.admin_option" in sql and "NOT rolinherit" in sql

def test_compensation_is_transactional_and_verifies_exact_two():
    runner = RecordingRunner([helper.ProcessResult(0, b""), helper.ProcessResult(0, b"2|t\n")])
    helper.Postgres(runner).compensate()
    sql = runner.calls[0][1]
    assert sql.startswith(b"BEGIN;") and sql.endswith(b"COMMIT;\n")
    assert sql.count(b"ALTER ROLE") == 2
    assert b"count(*)" in sql and b"rolcanlogin" in sql


@pytest.mark.parametrize("verification", [b"0|\n", b"1|t\n", b"2|f\n", b"3|t\n"])
def test_compensation_failure_or_wrong_cardinality_escalates(verification):
    runner = RecordingRunner([helper.ProcessResult(1, b""), helper.ProcessResult(0, verification)])
    with pytest.raises(helper.BootstrapError, match="high-severity"):
        helper.Postgres(runner).compensate()


def test_reconcile_distinguishes_absent_committed_and_partial():
    absent = RecordingRunner([helper.ProcessResult(0, b"")])
    assert helper.Postgres(absent).reconcile() is helper.LifecycleState.DB_ROLLED_BACK
    all_roles = ("\n".join(helper.ROLES) + "\n").encode()
    committed = RecordingRunner([helper.ProcessResult(0, all_roles), helper.ProcessResult(0, b"")])
    assert helper.Postgres(committed).reconcile() is helper.LifecycleState.DB_COMMITTED
    partial = RecordingRunner([helper.ProcessResult(0, (helper.CANDIDATE_ROLE + "\n").encode())])
    with pytest.raises(helper.BootstrapError, match="partial or unexpected"):
        helper.Postgres(partial).reconcile()


def test_lost_commit_response_reconciles_committed_then_authenticates(fixture_policy):
    postgres = FakePostgres(provision_failure=True, auth=True, outcome=helper.LifecycleState.DB_COMMITTED)
    helper.bootstrap(fixture_policy, postgres, deterministic_generator())
    assert postgres.events == ["preflight", "preflight", "provision", "reconcile", "revalidate", "authenticate"]


def test_ambiguous_partial_state_preserves_staged_environment(fixture_policy):
    class Partial(FakePostgres):
        def reconcile(self):
            self.events.append("reconcile")
            raise helper.BootstrapError("database outcome is partial or unexpected")
    postgres = Partial(provision_failure=True)
    with pytest.raises(helper.BootstrapError, match="outcome remains unknown"):
        helper.bootstrap(fixture_policy, postgres, deterministic_generator())
    assert helper.CANDIDATE_KEY.encode() in fixture_policy.env_file.read_bytes()


def test_signal_guard_restores_handlers():
    before = {sig: signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM)}
    with pytest.raises(helper.BootstrapError, match="interrupted"):
        with helper.SignalGuard() as guard:
            guard._interrupt(signal.SIGTERM, None)
            guard.check()
    assert {sig: signal.getsignal(sig) for sig in before} == before

def test_partial_compensation_failure_preserves_staged_keys(fixture_policy):
    class CompensationFails(FakePostgres):
        def compensate(self):
            self.events.append("compensate")
            raise helper.BootstrapError("high-severity NOLOGIN compensation failure")
    postgres = CompensationFails(auth=False)
    with pytest.raises(helper.BootstrapError, match="high-severity"):
        helper.bootstrap(fixture_policy, postgres, deterministic_generator())
    assert helper.CANDIDATE_KEY.encode() in fixture_policy.env_file.read_bytes()
    assert helper.POSTING_KEY.encode() in fixture_policy.env_file.read_bytes()


def test_failed_new_lock_initialization_removes_only_new_inode(fixture_policy, monkeypatch):
    monkeypatch.setattr(helper.os, "fchown", lambda *_: (_ for _ in ()).throw(OSError("simulated")))
    with pytest.raises(helper.BootstrapError, match="lock unavailable"):
        with helper.ExclusiveLock(fixture_policy):
            pass
    assert not fixture_policy.lock_file.exists()


@pytest.mark.parametrize("outcome", [helper.LifecycleState.DB_ROLLED_BACK, helper.LifecycleState.DB_COMMITTED])
def test_lost_client_response_uses_authoritative_outcome(fixture_policy, outcome):
    postgres = FakePostgres(provision_failure=True, auth=True, outcome=outcome)
    if outcome is helper.LifecycleState.DB_ROLLED_BACK:
        with pytest.raises(helper.BootstrapError, match="rolled back"):
            helper.bootstrap(fixture_policy, postgres, deterministic_generator())
        assert fixture_policy.env_file.read_bytes() == b"UNCHANGED=yes\n"
    else:
        helper.bootstrap(fixture_policy, postgres, deterministic_generator())
        assert helper.CANDIDATE_KEY.encode() in fixture_policy.env_file.read_bytes()
    assert "reconcile" in postgres.events


def test_runtime_env_hardlink_rejected_before_every_side_effect(fixture_policy, monkeypatch):
    linked = fixture_policy.env_file.with_name("runtime.env.link")
    os.link(fixture_policy.env_file, linked)
    before = {entry.name: (entry.stat().st_ino, entry.read_bytes()) for entry in fixture_policy.env_file.parent.iterdir()}
    calls = {"generator": 0, "db": 0, "write": 0}

    class NoDatabase:
        def preflight(self):
            calls["db"] += 1

    def no_generator():
        calls["generator"] += 1
        return secret(b"x")

    def no_write(*_args, **_kwargs):
        calls["write"] += 1

    monkeypatch.setattr(helper, "atomic_write", no_write)
    with pytest.raises(helper.BootstrapError, match="filesystem invariant failed"):
        helper.bootstrap(fixture_policy, NoDatabase(), no_generator)
    after = {entry.name: (entry.stat().st_ino, entry.read_bytes()) for entry in fixture_policy.env_file.parent.iterdir()}
    assert before == after
    assert calls == {"generator": 0, "db": 0, "write": 0}
    assert not fixture_policy.lock_file.exists()


def test_public_acl_preflight_requires_four_tables_and_zero_acl_rows():
    safe = RecordingRunner([
        helper.ProcessResult(0, b"none|-1|off|panic|-1|0|0||||\n"),
        helper.ProcessResult(0, b""),
        helper.ProcessResult(0, b"4|0\n0\n"),
    ])
    helper.Postgres(safe).preflight()
    for output in (b"4|1\n0\n", b"4|0\n1\n", b"3|0\n0\n"):
        runner = RecordingRunner([
            helper.ProcessResult(0, b"none|-1|off|panic|-1|0|0||||\n"),
            helper.ProcessResult(0, b""),
            helper.ProcessResult(0, output),
        ])
        with pytest.raises(helper.BootstrapError, match="unsafe PUBLIC governed ACL posture"):
            helper.Postgres(runner).preflight()


def test_authentication_probe_is_frozen_to_numeric_loopback():
    value = secret(b"u")
    runner = RecordingRunner()
    assert helper.Postgres(runner)._probe(helper.CANDIDATE_LOGIN, value)
    argv, program, _, _ = runner.calls[0]
    assert argv == (*helper.RUNTIME_PROBE_ARGV, helper.CANDIDATE_LOGIN)
    assert b"127.0.0.1" in program and b"5432" in program and b"aios" in program
    assert b"localhost" not in program and b"/var/run/postgresql" not in program
    assert helper.DOCKER not in argv
    with pytest.raises(helper.BootstrapError, match="login target is invalid"):
        helper.Postgres(runner)._probe("arbitrary", value)


def test_production_helper_has_only_frozen_runtime_target():
    source = MODULE_PATH.read_text()
    assert '"localhost"' not in source
    assert source.count('RUNTIME_PROBE_HOST = "127.0.0.1"') == 1
    assert source.count('RUNTIME_PROBE_PORT = "5432"') == 1
    assert source.count('RUNTIME_PROBE_DATABASE = "aios"') == 1
    assert "RUNTIME_PG_SOCKET" not in source
    assert "PGHOST" not in source




@pytest.mark.parametrize("identity", helper.ROLES)
def test_each_collision_precedes_secret_generation_and_mutation(identity, fixture_policy, monkeypatch):
    calls = {"generator": 0, "write": 0}
    runner = RecordingRunner([
        helper.ProcessResult(0, b"none|-1|off|panic|-1|0|0||||\n"),
        helper.ProcessResult(0, (identity + "\n").encode("ascii")),
    ])

    def generator():
        calls["generator"] += 1
        return secret(b"c")

    monkeypatch.setattr(helper, "atomic_write", lambda *_args, **_kwargs: calls.__setitem__("write", calls["write"] + 1))
    with pytest.raises(helper.BootstrapError, match="database identity collision"):
        helper.bootstrap(fixture_policy, helper.Postgres(runner), generator)
    assert calls == {"generator": 0, "write": 0}
    assert len(runner.calls) == 9
    assert identity.encode("ascii") in runner.calls[8][1]
    assert not fixture_policy.lock_file.exists()



def test_lifecycle_order_is_exercised_by_orchestrator(fixture_policy, monkeypatch):
    events = []
    real_validate = helper.validate_filesystem
    real_atomic = helper.atomic_write

    def validate(policy):
        events.append("filesystem")
        return real_validate(policy)

    def generate():
        events.append("secret")
        return secret(b"a" if events.count("secret") == 1 else b"b")

    def atomic(*args, **kwargs):
        events.append("env")
        return real_atomic(*args, **kwargs)

    class Ordered(FakePostgres):
        def preflight(self):
            events.append("preflight")
        def provision(self, *_args):
            events.append("provision")
            return True
        def authenticate(self, *_args):
            events.append("authenticate")
            return True

    monkeypatch.setattr(helper, "validate_filesystem", validate)
    monkeypatch.setattr(helper, "atomic_write", atomic)
    helper.bootstrap(fixture_policy, Ordered(), generate)
    assert events[:7] == ["filesystem", "preflight", "filesystem", "preflight", "secret", "secret", "env"]
    assert events.index("env") < events.index("provision") < events.index("authenticate")


def test_exact_loopback_binding_is_accepted():
    helper.validate_runtime_bindings(b'[{"HostIp":"127.0.0.1","HostPort":"5432"}]', b'[{"HostIp":"127.0.0.1","HostPort":"5432"}]')


@pytest.mark.parametrize("binding", [
    b'[{"HostIp":"0.0.0.0","HostPort":"5432"}]',
    b'[{"HostIp":"::","HostPort":"5432"}]',
    b'[{"HostIp":"203.0.113.8","HostPort":"5432"}]',
    b'[{"HostIp":"localhost","HostPort":"5432"}]',
    b'[{"HostIp":"/var/run/postgresql","HostPort":"5432"}]',
    b'[{"HostIp":"127.0.0.1","HostPort":"55432"}]',
    b'[{"HostIp":"127.0.0.1","HostPort":"5432"},{"HostIp":"::1","HostPort":"5432"}]',
    b'null', b'{}', b'not-json',
])
def test_unsafe_or_ambiguous_runtime_binding_is_rejected(binding):
    with pytest.raises(helper.BootstrapError):
        helper.validate_runtime_bindings(binding, b'[{"HostIp":"127.0.0.1","HostPort":"5432"}]')


@pytest.mark.parametrize("gateway", [
    b"", b"172.16.2.1\n172.17.0.1\n", b"127.0.0.1\n", b"8.8.8.8\n",
    b"169.254.10.1\n", b"192.0.2.1\n", b"0.0.0.0\n", b"::1\n",
    b"fe80::1\n", b"invalid\n", b"\xff\n",
])
def test_unsafe_or_ambiguous_runtime_gateway_is_governed_error(gateway):
    with pytest.raises(helper.BootstrapError):
        helper.validate_runtime_gateway(gateway)


@pytest.mark.parametrize(("gateway", "expected"), [
    (b"10.0.0.1\n", "10.0.0.1"),
    (b"172.16.2.1\n", "172.16.2.1"),
    (b"172.31.255.1\n", "172.31.255.1"),
    (b"192.168.10.1\n", "192.168.10.1"),
])
def test_rfc1918_runtime_gateway_is_accepted(gateway, expected):
    assert helper.validate_runtime_gateway(gateway) == expected


@pytest.mark.parametrize(("rules", "accepted"), [
    ([hba_rule(1, auth="trust"), hba_rule(2)], False),
    ([hba_rule(1, auth="md5"), hba_rule(2)], False),
    ([hba_rule(1, auth="reject"), hba_rule(2)], False),
    ([hba_rule(1, rule_type="hostssl", auth="trust"), hba_rule(2)], True),
    ([hba_rule(1, rule_type="hostnossl"), hba_rule(2, auth="trust")], True),
    ([hba_rule(1, database=["other"], auth="trust"), hba_rule(2)], True),
    ([hba_rule(1, users=["other"], auth="trust"), hba_rule(2)], True),
    ([hba_rule(1, database=["other"])], False),
    ([{"unexpected": "rule"}], False),
    ([
        hba_rule(1, address="172.16.0.0", netmask="255.255.0.0", auth="trust"),
        hba_rule(2, address="172.16.2.0", netmask="255.255.255.0"),
    ], False),
    ([hba_rule(1, database=["aios"])], True),
    ([hba_rule(1, database=["all"])], True),
    ([
        hba_rule(1, users=[helper.CANDIDATE_LOGIN]),
        hba_rule(2, users=[helper.POSTING_LOGIN]),
    ], True),
    ([
        hba_rule(1, users=["+" + helper.CANDIDATE_ROLE]),
        hba_rule(2, users=["+" + helper.POSTING_ROLE]),
    ], True),
])
def test_actual_hba_first_match_resolver(rules, accepted):
    if accepted:
        helper.validate_runtime_auth_output(auth_output(rules), "172.16.2.1")
    else:
        with pytest.raises(helper.BootstrapError):
            helper.validate_runtime_auth_output(auth_output(rules), "172.16.2.1")


@pytest.mark.parametrize("payload", [
    b"not-json", b"\xff", b"{}", auth_output([], "md5"),
    auth_output([hba_rule(1, error="bad rule")]),
    auth_output([hba_rule(1, rule_type="hostgssenc")]),
    auth_output([hba_rule(2), hba_rule(1)]),
])
def test_malformed_or_unsafe_hba_output_fails_closed(payload):
    with pytest.raises(helper.BootstrapError):
        helper.validate_runtime_auth_output(payload, "172.16.2.1")


def test_unsafe_runtime_binding_precedes_secret_generation_and_mutation(fixture_policy, monkeypatch):
    calls = {"generator": 0, "write": 0}

    def runner(argv, stdin, env, pass_fds):
        if tuple(argv) == helper.CONTAINER_INSPECT_ARGV:
            output = f"/{helper.POSTGRES_CONTAINER}|true|healthy|{helper.POSTGRES_IMAGE}\n".encode()
            return helper.ProcessResult(0, output)
        if stdin == helper.admin_identity_preflight_sql():
            output = f"{helper.ADMIN_ROLE}|{helper.ADMIN_ROLE}|{helper.DATABASE}|17|{helper.ADMIN_PG_SOCKET}\nt|t|t\n1|0\n".encode()
            return helper.ProcessResult(0, output)
        if tuple(argv) == helper.RUNTIME_BINDING_INSPECT_ARGV:
            return helper.ProcessResult(0, b'[{"HostIp":"0.0.0.0","HostPort":"5432"}]\n')
        return helper.ProcessResult(0, b"")

    def generator():
        calls["generator"] += 1
        return secret(b"x")

    monkeypatch.setattr(
        helper, "atomic_write",
        lambda *_args, **_kwargs: calls.__setitem__("write", calls["write"] + 1),
    )
    with pytest.raises(helper.BootstrapError, match="unsafe runtime PostgreSQL publication"):
        helper.bootstrap(fixture_policy, helper.Postgres(runner), generator)
    assert calls == {"generator": 0, "write": 0}
    assert not fixture_policy.lock_file.exists()


def test_compensation_and_reconciliation_remain_admin_only():
    compensation = RecordingRunner([
        helper.ProcessResult(0, b""),
        helper.ProcessResult(0, b"2|t\n"),
    ])
    helper.Postgres(compensation).compensate()
    assert all(call[0] == helper.ADMIN_ARGV for call in compensation.calls)

    reconciliation = RecordingRunner([helper.ProcessResult(0, b"")])
    assert helper.Postgres(reconciliation).reconcile() is helper.LifecycleState.DB_ROLLED_BACK
    assert all(call[0] == helper.ADMIN_ARGV for call in reconciliation.calls)

@pytest.mark.parametrize(("effective", "configured"), [
    (b'[{"HostIp":"0.0.0.0","HostPort":"5432"}]', b'[{"HostIp":"127.0.0.1","HostPort":"5432"}]'),
    (b'null', b'[{"HostIp":"127.0.0.1","HostPort":"5432"}]'),
    (b'[{"HostIp":"127.0.0.1","HostPort":"5432"},{"HostIp":"0.0.0.0","HostPort":"5432"}]', b'[{"HostIp":"127.0.0.1","HostPort":"5432"}]'),
    (b'[{"HostIp":"127.0.0.1","HostPort":"55432"}]', b'[{"HostIp":"127.0.0.1","HostPort":"5432"}]'),
    (b'[{"HostIp":"::","HostPort":"5432"}]', b'[{"HostIp":"127.0.0.1","HostPort":"5432"}]'),
    (b'[{"HostIp":"127.0.0.1","HostPort":"5432"}]', b'[{"HostIp":"0.0.0.0","HostPort":"5432"}]'),
])
def test_effective_and_configured_binding_disagreement_fails_closed(effective, configured):
    with pytest.raises(helper.BootstrapError, match="unsafe runtime PostgreSQL publication"):
        helper.validate_runtime_bindings(effective, configured)


def test_runtime_probe_disables_tls_and_gss_fallback():
    program = helper.runtime_probe_program()
    assert b"sslmode='disable'" in program
    assert b"gssencmode='disable'" in program


@pytest.mark.parametrize("drift", ["wildcard binding", "port change", "weaker HBA", "endpoint disappeared"])
def test_post_commit_runtime_drift_compensates_without_authentication(fixture_policy, drift):
    original = fixture_policy.env_file.read_bytes()

    class Drifted(FakePostgres):
        def revalidate_runtime_transport(self):
            self.events.append("revalidate:" + drift)
            raise helper.BootstrapError("runtime transport drift")

    postgres = Drifted(auth=True)
    with pytest.raises(helper.BootstrapError, match="authentication verification failed; identities disabled"):
        helper.bootstrap(fixture_policy, postgres, deterministic_generator())
    assert "authenticate" not in postgres.events
    assert postgres.events[-1] == "compensate"
    assert fixture_policy.env_file.read_bytes() == original



def test_post_commit_nonascii_gateway_failure_is_compensated(fixture_policy):
    original = fixture_policy.env_file.read_bytes()

    class MalformedGateway(FakePostgres):
        def revalidate_runtime_transport(self):
            self.events.append("revalidate")
            helper.validate_runtime_gateway(b"\xff\n")

    postgres = MalformedGateway(auth=True)
    with pytest.raises(helper.BootstrapError, match="authentication verification failed; identities disabled"):
        helper.bootstrap(fixture_policy, postgres, deterministic_generator())
    assert postgres.events == [
        "preflight", "preflight", "provision", "revalidate", "compensate",
    ]
    assert fixture_policy.env_file.read_bytes() == original
