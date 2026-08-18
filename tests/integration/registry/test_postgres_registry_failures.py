import inspect
import os
import socket
import time
import unittest
import uuid
from pathlib import Path
from unittest.mock import AsyncMock, patch

import psycopg
from psycopg import conninfo, sql

from core.registry import postgres_registry
from core.registry.postgres_registry import (
    PostgresRegistry,
    RegistryPersistenceError,
    RegistryPersistenceInput,
    RegistryUpdate,
)


TEST_DATABASE_URL = os.environ.get("AIOS_REGISTRY_TEST_DATABASE_URL")
ROOT = Path(__file__).resolve().parents[3]
UP = (ROOT / "migrations/postgres/0001_create_registry_records.up.sql").read_text()


@unittest.skipUnless(
    TEST_DATABASE_URL,
    "AIOS_REGISTRY_TEST_DATABASE_URL is required for isolated PostgreSQL tests",
)
class PostgresRegistryFailureTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.schema = "aios_registry_failures_" + uuid.uuid4().hex
        async with await psycopg.AsyncConnection.connect(
            TEST_DATABASE_URL, autocommit=True
        ) as admin:
            await admin.execute(
                sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.schema))
            )
        self.scoped_url = conninfo.make_conninfo(
            TEST_DATABASE_URL, options=f"-csearch_path={self.schema}"
        )
        async with await psycopg.AsyncConnection.connect(
            self.scoped_url, autocommit=True
        ) as connection:
            await connection.execute(UP)
        self.registry = PostgresRegistry(self.scoped_url)

    async def asyncTearDown(self):
        async with await psycopg.AsyncConnection.connect(
            TEST_DATABASE_URL, autocommit=True
        ) as admin:
            await admin.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(
                    sql.Identifier(self.schema)
                )
            )

    def input(self, identity_ref="identity:failure"):
        return RegistryPersistenceInput(
            identity_ref=identity_ref,
            represented_media_type="text",
            metadata={"value": "before", "unchanged": True},
            relationships=[{"ref": "identity:parent"}],
            manifest_ref="manifest:failure",
            registration_status="before",
            storage_path="/test/original",
            source_url="https://example.test/original",
        )

    def read_only_url(self):
        return conninfo.make_conninfo(
            TEST_DATABASE_URL,
            options=(
                f"-csearch_path={self.schema} "
                "-cdefault_transaction_read_only=on"
            ),
        )

    async def count_rows(self):
        async with await psycopg.AsyncConnection.connect(
            self.scoped_url
        ) as connection:
            return (
                await (
                    await connection.execute(
                        "SELECT count(*) FROM registry_records"
                    )
                ).fetchone()
            )[0]

    async def test_register_persistence_failure_is_atomic_and_not_retried(self):
        failing_registry = PostgresRegistry(self.read_only_url())
        with self.assertRaises(RegistryPersistenceError):
            await failing_registry.register(self.input())
        self.assertEqual(await self.count_rows(), 0)

        independent = await self.registry.register(
            self.input(identity_ref="identity:independent")
        )
        self.assertEqual(await self.count_rows(), 1)
        self.assertEqual(await self.registry.read(independent.record_id), independent)

    async def test_read_not_found_is_none(self):
        self.assertIsNone(await self.registry.read(9_999_999))

    async def test_read_database_failure_is_registry_local(self):
        empty_schema = "aios_registry_empty_" + uuid.uuid4().hex
        async with await psycopg.AsyncConnection.connect(
            TEST_DATABASE_URL, autocommit=True
        ) as admin:
            await admin.execute(
                sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(empty_schema))
            )
        empty_url = conninfo.make_conninfo(
            TEST_DATABASE_URL, options=f"-csearch_path={empty_schema}"
        )
        try:
            with self.assertRaises(RegistryPersistenceError):
                await PostgresRegistry(empty_url).read(1)
        finally:
            async with await psycopg.AsyncConnection.connect(
                TEST_DATABASE_URL, autocommit=True
            ) as admin:
                await admin.execute(
                    sql.SQL("DROP SCHEMA {} CASCADE").format(
                        sql.Identifier(empty_schema)
                    )
                )

    async def test_update_not_found_is_none(self):
        result = await self.registry.update(
            9_999_999, RegistryUpdate(registration_status="missing")
        )
        self.assertIsNone(result)

    async def test_empty_update_never_opens_connection(self):
        connect = AsyncMock()
        with patch.object(
            postgres_registry.psycopg.AsyncConnection, "connect", connect
        ):
            with self.assertRaises(ValueError):
                await self.registry.update(1, RegistryUpdate())
        connect.assert_not_awaited()

    async def test_multifield_update_failure_rolls_back_every_field(self):
        registered = await self.registry.register(self.input())
        failing_registry = PostgresRegistry(self.read_only_url())
        with self.assertRaises(RegistryPersistenceError):
            await failing_registry.update(
                registered.record_id,
                RegistryUpdate(
                    metadata={"value": "failed", "unchanged": False},
                    relationships=[],
                    registration_status="failed",
                    storage_path="/test/failed",
                    source_url=None,
                ),
            )

        observed = await PostgresRegistry(self.scoped_url).read(
            registered.record_id
        )
        self.assertEqual(observed, registered)

    async def test_unavailable_loopback_endpoint_fails_once_without_fallback(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind(("127.0.0.1", 0))
            unavailable_port = probe.getsockname()[1]
        unavailable_url = conninfo.make_conninfo(
            "",
            host="127.0.0.1",
            port=unavailable_port,
            dbname="aios_registry_unavailable_test",
            user="aios_registry_unavailable_test",
            password="disposable-test-only",
            connect_timeout=1,
        )
        original_connect = psycopg.AsyncConnection.connect
        counted_connect = AsyncMock(side_effect=original_connect)
        started = time.monotonic()
        with (
            patch.dict(
                os.environ,
                {"AIOS_REGISTRY_TEST_DATABASE_URL": TEST_DATABASE_URL},
                clear=True,
            ),
            patch.object(
                postgres_registry.psycopg.AsyncConnection,
                "connect",
                counted_connect,
            ),
        ):
            with self.assertRaises(RegistryPersistenceError):
                await PostgresRegistry(unavailable_url).read(1)
        self.assertEqual(counted_connect.await_count, 1)
        self.assertLess(time.monotonic() - started, 5)
        self.assertNotIn("AIOS_REGISTRY_DATABASE_URL", os.environ)

    def test_retry_storage_manifest_and_binary_boundaries_are_absent(self):
        source = inspect.getsource(postgres_registry).lower()
        for marker in (
            "retry",
            "backoff",
            "sleep(",
            "core.storage",
            "document_manifest",
            "unlink(",
            "remove(",
            "rename(",
            "replace(",
            "bytea",
            "base64",
            "original_binary",
            "original_body",
        ):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, source)
        self.assertIn("manifest_ref", source)
        self.assertIn("storage_path", source)
        self.assertFalse(hasattr(postgres_registry, "Registry" + "Entry"))


if __name__ == "__main__":
    unittest.main()
