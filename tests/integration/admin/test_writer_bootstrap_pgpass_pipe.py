from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).parents[3] / "scripts/admin/bootstrap_material_writer_secrets.py"
SPEC = importlib.util.spec_from_file_location("writer_bootstrap_pgpass_integration", MODULE_PATH)
assert SPEC and SPEC.loader
helper = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = helper
SPEC.loader.exec_module(helper)


def test_real_libpq_accepts_private_pgpass_descriptor():
    executable = os.environ.get("AIOS_TEST_PGPASS_PSQL")
    if not executable:
        pytest.skip("disposable PostgreSQL psql path not configured")
    host = os.environ.get("AIOS_TEST_PGPASS_HOST", "/var/run/postgresql")
    if not host.startswith("/"):
        pytest.fail("real pgpass integration requires a Unix socket directory")
    port = os.environ.get("AIOS_TEST_PGPASS_PORT", "55434")
    database = os.environ.get("AIOS_TEST_PGPASS_DATABASE", "aios")
    login = os.environ.get("AIOS_TEST_PGPASS_USER", "pipe_test_user")
    password_bytes = os.environ.get("AIOS_TEST_PGPASS_PASSWORD", "disposable-pipe-only-test").encode("ascii")
    password = helper.Secret(password_bytes)
    observed = {}

    def real_runner(argv, stdin, env, pass_fds):
        completed = subprocess.run(list(argv), input=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=dict(env), pass_fds=pass_fds, check=False)
        observed.update(argv=tuple(argv), stdout=completed.stdout, stderr=completed.stderr, pass_fds=pass_fds)
        return helper.ProcessResult(completed.returncode, completed.stdout)

    argv = (executable, "-X", "-A", "-t", "-q", "-v", "ON_ERROR_STOP=1", "-h", host, "-p", port, "-U", login, "-d", database)
    succeeded = helper.private_pgpass_probe(real_runner, argv, host, port, database, login, password, b"SELECT 1;\n")
    assert succeeded
    joined_argv = b" ".join(part.encode("utf-8") for part in observed["argv"])
    assert password_bytes not in joined_argv
    assert password_bytes not in observed["stdout"]
    assert password_bytes not in observed["stderr"]
    assert len(observed["pass_fds"]) == 1
    with pytest.raises(OSError):
        os.fstat(observed["pass_fds"][0])

    # The same Unix-socket connection must reject a localhost-bound pgpass
    # record. Explicit socket-directory connections match that exact directory.
    assert not helper.private_pgpass_probe(
        real_runner, argv, "localhost", port, database, login, password, b"SELECT 1;\n"
    )
    assert observed["argv"][observed["argv"].index("-h") + 1] == host
    assert "localhost" not in observed["argv"] and "127.0.0.1" not in observed["argv"]


def test_real_postgresql_exact_validator_and_compensation(monkeypatch):
    executable = os.environ.get("AIOS_TEST_PGPASS_PSQL")
    if not executable or os.environ.get("AIOS_TEST_FULL_BOOTSTRAP_SQL") != "1":
        pytest.skip("disposable full SQL fixture not configured")
    host = os.environ.get("AIOS_TEST_PGPASS_HOST", "/var/run/postgresql")
    port = os.environ.get("AIOS_TEST_PGPASS_PORT", "55434")
    database = os.environ.get("AIOS_TEST_PGPASS_DATABASE", "aios")
    login = os.environ.get("AIOS_TEST_PGPASS_USER", "pipe_test_user")
    if not host.startswith("/"):
        pytest.fail("full SQL integration requires a Unix socket directory")
    monkeypatch.setattr(helper, "RUNTIME_PG_SOCKET", host)

    diagnostics = []
    observed_calls = []

    def admin_runner(requested_argv, stdin, requested_env, requested_pass_fds):
        if requested_pass_fds:
            argv = (executable, *requested_argv[1:])
            child_env = dict(requested_env)
            pass_fds = requested_pass_fds
        else:
            argv = (executable, "-X", "-A", "-t", "-q", "-v", "ON_ERROR_STOP=1", "-h", host, "-p", port, "-U", login, "-d", database)
            child_env = dict(helper.ADMIN_ENV)
            admin_password = os.environ.get("AIOS_TEST_ADMIN_PASSWORD")
            if admin_password:
                child_env["PGPASSWORD"] = admin_password
            pass_fds = ()
        completed = subprocess.run(list(argv), input=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=child_env, pass_fds=pass_fds, check=False)
        observed_calls.append((argv, pass_fds))
        diagnostics.append(completed.stderr.replace(b"A" * 43, b"<redacted>").replace(b"B" * 43, b"<redacted>"))
        return helper.ProcessResult(completed.returncode, completed.stdout)

    migrations = Path(__file__).parents[3] / "migrations/postgres"
    assert admin_runner((), (migrations / "0002_create_material_stock.up.sql").read_bytes(), None, ()).returncode == 0
    assert admin_runner((), (migrations / "0003_create_material_receipt_inventory_movement.up.sql").read_bytes(), None, ()).returncode == 0
    postgres = helper.Postgres(admin_runner)
    postgres.preflight()
    candidate = helper.Secret(b"A" * 43)
    posting = helper.Secret(b"B" * 43)
    assert postgres.provision(candidate, posting), diagnostics[-1].decode("utf-8", "replace")
    assert postgres.reconcile() is helper.LifecycleState.DB_COMMITTED
    assert postgres.authenticate(candidate, posting), diagnostics[-1].decode("utf-8", "replace")
    probe_argv = [argv for argv, passed in observed_calls if passed]
    assert len(probe_argv) == 2
    assert all(argv[argv.index("-h") + 1] == host for argv in probe_argv)
    assert all("localhost" not in argv and "127.0.0.1" not in argv for argv in probe_argv)
    assert all(argv[argv.index("-p") + 1] == "5432" and argv[argv.index("-d") + 1] == "aios" for argv in probe_argv)

    def validation_passes():
        return admin_runner((), helper.validation_sql().encode("ascii"), None, ()).returncode == 0
    def execute(sql):
        assert admin_runner((), sql.encode("ascii"), None, ()).returncode == 0

    adversarial = (
        (f"GRANT INSERT (movement_id) ON public.inventory_movements TO {helper.CANDIDATE_ROLE};", f"REVOKE INSERT (movement_id) ON public.inventory_movements FROM {helper.CANDIDATE_ROLE};"),
        (f"GRANT UPDATE (supplier_name) ON public.material_receipts TO {helper.POSTING_ROLE};", f"REVOKE UPDATE (supplier_name) ON public.material_receipts FROM {helper.POSTING_ROLE};"),
        (f"GRANT {helper.POSTING_ROLE} TO {helper.CANDIDATE_LOGIN};", f"REVOKE {helper.POSTING_ROLE} FROM {helper.CANDIDATE_LOGIN};"),
        (f"ALTER ROLE {helper.CANDIDATE_LOGIN} NOINHERIT;", f"ALTER ROLE {helper.CANDIDATE_LOGIN} INHERIT;"),
        (f"GRANT SELECT ON public.inventory_movements TO {helper.CANDIDATE_LOGIN};", f"REVOKE SELECT ON public.inventory_movements FROM {helper.CANDIDATE_LOGIN};"),
        (f"GRANT SELECT ON public.material_stock TO {helper.CANDIDATE_ROLE} WITH GRANT OPTION;", f"REVOKE GRANT OPTION FOR SELECT ON public.material_stock FROM {helper.CANDIDATE_ROLE};"),
        ("GRANT SELECT ON public.material_receipts TO PUBLIC;", "REVOKE SELECT ON public.material_receipts FROM PUBLIC;"),
        ("GRANT UPDATE ON public.material_stock TO PUBLIC;", "REVOKE UPDATE ON public.material_stock FROM PUBLIC;"),
        (f"GRANT UPDATE (material_id) ON public.material_stock TO {helper.POSTING_ROLE};", f"REVOKE UPDATE (material_id) ON public.material_stock FROM {helper.POSTING_ROLE};"),
    )
    for apply_sql, undo_sql in adversarial:
        execute(apply_sql)
        assert not validation_passes()
        execute(undo_sql)
        assert validation_passes()

    postgres.compensate()
    assert postgres.verify_disabled()
