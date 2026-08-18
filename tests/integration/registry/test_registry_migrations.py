import os
import unittest
import uuid
from pathlib import Path

import psycopg
from psycopg import conninfo, sql
from psycopg.types.json import Jsonb


TEST_DATABASE_URL = os.environ.get("AIOS_REGISTRY_TEST_DATABASE_URL")
ROOT = Path(__file__).resolve().parents[3]
UP = (ROOT / "migrations/postgres/0001_create_registry_records.up.sql").read_text()
DOWN = (ROOT / "migrations/postgres/0001_create_registry_records.down.sql").read_text()


@unittest.skipUnless(
    TEST_DATABASE_URL,
    "AIOS_REGISTRY_TEST_DATABASE_URL is required for isolated PostgreSQL tests",
)
class RegistryMigrationIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_apply_catalog_reverse_and_reapply(self):
        schema = "aios_registry_migration_" + uuid.uuid4().hex
        async with await psycopg.AsyncConnection.connect(
            TEST_DATABASE_URL, autocommit=True
        ) as admin:
            await admin.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
        scoped_url = conninfo.make_conninfo(
            TEST_DATABASE_URL, options=f"-csearch_path={schema}"
        )
        try:
            async with await psycopg.AsyncConnection.connect(
                scoped_url, autocommit=True
            ) as connection:
                await connection.execute(UP)
                columns = await (
                    await connection.execute(
                        """
                        SELECT column_name, data_type, is_nullable, is_identity
                        FROM information_schema.columns
                        WHERE table_schema = %s AND table_name = 'registry_records'
                        ORDER BY ordinal_position
                        """,
                        (schema,),
                    )
                ).fetchall()
                self.assertEqual(
                    columns,
                    [
                        ("record_id", "bigint", "NO", "YES"),
                        ("identity_ref", "text", "NO", "NO"),
                        ("represented_media_type", "text", "NO", "NO"),
                        ("metadata", "jsonb", "NO", "NO"),
                        ("relationships", "jsonb", "NO", "NO"),
                        ("manifest_ref", "text", "NO", "NO"),
                        ("registration_status", "text", "YES", "NO"),
                        ("storage_path", "text", "YES", "NO"),
                        ("source_url", "text", "YES", "NO"),
                    ],
                )
                constraints = await (
                    await connection.execute(
                        """
                        SELECT contype, pg_get_constraintdef(oid)
                        FROM pg_constraint
                        WHERE conrelid = %s::regclass
                        ORDER BY contype, conname
                        """,
                        ("registry_records",),
                    )
                ).fetchall()
                self.assertEqual([kind for kind, _ in constraints], ["c", "c", "p"])
                definitions = " ".join(definition for _, definition in constraints)
                self.assertIn("jsonb_typeof(metadata)", definitions)
                self.assertIn("jsonb_typeof(relationships)", definitions)
                indexes = await (
                    await connection.execute(
                        """
                        SELECT indexdef FROM pg_indexes
                        WHERE schemaname = %s AND tablename = 'registry_records'
                        """,
                        (schema,),
                    )
                ).fetchall()
                self.assertEqual(len(indexes), 1)
                self.assertIn("PRIMARY KEY", constraints[-1][1])
                self.assertNotIn("bytea", " ".join(str(row) for row in columns).lower())

                for invalid_metadata in ([], 7, "text"):
                    with self.subTest(metadata=invalid_metadata):
                        with self.assertRaises(psycopg.errors.CheckViolation):
                            await connection.execute(
                                """
                                INSERT INTO registry_records
                                (identity_ref, represented_media_type, metadata, manifest_ref)
                                VALUES ('i', 'text', %s, 'm')
                                """,
                                (Jsonb(invalid_metadata),),
                            )
                for invalid_relationships in ({}, 7, "text"):
                    with self.subTest(relationships=invalid_relationships):
                        with self.assertRaises(psycopg.errors.CheckViolation):
                            await connection.execute(
                                """
                                INSERT INTO registry_records
                                (identity_ref, represented_media_type, metadata, relationships, manifest_ref)
                                VALUES ('i', 'text', '{}'::jsonb, %s, 'm')
                                """,
                                (Jsonb(invalid_relationships),),
                            )
                await connection.execute(
                    """
                    INSERT INTO registry_records
                    (identity_ref, represented_media_type, metadata, relationships, manifest_ref)
                    VALUES ('valid', 'text', %s, %s, 'manifest:valid')
                    """,
                    (Jsonb({"structured": True}), Jsonb([])),
                )

                await connection.execute(DOWN)
                exists = await (
                    await connection.execute(
                        "SELECT to_regclass('registry_records')"
                    )
                ).fetchone()
                self.assertEqual(exists, (None,))
                await connection.execute(UP)
                exists = await (
                    await connection.execute(
                        "SELECT to_regclass('registry_records')"
                    )
                ).fetchone()
                self.assertEqual(exists, ("registry_records",))
        finally:
            async with await psycopg.AsyncConnection.connect(
                TEST_DATABASE_URL, autocommit=True
            ) as admin:
                await admin.execute(
                    sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema))
                )


if __name__ == "__main__":
    unittest.main()
