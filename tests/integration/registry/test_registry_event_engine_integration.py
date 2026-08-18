import os
import sys
import tempfile
import unittest
import uuid
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import psycopg
from psycopg import conninfo, sql


TEST_DATABASE_URL = os.environ.get("AIOS_REGISTRY_TEST_DATABASE_URL")
ROOT = Path(__file__).resolve().parents[3]
UP = (ROOT / "migrations/postgres/0001_create_registry_records.up.sql").read_text()

telegram_module = SimpleNamespace(Message=object)
telegram_ext_module = SimpleNamespace(
    ContextTypes=SimpleNamespace(DEFAULT_TYPE=object)
)

with patch.dict(
    sys.modules,
    {
        "telegram": telegram_module,
        "telegram.ext": telegram_ext_module,
        "core.storage.document_manifest": SimpleNamespace(
            create_document_manifest=Mock()
        ),
        "core.storage.metadata_engine": SimpleNamespace(
            extract_basic_metadata=Mock()
        ),
        "core.storage.telegram_storage": SimpleNamespace(
            save_telegram_attachment=AsyncMock()
        ),
    },
):
    from core.app.input_classifier import InputType
    from core.domain.domain_event import DomainEvent
    from core.event import EventDeliveryFailureCode, EventEngine
    from core.ingestion import universal_ingestion
    from core.pipeline import asset_pipeline
    from core.registry import PostgresRegistry, RegistryPersistenceError


class SuppliedDomainEvent(DomainEvent):
    def __init__(self, event_id, occurred_at, event_name):
        super().__init__(event_id, occurred_at, event_name)


def telegram_message():
    return SimpleNamespace(
        photo=None,
        voice=None,
        document=SimpleNamespace(file_name="original.bin"),
        video=None,
        audio=None,
        text=None,
        caption=None,
        from_user=SimpleNamespace(id=7),
        chat=SimpleNamespace(id=8),
        message_id=9,
    )


@unittest.skipUnless(
    TEST_DATABASE_URL,
    "AIOS_REGISTRY_TEST_DATABASE_URL is required for isolated PostgreSQL tests",
)
class RegistryEventEngineIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.schema = "aios_registry_event_" + uuid.uuid4().hex
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
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        root = Path(self.tempdir.name)
        self.original_path = root / "original.bin"
        self.manifest_path = root / "manifest.json"
        self.original_path.write_bytes(b"exact-original")
        self.manifest_path.write_text('{"exact": true}', encoding="utf-8")
        self.metadata = {"media_type": "document", "exact": True}
        self.pipeline_result = asset_pipeline.AssetPipelineResult(
            success=True,
            stored_path=str(self.original_path),
            metadata=self.metadata,
            manifest_path=str(self.manifest_path),
            register_handoff_ready=True,
        )
        self.event = SuppliedDomainEvent(
            "domain-event-632",
            datetime(2026, 8, 19, 5, 0, tzinfo=timezone.utc),
            "document.registered",
        )
        self.pipeline_patch = patch.object(
            universal_ingestion,
            "run_asset_pipeline",
            AsyncMock(return_value=self.pipeline_result),
        )
        self.recognition_patch = patch.object(
            universal_ingestion,
            "recognize_telegram_message",
            return_value=InputType.DOCUMENT,
        )
        self.classification_patch = patch.object(
            universal_ingestion,
            "classify_telegram_message",
            return_value=InputType.DOCUMENT,
        )
        for active_patch in (
            self.pipeline_patch, self.recognition_patch, self.classification_patch
        ):
            active_patch.start()
            self.addCleanup(active_patch.stop)

    async def asyncTearDown(self):
        async with await psycopg.AsyncConnection.connect(
            TEST_DATABASE_URL, autocommit=True
        ) as admin:
            await admin.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(
                    sql.Identifier(self.schema)
                )
            )

    async def ingest(self, *, registry=None, **kwargs):
        return await universal_ingestion.ingest_telegram_message(
            telegram_message(),
            SimpleNamespace(),
            registry=self.registry if registry is None else registry,
            **kwargs,
        )

    async def test_successful_registry_commit_precedes_exact_publication(self):
        engine = EventEngine()
        handled = []

        async def handler(envelope):
            async with await psycopg.AsyncConnection.connect(
                self.scoped_url
            ) as connection:
                committed_count = await (
                    await connection.execute("SELECT count(*) FROM registry_records")
                ).fetchone()
            handled.append((envelope, committed_count[0]))

        engine.register(self.event.event_name, handler)
        process = AsyncMock(wraps=engine.process)
        engine.process = process
        result = await self.ingest(
            domain_event=self.event,
            event_engine=engine,
            event_schema_version=11,
        )

        persisted = await self.registry.read(result.registry_record_id)
        self.assertIsNotNone(persisted)
        process.assert_awaited_once()
        self.assertEqual(len(handled), 1)
        self.assertEqual(handled[0][1], 1)
        envelope = handled[0][0]
        self.assertIs(envelope.event, self.event)
        self.assertEqual(envelope.event_id, self.event.id)
        self.assertEqual(envelope.event_name, self.event.event_name)
        self.assertEqual(envelope.occurred_at, self.event.occurred_at)
        self.assertIsNone(envelope.aggregate_id)
        self.assertIsNone(envelope.correlation_id)
        self.assertIsNone(envelope.causation_id)
        self.assertEqual(envelope.schema_version, 11)
        self.assertNotEqual(envelope.event_id, result.registry_record_id)
        self.assertTrue(result.registration_succeeded)
        self.assertTrue(result.event_publication_attempted)
        self.assertTrue(result.event_delivery_succeeded)
        self.assertIsNone(result.event_delivery_failure_code)

    async def test_no_domain_event_commits_without_invoking_engine(self):
        engine = SimpleNamespace(process=AsyncMock())
        result = await self.ingest(event_engine=engine, event_schema_version=2)

        self.assertIsNotNone(await self.registry.read(result.registry_record_id))
        engine.process.assert_not_awaited()
        self.assertTrue(result.registration_succeeded)
        self.assertFalse(result.event_publication_attempted)
        self.assertFalse(result.event_delivery_succeeded)
        self.assertIsNone(result.event_delivery_failure_code)

    async def test_handler_failure_preserves_committed_row_and_upstream_artifacts(self):
        engine = EventEngine()
        handler_calls = 0

        async def failing_handler(_envelope):
            nonlocal handler_calls
            handler_calls += 1
            raise RuntimeError("bounded handler failure")

        engine.register(self.event.event_name, failing_handler)
        process = AsyncMock(wraps=engine.process)
        engine.process = process
        result = await self.ingest(
            domain_event=self.event,
            event_engine=engine,
            event_schema_version=5,
        )

        persisted = await self.registry.read(result.registry_record_id)
        self.assertIsNotNone(persisted)
        self.assertEqual(persisted.metadata, self.metadata)
        self.assertEqual(self.original_path.read_bytes(), b"exact-original")
        self.assertEqual(
            self.manifest_path.read_text(encoding="utf-8"), '{"exact": true}'
        )
        self.assertEqual(handler_calls, 1)
        process.assert_awaited_once()
        self.assertTrue(result.registration_succeeded)
        self.assertFalse(result.event_delivery_succeeded)
        self.assertIs(
            result.event_delivery_failure_code,
            EventDeliveryFailureCode.HANDLER_FAILURE,
        )

    async def test_registry_failure_makes_zero_event_engine_calls(self):
        registry = SimpleNamespace(
            register=AsyncMock(side_effect=RegistryPersistenceError("failed"))
        )
        engine = SimpleNamespace(process=AsyncMock())
        result = await self.ingest(
            registry=registry,
            domain_event=self.event,
            event_engine=engine,
            event_schema_version=1,
        )

        registry.register.assert_awaited_once()
        engine.process.assert_not_awaited()
        self.assertFalse(result.registration_succeeded)
        self.assertFalse(result.event_publication_attempted)


if __name__ == "__main__":
    unittest.main()
