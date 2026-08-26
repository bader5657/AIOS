from datetime import datetime, timezone
from decimal import Decimal
import os
from pathlib import Path
import unittest
import uuid

import psycopg
from psycopg import conninfo, sql


TEST_URL = os.environ.get("AIOS_MATERIAL_TEST_DATABASE_URL")
ROOT = Path(__file__).resolve().parents[3]
STOCK_SQL = (ROOT / "migrations/postgres/0002_create_material_stock.up.sql").read_text()
RECEIPT_SQL = (ROOT / "migrations/postgres/0003_create_material_receipt_inventory_movement.up.sql").read_text()


@unittest.skipUnless(TEST_URL, "AIOS_MATERIAL_TEST_DATABASE_URL is required")
class MaterialWriterSecurityBoundaryTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        parsed = conninfo.conninfo_to_dict(TEST_URL)
        if parsed.get("dbname") == "aios":
            self.fail("production database name is prohibited for disposable tests")
        suffix = uuid.uuid4().hex[:12]
        self.schema = "security_" + suffix
        self.candidate = "candidate_" + suffix
        self.posting = "posting_" + suffix
        self.reader = "reader_" + suffix
        self.password = "disposable-test-only"
        async with await psycopg.AsyncConnection.connect(TEST_URL, autocommit=True) as admin:
            for role in (self.candidate, self.posting, self.reader):
                await admin.execute(
                    sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(
                        sql.Identifier(role), sql.Literal(self.password)
                    )
                )
            await admin.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.schema)))
        self.admin_url = conninfo.make_conninfo(TEST_URL, options=f"-csearch_path={self.schema}")
        async with await psycopg.AsyncConnection.connect(self.admin_url, autocommit=True) as con:
            await con.execute(STOCK_SQL); await con.execute(RECEIPT_SQL)
            await con.execute("CREATE TABLE unrelated_records (id integer)")
            schema = sql.Identifier(self.schema)
            for role in (self.candidate, self.posting, self.reader):
                await con.execute(sql.SQL("GRANT USAGE ON SCHEMA {} TO {}").format(schema, sql.Identifier(role)))
            await con.execute(sql.SQL("GRANT SELECT ON material_receipts, material_receipt_items, material_stock TO {}").format(sql.Identifier(self.candidate)))
            await con.execute(sql.SQL("GRANT INSERT (receipt_id,supplier_name,document_number,document_date,received_at,source_asset_reference), UPDATE (supplier_name,document_number,document_date,received_at,source_asset_reference,status,version,confirmed_version,confirmed_at,confirmation_actor_reference,updated_at) ON material_receipts TO {}").format(sql.Identifier(self.candidate)))
            await con.execute(sql.SQL("GRANT INSERT (receipt_item_id,receipt_id,line_number,candidate_material_description,canonical_display_name,size_description,specification,material_id,full_colly_count,qty_per_full_colly,partial_qty,total_qty,unit), UPDATE (line_number,candidate_material_description,canonical_display_name,size_description,specification,material_id,full_colly_count,qty_per_full_colly,partial_qty,total_qty,unit,status,updated_at) ON material_receipt_items TO {}").format(sql.Identifier(self.candidate)))
            await con.execute(sql.SQL("GRANT SELECT ON material_receipts,material_receipt_items,inventory_movements,material_stock TO {}").format(sql.Identifier(self.posting)))
            await con.execute(sql.SQL("GRANT UPDATE (status,updated_at) ON material_receipts,material_receipt_items TO {}").format(sql.Identifier(self.posting)))
            await con.execute(sql.SQL("GRANT INSERT (movement_id,material_id,movement_type,quantity_delta,unit,source_receipt_item_id,occurred_at,posting_actor_reference,balance_before,balance_after) ON inventory_movements TO {}").format(sql.Identifier(self.posting)))
            await con.execute(sql.SQL("GRANT UPDATE (stock_qty,updated_at) ON material_stock TO {}").format(sql.Identifier(self.posting)))
            await con.execute(sql.SQL("GRANT SELECT ON material_stock TO {}").format(sql.Identifier(self.reader)))
            material = uuid.uuid4(); receipt = uuid.uuid4(); item = uuid.uuid4(); now = datetime.now(timezone.utc)
            await con.execute("INSERT INTO material_stock VALUES (%s,'EF',0,'sheet',true,%s)", (material, now))
            await con.execute("INSERT INTO material_receipts (receipt_id,supplier_name,received_at,source_asset_reference) VALUES (%s,'Supplier',%s,'asset:test')", (receipt, now))
            await con.execute("INSERT INTO material_receipt_items (receipt_item_id,receipt_id,line_number,material_id,full_colly_count,qty_per_full_colly,partial_qty,total_qty,unit) VALUES (%s,%s,1,%s,1,1,0,1,'sheet')", (item, receipt, material))
            self.ids = material, receipt, item
        base = conninfo.conninfo_to_dict(TEST_URL)
        base.update(user=self.candidate, password=self.password,
                    options=f"-csearch_path={self.schema}")
        self.candidate_url = conninfo.make_conninfo(**base)
        base.update(user=self.posting)
        self.posting_url = conninfo.make_conninfo(**base)
        base.update(user=self.reader)
        self.reader_url = conninfo.make_conninfo(**base)

    async def asyncTearDown(self):
        async with await psycopg.AsyncConnection.connect(TEST_URL, autocommit=True) as admin:
            await admin.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(self.schema)))
            for role in (self.candidate, self.posting, self.reader):
                await admin.execute(sql.SQL("DROP ROLE {}").format(sql.Identifier(role)))

    async def denied(self, url, statement, parameters=()):
        with self.assertRaises(psycopg.errors.InsufficientPrivilege):
            async with await psycopg.AsyncConnection.connect(url, autocommit=True) as con:
                await con.execute(statement, parameters)

    async def test_candidate_denials(self):
        material, receipt, item = self.ids
        now = datetime.now(timezone.utc)
        await self.denied(self.candidate_url, "INSERT INTO inventory_movements (movement_id,material_id,movement_type,quantity_delta,unit,source_receipt_item_id,occurred_at,posting_actor_reference,balance_before,balance_after) VALUES (%s,%s,'RECEIPT',1,'sheet',%s,%s,'x',0,1)", (uuid.uuid4(), material, item, now))
        await self.denied(self.candidate_url, "UPDATE material_stock SET stock_qty=1")
        await self.denied(self.candidate_url, "DELETE FROM material_receipt_items")
        await self.denied(self.candidate_url, "DELETE FROM material_receipts")
        await self.denied(self.candidate_url, "INSERT INTO unrelated_records VALUES (1)")

    async def test_posting_denials(self):
        await self.denied(self.posting_url, "UPDATE material_receipts SET supplier_name='rewrite'")
        await self.denied(self.posting_url, "UPDATE material_receipt_items SET material_id=NULL")
        await self.denied(self.posting_url, "UPDATE material_receipt_items SET total_qty=2")
        await self.denied(self.posting_url, "UPDATE inventory_movements SET quantity_delta=2")
        await self.denied(self.posting_url, "DELETE FROM inventory_movements")
        await self.denied(self.posting_url, "TRUNCATE inventory_movements")
        await self.denied(self.posting_url, "UPDATE material_stock SET name='rewrite'")
        await self.denied(self.posting_url, "INSERT INTO unrelated_records VALUES (1)")

    async def test_reader_is_read_only(self):
        async with await psycopg.AsyncConnection.connect(self.reader_url) as con:
            row = await (await con.execute("SELECT count(*) FROM material_stock")).fetchone()
        self.assertEqual(row[0], 1)
        await self.denied(self.reader_url, "UPDATE material_stock SET stock_qty=1")
        await self.denied(self.reader_url, "SELECT * FROM material_receipts")


if __name__ == "__main__":
    unittest.main()
