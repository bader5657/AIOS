from __future__ import annotations

import contextlib
import importlib.util
import io
import logging
import os
import stat
import subprocess
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
    with helper.ExclusiveLock(fixture_policy.lock_file):
        with pytest.raises(helper.BootstrapError, match="bootstrap lock unavailable"):
            with helper.ExclusiveLock(fixture_policy.lock_file):
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


class RecordingRunner:
    def __init__(self, replies=None):
        self.calls = []
        self.replies = iter(replies or [])

    def __call__(self, argv, stdin, env, pass_fds):
        self.calls.append((tuple(argv), stdin, env, pass_fds))
        try:
            return next(self.replies)
        except StopIteration:
            return helper.ProcessResult(0, b"")


def test_logging_preflight_safe_then_no_collision():
    runner = RecordingRunner([helper.ProcessResult(0, b"none|-1|off|\n"), helper.ProcessResult(0, b"")])
    helper.Postgres(runner).preflight()
    assert runner.calls[0][0] == helper.ADMIN_ARGV
    assert b"log_statement" in runner.calls[0][1]
    assert all(call[2] == helper.ADMIN_ENV for call in runner.calls)


@pytest.mark.parametrize("posture", [b"all|-1|off|\n", b"none|0|off|\n", b"none|-1|on|\n", b"none|-1|off|write\n"])
def test_unsafe_logging_posture_blocks_before_collision(posture):
    runner = RecordingRunner([helper.ProcessResult(0, posture)])
    with pytest.raises(helper.BootstrapError, match="unsafe PostgreSQL logging posture"):
        helper.Postgres(runner).preflight()
    assert len(runner.calls) == 1


def test_role_collision_blocks():
    runner = RecordingRunner([helper.ProcessResult(0, b"none|-1|off|\n"), helper.ProcessResult(0, b"existing\n")])
    with pytest.raises(helper.BootstrapError, match="database identity collision"):
        helper.Postgres(runner).preflight()


def test_sql_is_fixed_transaction_and_exact_contract():
    sql = helper.provisioning_sql(secret(b"a"), secret(b"b")).decode()
    assert sql.startswith("BEGIN;\n") and sql.endswith("COMMIT;\n")
    assert sql.index("SET LOCAL log_statement") < sql.index("CREATE ROLE") < sql.index("GRANT") < sql.index("DO $verify$") < sql.index("COMMIT")
    for identity in helper.ROLES:
        assert identity in sql
    for key_fragment in (
        "GRANT SELECT ON TABLE material_receipts, material_receipt_items, material_stock TO aios_material_receipt_candidate_writer",
        "GRANT UPDATE (status, updated_at) ON material_receipts TO aios_material_inventory_posting_writer",
        "GRANT UPDATE (stock_qty, updated_at) ON material_stock TO aios_material_inventory_posting_writer",
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
        observed["pipe"] = os.read(fd, 4096)
        return helper.ProcessResult(0, b"")

    assert helper.Postgres(runner)._probe(helper.CANDIDATE_LOGIN, value)
    assert value._value not in b" ".join(x.encode() for x in observed["argv"])
    assert value._value not in observed["stdin"]
    assert value._value in observed["pipe"]
    assert observed["pass_fds"]


class FakePostgres:
    def __init__(self, *, provision_failure=False, auth=False):
        self.events = []
        self.provision_failure = provision_failure
        self.auth = auth

    def preflight(self):
        self.events.append("preflight")

    def provision(self, *_):
        self.events.append("provision")
        if self.provision_failure:
            raise helper.BootstrapError("database provisioning failed")

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
    with pytest.raises(helper.BootstrapError, match="database provisioning failed"):
        helper.bootstrap(fixture_policy, postgres, deterministic_generator())
    assert fixture_policy.env_file.read_bytes() == original
    assert postgres.events == ["preflight", "provision"]
    assert not list(fixture_policy.env_file.parent.glob(".runtime.env.bootstrap.*"))


def test_post_commit_auth_failure_disables_then_restores_and_verifies(fixture_policy):
    original = fixture_policy.env_file.read_bytes()
    postgres = FakePostgres(auth=False)
    with pytest.raises(helper.BootstrapError, match="identities disabled"):
        helper.bootstrap(fixture_policy, postgres, deterministic_generator())
    assert fixture_policy.env_file.read_bytes() == original
    assert postgres.events == ["preflight", "provision", "authenticate", "compensate", "verify_disabled"]
    assert not list(fixture_policy.env_file.parent.glob(".runtime.env.bootstrap.*"))


def test_success_keeps_replacement_and_cleans(fixture_policy):
    postgres = FakePostgres(auth=True)
    helper.bootstrap(fixture_policy, postgres, deterministic_generator())
    content = fixture_policy.env_file.read_bytes()
    assert helper.CANDIDATE_KEY.encode() in content and helper.POSTING_KEY.encode() in content
    assert postgres.events == ["preflight", "provision", "authenticate"]
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
