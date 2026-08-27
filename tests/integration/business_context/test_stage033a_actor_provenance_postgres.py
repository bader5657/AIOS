"""Permanent disposable PostgreSQL proof for Stage 0.33A."""

from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
import unittest
import uuid

import psycopg

from tests.integration.business_context.disposable_postgres import OPT_IN, admit_disposable_postgres


ROOT = Path(__file__).resolve().parents[3]
MIGRATIONS = ROOT / "migrations/postgres"
STOCK_UP = (MIGRATIONS / "0002_create_material_stock.up.sql").read_text()
STOCK_DOWN = (MIGRATIONS / "0002_create_material_stock.down.sql").read_text()
RECEIPT_UP = (MIGRATIONS / "0003_create_material_receipt_inventory_movement.up.sql").read_text()
RECEIPT_DOWN = (MIGRATIONS / "0003_create_material_receipt_inventory_movement.down.sql").read_text()
STAGE032_UP = (MIGRATIONS / "0004_add_material_receipt_source_active_uniqueness.up.sql").read_text()
STAGE032_DOWN = (MIGRATIONS / "0004_add_material_receipt_source_active_uniqueness.down.sql").read_text()
UP = (MIGRATIONS / "0005_add_material_receipt_creator_provenance.up.sql").read_text()
DOWN = (MIGRATIONS / "0005_add_material_receipt_creator_provenance.down.sql").read_text()
ROLE = "aios_material_receipt_candidate_writer"
CONSTRAINT = "material_receipts_created_by_actor_reference_valid"
INDEX = "material_receipts_source_asset_active_uidx"
VALID = "operator:550e8400-e29b-41d4-a716-446655440000"
TEST_URL = os.environ.get("AIOS_MATERIAL_TEST_DATABASE_URL")


@unittest.skipUnless(TEST_URL or os.environ.get(OPT_IN), "disposable PostgreSQL configuration is required")
class Stage033AProvenancePostgresTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.target = admit_disposable_postgres(TEST_URL)
        async with await psycopg.AsyncConnection.connect(self.target.url, autocommit=True) as db:
            await db.execute(f"CREATE ROLE {ROLE} NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS")
            await db.execute(STOCK_UP)
            await db.execute(RECEIPT_UP)
            await db.execute(STAGE032_UP)
            self.before_indexes = tuple(await (await db.execute("SELECT indexname,indexdef FROM pg_indexes WHERE schemaname='public' ORDER BY indexname")).fetchall())
            self.before_roles = tuple(await (await db.execute("SELECT rolname,rolsuper,rolcreatedb,rolcreaterole,rolcanlogin FROM pg_roles ORDER BY rolname")).fetchall())
            await db.execute(UP)

    async def asyncTearDown(self) -> None:
        async with await psycopg.AsyncConnection.connect(self.target.url, autocommit=True) as db:
            exists = (await (await db.execute("SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='material_receipts' AND column_name='created_by_actor_reference'")).fetchone())
            if exists:
                await db.execute(DOWN)
            await db.execute(STAGE032_DOWN)
            await db.execute(RECEIPT_DOWN)
            await db.execute(STOCK_DOWN)
            await db.execute(f"DROP ROLE {ROLE}")

    async def insert(self, actor) -> None:
        async with await psycopg.AsyncConnection.connect(self.target.url, autocommit=True) as db:
            await db.execute("INSERT INTO public.material_receipts(receipt_id,supplier_name,received_at,source_asset_reference,created_by_actor_reference) VALUES(%s,'Stage 033A',%s,%s,%s)", (uuid.uuid4(), datetime.now(timezone.utc), "asset:" + uuid.uuid4().hex, actor))

    async def test_up_schema_constraint_grant_and_preservation_are_exact(self) -> None:
        async with await psycopg.AsyncConnection.connect(self.target.url) as db:
            column = await (await db.execute("SELECT data_type,is_nullable,column_default FROM information_schema.columns WHERE table_schema='public' AND table_name='material_receipts' AND column_name='created_by_actor_reference'")).fetchone()
            constraint = await (await db.execute("SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid='public.material_receipts'::regclass AND conname=%s", (CONSTRAINT,))).fetchone()
            indexes = tuple(await (await db.execute("SELECT indexname,indexdef FROM pg_indexes WHERE schemaname='public' ORDER BY indexname")).fetchall())
            roles = tuple(await (await db.execute("SELECT rolname,rolsuper,rolcreatedb,rolcreaterole,rolcanlogin FROM pg_roles ORDER BY rolname")).fetchall())
            grant = await (await db.execute("SELECT has_column_privilege(%s,'public.material_receipts','created_by_actor_reference','INSERT'),has_column_privilege(%s,'public.material_receipts','created_by_actor_reference','UPDATE')", (ROLE, ROLE))).fetchone()
        self.assertEqual(column, ("text", "NO", None))
        self.assertIn("operator:", constraint[0]); self.assertIn("4[0-9a-f]", constraint[0]); self.assertIn("[89ab]", constraint[0])
        self.assertEqual(indexes, self.before_indexes); self.assertEqual(roles, self.before_roles)
        self.assertEqual(grant, (True, False)); self.assertTrue(any(name == INDEX for name, _ in indexes))

    async def test_database_check_accepts_only_canonical_operator_uuidv4(self) -> None:
        await self.insert(VALID)
        rejected = [
            None, "", VALID.upper(), "operator:6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            "operator:9073926b-929f-31c2-abc9-fad77ae3e8eb",
            "operator:4d73d0f2-68c3-5c4c-8d58-7f97e9275c8d",
            "operator:00000000-0000-0000-0000-000000000000", "operator:not-a-uuid",
            "operator:550e8400e29b41d4a716446655440000", "operator:{550e8400-e29b-41d4-a716-446655440000}",
            " " + VALID, VALID + " ", VALID.replace("operator:", "reviewer:"), VALID.replace("operator:", "system:"),
        ]
        for actor in rejected:
            with self.subTest(actor=actor), self.assertRaises((psycopg.errors.CheckViolation, psycopg.errors.NotNullViolation)):
                await self.insert(actor)

    async def test_down_and_up_lifecycle_is_disposable_and_exact(self) -> None:
        async with await psycopg.AsyncConnection.connect(self.target.url, autocommit=True) as db:
            await db.execute(DOWN)
            column = await (await db.execute("SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='material_receipts' AND column_name='created_by_actor_reference'")).fetchone()
            self.assertIsNone(column)
            self.assertTrue((await (await db.execute("SELECT to_regclass('public.material_receipts_source_asset_active_uidx')")).fetchone())[0])
            await db.execute(UP)
        await self.insert(VALID)


if __name__ == "__main__":
    unittest.main()
