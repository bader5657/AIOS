import os
import unittest
import uuid
from pathlib import Path

import psycopg
from psycopg import conninfo, sql

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
class PostgresRegistryIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.schema = "aios_registry_runtime_" + uuid.uuid4().hex
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

    def input(self, **overrides):
        values = {
            "identity_ref": "identity:1",
            "represented_media_type": "text",
            "metadata": {"nested": {"count": 2}},
            "relationships": [{"kind": "parent", "ref": "identity:0"}],
            "manifest_ref": "manifest:1",
        }
        values.update(overrides)
        return RegistryPersistenceInput(**values)

    async def test_register_read_and_json_round_trip(self):
        registered = await self.registry.register(self.input())
        self.assertIsInstance(registered.record_id, int)
        self.assertGreater(registered.record_id, 0)
        self.assertEqual(registered.metadata, {"nested": {"count": 2}})
        self.assertEqual(
            registered.relationships,
            [{"kind": "parent", "ref": "identity:0"}],
        )
        self.assertIsNone(registered.registration_status)
        self.assertIsNone(registered.storage_path)
        self.assertIsNone(registered.source_url)
        self.assertEqual(await self.registry.read(registered.record_id), registered)
        self.assertIsNone(await self.registry.read(9_999_999))

    async def test_optional_values_and_allowed_update_preserve_immutables(self):
        registered = await self.registry.register(
            self.input(
                registration_status="pending",
                storage_path="/isolated/item",
                source_url="https://example.test/item",
            )
        )
        updated = await self.registry.update(
            registered.record_id,
            RegistryUpdate(
                metadata={"changed": True},
                relationships=[],
                registration_status=None,
                storage_path="/isolated/new",
                source_url=None,
            ),
        )
        self.assertIsNotNone(updated)
        self.assertEqual(updated.identity_ref, registered.identity_ref)
        self.assertEqual(
            updated.represented_media_type, registered.represented_media_type
        )
        self.assertEqual(updated.manifest_ref, registered.manifest_ref)
        self.assertEqual(updated.metadata, {"changed": True})
        self.assertEqual(updated.relationships, [])
        self.assertIsNone(updated.registration_status)
        self.assertEqual(updated.storage_path, "/isolated/new")
        self.assertIsNone(updated.source_url)

    async def test_update_not_found_and_empty_patch(self):
        self.assertIsNone(
            await self.registry.update(
                9_999_999, RegistryUpdate(registration_status="missing")
            )
        )
        with self.assertRaises(ValueError):
            await self.registry.update(9_999_999, RegistryUpdate())

    async def test_failed_update_rolls_back_scoped_transaction(self):
        registered = await self.registry.register(
            self.input(registration_status="before")
        )
        async with await psycopg.AsyncConnection.connect(
            self.scoped_url, autocommit=True
        ) as connection:
            await connection.execute(
                """
                ALTER TABLE registry_records
                ADD CONSTRAINT test_status_failure
                CHECK (registration_status <> 'reject')
                """
            )
        with self.assertRaises(RegistryPersistenceError):
            await self.registry.update(
                registered.record_id,
                RegistryUpdate(
                    metadata={"would": "change"},
                    registration_status="reject",
                ),
            )
        persisted = await self.registry.read(registered.record_id)
        self.assertEqual(persisted.metadata, registered.metadata)
        self.assertEqual(persisted.registration_status, "before")

    async def test_schema_has_no_original_content_column(self):
        async with await psycopg.AsyncConnection.connect(
            self.scoped_url
        ) as connection:
            columns = await (
                await connection.execute(
                    """
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_schema = %s AND table_name = 'registry_records'
                    """,
                    (self.schema,),
                )
            ).fetchall()
        names = {name for name, _ in columns}
        types = {data_type for _, data_type in columns}
        self.assertNotIn("original_binary", names)
        self.assertNotIn("original_body", names)
        self.assertNotIn("bytea", types)


if __name__ == "__main__":
    unittest.main()
