from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[3]
MODULE_PATH = ROOT / "scripts/admin/bootstrap_material_writer_secrets.py"
SPEC = importlib.util.spec_from_file_location("writer_bootstrap_runtime_loopback_integration", MODULE_PATH)
assert SPEC and SPEC.loader
helper = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = helper
SPEC.loader.exec_module(helper)

TEST_CONTAINER = "aios-writer-runtime-loopback-integration"
TEST_NETWORK = "aios-writer-runtime-loopback-integration-net"
CANDIDATE_PASSWORD = b"candidate-loopback-integration-password"
POSTING_PASSWORD = b"posting-loopback-integration-password"


def docker(*argv: str, stdin: bytes = b"") -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["/usr/bin/docker", *argv], input=stdin, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )


@pytest.fixture
def isolated_network():
    if docker("network", "inspect", TEST_NETWORK).returncode == 0:
        pytest.fail(f"refusing to reuse existing network {TEST_NETWORK}")
    created = docker("network", "create", TEST_NETWORK)
    assert created.returncode == 0, created.stderr.decode("utf-8", "replace")
    try:
        yield TEST_NETWORK
    finally:
        docker("network", "rm", TEST_NETWORK)


@pytest.fixture
def loopback_postgres(monkeypatch, isolated_network):
    if not Path("/usr/bin/docker").is_file() or docker("info").returncode != 0:
        pytest.skip("Docker daemon unavailable")
    if docker("inspect", TEST_CONTAINER).returncode == 0:
        pytest.fail(f"refusing to reuse existing container {TEST_CONTAINER}")
    started = docker(
        "run", "--rm", "-d", "--network", isolated_network, "--name", TEST_CONTAINER,
        "-p", "127.0.0.1::5432",
        "-e", "POSTGRES_USER=aios", "-e", "POSTGRES_DB=aios",
        "-e", "POSTGRES_PASSWORD=disposable-admin-only",
        "-e", "POSTGRES_HOST_AUTH_METHOD=scram-sha-256",
        "--health-cmd", "/usr/local/bin/pg_isready -U aios -d aios",
        "--health-interval", "1s", "--health-retries", "30",
        "postgres:17-alpine",
    )
    assert started.returncode == 0, started.stderr.decode("utf-8", "replace")
    try:
        deadline = time.monotonic() + 30.0
        while time.monotonic() < deadline:
            ready = docker(
                "exec", "-i", TEST_CONTAINER, "/usr/local/bin/psql", "-X", "-A", "-t", "-q",
                "-v", "ON_ERROR_STOP=1", "-h", "/var/run/postgresql", "-U", "aios", "-d", "aios",
                stdin=b"SELECT 1;\n",
            )
            if ready.returncode == 0 and ready.stdout.strip() == b"1":
                break
            time.sleep(0.25)
        else:
            pytest.fail("disposable PostgreSQL readiness query timed out")

        publication = docker("port", TEST_CONTAINER, "5432/tcp")
        assert publication.returncode == 0
        endpoint = publication.stdout.decode("ascii").strip()
        assert endpoint.startswith("127.0.0.1:")
        port = endpoint.rsplit(":", 1)[1]
        assert port.isdigit()

        role_sql = f"""\
SET password_encryption = 'scram-sha-256';
CREATE ROLE {helper.CANDIDATE_LOGIN} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
  NOREPLICATION NOBYPASSRLS PASSWORD '{CANDIDATE_PASSWORD.decode()}';
CREATE ROLE {helper.POSTING_LOGIN} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
  NOREPLICATION NOBYPASSRLS PASSWORD '{POSTING_PASSWORD.decode()}';
""".encode("ascii")
        created = docker(
            "exec", "-i", TEST_CONTAINER, "/usr/local/bin/psql", "-X", "-q",
            "-v", "ON_ERROR_STOP=1", "-U", "aios", "-d", "aios", stdin=role_sql,
        )
        assert created.returncode == 0, created.stderr.decode("utf-8", "replace")

        monkeypatch.setattr(helper, "RUNTIME_PROBE_PORT", port)
        monkeypatch.setattr(helper, "RUNTIME_PROBE_ARGV", (sys.executable, "-I", "-"))
        yield port
    finally:
        docker("stop", "--time", "1", TEST_CONTAINER)


def test_real_scram_runtime_probes_use_only_numeric_loopback(loopback_postgres, capsys):
    port = loopback_postgres
    runner = helper.subprocess_runner
    postgres = helper.Postgres(runner)
    assert not postgres._probe(helper.POSTING_LOGIN, helper.Secret(b"wrong-password"))
    assert CANDIDATE_PASSWORD != POSTING_PASSWORD

    assert postgres._probe(helper.CANDIDATE_LOGIN, helper.Secret(CANDIDATE_PASSWORD))
    assert postgres._probe(helper.POSTING_LOGIN, helper.Secret(POSTING_PASSWORD))
    assert not postgres._probe(helper.CANDIDATE_LOGIN, helper.Secret(POSTING_PASSWORD))
    assert not postgres._probe(helper.POSTING_LOGIN, helper.Secret(CANDIDATE_PASSWORD))
    assert not postgres._probe(helper.CANDIDATE_LOGIN, helper.Secret(b"wrong-password"))
    captured = capsys.readouterr()
    assert CANDIDATE_PASSWORD.decode() not in captured.out + captured.err
    assert POSTING_PASSWORD.decode() not in captured.out + captured.err

    argv = (*helper.RUNTIME_PROBE_ARGV, helper.CANDIDATE_LOGIN)
    assert not helper.private_pgpass_probe(
        runner, argv, "localhost", port, helper.RUNTIME_PROBE_DATABASE,
        helper.CANDIDATE_LOGIN, helper.Secret(CANDIDATE_PASSWORD),
        helper.runtime_probe_program(),
    )

    inspected = docker(
        "inspect", "--format", '{{json (index .NetworkSettings.Ports "5432/tcp")}}',
        TEST_CONTAINER,
    )
    assert b"sslmode='disable'" in helper.runtime_probe_program()
    assert b"gssencmode='disable'" in helper.runtime_probe_program()
    bindings = json.loads(inspected.stdout)
    assert len(bindings) == 1
    assert bindings[0]["HostIp"] == "127.0.0.1"
    assert bindings[0]["HostPort"] == port
    assert helper.DOCKER not in argv
    assert b"/var/run/postgresql" not in helper.runtime_probe_program()
