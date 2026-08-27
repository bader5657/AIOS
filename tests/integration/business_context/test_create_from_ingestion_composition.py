"""Disposable PostgreSQL proof for the Stage 0.31B create-only composition."""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import uuid

import psycopg
from psycopg import conninfo, sql

from core.app.input_classifier import InputType
from core.app.material_receipts import review_use_cases
from core.app.material_receipts.candidate_input import (
    TrustedReceiptFacts,
    TrustedReceiptItemFacts,
)
from core.app.material_receipts.create_from_ingestion import (
    create_review_candidate_from_ingestion,
)
from core.app.material_receipts.review_use_cases import ActorContext
from core.app.material_receipts.results import ReviewApplicationError, ReviewFailureCode
from core.ingestion.universal_ingestion import IngestionResult
from core.material_receipts.models import ReceiptStatus
from core.material_receipts.repository import (
    CandidateDatabaseConfig,
    MaterialReceiptRepository,
)
from tests.integration.business_context.disposable_postgres import (
    OPT_IN,
    admit_disposable_postgres,
)


TEST_URL = os.environ.get("AIOS_MATERIAL_TEST_DATABASE_URL")
ROOT = Path(__file__).resolve().parents[3]
ACTOR = ActorContext("operator:550e8400-e29b-41d4-a716-446655440000")
STOCK_SQL = (ROOT / "migrations/postgres/0002_create_material_stock.up.sql").read_text()
RECEIPT_SQL = (
    ROOT / "migrations/postgres/0003_create_material_receipt_inventory_movement.up.sql"
).read_text()


def manifest_values(identifier: uuid.UUID) -> dict[str, object]:
    return {
        "manifest_id": str(identifier),
        "represented_media_type": "text",
        "received_at": "2026-08-27T00:00:00Z",
        "manifest_status": "created",
        "metadata": {"media_type": "text", "character_count": 1},
    }


def evidence(path: Path) -> IngestionResult:
    return IngestionResult(
        input_type=InputType.TEXT,
        recognized_input_type=InputType.TEXT,
        stored_path=None,
        manifest_path=str(path),
        metadata={"supplier": "untrusted"},
        text="untrusted",
        register_handoff_ready=True,
        process_handoff_ready=False,
        route_handoff_ready=False,
        respond_acknowledgement_ready=True,
    )


def item(line: int, *, full: int, partial: str, total: str) -> TrustedReceiptItemFacts:
    return TrustedReceiptItemFacts(
        line_number=line,
        candidate_material_description=f"Steel sheet {line}",
        canonical_display_name=None,
        size_description=None,
        specification=None,
        material_id=None,
        full_colly_count=full,
        qty_per_full_colly=Decimal("50"),
        partial_qty=Decimal(partial),
        total_qty=Decimal(total),
        unit="sheet",
    )


def facts(*items: TrustedReceiptItemFacts) -> TrustedReceiptFacts:
    return TrustedReceiptFacts(
        supplier_name="PT Stage 031B",
        document_number="DO-31B",
        document_date=date(2026, 8, 27),
        received_at=datetime(2026, 8, 27, tzinfo=timezone.utc),
        items=items or (item(1, full=125, partial="0", total="6250"),),
    )


@unittest.skipUnless(
    TEST_URL or os.environ.get(OPT_IN),
    "disposable PostgreSQL configuration is required",
)
class CreateFromIngestionIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.target = admit_disposable_postgres(TEST_URL)
        self.schema = "stage031b_" + uuid.uuid4().hex
        self.runtime_user = "aios_material_receipt_candidate_runtime"
        self.runtime_password = "candidate-stage031b-disposable-only"
        self.manifest_directory = tempfile.TemporaryDirectory()
        self.manifest_root = Path(self.manifest_directory.name)
        self.original_manifest_root = review_use_cases._MANIFEST_ROOT
        review_use_cases._MANIFEST_ROOT = self.manifest_root

        async with await psycopg.AsyncConnection.connect(
            self.target.url, autocommit=True
        ) as admin:
            await admin.execute(
                sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(
                    sql.Identifier(self.runtime_user),
                    sql.Literal(self.runtime_password),
                )
            )
            await admin.execute(
                sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.schema))
            )
        self.admin_url = conninfo.make_conninfo(
            self.target.url, options=f"-csearch_path={self.schema}"
        )
        async with await psycopg.AsyncConnection.connect(
            self.admin_url, autocommit=True
        ) as admin:
            await admin.execute(STOCK_SQL)
            await admin.execute(RECEIPT_SQL)
            await admin.execute("ALTER TABLE material_receipts ADD COLUMN created_by_actor_reference TEXT NOT NULL, ADD CONSTRAINT material_receipts_created_by_actor_reference_valid CHECK (created_by_actor_reference ~ '^operator:[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')")
            role = sql.Identifier(self.runtime_user)
            schema = sql.Identifier(self.schema)
            await admin.execute(
                sql.SQL("GRANT USAGE ON SCHEMA {} TO {}").format(schema, role)
            )
            await admin.execute(
                sql.SQL(
                    "GRANT SELECT ON material_receipts, material_receipt_items, "
                    "material_stock TO {}"
                ).format(role)
            )
            await admin.execute(
                sql.SQL(
                    "GRANT INSERT (receipt_id,supplier_name,document_number,"
                    "document_date,received_at,source_asset_reference,"
                    "created_by_actor_reference), UPDATE "
                    "(supplier_name,document_number,document_date,received_at,"
                    "source_asset_reference,status,version,confirmed_version,"
                    "confirmed_at,confirmation_actor_reference,updated_at) ON "
                    "material_receipts TO {}"
                ).format(role)
            )
            await admin.execute(
                sql.SQL(
                    "GRANT INSERT (receipt_item_id,receipt_id,line_number,"
                    "candidate_material_description,canonical_display_name,"
                    "size_description,specification,material_id,full_colly_count,"
                    "qty_per_full_colly,partial_qty,total_qty,unit), UPDATE "
                    "(line_number,candidate_material_description,canonical_display_name,"
                    "size_description,specification,material_id,full_colly_count,"
                    "qty_per_full_colly,partial_qty,total_qty,unit,status,updated_at) "
                    "ON material_receipt_items TO {}"
                ).format(role)
            )
        self.repository = MaterialReceiptRepository(
            CandidateDatabaseConfig(
                password=self.runtime_password,
                host=self.target.host,
                port=self.target.port,
                dbname=self.target.dbname,
                search_path=self.schema,
            )
        )
        self.runtime_url = conninfo.make_conninfo(
            host=self.target.host,
            port=self.target.port,
            dbname=self.target.dbname,
            user=self.runtime_user,
            password=self.runtime_password,
            options=f"-csearch_path={self.schema}",
            sslmode="disable",
        )

    async def asyncTearDown(self) -> None:
        review_use_cases._MANIFEST_ROOT = self.original_manifest_root
        self.manifest_directory.cleanup()
        async with await psycopg.AsyncConnection.connect(
            self.target.url, autocommit=True
        ) as admin:
            await admin.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(self.schema))
            )
            await admin.execute(
                sql.SQL("DROP ROLE {}").format(sql.Identifier(self.runtime_user))
            )

    def retained_manifest(self) -> Path:
        identifier = uuid.uuid4()
        path = self.manifest_root / f"{identifier}.json"
        path.write_text(json.dumps(manifest_values(identifier)), encoding="utf-8")
        return path

    async def counts(self) -> tuple[int, int, int, int]:
        async with await psycopg.AsyncConnection.connect(self.admin_url) as admin:
            row = await (
                await admin.execute(
                    "SELECT (SELECT count(*) FROM material_receipts), "
                    "(SELECT count(*) FROM material_receipt_items), "
                    "(SELECT count(*) FROM inventory_movements), "
                    "(SELECT count(*) FROM material_stock)"
                )
            ).fetchone()
        return tuple(row)

    async def create(self, path: Path, trusted: TrustedReceiptFacts):
        with patch.object(
            MaterialReceiptRepository,
            "from_environment",
            return_value=self.repository,
        ) as factory:
            result = await create_review_candidate_from_ingestion(
                evidence(path), trusted, ACTOR
            )
        self.assertEqual(factory.call_count, 1)
        return result

    async def test_real_create_path_is_atomic_review_safe_and_stock_inert(self) -> None:
        path = self.retained_manifest()
        before = await self.counts()
        result = await self.create(
            path,
            facts(
                item(1, full=125, partial="0", total="6250"),
                item(2, full=62, partial="38", total="3138"),
            ),
        )
        after = await self.counts()

        self.assertEqual(result.status, ReceiptStatus.NEEDS_REVIEW)
        self.assertEqual(result.source_asset_reference, str(path))
        self.assertEqual(len(result.items), 2)
        self.assertTrue(
            all(value.status is ReceiptStatus.NEEDS_REVIEW for value in result.items)
        )
        self.assertIsNone(result.confirmed_version)
        self.assertIsNone(result.confirmed_at)
        self.assertIsNone(result.confirmation_actor_reference)
        self.assertEqual(after, (before[0] + 1, before[1] + 2, before[2], before[3]))

    async def test_candidate_identity_cannot_mutate_stock_or_movements(self) -> None:
        async with await psycopg.AsyncConnection.connect(self.runtime_url) as runtime:
            with self.assertRaises(psycopg.errors.InsufficientPrivilege):
                await runtime.execute(
                    "UPDATE material_stock SET stock_qty = stock_qty + 1"
                )
            await runtime.rollback()
            with self.assertRaises(psycopg.errors.InsufficientPrivilege):
                await runtime.execute(
                    "INSERT INTO inventory_movements DEFAULT VALUES"
                )

    async def test_candidate_transaction_failure_rolls_back_receipt_and_items(self) -> None:
        async with await psycopg.AsyncConnection.connect(
            self.admin_url, autocommit=True
        ) as admin:
            await admin.execute(
                "CREATE FUNCTION fail_second_item() RETURNS trigger LANGUAGE plpgsql "
                "AS $$ BEGIN IF NEW.line_number = 2 THEN RAISE EXCEPTION "
                "'controlled disposable failure'; END IF; RETURN NEW; END $$"
            )
            await admin.execute(
                "CREATE TRIGGER stage031b_fail_second BEFORE INSERT ON "
                "material_receipt_items FOR EACH ROW EXECUTE FUNCTION fail_second_item()"
            )
        before = await self.counts()
        with self.assertRaises(ReviewApplicationError) as caught:
            await self.create(
                self.retained_manifest(),
                facts(
                    item(1, full=1, partial="0", total="50"),
                    item(2, full=1, partial="0", total="50"),
                ),
            )
        self.assertIs(caught.exception.code, ReviewFailureCode.CANDIDATE_OPERATION_FAILED)
        self.assertEqual(await self.counts(), before)

    async def test_duplicate_invocation_is_non_idempotent_pre_activation(self) -> None:
        path = self.retained_manifest()
        trusted = facts()
        first = await self.create(path, trusted)
        second = await self.create(path, trusted)
        self.assertNotEqual(first.receipt_id, second.receipt_id)
        async with await psycopg.AsyncConnection.connect(self.admin_url) as admin:
            count = await (
                await admin.execute(
                    "SELECT count(*) FROM material_receipts "
                    "WHERE source_asset_reference = %s",
                    (str(path),),
                )
            ).fetchone()
        self.assertEqual(count[0], 2)


if __name__ == "__main__":
    unittest.main()
