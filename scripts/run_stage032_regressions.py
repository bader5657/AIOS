#!/usr/bin/env python3
"""Run mandatory Stage 0.32 PostgreSQL tests in an isolated environment."""

from __future__ import annotations

import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
IMAGE = "postgres:17-alpine"
DB = "aios_material_disposable_stage032"
ADMIN_PASSWORD = "stage032-admin-" + secrets.token_hex(12)
CONTAINER = "aios-stage032-test-" + secrets.token_hex(6)


def free_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    if port == 5432 or port < 1024:
        return free_port()
    return port


def closed(port: int) -> bool:
    with socket.socket() as probe:
        probe.settimeout(0.2)
        return probe.connect_ex(("127.0.0.1", port)) != 0


def main() -> int:
    if os.environ.get("AIOS_STAGE032_DISPOSABLE_TEST_OPT_IN") != "1":
        print("Stage 0.32 infrastructure unavailable: explicit disposable-test opt-in required", file=sys.stderr)
        return 2
    port = free_port()
    command = [
        "docker", "run", "--detach", "--rm", "--network", "host",
        "--name", CONTAINER, "--tmpfs", "/var/lib/postgresql/data:rw,noexec,nosuid",
        "-e", f"POSTGRES_PASSWORD={ADMIN_PASSWORD}", "-e", f"POSTGRES_DB={DB}",
        IMAGE, "postgres", "-c", "listen_addresses=127.0.0.1", "-c", f"port={port}",
    ]
    started = False
    try:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        if result.returncode:
            print("Stage 0.32 infrastructure unavailable: disposable PostgreSQL 17 could not start", file=sys.stderr)
            return 2
        started = True
        deadline = time.monotonic() + 30
        while closed(port) and time.monotonic() < deadline:
            time.sleep(0.1)
        if closed(port):
            print("Stage 0.32 infrastructure unavailable: disposable listener was not ready", file=sys.stderr)
            return 2

        # Deliberately do not inherit dotenv/runtime configuration or secret variables.
        env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "LANG": os.environ.get("LANG", "C.UTF-8"),
            "LC_ALL": os.environ.get("LC_ALL", "C.UTF-8"),
            "PYTHONPATH": str(ROOT),
            "PYTHONDONTWRITEBYTECODE": "1",
            "AIOS_MATERIAL_DISPOSABLE_TESTS": "1",
            "AIOS_MATERIAL_TEST_DATABASE_URL":
                f"postgresql://postgres:{ADMIN_PASSWORD}@127.0.0.1:{port}/{DB}?sslmode=disable",
            "AIOS_STAGE032_SENTINEL": "stage032-output-secret-sentinel",
        }
        pytest = [sys.executable, "-m", "pytest", "-q", "-ra", "--tb=short",
                  "tests/integration/business_context/test_stage032_postgres.py",
                  "tests/unit/app/material_receipts/test_stage032_idempotency.py"]
        return subprocess.run(pytest, cwd=ROOT, env=env).returncode
    finally:
        if started:
            subprocess.run(["docker", "rm", "-f", CONTAINER], capture_output=True)
            deadline = time.monotonic() + 10
            while not closed(port) and time.monotonic() < deadline:
                time.sleep(0.1)
            if not closed(port):
                print("Stage 0.32 cleanup failure: disposable listener remains open", file=sys.stderr)
                raise SystemExit(3)


if __name__ == "__main__":
    raise SystemExit(main())
