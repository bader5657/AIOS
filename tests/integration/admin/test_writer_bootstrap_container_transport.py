from __future__ import annotations

import importlib.util
import subprocess
import sys
import time
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[3]
MODULE_PATH = ROOT / "scripts/admin/bootstrap_material_writer_secrets.py"
SPEC = importlib.util.spec_from_file_location("writer_bootstrap_container_integration", MODULE_PATH)
assert SPEC and SPEC.loader
helper = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = helper
SPEC.loader.exec_module(helper)

TEST_CONTAINER = "aios-writer-bootstrap-integration"


def docker(*argv: str, stdin: bytes = b"") -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["/usr/bin/docker", *argv], input=stdin, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )


@pytest.fixture
def disposable_postgres(monkeypatch):
    if not Path("/usr/bin/docker").is_file() or docker("info").returncode != 0:
        pytest.skip("Docker daemon unavailable")
    if docker("inspect", TEST_CONTAINER).returncode == 0:
        pytest.fail(f"refusing to reuse existing container {TEST_CONTAINER}")
    started = docker(
        "run", "--rm", "-d", "--network", "none", "--name", TEST_CONTAINER,
        "-e", "POSTGRES_USER=aios", "-e", "POSTGRES_DB=aios",
        "-e", "POSTGRES_HOST_AUTH_METHOD=trust", "postgres:17-alpine",
    )
    assert started.returncode == 0, started.stderr.decode("utf-8", "replace")
    try:
        for _ in range(120):
            ready = docker("exec", "-i", TEST_CONTAINER, "/usr/local/bin/psql", "-X", "-q", "-U", "aios",
                           "-d", "aios", stdin=b"SELECT 1;\n")
            if ready.returncode == 0:
                break
            time.sleep(0.25)
        else:
            pytest.fail("disposable PostgreSQL did not become ready")

        monkeypatch.setattr(helper, "POSTGRES_CONTAINER", TEST_CONTAINER)
        monkeypatch.setattr(
            helper, "CONTAINER_INSPECT_ARGV",
            (helper.DOCKER, "inspect", "--format", "{{.Name}}|{{.State.Running}}|{{.Config.Image}}", TEST_CONTAINER),
        )
        monkeypatch.setattr(
            helper, "ADMIN_ARGV",
            (helper.DOCKER, "exec", "-i", TEST_CONTAINER, helper.CONTAINER_PSQL,
             "-X", "-A", "-t", "-q", "-v", "ON_ERROR_STOP=1", "-h", helper.ADMIN_PG_SOCKET,
             "-p", helper.PG_PORT, "-U", helper.ADMIN_ROLE, "-d", helper.DATABASE),
        )
        yield
    finally:
        docker("stop", "--time", "1", TEST_CONTAINER)


def test_disposable_container_admin_lifecycle(disposable_postgres):
    postgres = helper.Postgres()
    for migration in (
        "0002_create_material_stock.up.sql",
        "0003_create_material_receipt_inventory_movement.up.sql",
    ):
        sql = (ROOT / "migrations/postgres" / migration).read_bytes()
        assert postgres._admin(sql).returncode == 0

    postgres.preflight()
    rollback_sql = b"BEGIN; CREATE ROLE aios_writer_bootstrap_rollback_probe NOLOGIN; ROLLBACK;\n"
    assert postgres._admin(rollback_sql).returncode == 0
    absent = postgres._admin(
        b"SELECT rolname FROM pg_roles WHERE rolname='aios_writer_bootstrap_rollback_probe';\n"
    )
    assert absent.returncode == 0 and not absent.stdout.strip()

    candidate = helper.Secret(b"A" * 43)
    posting = helper.Secret(b"B" * 43)
    assert postgres.provision(candidate, posting)
    assert postgres.reconcile() is helper.LifecycleState.DB_COMMITTED
    postgres.compensate()
    assert postgres.verify_disabled()


def test_disposable_container_rejects_wrong_admin_identity(disposable_postgres, monkeypatch):
    monkeypatch.setattr(helper, "ADMIN_ROLE", "postgres")
    with pytest.raises(helper.BootstrapError, match="administrative identity preflight failed"):
        helper.Postgres().preflight()
