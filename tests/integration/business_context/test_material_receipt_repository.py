from datetime import date, datetime, timezone
from decimal import Decimal
import os
from pathlib import Path
import unittest
import uuid

import psycopg
from psycopg import conninfo, sql

from core.material_receipts import (
    MaterialReceiptError, MaterialReceiptFailureCode as Code,
    MaterialReceiptRepository, ReceiptCandidateRequest, ReceiptItemCandidate,
    ReceiptStatus,
)
from core.material_receipts.repository import CandidateDatabaseConfig
from tests.integration.business_context.disposable_postgres import (
    OPT_IN,
    admit_disposable_postgres,
)


TEST_URL = os.environ.get("AIOS_MATERIAL_TEST_DATABASE_URL")
ROOT = Path(__file__).resolve().parents[3]
STOCK_SQL = (ROOT / "migrations/postgres/0002_create_material_stock.up.sql").read_text()
RECEIPT_SQL = (ROOT / "migrations/postgres/0003_create_material_receipt_inventory_movement.up.sql").read_text()


def candidate_item(line=1, **overrides):
    values = dict(
        receipt_item_id=uuid.uuid4(), line_number=line,
        candidate_material_description="EF sheet", canonical_display_name=None,
        size_description=None, specification=None, material_id=None,
        full_colly_count=125, qty_per_full_colly=Decimal("50"),
        partial_qty=Decimal("0"), total_qty=Decimal("6250"), unit="sheet",
    )
    values.update(overrides)
    return ReceiptItemCandidate(**values)


def candidate_request(*items, receipt_id=None, **overrides):
    values = dict(
        receipt_id=receipt_id or uuid.uuid4(), supplier_name="Supplier",
        document_number="SJ-1", document_date=date(2026, 8, 26),
        received_at=datetime.now(timezone.utc), source_asset_reference="asset:test",
        items=tuple(items or (candidate_item(),)),
    )
    values.update(overrides)
    return ReceiptCandidateRequest(**values)


@unittest.skipUnless(
    TEST_URL or os.environ.get(OPT_IN),
    "disposable PostgreSQL configuration is required",
)
class CandidateRepositoryIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.target = admit_disposable_postgres(TEST_URL)
        self.schema = "candidate_" + uuid.uuid4().hex
        self.runtime_user = "aios_material_receipt_candidate_runtime"
        self.runtime_password = "candidate-disposable-only"
        async with await psycopg.AsyncConnection.connect(
            self.target.url, autocommit=True
        ) as admin:
            await admin.execute(
                sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(
                    sql.Identifier(self.runtime_user),
                    sql.Literal(self.runtime_password),
                )
            )
            await admin.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.schema)))
        self.url = conninfo.make_conninfo(
            self.target.url, options=f"-csearch_path={self.schema}"
        )
        async with await psycopg.AsyncConnection.connect(self.url, autocommit=True) as con:
            await con.execute(STOCK_SQL)
            await con.execute(RECEIPT_SQL)
            role = sql.Identifier(self.runtime_user)
            schema = sql.Identifier(self.schema)
            await con.execute(
                sql.SQL("GRANT USAGE ON SCHEMA {} TO {}").format(schema, role)
            )
            await con.execute(sql.SQL(
                "GRANT SELECT ON material_receipts, material_receipt_items, "
                "material_stock TO {}"
            ).format(role))
            await con.execute(sql.SQL(
                "GRANT INSERT (receipt_id,supplier_name,document_number,document_date,"
                "received_at,source_asset_reference), UPDATE (supplier_name,"
                "document_number,document_date,received_at,source_asset_reference,"
                "status,version,confirmed_version,confirmed_at,"
                "confirmation_actor_reference,updated_at) ON material_receipts TO {}"
            ).format(role))
            await con.execute(sql.SQL(
                "GRANT INSERT (receipt_item_id,receipt_id,line_number,"
                "candidate_material_description,canonical_display_name,size_description,"
                "specification,material_id,full_colly_count,qty_per_full_colly,"
                "partial_qty,total_qty,unit), UPDATE (line_number,"
                "candidate_material_description,canonical_display_name,size_description,"
                "specification,material_id,full_colly_count,qty_per_full_colly,"
                "partial_qty,total_qty,unit,status,updated_at) "
                "ON material_receipt_items TO {}"
            ).format(role))
        self.repository = MaterialReceiptRepository(
            CandidateDatabaseConfig(
                password=self.runtime_password,
                host=self.target.host,
                port=self.target.port,
                dbname=self.target.dbname,
                search_path=self.schema,
            )
        )

    async def asyncTearDown(self):
        async with await psycopg.AsyncConnection.connect(
            self.target.url, autocommit=True
        ) as admin:
            await admin.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(self.schema)))
            await admin.execute(
                sql.SQL("DROP ROLE {}").format(sql.Identifier(self.runtime_user))
            )

    async def material(self, *, active=True, unit="sheet"):
        material_id = uuid.uuid4()
        async with await psycopg.AsyncConnection.connect(self.url, autocommit=True) as con:
            await con.execute(
                "INSERT INTO material_stock VALUES (%s,%s,0,%s,%s,%s)",
                (material_id, "EF", unit, active, datetime.now(timezone.utc)),
            )
        return material_id

    async def test_create_valid_multi_item_and_packaging_examples(self):
        request = candidate_request(
            candidate_item(),
            candidate_item(2, full_colly_count=62, partial_qty=Decimal("38"),
                           total_qty=Decimal("3138")),
        )
        result = await self.repository.create_receipt_candidate(request)
        self.assertEqual(result.status, ReceiptStatus.NEEDS_REVIEW)
        self.assertEqual(result.version, 1)
        self.assertEqual([item.total_qty for item in result.items],
                         [Decimal("6250"), Decimal("3138")])

    async def test_unresolved_allowed_but_confirmation_requires_resolution(self):
        result = await self.repository.create_receipt_candidate(candidate_request())
        with self.assertRaises(MaterialReceiptError) as caught:
            await self.repository.confirm_receipt(result.receipt_id, 1, "operator:1")
        self.assertEqual(caught.exception.code, Code.MATERIAL_UNRESOLVED)

    async def test_revision_increments_version_and_confirmation_then_edit_invalidates(self):
        material_id = await self.material()
        request = candidate_request(candidate_item(material_id=material_id))
        created = await self.repository.create_receipt_candidate(request)
        confirmed = await self.repository.confirm_receipt(created.receipt_id, 1, "operator:1")
        self.assertEqual(confirmed.confirmed_version, 1)
        revised_request = candidate_request(
            candidate_item(receipt_item_id=request.items[0].receipt_item_id,
                           material_id=material_id, canonical_display_name="EF canonical"),
            receipt_id=request.receipt_id,
        )
        revised = await self.repository.revise_receipt_candidate(revised_request, 1)
        self.assertEqual(revised.version, 2)
        self.assertEqual(revised.status, ReceiptStatus.NEEDS_REVIEW)
        self.assertIsNone(revised.confirmed_version)
        with self.assertRaises(MaterialReceiptError) as caught:
            await self.repository.revise_receipt_candidate(revised_request, 1)
        self.assertEqual(caught.exception.code, Code.STALE_RECEIPT_VERSION)

    async def test_confirmation_rejects_inactive_and_unit_mismatch(self):
        inactive = await self.material(active=False)
        first = await self.repository.create_receipt_candidate(
            candidate_request(candidate_item(material_id=inactive))
        )
        with self.assertRaises(MaterialReceiptError) as caught:
            await self.repository.confirm_receipt(first.receipt_id, 1, "operator:1")
        self.assertEqual(caught.exception.code, Code.MATERIAL_INACTIVE)
        kg = await self.material(unit="kg")
        second = await self.repository.create_receipt_candidate(
            candidate_request(candidate_item(material_id=kg))
        )
        with self.assertRaises(MaterialReceiptError) as caught:
            await self.repository.confirm_receipt(second.receipt_id, 1, "operator:1")
        self.assertEqual(caught.exception.code, Code.UNIT_MISMATCH)

    async def test_cancelled_item_retained_excluded_and_no_delete(self):
        material_id = await self.material()
        request = candidate_request(
            candidate_item(material_id=material_id),
            candidate_item(2, material_id=None, full_colly_count=1,
                           total_qty=Decimal("50")),
        )
        created = await self.repository.create_receipt_candidate(request)
        cancelled = await self.repository.cancel_receipt_item(
            created.receipt_id, request.items[1].receipt_item_id, 1, "operator:1"
        )
        self.assertEqual(cancelled.version, 2)
        self.assertEqual(cancelled.items[1].status, ReceiptStatus.CANCELLED)
        confirmed = await self.repository.confirm_receipt(
            created.receipt_id, 2, "operator:1"
        )
        self.assertEqual(confirmed.items[0].status, ReceiptStatus.CONFIRMED)
        self.assertEqual(confirmed.items[1].status, ReceiptStatus.CANCELLED)
        async with await psycopg.AsyncConnection.connect(self.url) as con:
            count = await (await con.execute(
                "SELECT count(*) FROM material_receipt_items WHERE receipt_id=%s",
                (created.receipt_id,),
            )).fetchone()
        self.assertEqual(count[0], 2)
        self.assertFalse(hasattr(self.repository, "delete"))

    async def test_invalid_transition_after_terminal(self):
        created = await self.repository.create_receipt_candidate(candidate_request())
        await self.repository.cancel_receipt(created.receipt_id, 1, "operator:1")
        with self.assertRaises(MaterialReceiptError) as caught:
            await self.repository.confirm_receipt(created.receipt_id, 2, "operator:1")
        self.assertEqual(caught.exception.code, Code.INVALID_RECEIPT_STATE)


if __name__ == "__main__":
    unittest.main()
