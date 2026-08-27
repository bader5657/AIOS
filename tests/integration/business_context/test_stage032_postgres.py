"""Permanent real-PostgreSQL regression authority for Stage 0.32."""

from __future__ import annotations

import asyncio
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
from core.app.material_receipts.candidate_input import TrustedReceiptFacts, TrustedReceiptItemFacts
from core.app.material_receipts.create_from_ingestion import create_review_candidate_from_ingestion
from core.app.material_receipts.results import ReviewApplicationError, ReviewFailureCode
from core.ingestion.universal_ingestion import IngestionResult
from core.material_receipts.errors import MaterialReceiptError, MaterialReceiptFailureCode
from core.material_receipts.models import ReceiptCandidateRequest, ReceiptItemCandidate
from core.material_receipts.repository import CandidateDatabaseConfig, MaterialReceiptRepository
from tests.integration.business_context.disposable_postgres import admit_disposable_postgres


ROOT = Path(__file__).resolve().parents[3]
TEST_URL = os.environ.get("AIOS_MATERIAL_TEST_DATABASE_URL")
MIGRATIONS = ROOT / "migrations/postgres"
STOCK_UP = (MIGRATIONS / "0002_create_material_stock.up.sql").read_text()
RECEIPT_UP = (MIGRATIONS / "0003_create_material_receipt_inventory_movement.up.sql").read_text()
STAGE_UP = (MIGRATIONS / "0004_add_material_receipt_source_active_uniqueness.up.sql").read_text()
STAGE_DOWN = (MIGRATIONS / "0004_add_material_receipt_source_active_uniqueness.down.sql").read_text()
INDEX = "material_receipts_source_asset_active_uidx"
CANDIDATE = "aios_material_receipt_candidate_runtime"
CANDIDATE_PASSWORD = "stage032-candidate-disposable-sentinel"


def request(source: str, *, supplier: str = "Stage 032") -> ReceiptCandidateRequest:
    return ReceiptCandidateRequest(uuid.uuid4(), supplier, "DO-032", date(2026, 8, 27),
        datetime(2026, 8, 27, tzinfo=timezone.utc), source,
        (ReceiptItemCandidate(uuid.uuid4(), 1, "Steel", None, None, None, None,
         1, Decimal("50"), Decimal("0"), Decimal("50"), "sheet"),))


@unittest.skipUnless(TEST_URL, "Stage 0.32 disposable PostgreSQL infrastructure unavailable")
class Stage032PostgresTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.target = admit_disposable_postgres(TEST_URL)
        self.schema = "stage032_" + uuid.uuid4().hex
        self.manifests = tempfile.TemporaryDirectory()
        self.manifest_root = Path(self.manifests.name)
        self.old_root = review_use_cases._MANIFEST_ROOT
        review_use_cases._MANIFEST_ROOT = self.manifest_root
        async with await psycopg.AsyncConnection.connect(self.target.url, autocommit=True) as db:
            await db.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.schema)))
            exists = (await (await db.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (CANDIDATE,))).fetchone())
            if not exists:
                await db.execute(sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(sql.Identifier(CANDIDATE), sql.Literal(CANDIDATE_PASSWORD)))
        self.admin_url = conninfo.make_conninfo(self.target.url, options=f"-csearch_path={self.schema}")
        async with await psycopg.AsyncConnection.connect(self.admin_url, autocommit=True) as db:
            await db.execute(STOCK_UP); await db.execute(RECEIPT_UP)
        await self._grant_candidate()
        self.repo = MaterialReceiptRepository(CandidateDatabaseConfig(password=CANDIDATE_PASSWORD,
            host=self.target.host, port=self.target.port, dbname=self.target.dbname, search_path=self.schema))

    async def asyncTearDown(self):
        review_use_cases._MANIFEST_ROOT = self.old_root
        self.manifests.cleanup()
        async with await psycopg.AsyncConnection.connect(self.target.url, autocommit=True) as db:
            await db.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(self.schema)))

    async def _grant_candidate(self):
        async with await psycopg.AsyncConnection.connect(self.admin_url, autocommit=True) as db:
            role = sql.Identifier(CANDIDATE); schema = sql.Identifier(self.schema)
            await db.execute(sql.SQL("GRANT USAGE ON SCHEMA {} TO {}").format(schema, role))
            await db.execute(sql.SQL("GRANT SELECT ON material_receipts,material_receipt_items,material_stock TO {}").format(role))
            await db.execute(sql.SQL("GRANT INSERT (receipt_id,supplier_name,document_number,document_date,received_at,source_asset_reference), UPDATE (supplier_name,document_number,document_date,received_at,source_asset_reference,status,version,confirmed_version,confirmed_at,confirmation_actor_reference,updated_at) ON material_receipts TO {}").format(role))
            await db.execute(sql.SQL("GRANT INSERT (receipt_item_id,receipt_id,line_number,candidate_material_description,canonical_display_name,size_description,specification,material_id,full_colly_count,qty_per_full_colly,partial_qty,total_qty,unit), UPDATE (line_number,candidate_material_description,canonical_display_name,size_description,specification,material_id,full_colly_count,qty_per_full_colly,partial_qty,total_qty,unit,status,updated_at) ON material_receipt_items TO {}").format(role))

    async def apply(self):
        async with await psycopg.AsyncConnection.connect(self.admin_url, autocommit=True) as db: await db.execute(STAGE_UP)

    async def counts(self):
        async with await psycopg.AsyncConnection.connect(self.admin_url) as db:
            return tuple(await (await db.execute("SELECT (SELECT count(*) FROM material_receipts),(SELECT count(*) FROM material_receipt_items),(SELECT count(*) FROM material_stock),(SELECT count(*) FROM inventory_movements)")).fetchone())

    async def test_catalog_structure_and_up_down_up_are_exact_and_non_mutating(self):
        async with await psycopg.AsyncConnection.connect(self.admin_url) as db:
            baseline = tuple(await (await db.execute("SELECT (SELECT array_agg(rolname ORDER BY rolname) FROM pg_roles),(SELECT array_agg(nspname ORDER BY nspname) FROM pg_namespace),(SELECT count(*) FROM pg_proc WHERE pronamespace=current_schema()::regnamespace),(SELECT count(*) FROM pg_trigger WHERE tgrelid IN ('material_receipts'::regclass,'material_receipt_items'::regclass) AND NOT tgisinternal),(SELECT array_agg((c.relname,c.relacl::text)::text ORDER BY c.relname) FROM pg_class c WHERE c.relnamespace=current_schema()::regnamespace AND c.relkind='r'),(SELECT nspacl::text FROM pg_namespace WHERE oid=current_schema()::regnamespace)")).fetchone())
        await self.apply()
        async with await psycopg.AsyncConnection.connect(self.admin_url) as db:
            row = await (await db.execute("SELECT i.indisunique,c.relname,a.attname,pg_get_expr(i.indpred,i.indrelid) FROM pg_index i JOIN pg_class x ON x.oid=i.indexrelid JOIN pg_class c ON c.oid=i.indrelid JOIN pg_attribute a ON a.attrelid=c.oid AND a.attnum=i.indkey[0] WHERE x.relname=%s", (INDEX,))).fetchone()
            old = await (await db.execute("SELECT i.indisunique FROM pg_index i JOIN pg_class x ON x.oid=i.indexrelid WHERE x.relname='material_receipts_source_asset_idx'")).fetchone()
            after = tuple(await (await db.execute("SELECT (SELECT array_agg(rolname ORDER BY rolname) FROM pg_roles),(SELECT array_agg(nspname ORDER BY nspname) FROM pg_namespace),(SELECT count(*) FROM pg_proc WHERE pronamespace=current_schema()::regnamespace),(SELECT count(*) FROM pg_trigger WHERE tgrelid IN ('material_receipts'::regclass,'material_receipt_items'::regclass) AND NOT tgisinternal),(SELECT array_agg((c.relname,c.relacl::text)::text ORDER BY c.relname) FROM pg_class c WHERE c.relnamespace=current_schema()::regnamespace AND c.relkind='r'),(SELECT nspacl::text FROM pg_namespace WHERE oid=current_schema()::regnamespace)")).fetchone())
        self.assertEqual(row[:3], (True, "material_receipts", "source_asset_reference")); self.assertIn("REJECTED", row[3]); self.assertIn("CANCELLED", row[3]); self.assertEqual(old, (False,)); self.assertEqual(after, baseline)
        async with await psycopg.AsyncConnection.connect(self.admin_url, autocommit=True) as db:
            await db.execute(STAGE_DOWN)
            names = {r[0] for r in await (await db.execute("SELECT indexname FROM pg_indexes WHERE schemaname=current_schema() AND tablename='material_receipts'")).fetchall()}
            self.assertNotIn(INDEX, names); self.assertIn("material_receipts_source_asset_idx", names)
            await db.execute(STAGE_UP)
        self.assertEqual(STAGE_UP, "CREATE UNIQUE INDEX material_receipts_source_asset_active_uidx\nON material_receipts (source_asset_reference)\nWHERE status NOT IN ('REJECTED', 'CANCELLED');\n")

    async def test_preexisting_duplicates_make_migration_fail_without_data_mutation(self):
        source = "asset:preexisting"; ids = (uuid.uuid4(), uuid.uuid4())
        async with await psycopg.AsyncConnection.connect(self.admin_url, autocommit=True) as db:
            for rid in ids: await db.execute("INSERT INTO material_receipts(receipt_id,supplier_name,received_at,source_asset_reference,status) VALUES(%s,'S',now(),%s,'NEEDS_REVIEW')", (rid, source))
            with self.assertRaises(psycopg.errors.UniqueViolation): await db.execute(STAGE_UP)
            rows = await (await db.execute("SELECT receipt_id,status FROM material_receipts ORDER BY receipt_id")).fetchall()
        self.assertEqual(set(rows), {(ids[0], "NEEDS_REVIEW"), (ids[1], "NEEDS_REVIEW")})

    async def test_active_status_matrix_and_terminal_history(self):
        await self.apply()
        for status in ("EXTRACTED", "NEEDS_REVIEW", "CONFIRMED", "POSTED"):
            source = "asset:" + status; rid = uuid.uuid4(); confirmed = status in {"CONFIRMED", "POSTED"}
            async with await psycopg.AsyncConnection.connect(self.admin_url, autocommit=True) as db:
                await db.execute("INSERT INTO material_receipts(receipt_id,supplier_name,received_at,source_asset_reference,status,confirmed_version,confirmed_at,confirmation_actor_reference) VALUES(%s,'S',now(),%s,%s,%s,%s,%s)", (rid, source, status, 1 if confirmed else None, datetime.now(timezone.utc) if confirmed else None, "reviewer:test" if confirmed else None))
            with self.assertRaises(MaterialReceiptError) as caught: await self.repo.create_receipt_candidate(request(source))
            self.assertIs(caught.exception.code, MaterialReceiptFailureCode.SOURCE_ACTIVE_RECEIPT_EXISTS)
        for terminal in ("REJECTED", "CANCELLED"):
            source = "asset:" + terminal
            async with await psycopg.AsyncConnection.connect(self.admin_url, autocommit=True) as db:
                for _ in range(2): await db.execute("INSERT INTO material_receipts(receipt_id,supplier_name,received_at,source_asset_reference,status) VALUES(%s,'S',now(),%s,%s)", (uuid.uuid4(), source, terminal))
            created = await self.repo.create_receipt_candidate(request(source))
            async with await psycopg.AsyncConnection.connect(self.admin_url) as db:
                statuses = [r[0] for r in await (await db.execute("SELECT status FROM material_receipts WHERE source_asset_reference=%s", (source,))).fetchall()]
            self.assertEqual(statuses.count(terminal), 2); self.assertEqual(statuses.count("NEEDS_REVIEW"), 1); self.assertNotIn(created.receipt_id, ())

    async def test_sequential_same_and_different_facts_are_create_only_and_inert(self):
        await self.apply(); source = "asset:sequential"; before = await self.counts()
        first = await self.repo.create_receipt_candidate(request(source, supplier="First"))
        for supplier in ("First", "Different valid facts"):
            with self.assertRaises(MaterialReceiptError) as caught: await self.repo.create_receipt_candidate(request(source, supplier=supplier))
            self.assertIs(caught.exception.code, MaterialReceiptFailureCode.SOURCE_ACTIVE_RECEIPT_EXISTS)
        async with await psycopg.AsyncConnection.connect(self.admin_url) as db:
            row = await (await db.execute("SELECT receipt_id,supplier_name,status,version,confirmed_at FROM material_receipts WHERE source_asset_reference=%s", (source,))).fetchone()
        self.assertEqual(row, (first.receipt_id, "First", "NEEDS_REVIEW", 1, None)); self.assertEqual(await self.counts(), (before[0]+1, before[1]+1, before[2], before[3]))

    async def test_exact_unique_diagnostic_mapping_and_unrelated_unique(self):
        await self.apply(); source = "asset:mapping"; first = request(source); await self.repo.create_receipt_candidate(first)
        with self.assertRaises(MaterialReceiptError) as duplicate: await self.repo.create_receipt_candidate(request(source))
        self.assertIs(duplicate.exception.code, MaterialReceiptFailureCode.SOURCE_ACTIVE_RECEIPT_EXISTS)
        other = request("asset:other"); object.__setattr__(other, "receipt_id", first.receipt_id)
        with self.assertRaises(MaterialReceiptError) as unrelated: await self.repo.create_receipt_candidate(other)
        self.assertIs(unrelated.exception.code, MaterialReceiptFailureCode.DATA_INTEGRITY_ERROR)
        async with await psycopg.AsyncConnection.connect(self.admin_url, autocommit=True) as db:
            await db.execute(STAGE_DOWN)
            await db.execute("CREATE UNIQUE INDEX stage032_wrong_identity ON material_receipts(source_asset_reference) WHERE status NOT IN ('REJECTED','CANCELLED')")
        with self.assertRaises(MaterialReceiptError) as wrong_identity: await self.repo.create_receipt_candidate(request(source))
        self.assertIs(wrong_identity.exception.code, MaterialReceiptFailureCode.DATA_INTEGRITY_ERROR)
        missing_identity = psycopg.errors.UniqueViolation("diagnostic unavailable")
        with patch.object(psycopg.AsyncConnection, "connect", side_effect=missing_identity):
            with self.assertRaises(MaterialReceiptError) as missing: await self.repo.create_receipt_candidate(request("asset:missing-diag"))
        self.assertIs(missing.exception.code, MaterialReceiptFailureCode.DATA_INTEGRITY_ERROR)

    async def test_real_concurrent_race_rolls_back_loser_and_preserves_inventory(self):
        await self.apply(); source = "asset:race"; before = await self.counts(); barrier = asyncio.Barrier(2)
        async def compete():
            await barrier.wait()
            try: await self.repo.create_receipt_candidate(request(source)); return "success"
            except MaterialReceiptError as exc: return "duplicate" if exc.code is MaterialReceiptFailureCode.SOURCE_ACTIVE_RECEIPT_EXISTS else "other"
            except Exception: return "other"
        outcomes = await asyncio.gather(compete(), compete())
        self.assertEqual(outcomes.count("success"), 1); self.assertEqual(outcomes.count("duplicate"), 1); self.assertEqual(outcomes.count("other"), 0)
        after = await self.counts(); self.assertEqual(after, (before[0]+1, before[1]+1, before[2], before[3]))

    async def test_candidate_privileges_and_public_exception_graph_are_bounded(self):
        await self.apply(); source = "asset:bounded"; await self.repo.create_receipt_candidate(request(source))
        runtime_url = conninfo.make_conninfo(host=self.target.host,port=self.target.port,dbname=self.target.dbname,user=CANDIDATE,password=CANDIDATE_PASSWORD,options=f"-csearch_path={self.schema}",sslmode="disable")
        denied = ("CREATE INDEX forbidden ON material_receipts(supplier_name)", "CREATE TABLE forbidden(id int)", "ALTER SCHEMA " + self.schema + " OWNER TO " + CANDIDATE, "UPDATE material_stock SET stock_qty=1", "INSERT INTO inventory_movements DEFAULT VALUES")
        for statement in denied:
            with self.subTest(statement=statement):
                with self.assertRaises(psycopg.errors.InsufficientPrivilege):
                    async with await psycopg.AsyncConnection.connect(runtime_url, autocommit=True) as db: await db.execute(statement)
        manifest_id = uuid.uuid4(); manifest = self.manifest_root / (str(manifest_id) + ".json"); manifest.write_text(json.dumps({"manifest_id": str(manifest_id), "represented_media_type": "text", "received_at": "2026-08-27T00:00:00Z", "manifest_status": "created", "metadata": {"media_type": "text", "character_count": 1}}), encoding="utf-8")
        trusted = TrustedReceiptFacts("S", None, None, datetime.now(timezone.utc), (TrustedReceiptItemFacts(1,"Steel",None,None,None,None,1,Decimal("50"),Decimal("0"),Decimal("50"),"sheet"),))
        evidence = IngestionResult(InputType.TEXT, InputType.TEXT, None, str(manifest), {}, "x", True, False, False, True)
        # Seed the canonical path, then prove the outward terminal graph carries enums only.
        with patch.object(MaterialReceiptRepository, "from_environment", return_value=self.repo): await create_review_candidate_from_ingestion(evidence, trusted)
        with patch.object(MaterialReceiptRepository, "from_environment", return_value=self.repo):
            with self.assertRaises(ReviewApplicationError) as caught: await create_review_candidate_from_ingestion(evidence, trusted)
        self.assertIs(caught.exception.code, ReviewFailureCode.SOURCE_ACTIVE_RECEIPT_EXISTS)
        seen=set(); stack=[caught.exception]
        while stack:
            value=stack.pop()
            if id(value) in seen: continue
            seen.add(id(value)); self.assertNotIsInstance(value, (psycopg.Error, MaterialReceiptRepository, review_use_cases.ReviewFacade, CandidateDatabaseConfig))
            if isinstance(value, BaseException): stack.extend(x for x in (value.__cause__,value.__context__) if x is not None)
        self.assertIsNone(caught.exception.__cause__); self.assertIsNone(caught.exception.__context__)
