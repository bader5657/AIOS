import inspect
import os
import unittest
import uuid
from pathlib import Path

import psycopg
from psycopg import conninfo, sql
from psycopg.types.json import Jsonb

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
class PostgresRegistryIsolationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.schema = "aios_registry_isolation_" + uuid.uuid4().hex
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

    def input(self, identity_ref="identity:isolation"):
        return RegistryPersistenceInput(
            identity_ref=identity_ref,
            represented_media_type="text",
            metadata={"value": "committed"},
            relationships=[],
            manifest_ref="manifest:isolation",
            registration_status="before",
            storage_path="/test/original",
        )

    def read_only_url(self):
        return conninfo.make_conninfo(
            TEST_DATABASE_URL,
            options=(
                f"-csearch_path={self.schema} "
                "-cdefault_transaction_read_only=on"
            ),
        )

    async def test_actual_registry_isolation_is_read_committed(self):
        async with await psycopg.AsyncConnection.connect(
            self.scoped_url
        ) as connection:
            async with connection.transaction():
                await connection.execute(
                    "SET TRANSACTION ISOLATION LEVEL READ COMMITTED"
                )
                observed = await (
                    await connection.execute("SHOW transaction_isolation")
                ).fetchone()
        self.assertEqual(observed, ("read committed",))
        runtime_source = inspect.getsource(postgres_registry)
        self.assertIn(
            "SET TRANSACTION ISOLATION LEVEL READ COMMITTED", runtime_source
        )

    async def test_commit_is_visible_to_later_registry_connection(self):
        registered = await self.registry.register(self.input())
        later_registry = PostgresRegistry(self.scoped_url)
        observed = await later_registry.read(registered.record_id)
        self.assertEqual(observed, registered)
        self.assertEqual(observed.metadata, {"value": "committed"})

    async def test_rollback_is_invisible_and_next_operation_is_independent(self):
        registered = await self.registry.register(self.input())
        failing_registry = PostgresRegistry(self.read_only_url())
        with self.assertRaises(RegistryPersistenceError):
            await failing_registry.update(
                registered.record_id,
                RegistryUpdate(
                    metadata={"value": "rolled-back"},
                    registration_status="rolled-back",
                ),
            )

        later_registry = PostgresRegistry(self.scoped_url)
        observed = await later_registry.read(registered.record_id)
        self.assertEqual(observed.metadata, {"value": "committed"})
        self.assertEqual(observed.registration_status, "before")

        independent = await later_registry.register(
            self.input(identity_ref="identity:after-rollback")
        )
        self.assertGreater(independent.record_id, registered.record_id)
        self.assertEqual(
            await PostgresRegistry(self.scoped_url).read(independent.record_id),
            independent,
        )

    async def test_concurrent_reader_never_observes_dirty_update(self):
        registered = await self.registry.register(self.input())
        async with await psycopg.AsyncConnection.connect(
            self.scoped_url
        ) as writer:
            async with writer.transaction():
                isolation = await (
                    await writer.execute("SHOW transaction_isolation")
                ).fetchone()
                self.assertEqual(isolation, ("read committed",))
                await writer.execute(
                    """
                    UPDATE registry_records
                    SET metadata = %s, registration_status = %s
                    WHERE record_id = %s
                    """,
                    (
                        Jsonb({"value": "uncommitted"}),
                        "after",
                        registered.record_id,
                    ),
                )
                concurrent = await PostgresRegistry(self.scoped_url).read(
                    registered.record_id
                )
                self.assertEqual(concurrent.metadata, {"value": "committed"})
                self.assertEqual(concurrent.registration_status, "before")

        after_commit = await PostgresRegistry(self.scoped_url).read(
            registered.record_id
        )
        self.assertEqual(after_commit.metadata, {"value": "uncommitted"})
        self.assertEqual(after_commit.registration_status, "after")

    def test_no_same_row_or_lost_update_policy_is_introduced(self):
        source = inspect.getsource(postgres_registry).lower()
        for marker in (
            "select for update",
            "serializable",
            "optimistic",
            "compare-and-swap",
            "version_column",
            "lost_update",
            "retry",
        ):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, source)


if __name__ == "__main__":
    unittest.main()
