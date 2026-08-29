"""Isolated PostgreSQL 17 validation for Stage 0.33C persistence effects."""

from __future__ import annotations

import asyncio
from datetime import date, datetime, timezone
from decimal import Decimal
import os
from pathlib import Path
import unittest
import uuid

import psycopg
from psycopg import conninfo, sql

from core.material_receipts.errors import MaterialReceiptError, MaterialReceiptFailureCode
from core.material_receipts.models import ReceiptCandidateRequest, ReceiptItemCandidate
from core.material_receipts.repository import CandidateDatabaseConfig, MaterialReceiptRepository
from tests.integration.business_context.disposable_postgres import admit_disposable_postgres


ROOT = Path(__file__).resolve().parents[3]
TEST_URL = os.environ.get("AIOS_MATERIAL_TEST_DATABASE_URL")
MIGRATIONS = ROOT / "migrations/postgres"
STOCK_UP = (MIGRATIONS / "0002_create_material_stock.up.sql").read_text()
RECEIPT_UP = (
    MIGRATIONS / "0003_create_material_receipt_inventory_movement.up.sql"
).read_text()
SOURCE_UNIQUENESS_UP = (
    MIGRATIONS / "0004_add_material_receipt_source_active_uniqueness.up.sql"
).read_text()
CANDIDATE = "aios_material_receipt_candidate_runtime"
ACTOR = "operator:550e8400-e29b-41d4-a716-446655440000"


def candidate(source: str, *, later_item_invalid: bool = False) -> ReceiptCandidateRequest:
    missing_material = uuid.uuid4() if later_item_invalid else None
    return ReceiptCandidateRequest(
        uuid.uuid4(),
        "Stage 033C",
        "DO-033C",
        date(2026, 8, 29),
        datetime(2026, 8, 29, tzinfo=timezone.utc),
        source,
        (
            ReceiptItemCandidate(
                uuid.uuid4(), 1, "Steel", None, None, None, None,
                1, Decimal("50"), Decimal("0"), Decimal("50"), "sheet",
            ),
            ReceiptItemCandidate(
                uuid.uuid4(), 2, "Roll", None, None, None, missing_material,
                0, None, Decimal("2"), Decimal("2"), "roll",
            ),
        ),
    )


class _InsertBarrierConnection:
    def __init__(self, connection, barrier):
        self.connection = connection
        self.barrier = barrier

    async def __aenter__(self):
        await self.connection.__aenter__()
        return self

    async def __aexit__(self, *args):
        return await self.connection.__aexit__(*args)

    def transaction(self):
        return self.connection.transaction()

    async def execute(self, statement, parameters=None):
        if "INSERT INTO material_receipts" in str(statement):
            await self.barrier.wait()
        return await self.connection.execute(statement, parameters)


@unittest.skipUnless(TEST_URL, "Stage 0.33C disposable PostgreSQL unavailable")
class Stage033CPostgresTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.target = admit_disposable_postgres(TEST_URL)
        self.schema = "stage033c_" + uuid.uuid4().hex
        self.password = "stage033c-candidate-" + uuid.uuid4().hex
        self.forbidden_role = "stage033c_forbidden_" + uuid.uuid4().hex
        async with await psycopg.AsyncConnection.connect(
            self.target.url, autocommit=True
        ) as db:
            await db.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.schema)))
            exists = await (
                await db.execute(
                    "SELECT 1 FROM pg_roles WHERE rolname=%s", (CANDIDATE,)
                )
            ).fetchone()
            if not exists:
                await db.execute(
                    sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(
                        sql.Identifier(CANDIDATE), sql.Literal(self.password)
                    )
                )
            else:
                await db.execute(
                    sql.SQL("ALTER ROLE {} PASSWORD {}").format(
                        sql.Identifier(CANDIDATE), sql.Literal(self.password)
                    )
                )
            await db.execute(
                sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(
                    sql.Identifier(self.forbidden_role), sql.Literal(self.password + "-no")
                )
            )
        self.admin_url = conninfo.make_conninfo(
            self.target.url, options=f"-csearch_path={self.schema}"
        )
        async with await psycopg.AsyncConnection.connect(
            self.admin_url, autocommit=True
        ) as db:
            await db.execute(STOCK_UP)
            await db.execute(RECEIPT_UP)
            await db.execute(
                "ALTER TABLE material_receipts ADD COLUMN "
                "created_by_actor_reference TEXT NOT NULL, ADD CONSTRAINT "
                "material_receipts_created_by_actor_reference_valid CHECK "
                "(created_by_actor_reference ~ "
                "'^operator:[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-"
                "[89ab][0-9a-f]{3}-[0-9a-f]{12}$')"
            )
            await db.execute(SOURCE_UNIQUENESS_UP)
            role = sql.Identifier(CANDIDATE)
            schema = sql.Identifier(self.schema)
            await db.execute(sql.SQL("GRANT USAGE ON SCHEMA {} TO {}").format(schema, role))
            await db.execute(
                sql.SQL(
                    "GRANT SELECT ON material_receipts,material_receipt_items,"
                    "material_stock,inventory_movements TO {}"
                ).format(role)
            )
            await db.execute(
                sql.SQL(
                    "GRANT INSERT (receipt_id,supplier_name,document_number,"
                    "document_date,received_at,source_asset_reference,"
                    "created_by_actor_reference), UPDATE (status,updated_at) "
                    "ON material_receipts TO {}"
                ).format(role)
            )
            await db.execute(
                sql.SQL(
                    "GRANT INSERT (receipt_item_id,receipt_id,line_number,"
                    "candidate_material_description,canonical_display_name,"
                    "size_description,specification,material_id,full_colly_count,"
                    "qty_per_full_colly,partial_qty,total_qty,unit), "
                    "UPDATE (status,updated_at) ON material_receipt_items TO {}"
                ).format(role)
            )
            await db.execute(
                sql.SQL("GRANT USAGE ON SCHEMA {} TO {}").format(
                    schema, sql.Identifier(self.forbidden_role)
                )
            )
        self.repository = MaterialReceiptRepository(
            CandidateDatabaseConfig(
                password=self.password,
                host=self.target.host,
                port=self.target.port,
                dbname=self.target.dbname,
                search_path=self.schema,
            )
        )

    async def asyncTearDown(self):
        async with await psycopg.AsyncConnection.connect(
            self.target.url, autocommit=True
        ) as db:
            await db.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(self.schema)))
            await db.execute(sql.SQL("DROP ROLE {}").format(sql.Identifier(self.forbidden_role)))
            exists = await (await db.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (CANDIDATE,))).fetchone()
            if exists:
                await db.execute(sql.SQL("DROP ROLE {}").format(sql.Identifier(CANDIDATE)))

    async def counts(self):
        async with await psycopg.AsyncConnection.connect(self.admin_url) as db:
            return tuple(
                await (
                    await db.execute(
                        "SELECT (SELECT count(*) FROM material_receipts),"
                        "(SELECT count(*) FROM material_receipt_items),"
                        "(SELECT count(*) FROM inventory_movements),"
                        "(SELECT count(*) FROM material_stock)"
                    )
                ).fetchone()
            )

    async def test_candidate_writer_creates_one_plus_n_needs_review_only(self):
        before = await self.counts()
        result = await self.repository._create_receipt_candidate(
            candidate("stage033c:success"), ACTOR
        )
        self.assertEqual(result.status.value, "NEEDS_REVIEW")
        self.assertEqual([item.status.value for item in result.items], ["NEEDS_REVIEW"] * 2)
        self.assertIsNone(result.confirmed_at)
        after = await self.counts()
        self.assertEqual(after, (before[0] + 1, before[1] + 2, before[2], before[3]))
        async with await psycopg.AsyncConnection.connect(self.admin_url) as db:
            identity = await (
                await db.execute(
                    "SELECT created_by_actor_reference FROM material_receipts "
                    "WHERE receipt_id=%s", (result.receipt_id,)
                )
            ).fetchone()
            version = await (await db.execute("SHOW server_version")).fetchone()
        self.assertEqual(identity, (ACTOR,))
        self.assertTrue(version[0].startswith("17."), version)

    async def test_later_item_failure_rolls_back_same_transaction(self):
        before = await self.counts()
        with self.assertRaises(MaterialReceiptError):
            await self.repository._create_receipt_candidate(
                candidate("stage033c:rollback", later_item_invalid=True), ACTOR
            )
        self.assertEqual(await self.counts(), before)

    async def test_duplicate_and_source_race_are_database_separate(self):
        source = "stage033c:duplicate"
        await self.repository._create_receipt_candidate(candidate(source), ACTOR)
        with self.assertRaises(MaterialReceiptError) as duplicate:
            await self.repository._create_receipt_candidate(candidate(source), ACTOR)
        self.assertIs(
            duplicate.exception.code,
            MaterialReceiptFailureCode.SOURCE_ACTIVE_RECEIPT_EXISTS,
        )
        race_source = "stage033c:race"
        contenders = (candidate(race_source), candidate(race_source))
        barrier = asyncio.Barrier(2)
        real_connect = psycopg.AsyncConnection.connect

        async def synchronized_connect(*args, **kwargs):
            return _InsertBarrierConnection(await real_connect(*args, **kwargs), barrier)

        async def compete(value):
            try:
                await self.repository._create_receipt_candidate(value, ACTOR)
                return "success"
            except MaterialReceiptError as exc:
                if exc.code is MaterialReceiptFailureCode.SOURCE_ACTIVE_RECEIPT_EXISTS:
                    return "duplicate"
                return "other"

        from unittest.mock import patch
        with patch.object(psycopg.AsyncConnection, "connect", side_effect=synchronized_connect):
            outcomes = await asyncio.wait_for(
                asyncio.gather(*(compete(value) for value in contenders)), timeout=10
            )
        self.assertCountEqual(outcomes, ["success", "duplicate"])

    async def test_forbidden_role_cannot_write_candidate_or_side_effect_tables(self):
        forbidden_url = conninfo.make_conninfo(
            host=self.target.host,
            port=self.target.port,
            dbname=self.target.dbname,
            user=self.forbidden_role,
            password=self.password + "-no",
            options=f"-csearch_path={self.schema}",
            sslmode="disable",
        )
        statements = (
            "INSERT INTO material_receipts (receipt_id,supplier_name,received_at,"
            "source_asset_reference,created_by_actor_reference) VALUES "
            f"('{uuid.uuid4()}','x',now(),'x','{ACTOR}')",
            "INSERT INTO inventory_movements DEFAULT VALUES",
            "UPDATE material_stock SET stock_qty=1",
        )
        for statement in statements:
            with self.subTest(statement=statement):
                with self.assertRaises(psycopg.errors.InsufficientPrivilege):
                    async with await psycopg.AsyncConnection.connect(
                        forbidden_url, autocommit=True
                    ) as db:
                        await db.execute(statement)
