import configparser
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SERVICE_PATH = ROOT / "deploy/systemd/aios.service"

class AIOSSystemdServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = SERVICE_PATH.read_text(encoding="utf-8")
        cls.unit = configparser.ConfigParser(interpolation=None, strict=True)
        cls.unit.optionxform = str
        cls.unit.read_string(cls.source)

    def test_exact_file_and_section_structure(self):
        self.assertTrue(SERVICE_PATH.is_file())
        self.assertEqual(self.unit.sections(), ["Unit", "Service", "Install"])
        for section in ("Unit", "Service", "Install"):
            self.assertEqual(self.source.count(f"[{section}]"), 1)

    def test_unit_identity_ordering_and_start_limits(self):
        unit = self.unit["Unit"]
        self.assertEqual(
            set(unit),
            {
                "Description", "Wants", "After", "StartLimitIntervalSec",
                "StartLimitBurst",
            },
        )
        self.assertEqual(
            unit["Description"], "AIOS Production Telegram Application"
        )
        approved_targets = {"network-online.target", "docker.service"}
        self.assertEqual(set(unit["Wants"].split()), approved_targets)
        self.assertEqual(set(unit["After"].split()), approved_targets)
        self.assertNotIn("Requires", unit)
        self.assertEqual(unit["StartLimitIntervalSec"], "300s")
        self.assertEqual(unit["StartLimitBurst"], "5")
        self.assertNotIn("StartLimitIntervalSec", self.unit["Service"])
        self.assertNotIn("StartLimitBurst", self.unit["Service"])

    def test_service_identity_paths_and_single_exec_start(self):
        service = self.unit["Service"]
        self.assertEqual(
            set(service),
            {
                "Type", "User", "Group", "WorkingDirectory",
                "EnvironmentFile", "Environment", "ExecStartPre", "ExecStart",
                "Restart", "RestartSec", "TimeoutStopSec", "KillMode",
                "NoNewPrivileges", "PrivateTmp", "ReadOnlyPaths", "UMask",
            },
        )
        self.assertEqual(service["Type"], "simple")
        self.assertEqual(service["User"], "aiosadmin")
        self.assertEqual(service["Group"], "aiosadmin")
        self.assertEqual(service["WorkingDirectory"], "/opt/aios-src")
        self.assertEqual(
            service["EnvironmentFile"],
            "/opt/aios/runtime/config/runtime.env",
        )
        self.assertFalse(service["EnvironmentFile"].startswith("-"))
        self.assertEqual(
            self.source.count(
                "EnvironmentFile=/opt/aios/runtime/config/runtime.env"
            ),
            1,
        )
        self.assertEqual(
            service["ExecStart"],
            "/opt/aios/runtime/venv/bin/python "
            "-m core.adapters.telegram.main",
        )
        exec_starts = re.findall(r"(?m)^ExecStart=", self.source)
        self.assertEqual(len(exec_starts), 1)

    def test_source_runtime_separation_policy(self):
        service = self.unit["Service"]
        cache_environment = (
            "PYTHONPYCACHEPREFIX=/opt/aios/runtime/cache/pycache"
        )
        self.assertEqual(service["Environment"], cache_environment)
        self.assertEqual(
            self.source.count(f"Environment={cache_environment}"),
            1,
        )
        self.assertEqual(service["ReadOnlyPaths"], "/opt/aios-src")
        self.assertEqual(self.source.count("ReadOnlyPaths=/opt/aios-src"), 1)
        self.assertNotIn("Environment", self.unit["Unit"])
        self.assertNotIn("Environment", self.unit["Install"])
        self.assertNotIn("ReadOnlyPaths", self.unit["Unit"])
        self.assertNotIn("ReadOnlyPaths", self.unit["Install"])
        self.assertNotIn("PYTHONDONTWRITEBYTECODE", self.source)
        self.assertNotIn("ReadWritePaths", service)
        self.assertIsNone(
            re.search(
                r"(?m)^ReadWritePaths=.*(?:^|\s)/opt/aios-src(?:\s|$)",
                self.source,
            )
        )
        pycache_lines = [
            line for line in self.source.splitlines()
            if "PYTHONPYCACHEPREFIX" in line
        ]
        self.assertEqual(
            pycache_lines,
            [f"Environment={cache_environment}"],
        )

    def test_interpreter_only_environment_preflight(self):
        service = self.unit["Service"]
        self.assertEqual(
            sum(1 for line in self.source.splitlines() if line.startswith("ExecStartPre=")),
            1,
        )
        preflight = service["ExecStartPre"]
        self.assertTrue(
            preflight.startswith("/opt/aios/runtime/venv/bin/python -c ")
        )
        self.assertIn("os.environ.get('TELEGRAM_BOT_TOKEN')", preflight)
        self.assertIn("os.environ.get('AIOS_REGISTRY_DATABASE_URL')", preflight)
        self.assertIn("sys.exit", preflight)
        self.assertNotIn("AIOS_REGISTRY_TEST_DATABASE_URL", preflight)
        for prohibited in (
            "/bin/sh", "bash", "curl", "wget", " nc ", "pg_isready",
            "psql", "docker", "socket", "requests", "httpx", "psycopg",
            "print(",
        ):
            with self.subTest(prohibited=prohibited):
                self.assertNotIn(prohibited, preflight.lower())

    def test_restart_shutdown_and_hardening(self):
        service = self.unit["Service"]
        expected = {
            "Restart": "on-failure",
            "RestartSec": "10s",
            "TimeoutStopSec": "30s",
            "KillMode": "control-group",
            "NoNewPrivileges": "true",
            "PrivateTmp": "true",
            "UMask": "0027",
        }
        for directive, value in expected.items():
            with self.subTest(directive=directive):
                self.assertEqual(service[directive], value)
        self.assertNotIn("KillSignal", service)
        self.assertNotIn("StandardOutput", service)
        self.assertNotIn("StandardError", service)

    def test_install_target_and_single_process_topology(self):
        self.assertEqual(set(self.unit["Install"]), {"WantedBy"})
        self.assertEqual(self.unit["Install"]["WantedBy"], "multi-user.target")
        service = self.unit["Service"]
        self.assertNotIn("ExecStartPost", service)
        self.assertNotIn("PIDFile", service)
        for prohibited in (
            "@.service", "--workers", "supervisor", "celery", "nohup",
            "run_polling", "docker run", "docker compose",
        ):
            with self.subTest(prohibited=prohibited):
                self.assertNotIn(prohibited, self.source.lower())

    def test_prohibited_execution_and_secret_content_is_absent(self):
        lowered = self.source.lower()
        for prohibited in (
            "aios_registry_test_database_url", "docker-compose", "pg_isready",
            "psql", "alembic", "curl", "wget", "redis", "kafka",
            "rabbitmq", "celery", "ollama", "n8n", "hermes", "openclaw",
            "brain", "migrate", "migration", "schema", "prometheus",
            "grafana", "http://", "https://", "postgresql://", "password=",
        ):
            with self.subTest(prohibited=prohibited):
                self.assertNotIn(prohibited, lowered)
        self.assertIsNone(
            re.search(
                r"(?im)^\s*(TELEGRAM_BOT_TOKEN|AIOS_REGISTRY_DATABASE_URL)\s*=",
                self.source,
            )
        )

if __name__ == "__main__":
    unittest.main()
