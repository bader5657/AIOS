from datetime import datetime, timezone
from decimal import Decimal
import os
from pathlib import Path
import unittest
import uuid
from unittest.mock import AsyncMock, patch

import psycopg
from psycopg import conninfo, sql

from tests.integration.business_context.disposable_postgres import (
    OPT_IN,
    admit_disposable_postgres,
)


TEST_URL = os.environ.get("AIOS_MATERIAL_TEST_DATABASE_URL")
ROOT = Path(__file__).resolve().parents[3]
STOCK_SQL = (ROOT / "migrations/postgres/0002_create_material_stock.up.sql").read_text()
RECEIPT_SQL = (ROOT / "migrations/postgres/0003_create_material_receipt_inventory_movement.up.sql").read_text()
CREATOR = "operator:550e8400-e29b-41d4-a716-446655440000"


class DisposableAdmissionTests(unittest.TestCase):
    valid_url = (
        "postgresql://postgres:disposable-only@127.0.0.1:32888/"
        "aios_material_disposable_review"
    )
    admitted_environment = {OPT_IN: "1"}

    def assert_denied_without_connection(self, url, environment):
        connect = AsyncMock()
        with patch.object(psycopg.AsyncConnection, "connect", connect):
            with self.assertRaises(RuntimeError):
                admit_disposable_postgres(url, environment=environment)
        connect.assert_not_called()

    def test_missing_opt_in_and_otherwise_valid_target_are_denied(self):
        self.assert_denied_without_connection(self.valid_url, {})

    def test_production_database_and_endpoint_are_denied(self):
        self.assert_denied_without_connection(
            "postgresql://postgres:x@127.0.0.1:32888/aios",
            self.admitted_environment,
        )
        self.assert_denied_without_connection(
            "postgresql://postgres:x@127.0.0.1:5432/"
            "aios_material_disposable_review",
            self.admitted_environment,
        )

    def test_governed_and_unexpected_setup_identities_are_denied(self):
        for username in (
            "aios",
            "aios_material_receipt_candidate_runtime",
            "aios_material_inventory_posting_runtime",
            "aios_material_stock_reader",
            "unexpected_admin",
        ):
            url = (
                f"postgresql://{username}:x@127.0.0.1:32888/"
                "aios_material_disposable_review"
            )
            with self.subTest(username=username):
                self.assert_denied_without_connection(
                    url, self.admitted_environment
                )

    def test_governed_candidate_and_posting_passwords_are_denied(self):
        for key in (
            "AIOS_MATERIAL_RECEIPT_CANDIDATE_DB_PASSWORD",
            "AIOS_MATERIAL_INVENTORY_POSTING_DB_PASSWORD",
            "AIOS_MATERIAL_STOCK_DB_PASSWORD",
            "AIOS_MATERIAL_STOCK_READER_DB_PASSWORD",
        ):
            environment = {OPT_IN: "1", key: "governed-secret"}
            self.assert_denied_without_connection(
                "postgresql://postgres:governed-secret@127.0.0.1:32888/"
                "aios_material_disposable_review",
                environment,
            )

    def test_malformed_ambiguous_and_unexpected_targets_are_denied(self):
        for url in (
            "not a postgres target",
            "postgresql://postgres:x@localhost:32888/"
            "aios_material_disposable_review",
            "postgresql://postgres:x@127.0.0.1:32888/test_database",
            "postgresql://postgres@127.0.0.1:32888/"
            "aios_material_disposable_review",
            "postgresql://postgres:x@127.0.0.1:32888/"
            "aios_material_disposable_review?service=production",
        ):
            with self.subTest(url=url):
                self.assert_denied_without_connection(
                    url, self.admitted_environment
                )

    def test_positive_disposable_contract_is_admitted_without_mutation(self):
        target = admit_disposable_postgres(
            self.valid_url, environment=self.admitted_environment
        )
        self.assertEqual(target.host, "127.0.0.1")
        self.assertEqual(target.port, 32888)
        self.assertEqual(target.dbname, "aios_material_disposable_review")
        self.assertEqual(target.admin_user, "postgres")


@unittest.skipUnless(
    TEST_URL or os.environ.get(OPT_IN),
    "disposable PostgreSQL configuration is required",
)
class MaterialWriterSecurityBoundaryTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.target = admit_disposable_postgres(TEST_URL)
        suffix = uuid.uuid4().hex[:12]
        self.schema = "security_" + suffix
        self.candidate_writer = "candidate_writer_" + suffix
        self.candidate_runtime = "candidate_runtime_" + suffix
        self.posting_writer = "posting_writer_" + suffix
        self.posting_runtime = "posting_runtime_" + suffix
        self.reader = "reader_" + suffix
        self.password = "disposable-test-only"
        async with await psycopg.AsyncConnection.connect(
            self.target.url, autocommit=True
        ) as admin:
            for role in (self.candidate_writer, self.posting_writer):
                await admin.execute(
                    sql.SQL("CREATE ROLE {} NOLOGIN NOSUPERUSER NOCREATEDB "
                            "NOCREATEROLE NOREPLICATION NOBYPASSRLS").format(
                        sql.Identifier(role)
                    )
                )
            for role in (self.candidate_runtime, self.posting_runtime, self.reader):
                await admin.execute(
                    sql.SQL("CREATE ROLE {} LOGIN PASSWORD {} NOSUPERUSER "
                            "NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS").format(
                        sql.Identifier(role), sql.Literal(self.password)
                    )
                )
            await admin.execute(
                sql.SQL("GRANT {} TO {}").format(
                    sql.Identifier(self.candidate_writer),
                    sql.Identifier(self.candidate_runtime),
                )
            )
            await admin.execute(
                sql.SQL("GRANT {} TO {}").format(
                    sql.Identifier(self.posting_writer),
                    sql.Identifier(self.posting_runtime),
                )
            )
            await admin.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.schema)))
        self.admin_url = conninfo.make_conninfo(
            self.target.url, options=f"-csearch_path={self.schema}"
        )
        async with await psycopg.AsyncConnection.connect(self.admin_url, autocommit=True) as con:
            await con.execute(STOCK_SQL); await con.execute(RECEIPT_SQL)
            await con.execute("ALTER TABLE material_receipts ADD COLUMN created_by_actor_reference TEXT NOT NULL, ADD CONSTRAINT material_receipts_created_by_actor_reference_valid CHECK (created_by_actor_reference ~ '^operator:[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')")
            await con.execute("CREATE TABLE unrelated_records (id integer)")
            schema = sql.Identifier(self.schema)
            for role in (self.candidate_writer, self.posting_writer, self.reader):
                await con.execute(sql.SQL("GRANT USAGE ON SCHEMA {} TO {}").format(schema, sql.Identifier(role)))
            await con.execute(sql.SQL("GRANT SELECT ON material_receipts, material_receipt_items, material_stock TO {}").format(sql.Identifier(self.candidate_writer)))
            await con.execute(sql.SQL("GRANT INSERT (receipt_id,supplier_name,document_number,document_date,received_at,source_asset_reference,created_by_actor_reference), UPDATE (supplier_name,document_number,document_date,received_at,source_asset_reference,status,version,confirmed_version,confirmed_at,confirmation_actor_reference,updated_at) ON material_receipts TO {}").format(sql.Identifier(self.candidate_writer)))
            await con.execute(sql.SQL("GRANT INSERT (receipt_item_id,receipt_id,line_number,candidate_material_description,canonical_display_name,size_description,specification,material_id,full_colly_count,qty_per_full_colly,partial_qty,total_qty,unit), UPDATE (line_number,candidate_material_description,canonical_display_name,size_description,specification,material_id,full_colly_count,qty_per_full_colly,partial_qty,total_qty,unit,status,updated_at) ON material_receipt_items TO {}").format(sql.Identifier(self.candidate_writer)))
            await con.execute(sql.SQL("GRANT SELECT ON material_receipts,material_receipt_items,inventory_movements,material_stock TO {}").format(sql.Identifier(self.posting_writer)))
            await con.execute(sql.SQL("GRANT UPDATE (status,updated_at) ON material_receipts,material_receipt_items TO {}").format(sql.Identifier(self.posting_writer)))
            await con.execute(sql.SQL("GRANT INSERT (movement_id,material_id,movement_type,quantity_delta,unit,source_receipt_item_id,occurred_at,posting_actor_reference,balance_before,balance_after) ON inventory_movements TO {}").format(sql.Identifier(self.posting_writer)))
            await con.execute(sql.SQL("GRANT UPDATE (stock_qty,updated_at) ON material_stock TO {}").format(sql.Identifier(self.posting_writer)))
            await con.execute(sql.SQL("GRANT SELECT ON material_stock TO {}").format(sql.Identifier(self.reader)))
            material = uuid.uuid4(); receipt = uuid.uuid4(); item = uuid.uuid4(); now = datetime.now(timezone.utc)
            await con.execute("INSERT INTO material_stock VALUES (%s,'EF',0,'sheet',true,%s)", (material, now))
            await con.execute("INSERT INTO material_receipts (receipt_id,supplier_name,received_at,source_asset_reference,created_by_actor_reference) VALUES (%s,'Supplier',%s,'asset:test',%s)", (receipt, now, CREATOR))
            await con.execute("INSERT INTO material_receipt_items (receipt_item_id,receipt_id,line_number,material_id,full_colly_count,qty_per_full_colly,partial_qty,total_qty,unit) VALUES (%s,%s,1,%s,1,1,0,1,'sheet')", (item, receipt, material))
            self.ids = material, receipt, item
        base = conninfo.conninfo_to_dict(self.target.url)
        base.update(user=self.candidate_runtime, password=self.password,
                    options=f"-csearch_path={self.schema}")
        self.candidate_url = conninfo.make_conninfo(**base)
        base.update(user=self.posting_runtime)
        self.posting_url = conninfo.make_conninfo(**base)
        base.update(user=self.reader)
        self.reader_url = conninfo.make_conninfo(**base)

    async def asyncTearDown(self):
        async with await psycopg.AsyncConnection.connect(
            self.target.url, autocommit=True
        ) as admin:
            await admin.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(self.schema)))
            for role in (
                self.candidate_runtime, self.posting_runtime, self.reader,
                self.candidate_writer, self.posting_writer,
            ):
                await admin.execute(sql.SQL("DROP ROLE {}").format(sql.Identifier(role)))

    async def denied(self, url, statement, parameters=()):
        with self.assertRaises(psycopg.errors.InsufficientPrivilege):
            async with await psycopg.AsyncConnection.connect(url, autocommit=True) as con:
                await con.execute(statement, parameters)

    async def test_runtime_membership_is_exact_non_admin_and_candidate_insert_works(self):
        expected = {
            (self.candidate_runtime, self.candidate_writer, False),
            (self.posting_runtime, self.posting_writer, False),
        }
        governed = (
            self.candidate_runtime, self.posting_runtime, self.reader,
            self.candidate_writer, self.posting_writer,
        )
        async with await psycopg.AsyncConnection.connect(self.target.url) as admin:
            memberships = set(await (await admin.execute(
                "SELECT member.rolname, granted.rolname, membership.admin_option "
                "FROM pg_auth_members membership "
                "JOIN pg_roles member ON member.oid=membership.member "
                "JOIN pg_roles granted ON granted.oid=membership.roleid "
                "WHERE member.rolname = ANY(%s) OR granted.rolname = ANY(%s)",
                (list(governed), list(governed)),
            )).fetchall())
            attributes = tuple(await (await admin.execute(
                "SELECT rolname,rolsuper,rolcreatedb,rolcreaterole,rolreplication,"
                "rolbypassrls FROM pg_roles WHERE rolname = ANY(%s)",
                (list(governed),),
            )).fetchall())
        self.assertEqual(memberships, expected)
        self.assertEqual({row[0] for row in attributes}, set(governed))
        self.assertTrue(all(row[1:] == (False, False, False, False, False)
                            for row in attributes))

        receipt = uuid.uuid4()
        item = uuid.uuid4()
        now = datetime.now(timezone.utc)
        async with await psycopg.AsyncConnection.connect(
            self.candidate_url, autocommit=True
        ) as runtime:
            identity = await (await runtime.execute(
                "SELECT current_user,session_user"
            )).fetchone()
            self.assertEqual(identity, (self.candidate_runtime, self.candidate_runtime))
            await runtime.execute(
                "INSERT INTO material_receipts "
                "(receipt_id,supplier_name,received_at,source_asset_reference,"
                "created_by_actor_reference) VALUES (%s,'Runtime candidate',%s,%s,%s)",
                (receipt, now, "asset:" + uuid.uuid4().hex, CREATOR),
            )
            await runtime.execute(
                "INSERT INTO material_receipt_items "
                "(receipt_item_id,receipt_id,line_number,full_colly_count,"
                "qty_per_full_colly,partial_qty,total_qty,unit) "
                "VALUES (%s,%s,1,1,1,0,1,'sheet')",
                (item, receipt),
            )

    async def test_candidate_denials(self):
        material, receipt, item = self.ids
        now = datetime.now(timezone.utc)
        await self.denied(self.candidate_url, "INSERT INTO inventory_movements (movement_id,material_id,movement_type,quantity_delta,unit,source_receipt_item_id,occurred_at,posting_actor_reference,balance_before,balance_after) VALUES (%s,%s,'RECEIPT',1,'sheet',%s,%s,'x',0,1)", (uuid.uuid4(), material, item, now))
        await self.denied(self.candidate_url, "UPDATE material_stock SET stock_qty=1")
        await self.denied(self.candidate_url, "DELETE FROM material_receipt_items")
        await self.denied(self.candidate_url, "DELETE FROM material_receipts")
        await self.denied(self.candidate_url, "INSERT INTO unrelated_records VALUES (1)")
        await self.denied(self.candidate_url, "UPDATE material_receipts SET created_by_actor_reference=%s", ("operator:6ba7b810-9dad-4d80-b000-000000000001",))
        await self.denied(self.candidate_url, "CREATE TABLE forbidden_stage033a(id integer)")

    async def test_posting_denials(self):
        await self.denied(self.posting_url, "UPDATE material_receipts SET created_by_actor_reference=%s", (CREATOR,))
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
