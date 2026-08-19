import inspect
import json
import os
import tempfile
import unittest
import uuid
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import psycopg
from psycopg import conninfo, sql

from core.aios_core import AIOSCore
from core.app.input_classifier import InputType
from core.domain.domain_event import DomainEvent
from core.event import EventDeliveryFailureCode, EventEngine
from core.ingestion import universal_ingestion
from core.pipeline import asset_pipeline
from core.registry import PostgresRegistry
from core.storage import document_manifest


TEST_DATABASE_URL = os.environ.get("AIOS_REGISTRY_TEST_DATABASE_URL")
ROOT = Path(__file__).resolve().parents[3]
UP = (ROOT / "migrations/postgres/0001_create_registry_records.up.sql").read_text()


class SuppliedDomainEvent(DomainEvent):
    __slots__ = ()

    def __init__(self, event_id, occurred_at, event_name):
        super().__init__(event_id, occurred_at, event_name)


def telegram_document_message():
    return SimpleNamespace(
        photo=None,
        voice=None,
        document=SimpleNamespace(file_name="original.pdf"),
        video=None,
        audio=None,
        text=None,
        caption=None,
        from_user=SimpleNamespace(id=7101, username="telegram-user"),
        chat=SimpleNamespace(id=-8102),
        message_id=9103,
    )


def telegram_web_message(text):
    return SimpleNamespace(
        photo=None,
        voice=None,
        document=None,
        video=None,
        audio=None,
        text=text,
        caption=None,
        from_user=SimpleNamespace(id=7101, username="telegram-user"),
        chat=SimpleNamespace(id=-8102),
        message_id=9103,
    )


class ObservedRegistry:
    def __init__(self, registry, observations):
        self.registry = registry
        self.observations = observations
        self.calls = 0

    async def register(self, persistence_input):
        self.calls += 1
        manifest_path = Path(persistence_input.manifest_ref)
        self.observations.append("registry")
        if not manifest_path.is_file():
            raise AssertionError("completed manifest must exist before Registry")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest["manifest_status"] != "created":
            raise AssertionError("manifest must be completed before Registry")
        self.persistence_input = persistence_input
        return await self.registry.register(persistence_input)


@unittest.skipUnless(
    TEST_DATABASE_URL,
    "AIOS_REGISTRY_TEST_DATABASE_URL is required for isolated PostgreSQL tests",
)
class DocumentManifestRegistryEventEngineIntegrationTests(
    unittest.IsolatedAsyncioTestCase
):
    async def asyncSetUp(self):
        self.schema = "aios_stage_8_1_3_" + uuid.uuid4().hex
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
        self.root = Path(self.tempdir.name)
        self.manifest_root = self.root / "manifests"
        self.original_path = self.root / "original.pdf"
        self.original_bytes = b"stage-8.1.3-preserved-original"
        self.original_path.write_bytes(self.original_bytes)
        self.event = SuppliedDomainEvent(
            "caller-supplied-event-813",
            datetime(2026, 8, 20, 3, 4, 5, tzinfo=timezone.utc),
            "document.registration.approved",
        )

    async def asyncTearDown(self):
        async with await psycopg.AsyncConnection.connect(
            TEST_DATABASE_URL, autocommit=True
        ) as admin:
            await admin.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(self.schema))
            )

    async def ingest_document(self, *, registry=None, **kwargs):
        async def preserve_original(*_args, **_kwargs):
            return str(self.original_path)

        with (
            patch.object(document_manifest, "MANIFEST_ROOT", self.manifest_root),
            patch.object(
                asset_pipeline,
                "create_document_manifest",
                wraps=document_manifest.create_document_manifest,
            ) as create_manifest,
            patch.object(
                asset_pipeline,
                "save_telegram_attachment",
                AsyncMock(side_effect=preserve_original),
            ),
        ):
            result = await universal_ingestion.ingest_telegram_message(
                telegram_document_message(),
                SimpleNamespace(),
                registry=self.registry if registry is None else registry,
                **kwargs,
            )
        return result, create_manifest

    async def count_rows(self):
        async with await psycopg.AsyncConnection.connect(self.scoped_url) as connection:
            row = await (
                await connection.execute("SELECT count(*) FROM registry_records")
            ).fetchone()
        return row[0]

    async def test_manifest_precedes_single_registry_call_with_exact_mapping(self):
        observations = []
        observed_registry = ObservedRegistry(self.registry, observations)
        result, create_manifest = await self.ingest_document(registry=observed_registry)

        create_manifest.assert_called_once()
        self.assertEqual(observations, ["registry"])
        self.assertEqual(observed_registry.calls, 1)
        persistence_input = observed_registry.persistence_input
        self.assertEqual(
            {
                field: getattr(persistence_input, field)
                for field in persistence_input.__dataclass_fields__
            },
            {
                "identity_ref": result.manifest_path,
                "represented_media_type": InputType.PDF.value,
                "metadata": result.metadata,
                "relationships": [],
                "manifest_ref": result.manifest_path,
                "registration_status": None,
                "storage_path": result.stored_path,
                "source_url": None,
            },
        )
        self.assertIs(persistence_input.metadata, result.metadata)
        for telegram_identifier in (
            "telegram_user_id",
            "telegram_chat_id",
            "telegram_message_id",
            "username",
        ):
            self.assertNotIn(telegram_identifier, persistence_input.__dataclass_fields__)
        persisted = await self.registry.read(result.registry_record_id)
        self.assertIsNotNone(persisted)
        self.assertEqual(await self.count_rows(), 1)

    async def test_web_source_url_is_exact_and_has_no_storage_path(self):
        exact_url = "https://example.test/watch?v=Exact%2BText"
        observed_registry = ObservedRegistry(self.registry, [])
        with patch.object(document_manifest, "MANIFEST_ROOT", self.manifest_root):
            result = await universal_ingestion.ingest_telegram_message(
                telegram_web_message(exact_url),
                SimpleNamespace(),
                registry=observed_registry,
            )

        self.assertTrue(result.registration_succeeded)
        self.assertEqual(observed_registry.calls, 1)
        self.assertEqual(observed_registry.persistence_input.source_url, exact_url)
        self.assertIsNone(observed_registry.persistence_input.storage_path)

    async def test_commit_is_visible_to_independent_handler_before_processing(self):
        observed_registry = ObservedRegistry(self.registry, [])
        engine = EventEngine()
        handler_observations = []

        async def independently_observe_commit(envelope):
            async with await psycopg.AsyncConnection.connect(
                self.scoped_url
            ) as connection:
                visible = await (
                    await connection.execute(
                        "SELECT record_id, metadata FROM registry_records"
                    )
                ).fetchone()
            handler_observations.append((envelope, visible))

        engine.register(self.event.event_name, independently_observe_commit)
        process = AsyncMock(wraps=engine.process)
        engine.process = process
        with patch.object(
            universal_ingestion,
            "EventEnvelope",
            wraps=universal_ingestion.EventEnvelope,
        ) as envelope_type:
            result, _ = await self.ingest_document(
                registry=observed_registry,
                domain_event=self.event,
                event_engine=engine,
                event_schema_version=13,
                aios_core=AIOSCore(),
            )

        envelope_type.assert_called_once()
        process.assert_awaited_once()
        self.assertEqual(len(handler_observations), 1)
        envelope, visible = handler_observations[0]
        self.assertEqual(visible[0], result.registry_record_id)
        self.assertEqual(visible[1], result.metadata)
        self.assertIs(envelope.event, self.event)
        self.assertEqual(envelope.event_id, self.event.id)
        self.assertEqual(envelope.event_name, self.event.event_name)
        self.assertEqual(envelope.occurred_at, self.event.occurred_at)
        self.assertIsNone(envelope.aggregate_id)
        self.assertIsNone(envelope.correlation_id)
        self.assertIsNone(envelope.causation_id)
        self.assertEqual(envelope.schema_version, 13)
        self.assertNotEqual(envelope.event_id, result.registry_record_id)
        self.assertTrue(result.registration_succeeded)
        self.assertTrue(result.event_publication_attempted)
        self.assertTrue(result.event_delivery_succeeded)
        self.assertIsNone(result.event_delivery_failure_code)

    async def test_registry_failure_stops_event_and_preserves_upstream_artifacts(self):
        missing_schema_url = conninfo.make_conninfo(
            TEST_DATABASE_URL,
            options=f"-csearch_path=missing_stage_8_1_3_{uuid.uuid4().hex}",
        )
        observed_registry = ObservedRegistry(
            PostgresRegistry(missing_schema_url), []
        )
        engine = SimpleNamespace(process=AsyncMock())
        with patch.object(
            universal_ingestion,
            "EventEnvelope",
            wraps=universal_ingestion.EventEnvelope,
        ) as envelope_type:
            result, create_manifest = await self.ingest_document(
                registry=observed_registry,
                domain_event=self.event,
                event_engine=engine,
                event_schema_version=1,
            )

        self.assertEqual(observed_registry.calls, 1)
        create_manifest.assert_called_once()
        envelope_type.assert_not_called()
        engine.process.assert_not_awaited()
        self.assertFalse(result.registration_succeeded)
        self.assertFalse(result.event_publication_attempted)
        self.assertEqual(self.original_path.read_bytes(), self.original_bytes)
        self.assertTrue(Path(result.manifest_path).is_file())
        manifest = json.loads(Path(result.manifest_path).read_text(encoding="utf-8"))
        self.assertEqual(manifest["metadata"], result.metadata)
        self.assertEqual(await self.count_rows(), 0)

    async def test_no_domain_event_commits_without_publication(self):
        engine = SimpleNamespace(process=AsyncMock())
        result, _ = await self.ingest_document(event_engine=engine)

        self.assertTrue(result.registration_succeeded)
        self.assertIsNotNone(await self.registry.read(result.registry_record_id))
        engine.process.assert_not_awaited()
        self.assertFalse(result.event_publication_attempted)
        self.assertFalse(result.event_delivery_succeeded)
        self.assertIsNone(result.event_delivery_failure_code)

    async def test_real_no_handler_maps_once_and_preserves_commit(self):
        engine = EventEngine()
        process = AsyncMock(wraps=engine.process)
        engine.process = process
        result, _ = await self.ingest_document(
            domain_event=self.event,
            event_engine=engine,
            event_schema_version=2,
        )

        process.assert_awaited_once()
        self.assertTrue(result.event_publication_attempted)
        self.assertFalse(result.event_delivery_succeeded)
        self.assertIs(
            result.event_delivery_failure_code, EventDeliveryFailureCode.NO_HANDLER
        )
        self.assertIsNotNone(await self.registry.read(result.registry_record_id))

    async def test_handler_failure_maps_once_without_compensation(self):
        engine = EventEngine()
        calls = 0

        async def failing_handler(_envelope):
            nonlocal calls
            calls += 1
            raise RuntimeError("approved bounded failure")

        engine.register(self.event.event_name, failing_handler)
        process = AsyncMock(wraps=engine.process)
        engine.process = process
        result, _ = await self.ingest_document(
            domain_event=self.event,
            event_engine=engine,
            event_schema_version=3,
        )

        process.assert_awaited_once()
        self.assertEqual(calls, 1)
        self.assertTrue(result.event_publication_attempted)
        self.assertFalse(result.event_delivery_succeeded)
        self.assertIs(
            result.event_delivery_failure_code,
            EventDeliveryFailureCode.HANDLER_FAILURE,
        )
        self.assertIsNotNone(await self.registry.read(result.registry_record_id))
        self.assertEqual(self.original_path.read_bytes(), self.original_bytes)
        self.assertTrue(Path(result.manifest_path).is_file())

    async def test_unexpected_engine_exception_propagates_after_commit_without_retry(self):
        engine = SimpleNamespace(
            process=AsyncMock(side_effect=RuntimeError("unexpected event defect"))
        )
        with self.assertRaisesRegex(RuntimeError, "unexpected event defect"):
            await self.ingest_document(
                domain_event=self.event,
                event_engine=engine,
                event_schema_version=4,
            )

        engine.process.assert_awaited_once()
        self.assertEqual(await self.count_rows(), 1)
        self.assertEqual(self.original_path.read_bytes(), self.original_bytes)
        self.assertEqual(len(tuple(self.manifest_root.glob("*.json"))), 1)

    async def test_repeated_explicit_calls_are_not_deduplicated(self):
        engine = EventEngine()
        handled = []

        async def handler(envelope):
            handled.append(envelope)

        engine.register(self.event.event_name, handler)
        process = AsyncMock(wraps=engine.process)
        engine.process = process
        first, _ = await self.ingest_document(
            domain_event=self.event,
            event_engine=engine,
            event_schema_version=5,
            aios_core=AIOSCore(),
        )
        second, _ = await self.ingest_document(
            domain_event=self.event,
            event_engine=engine,
            event_schema_version=5,
            aios_core=AIOSCore(),
        )

        self.assertNotEqual(first.registry_record_id, second.registry_record_id)
        self.assertEqual(await self.count_rows(), 2)
        self.assertEqual(process.await_count, 2)
        self.assertEqual(len(handled), 2)

    def test_static_endpoint_excludes_retry_dedup_and_cross_transaction(self):
        ingestion_source = inspect.getsource(universal_ingestion)
        registry_source = inspect.getsource(
            __import__("core.registry.postgres_registry", fromlist=["unused"])
        )
        engine_source = inspect.getsource(
            __import__("core.event.event_engine", fromlist=["unused"])
        )
        self.assertEqual(ingestion_source.count("registry_client.register("), 1)
        self.assertEqual(ingestion_source.count("event_engine.process("), 1)
        self.assertEqual(ingestion_source.count("aios_core.route("), 1)
        self.assertLess(
            ingestion_source.index("registry_client.register("),
            ingestion_source.index("event_engine.process("),
        )
        self.assertIn("SET TRANSACTION ISOLATION LEVEL READ COMMITTED", registry_source)
        self.assertNotIn("core.event", registry_source)
        self.assertNotIn("core.registry", engine_source)
        for prohibited in (
            "retry",
            "backoff",
            "idempotency",
            "dedup",
            "processed_event",
        ):
            with self.subTest(prohibited=prohibited):
                self.assertNotIn(prohibited, ingestion_source)


if __name__ == "__main__":
    unittest.main()
