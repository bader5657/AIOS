"""Permanent real-PostgreSQL regression authority for Stage 0.32."""

from __future__ import annotations

import asyncio
from dataclasses import fields, is_dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from functools import partial
import json
import os
from pathlib import Path
import tempfile
from types import FrameType, FunctionType, MethodType, TracebackType
import unittest
from unittest.mock import AsyncMock, patch
import uuid

import psycopg
from psycopg import conninfo, sql

from core.app.input_classifier import InputType
from core.app.material_receipts import create_from_ingestion as create_module
from core.app.material_receipts import review_use_cases
from core.app.material_receipts.review_use_cases import ActorContext
from core.app.material_receipts.candidate_input import TrustedReceiptFacts, TrustedReceiptItemFacts
from core.app.material_receipts.create_from_ingestion import create_review_candidate_from_ingestion
from core.app.material_receipts.results import ReviewApplicationError, ReviewFailureCode
from core.ingestion.universal_ingestion import IngestionResult
from core.inventory_posting import repository as posting_repository
from core.material_receipts.errors import MaterialReceiptError, MaterialReceiptFailureCode
from core.material_receipts.models import ReceiptCandidateRequest, ReceiptForReview, ReceiptItemCandidate
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
CREATOR_A = "operator:550e8400-e29b-41d4-a716-446655440000"
CREATOR_B = "operator:6ba7b810-9dad-4d80-b000-000000000001"
CREATOR_C = "operator:6ba7b810-9dad-4d80-a000-000000000002"
CANDIDATE = "aios_material_receipt_candidate_runtime"
CANDIDATE_PASSWORD = "stage032-candidate-" + uuid.uuid4().hex


def request(source: str, *, supplier: str = "Stage 032") -> ReceiptCandidateRequest:
    return ReceiptCandidateRequest(uuid.uuid4(), supplier, "DO-032", date(2026, 8, 27),
        datetime(2026, 8, 27, tzinfo=timezone.utc), source,
        (ReceiptItemCandidate(uuid.uuid4(), 1, "Steel", None, None, None, None,
         1, Decimal("50"), Decimal("0"), Decimal("50"), "sheet"),))


class _InsertBarrierConnection:
    """Test-only wrapper pausing real connections immediately before INSERT."""
    def __init__(self, connection, barrier, poised):
        self._connection = connection; self._barrier = barrier; self._poised = poised
    async def __aenter__(self):
        await self._connection.__aenter__(); return self
    async def __aexit__(self, *args):
        return await self._connection.__aexit__(*args)
    def transaction(self):
        return self._connection.transaction()
    async def execute(self, statement, parameters=None):
        if "INSERT INTO material_receipts" in str(statement):
            self._poised.append(id(self._connection)); await self._barrier.wait()
        return await self._connection.execute(statement, parameters)


def _reachable(root):
    """Walk bounded outward state, including tracebacks and frame locals."""
    stack = [root]; seen = set()
    while stack:
        value = stack.pop()
        if value is None or id(value) in seen: continue
        seen.add(id(value)); yield value
        if isinstance(value, BaseException):
            stack.extend(value.args); stack.extend(value.__dict__.values()); stack.extend((value.__cause__, value.__context__, value.__traceback__))
            if isinstance(value, BaseExceptionGroup): stack.extend(value.exceptions)
        elif isinstance(value, TracebackType): stack.extend((value.tb_next, value.tb_frame))
        elif isinstance(value, FrameType): stack.extend(value.f_locals.values())
        elif isinstance(value, dict): stack.extend(value.keys()); stack.extend(value.values())
        elif isinstance(value, (tuple, list, set, frozenset)): stack.extend(value)
        elif is_dataclass(value) and not isinstance(value, type): stack.extend(getattr(value, field.name) for field in fields(value))
        elif isinstance(value, MethodType): stack.extend((value.__self__, value.__func__))
        elif isinstance(value, FunctionType): stack.extend(cell.cell_contents for cell in (value.__closure__ or ()))
        elif isinstance(value, partial): stack.extend((value.func, value.args, value.keywords))
        else:
            for name in getattr(type(value), "__slots__", ()):
                if isinstance(name, str) and hasattr(value, name): stack.append(getattr(value, name))
            state = getattr(value, "__dict__", None)
            if isinstance(state, dict): stack.extend(state.values())


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
            await db.execute("ALTER TABLE material_receipts ADD COLUMN created_by_actor_reference TEXT NOT NULL, ADD CONSTRAINT material_receipts_created_by_actor_reference_valid CHECK (created_by_actor_reference ~ '^operator:[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')")
            await db.execute("CREATE TABLE unrelated_records(id integer)")
        await self._grant_candidate()
        self.repo = MaterialReceiptRepository(CandidateDatabaseConfig(password=CANDIDATE_PASSWORD,
            host=self.target.host, port=self.target.port, dbname=self.target.dbname, search_path=self.schema))

    async def asyncTearDown(self):
        review_use_cases._MANIFEST_ROOT = self.old_root
        self.manifests.cleanup()
        async with await psycopg.AsyncConnection.connect(self.target.url, autocommit=True) as db:
            await db.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(self.schema)))
            exists = await (await db.execute(
                "SELECT 1 FROM pg_roles WHERE rolname=%s", (CANDIDATE,)
            )).fetchone()
            if exists:
                await db.execute(sql.SQL("DROP ROLE {}").format(sql.Identifier(CANDIDATE)))

    async def _grant_candidate(self):
        async with await psycopg.AsyncConnection.connect(self.admin_url, autocommit=True) as db:
            role = sql.Identifier(CANDIDATE); schema = sql.Identifier(self.schema)
            await db.execute(sql.SQL("GRANT USAGE ON SCHEMA {} TO {}").format(schema, role))
            await db.execute(sql.SQL("GRANT SELECT ON material_receipts,material_receipt_items,material_stock TO {}").format(role))
            await db.execute(sql.SQL("GRANT INSERT (receipt_id,supplier_name,document_number,document_date,received_at,source_asset_reference,created_by_actor_reference), UPDATE (supplier_name,document_number,document_date,received_at,source_asset_reference,status,version,confirmed_version,confirmed_at,confirmation_actor_reference,updated_at) ON material_receipts TO {}").format(role))
            await db.execute(sql.SQL("GRANT INSERT (receipt_item_id,receipt_id,line_number,candidate_material_description,canonical_display_name,size_description,specification,material_id,full_colly_count,qty_per_full_colly,partial_qty,total_qty,unit), UPDATE (line_number,candidate_material_description,canonical_display_name,size_description,specification,material_id,full_colly_count,qty_per_full_colly,partial_qty,total_qty,unit,status,updated_at) ON material_receipt_items TO {}").format(role))

    async def apply(self):
        async with await psycopg.AsyncConnection.connect(self.admin_url, autocommit=True) as db: await db.execute(STAGE_UP)

    async def create_candidate(self, request_value, actor=CREATOR_A):
        return await self.repo._create_receipt_candidate(request_value, actor)

    async def counts(self):
        async with await psycopg.AsyncConnection.connect(self.admin_url) as db:
            return tuple(await (await db.execute("SELECT (SELECT count(*) FROM material_receipts),(SELECT count(*) FROM material_receipt_items),(SELECT count(*) FROM material_stock),(SELECT count(*) FROM inventory_movements)")).fetchone())

    def retained_evidence(self):
        identifier = uuid.uuid4(); path = self.manifest_root / f"{identifier}.json"
        path.write_text(json.dumps({"manifest_id": str(identifier), "represented_media_type": "text", "received_at": "2026-08-27T00:00:00Z", "manifest_status": "created", "metadata": {"media_type": "text", "character_count": 1}}), encoding="utf-8")
        return path, IngestionResult(InputType.TEXT, InputType.TEXT, None, str(path), {}, "x", True, False, False, True)

    @staticmethod
    def trusted(supplier="Stage 032"):
        return TrustedReceiptFacts(supplier, "DO-032", date(2026, 8, 27), datetime(2026, 8, 27, tzinfo=timezone.utc), (TrustedReceiptItemFacts(1,"Steel",None,None,None,None,1,Decimal("50"),Decimal("0"),Decimal("50"),"sheet"),))

    async def public_create(self, evidence, trusted, actor=CREATOR_A):
        with patch.object(MaterialReceiptRepository, "from_environment", return_value=self.repo):
            return await create_review_candidate_from_ingestion(
                evidence, trusted, ActorContext(actor)
            )

    async def fingerprint(self):
        async with await psycopg.AsyncConnection.connect(self.admin_url) as db:
            receipts = await (await db.execute("SELECT receipt_id,supplier_name,document_number,document_date,received_at,source_asset_reference,status,version,confirmed_version,confirmed_at,confirmation_actor_reference,created_at,updated_at FROM material_receipts ORDER BY receipt_id")).fetchall()
            items = await (await db.execute("SELECT * FROM material_receipt_items ORDER BY receipt_item_id")).fetchall()
            stock = await (await db.execute("SELECT * FROM material_stock ORDER BY material_id")).fetchall()
            movements = await (await db.execute("SELECT * FROM inventory_movements ORDER BY movement_id")).fetchall()
        return tuple(receipts), tuple(items), tuple(stock), tuple(movements)


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
            for rid in ids: await db.execute("INSERT INTO material_receipts(receipt_id,supplier_name,received_at,source_asset_reference,status,created_by_actor_reference) VALUES(%s,'S',now(),%s,'NEEDS_REVIEW',%s)", (rid, source, CREATOR_A))
            with self.assertRaises(psycopg.errors.UniqueViolation): await db.execute(STAGE_UP)
            rows = await (await db.execute("SELECT receipt_id,status FROM material_receipts ORDER BY receipt_id")).fetchall()
        self.assertEqual(set(rows), {(ids[0], "NEEDS_REVIEW"), (ids[1], "NEEDS_REVIEW")})

    async def test_active_status_matrix_and_terminal_history(self):
        await self.apply()
        for status in ("EXTRACTED", "NEEDS_REVIEW", "CONFIRMED", "POSTED"):
            source = "asset:" + status; rid = uuid.uuid4(); confirmed = status in {"CONFIRMED", "POSTED"}
            async with await psycopg.AsyncConnection.connect(self.admin_url, autocommit=True) as db:
                await db.execute("INSERT INTO material_receipts(receipt_id,supplier_name,received_at,source_asset_reference,status,confirmed_version,confirmed_at,confirmation_actor_reference,created_by_actor_reference) VALUES(%s,'S',now(),%s,%s,%s,%s,%s,%s)", (rid, source, status, 1 if confirmed else None, datetime.now(timezone.utc) if confirmed else None, "reviewer:test" if confirmed else None, CREATOR_A))
            with self.assertRaises(MaterialReceiptError) as caught: await self.create_candidate(request(source))
            self.assertIs(caught.exception.code, MaterialReceiptFailureCode.SOURCE_ACTIVE_RECEIPT_EXISTS)
        for terminal in ("REJECTED", "CANCELLED"):
            source = "asset:" + terminal
            async with await psycopg.AsyncConnection.connect(self.admin_url, autocommit=True) as db:
                for _ in range(2): await db.execute("INSERT INTO material_receipts(receipt_id,supplier_name,received_at,source_asset_reference,status,created_by_actor_reference) VALUES(%s,'S',now(),%s,%s,%s)", (uuid.uuid4(), source, terminal, CREATOR_A))
            created = await self.create_candidate(request(source))
            async with await psycopg.AsyncConnection.connect(self.admin_url) as db:
                statuses = [r[0] for r in await (await db.execute("SELECT status FROM material_receipts WHERE source_asset_reference=%s", (source,))).fetchall()]
            self.assertEqual(statuses.count(terminal), 2); self.assertEqual(statuses.count("NEEDS_REVIEW"), 1)

    async def _assert_public_duplicate(self, duplicate_facts):
        await self.apply(); _, evidence = self.retained_evidence()
        posting_password = "stage032-posting-must-not-load"
        with patch.dict(os.environ, {"AIOS_MATERIAL_INVENTORY_POSTING_DB_PASSWORD": posting_password}), \
             patch.object(posting_repository.InventoryPostingRepository, "__init__", return_value=None) as posting_repo_init, \
             patch.object(posting_repository.PostingDatabaseConfig, "__init__", return_value=None) as posting_config_init, \
             patch.object(posting_repository.InventoryPostingRepository, "from_environment", side_effect=AssertionError("posting credential load")) as posting_factory, \
             patch.object(posting_repository.InventoryPostingRepository, "post_confirmed_receipt", new_callable=AsyncMock) as post_call, \
             patch.object(MaterialReceiptRepository, "confirm_receipt", new_callable=AsyncMock) as confirm_call:
            first = await self.public_create(evidence, self.trusted("First"))
            self.assertIs(type(first), ReceiptForReview); self.assertEqual(first.status.value, "NEEDS_REVIEW"); self.assertIsNone(first.confirmed_version); self.assertIsNone(first.confirmed_at); self.assertIsNone(first.confirmation_actor_reference)
            before = await self.fingerprint()
            with self.assertRaises(ReviewApplicationError) as caught:
                await self.public_create(evidence, duplicate_facts, CREATOR_B)
            after = await self.fingerprint()
        self.assertIs(caught.exception.code, ReviewFailureCode.SOURCE_ACTIVE_RECEIPT_EXISTS)
        self.assertNotIn("creator", str(caught.exception).lower())
        self.assertFalse(hasattr(caught.exception, "created_by_actor_reference"))
        self.assertEqual(after, before); self.assertEqual(len(before[0]), 1); self.assertEqual(len(before[1]), 1)
        async with await psycopg.AsyncConnection.connect(self.admin_url) as db:
            creator = await (await db.execute("SELECT created_by_actor_reference FROM material_receipts")).fetchone()
        self.assertEqual(creator, (CREATOR_A,))
        posting_repo_init.assert_not_called(); posting_config_init.assert_not_called(); posting_factory.assert_not_called(); post_call.assert_not_awaited(); confirm_call.assert_not_awaited()

    async def test_public_same_facts_duplicate_is_create_only_and_inert(self):
        await self._assert_public_duplicate(self.trusted("First"))

    async def test_public_different_facts_duplicate_is_create_only_and_inert(self):
        await self._assert_public_duplicate(self.trusted("Different valid facts"))

    async def test_terminal_history_retains_exact_ids_and_allows_only_one_active(self):
        await self.apply(); path, _ = self.retained_evidence(); source = str(path)
        rejected, cancelled = uuid.uuid4(), uuid.uuid4()
        async with await psycopg.AsyncConnection.connect(self.admin_url, autocommit=True) as db:
            await db.execute("INSERT INTO material_receipts(receipt_id,supplier_name,received_at,source_asset_reference,status,created_by_actor_reference) VALUES(%s,'S',now(),%s,'REJECTED',%s),(%s,'S',now(),%s,'CANCELLED',%s)", (rejected, source, CREATOR_B, cancelled, source, CREATOR_C))
        replacement = await self.create_candidate(request(source))
        before_duplicate = await self.fingerprint()
        with self.assertRaises(MaterialReceiptError) as caught: await self.create_candidate(request(source))
        self.assertIs(caught.exception.code, MaterialReceiptFailureCode.SOURCE_ACTIVE_RECEIPT_EXISTS)
        after_duplicate = await self.fingerprint(); self.assertEqual(after_duplicate, before_duplicate)
        rows = {row[0]: row[6] for row in after_duplicate[0]}
        self.assertEqual(rows[rejected], "REJECTED"); self.assertEqual(rows[cancelled], "CANCELLED")
        self.assertNotIn(replacement.receipt_id, {rejected, cancelled})
        self.assertEqual(sum(status not in {"REJECTED", "CANCELLED"} for status in rows.values()), 1)
        async with await psycopg.AsyncConnection.connect(self.admin_url) as db:
            creators = dict(await (await db.execute("SELECT receipt_id,created_by_actor_reference FROM material_receipts WHERE source_asset_reference=%s", (source,))).fetchall())
        self.assertEqual(creators, {rejected: CREATOR_B, cancelled: CREATOR_C, replacement.receipt_id: CREATOR_A})


    async def test_sequential_same_and_different_facts_are_create_only_and_inert(self):
        await self.apply(); source = "asset:sequential"; before = await self.counts()
        first = await self.create_candidate(request(source, supplier="First"))
        for supplier in ("First", "Different valid facts"):
            with self.assertRaises(MaterialReceiptError) as caught: await self.create_candidate(request(source, supplier=supplier))
            self.assertIs(caught.exception.code, MaterialReceiptFailureCode.SOURCE_ACTIVE_RECEIPT_EXISTS)
        async with await psycopg.AsyncConnection.connect(self.admin_url) as db:
            row = await (await db.execute("SELECT receipt_id,supplier_name,status,version,confirmed_at FROM material_receipts WHERE source_asset_reference=%s", (source,))).fetchone()
        self.assertEqual(row, (first.receipt_id, "First", "NEEDS_REVIEW", 1, None)); self.assertEqual(await self.counts(), (before[0]+1, before[1]+1, before[2], before[3]))

    async def test_exact_unique_diagnostic_mapping_and_unrelated_unique(self):
        await self.apply(); source = "asset:mapping"; first = request(source); await self.create_candidate(first)
        with self.assertRaises(MaterialReceiptError) as duplicate: await self.create_candidate(request(source))
        self.assertIs(duplicate.exception.code, MaterialReceiptFailureCode.SOURCE_ACTIVE_RECEIPT_EXISTS)
        other = request("asset:other"); object.__setattr__(other, "receipt_id", first.receipt_id)
        with self.assertRaises(MaterialReceiptError) as unrelated: await self.create_candidate(other)
        self.assertIs(unrelated.exception.code, MaterialReceiptFailureCode.DATA_INTEGRITY_ERROR)
        async with await psycopg.AsyncConnection.connect(self.admin_url, autocommit=True) as db:
            await db.execute(STAGE_DOWN)
            await db.execute("CREATE UNIQUE INDEX stage032_wrong_identity ON material_receipts(source_asset_reference) WHERE status NOT IN ('REJECTED','CANCELLED')")
        with self.assertRaises(MaterialReceiptError) as wrong_identity: await self.create_candidate(request(source))
        self.assertIs(wrong_identity.exception.code, MaterialReceiptFailureCode.DATA_INTEGRITY_ERROR)
        missing_identity = psycopg.errors.UniqueViolation("diagnostic unavailable")
        with patch.object(psycopg.AsyncConnection, "connect", side_effect=missing_identity):
            with self.assertRaises(MaterialReceiptError) as missing: await self.create_candidate(request("asset:missing-diag"))
        self.assertIs(missing.exception.code, MaterialReceiptFailureCode.DATA_INTEGRITY_ERROR)

    async def test_real_concurrent_race_synchronizes_immediately_before_insert(self):
        await self.apply(); source = "asset:race"; before = await self.fingerprint()
        barrier = asyncio.Barrier(2); poised = []; real_connect = psycopg.AsyncConnection.connect
        async def synchronized_connect(*args, **kwargs):
            connection = await real_connect(*args, **kwargs)
            return _InsertBarrierConnection(connection, barrier, poised)
        async def compete(candidate):
            try: await self.create_candidate(candidate); return "success"
            except MaterialReceiptError as exc: return "duplicate" if exc.code is MaterialReceiptFailureCode.SOURCE_ACTIVE_RECEIPT_EXISTS else "other"
            except Exception: return "other"
        contenders = (request(source), request(source))
        with patch.object(psycopg.AsyncConnection, "connect", side_effect=synchronized_connect):
            outcomes = await asyncio.wait_for(asyncio.gather(*(compete(value) for value in contenders)), timeout=10)
        self.assertEqual(len(set(poised)), 2); self.assertEqual(len(poised), 2)
        self.assertEqual(outcomes.count("success"), 1); self.assertEqual(outcomes.count("duplicate"), 1); self.assertEqual(outcomes.count("other"), 0)
        after = await self.fingerprint(); self.assertEqual(len(after[0]), len(before[0])+1); self.assertEqual(len(after[1]), len(before[1])+1)
        self.assertEqual(after[2:], before[2:]); self.assertEqual(sum(row[5] == source and row[6] not in {"REJECTED", "CANCELLED"} for row in after[0]), 1)
        winner_receipts = {row[0] for row in after[0]} - {row[0] for row in before[0]}
        winner_items = {row[0] for row in after[1]} - {row[0] for row in before[1]}
        self.assertEqual(len(winner_receipts), 1); self.assertEqual(len(winner_items), 1)
        loser = next(value for value in contenders if value.receipt_id not in winner_receipts); self.assertNotIn(loser.receipt_id, winner_receipts); self.assertNotIn(loser.items[0].receipt_item_id, winner_items)


    async def test_candidate_identity_has_only_governed_candidate_privileges(self):
        await self.apply(); await self.create_candidate(request("asset:allowed"))
        async with await psycopg.AsyncConnection.connect(self.admin_url, autocommit=True) as db:
            await db.execute("INSERT INTO unrelated_records(id) VALUES (7)")
            unrelated_before = tuple(await (await db.execute("SELECT id FROM unrelated_records ORDER BY id")).fetchall())
        runtime_url = conninfo.make_conninfo(host=self.target.host,port=self.target.port,dbname=self.target.dbname,user=CANDIDATE,password=CANDIDATE_PASSWORD,options=f"-csearch_path={self.schema}",sslmode="disable")
        denied = ("CREATE INDEX forbidden ON material_receipts(supplier_name)", "ALTER TABLE material_receipts ADD COLUMN forbidden integer", "DROP TABLE unrelated_records", "CREATE TABLE forbidden(id int)", "ALTER SCHEMA " + self.schema + " OWNER TO " + CANDIDATE, "UPDATE material_stock SET stock_qty=1", "INSERT INTO inventory_movements DEFAULT VALUES", "INSERT INTO unrelated_records(id) VALUES (8)", "UPDATE unrelated_records SET id=8", "DELETE FROM unrelated_records")
        for statement in denied:
            with self.subTest(statement=statement):
                with self.assertRaises(psycopg.errors.InsufficientPrivilege):
                    async with await psycopg.AsyncConnection.connect(runtime_url, autocommit=True) as db: await db.execute(statement)
        async with await psycopg.AsyncConnection.connect(self.admin_url) as db:
            unrelated_after = tuple(await (await db.execute("SELECT id FROM unrelated_records ORDER BY id")).fetchall())
        self.assertEqual(unrelated_before, ((7,),)); self.assertEqual(unrelated_after, unrelated_before)
        async with await psycopg.AsyncConnection.connect(runtime_url) as db:
            identity = await (await db.execute("SELECT current_user")).fetchone()
            allowed = await (await db.execute("SELECT has_table_privilege(current_user,'material_receipts','SELECT'),has_column_privilege(current_user,'material_receipts','receipt_id','INSERT'),has_table_privilege(current_user,'material_receipt_items','SELECT'),has_column_privilege(current_user,'material_receipt_items','receipt_item_id','INSERT')")).fetchone()
        self.assertEqual(identity, (CANDIDATE,)); self.assertEqual(allowed, (True, True, True, True))
        async with await psycopg.AsyncConnection.connect(self.admin_url) as db:
            attributes = await (await db.execute("SELECT r.rolsuper,r.rolcreatedb,r.rolcreaterole,r.rolreplication,r.rolbypassrls,d.datdba=r.oid,n.nspowner=r.oid FROM pg_roles r CROSS JOIN pg_database d CROSS JOIN pg_namespace n WHERE r.rolname=%s AND d.datname=current_database() AND n.nspname=%s", (CANDIDATE,self.schema))).fetchone()
            memberships = await (await db.execute("SELECT parent.rolname,m.admin_option FROM pg_auth_members m JOIN pg_roles member ON member.oid=m.member JOIN pg_roles parent ON parent.oid=m.roleid WHERE member.rolname=%s", (CANDIDATE,))).fetchall()
            prohibited = await (await db.execute("SELECT has_database_privilege(%s,current_database(),'CREATE'),has_schema_privilege(%s,%s,'CREATE'),has_table_privilege(%s,%s||'.inventory_movements','INSERT'),has_table_privilege(%s,%s||'.material_stock','UPDATE'),has_table_privilege(%s,%s||'.unrelated_records','UPDATE')", (CANDIDATE,CANDIDATE,self.schema,CANDIDATE,self.schema,CANDIDATE,self.schema,CANDIDATE,self.schema))).fetchone()
            grant_options = await (await db.execute("SELECT has_table_privilege(%s,%s||'.material_receipts','SELECT WITH GRANT OPTION'),has_column_privilege(%s,%s||'.material_receipts','receipt_id','INSERT WITH GRANT OPTION'),has_table_privilege(%s,%s||'.material_receipt_items','SELECT WITH GRANT OPTION'),has_column_privilege(%s,%s||'.material_receipt_items','receipt_item_id','INSERT WITH GRANT OPTION')", (CANDIDATE,self.schema,CANDIDATE,self.schema,CANDIDATE,self.schema,CANDIDATE,self.schema))).fetchone()
            unrelated_acl = await (await db.execute("SELECT has_table_privilege(%s,%s||'.unrelated_records','INSERT'),has_table_privilege(%s,%s||'.unrelated_records','UPDATE'),has_table_privilege(%s,%s||'.unrelated_records','DELETE'),has_table_privilege(%s,%s||'.unrelated_records','TRUNCATE'),has_table_privilege(%s,%s||'.unrelated_records','REFERENCES'),has_table_privilege(%s,%s||'.unrelated_records','TRIGGER')", (CANDIDATE,self.schema,CANDIDATE,self.schema,CANDIDATE,self.schema,CANDIDATE,self.schema,CANDIDATE,self.schema,CANDIDATE,self.schema))).fetchone()
            unrelated_grants = await (await db.execute("SELECT has_table_privilege(%s,%s||'.unrelated_records','INSERT WITH GRANT OPTION'),has_table_privilege(%s,%s||'.unrelated_records','UPDATE WITH GRANT OPTION'),has_table_privilege(%s,%s||'.unrelated_records','DELETE WITH GRANT OPTION')", (CANDIDATE,self.schema,CANDIDATE,self.schema,CANDIDATE,self.schema))).fetchone()
            unrelated_owner = await (await db.execute("SELECT r.rolname FROM pg_class c JOIN pg_roles r ON r.oid=c.relowner WHERE c.oid=(%s||'.unrelated_records')::regclass", (self.schema,))).fetchone()
        self.assertEqual(attributes, (False,False,False,False,False,False,False)); self.assertEqual(memberships, []); self.assertEqual(prohibited, (False,False,False,False,False)); self.assertEqual(grant_options, (False,False,False,False))
        self.assertEqual(unrelated_acl, (False,False,False,False,False,False)); self.assertEqual(unrelated_grants, (False,False,False)); self.assertNotEqual(unrelated_owner, (CANDIDATE,))
        self.assertFalse(any("posting" in role for role, _ in memberships))
        with self.assertRaises(ValueError): posting_repository.PostingDatabaseConfig(password="stage032-posting-identity-sentinel", host=self.target.host, port=self.target.port, dbname=self.target.dbname, username=CANDIDATE, search_path=self.schema)

    async def test_real_db_check_failure_complete_exception_graph_is_bounded(self):
        await self.apply()
        _, evidence = self.retained_evidence()
        invalid_variant = "operator:550e8400-e29b-41d4-7716-446655440000"

        with patch.object(
            create_module,
            "authorize_candidate_creation_actor_reference",
            return_value=invalid_variant,
        ), patch.object(MaterialReceiptRepository, "from_environment", return_value=self.repo):
            with self.assertRaises(ReviewApplicationError) as caught:
                await create_review_candidate_from_ingestion(
                    evidence, self.trusted("DB CHECK graph"), ActorContext(CREATOR_A)
                )

        outward = caught.exception
        self.assertIs(outward.code, ReviewFailureCode.CANDIDATE_OPERATION_FAILED)
        self.assertIs(
            outward.candidate_code, MaterialReceiptFailureCode.DATA_INTEGRITY_ERROR
        )
        self.assertIsNone(outward.__cause__)
        self.assertIsNone(outward.__context__)
        self.assertEqual(await self.counts(), (0, 0, 0, 0))
        forbidden_types = (
            psycopg.Error, psycopg.AsyncConnection, MaterialReceiptRepository,
            review_use_cases.ReviewFacade, CandidateDatabaseConfig,
            posting_repository.InventoryPostingRepository,
            posting_repository.PostingDatabaseConfig,
        )
        for value in _reachable(outward):
            self.assertNotIsInstance(value, forbidden_types)
            if isinstance(value, str):
                lowered = value.lower()
                self.assertNotIn(invalid_variant, value)
                self.assertNotIn(CANDIDATE_PASSWORD, value)
                self.assertNotIn("23514", value)
                self.assertNotIn("postgresql://", lowered)
                self.assertNotIn("password=", lowered)
                self.assertNotIn("insert into", lowered)
                self.assertNotIn("check constraint", lowered)

    async def test_public_duplicate_complete_exception_graph_is_bounded(self):
        await self.apply(); _, evidence = self.retained_evidence(); trusted = self.trusted("Bounded")
        await self.public_create(evidence, trusted)
        async def capture(current_evidence, current_trusted):
            try:
                await create_review_candidate_from_ingestion(current_evidence, current_trusted, ActorContext(CREATOR_A))
            except ReviewApplicationError as error:
                return error
            raise AssertionError("duplicate did not fail")
        with patch.object(MaterialReceiptRepository, "from_environment", return_value=self.repo):
            outward = await capture(evidence, trusted)
        self.assertIs(outward.code, ReviewFailureCode.SOURCE_ACTIVE_RECEIPT_EXISTS); self.assertIsNone(outward.__cause__); self.assertIsNone(outward.__context__)
        forbidden_types = (psycopg.Error, psycopg.AsyncConnection, MaterialReceiptRepository, review_use_cases.ReviewFacade, CandidateDatabaseConfig, posting_repository.InventoryPostingRepository, posting_repository.PostingDatabaseConfig)
        for value in _reachable(outward):
            self.assertNotIsInstance(value, forbidden_types)
            if isinstance(value, str):
                lowered = value.lower()
                self.assertNotIn(CANDIDATE_PASSWORD, value); self.assertNotIn(INDEX, value); self.assertNotIn("23505", value)
                self.assertNotIn("postgresql://", lowered); self.assertNotIn("password=", lowered); self.assertNotIn("insert into", lowered); self.assertNotIn("select ", lowered)
