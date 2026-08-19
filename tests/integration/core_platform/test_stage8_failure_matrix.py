import base64
import inspect
import json
import os
import tempfile
import unittest
import uuid
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import psycopg
from psycopg import conninfo, sql

from core.adapters.telegram import main as telegram_adapter
from core.aios_core import CoreRouteFailureCode, CoreRouteResult
from core.domain.domain_event import DomainEvent
from core.event import (
    EventDeliveryFailureCode,
    EventDeliveryResult,
    EventEngine,
)
from core.ingestion import universal_ingestion
from core.pipeline import asset_pipeline
from core.registry import PostgresRegistry, RegistryPersistenceError
from core.storage import document_manifest, file_storage


TEST_DATABASE_URL = os.environ.get("AIOS_REGISTRY_TEST_DATABASE_URL")
ROOT = Path(__file__).resolve().parents[3]
UP = (ROOT / "migrations/postgres/0001_create_registry_records.up.sql").read_text()
PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


class FailureMatrixEvent(DomainEvent):
    __slots__ = ()

    def __init__(self):
        super().__init__(
            "stage-8-4-1-caller-event",
            datetime(2026, 8, 20, 8, 41, tzinfo=timezone.utc),
            "document.failure-matrix.approved",
        )


class FakeTelegramFile:
    def __init__(self, content=PNG_BYTES, *, error=None):
        self.content = content
        self.error = error
        self.download_calls = 0
        self.destinations = []

    async def download_to_drive(self, destination):
        self.download_calls += 1
        self.destinations.append(Path(destination))
        if self.error is not None:
            raise self.error
        Path(destination).write_bytes(self.content)


class ObservedRegistry:
    def __init__(self, registry):
        self.registry = registry
        self.calls = 0

    async def register(self, persistence_input):
        self.calls += 1
        return await self.registry.register(persistence_input)


def telegram_photo_message():
    message = SimpleNamespace(
        photo=[SimpleNamespace(file_id="stage-8-4-1-photo")],
        voice=None,
        document=None,
        video=None,
        audio=None,
        text=None,
        caption=None,
        from_user=SimpleNamespace(id=8401, username="failure-owner"),
        chat=SimpleNamespace(id=-8402),
        message_id=8403,
        acknowledgement=None,
    )

    async def reply_text(payload):
        message.acknowledgement = payload

    message.reply_text = AsyncMock(side_effect=reply_text)
    return message


def telegram_update(message):
    return SimpleNamespace(
        update_id=8404,
        message=message,
        effective_user=message.from_user,
        effective_chat=message.chat,
    )


@unittest.skipUnless(
    TEST_DATABASE_URL,
    "AIOS_REGISTRY_TEST_DATABASE_URL is required for isolated PostgreSQL tests",
)
class Stage8FailureMatrixIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.schema = "aios_stage_8_4_1_" + uuid.uuid4().hex
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
        self.storage_root = self.root / "images"
        self.manifest_root = self.root / "manifests"
        self.telegram_file = FakeTelegramFile()
        self.bot = SimpleNamespace(
            get_file=AsyncMock(side_effect=lambda _file_id: self.telegram_file)
        )
        self.context = SimpleNamespace(bot=self.bot)
        self.event = FailureMatrixEvent()

    async def asyncTearDown(self):
        async with await psycopg.AsyncConnection.connect(
            TEST_DATABASE_URL, autocommit=True
        ) as admin:
            await admin.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(
                    sql.Identifier(self.schema)
                )
            )

    def read_only_url(self):
        return conninfo.make_conninfo(
            TEST_DATABASE_URL,
            options=(
                f"-csearch_path={self.schema} "
                "-cdefault_transaction_read_only=on"
            ),
        )

    async def count_rows(self):
        async with await psycopg.AsyncConnection.connect(
            self.scoped_url
        ) as connection:
            return (
                await (
                    await connection.execute(
                        "SELECT count(*) FROM registry_records"
                    )
                ).fetchone()
            )[0]

    def stored_originals(self):
        if not self.storage_root.exists():
            return ()
        return tuple(self.storage_root.iterdir())

    def manifests(self):
        if not self.manifest_root.exists():
            return ()
        return tuple(self.manifest_root.glob("*.json"))

    def assert_completed_upstream_files(self):
        originals = self.stored_originals()
        manifests = self.manifests()
        self.assertEqual(len(originals), 1)
        self.assertEqual(originals[0].read_bytes(), PNG_BYTES)
        self.assertEqual(len(manifests), 1)
        manifest = json.loads(manifests[0].read_text(encoding="utf-8"))
        self.assertEqual(manifest["manifest_status"], "created")
        self.assertEqual(
            manifest["metadata"]["file_size_bytes"], len(PNG_BYTES)
        )
        return originals[0], manifests[0], manifest["metadata"]

    async def invoke_adapter(self, message, *, registry, engine, core):
        captured = {}

        async def injected_ingestion(received_message, received_context):
            result = await universal_ingestion.ingest_telegram_message(
                received_message,
                received_context,
                registry=registry,
                domain_event=self.event,
                event_engine=engine,
                event_schema_version=841,
                aios_core=core,
            )
            captured["result"] = result
            return result

        with (
            patch.object(
                telegram_adapter,
                "ingest_telegram_message",
                AsyncMock(side_effect=injected_ingestion),
            ),
            patch.dict(
                file_storage.STORAGE_ROOTS,
                {"image": self.storage_root},
            ),
            patch.object(document_manifest, "MANIFEST_ROOT", self.manifest_root),
        ):
            await telegram_adapter.handle_update(
                telegram_update(message), self.context
            )
        return captured.get("result")

    async def test_storage_failure_suppresses_every_later_stage_and_cleans_temporary(self):
        self.telegram_file = FakeTelegramFile(error=OSError("download failed"))
        message = telegram_photo_message()
        registry = SimpleNamespace(register=AsyncMock())
        engine = SimpleNamespace(process=AsyncMock())
        core = SimpleNamespace(route=AsyncMock())

        with (
            patch.object(asset_pipeline, "extract_basic_metadata", Mock()) as metadata,
            patch.object(asset_pipeline, "create_document_manifest", Mock()) as manifest,
        ):
            result = await self.invoke_adapter(
                message, registry=registry, engine=engine, core=core
            )

        self.assertIsNotNone(result)
        self.assertFalse(result.register_handoff_ready)
        self.assertEqual(self.telegram_file.download_calls, 1)
        self.assertTrue(self.telegram_file.destinations)
        self.assertTrue(
            all(not path.exists() for path in self.telegram_file.destinations)
        )
        metadata.assert_not_called()
        manifest.assert_not_called()
        registry.register.assert_not_awaited()
        engine.process.assert_not_awaited()
        core.route.assert_not_awaited()
        message.reply_text.assert_not_awaited()

    async def test_metadata_failure_preserves_original_and_suppresses_later_stages(self):
        message = telegram_photo_message()
        registry = SimpleNamespace(register=AsyncMock())
        engine = SimpleNamespace(process=AsyncMock())
        core = SimpleNamespace(route=AsyncMock())

        with (
            patch.object(
                asset_pipeline,
                "extract_basic_metadata",
                Mock(side_effect=RuntimeError("metadata defect")),
            ) as metadata,
            patch.object(asset_pipeline, "create_document_manifest", Mock()) as manifest,
        ):
            with self.assertRaisesRegex(RuntimeError, "metadata defect"):
                await self.invoke_adapter(
                    message, registry=registry, engine=engine, core=core
                )

        metadata.assert_called_once()
        manifest.assert_not_called()
        registry.register.assert_not_awaited()
        engine.process.assert_not_awaited()
        core.route.assert_not_awaited()
        message.reply_text.assert_not_awaited()
        self.assertEqual(self.telegram_file.download_calls, 1)
        self.assertEqual(len(self.stored_originals()), 1)
        self.assertEqual(self.stored_originals()[0].read_bytes(), PNG_BYTES)
        self.assertEqual(self.manifests(), ())

    async def test_manifest_failure_preserves_original_and_metadata_without_manifest(self):
        message = telegram_photo_message()
        registry = SimpleNamespace(register=AsyncMock())
        engine = SimpleNamespace(process=AsyncMock())
        core = SimpleNamespace(route=AsyncMock())
        observed_metadata = []
        real_metadata = asset_pipeline.extract_basic_metadata

        def capture_metadata(**kwargs):
            value = real_metadata(**kwargs)
            observed_metadata.append(value)
            return value

        with (
            patch.object(
                asset_pipeline,
                "extract_basic_metadata",
                side_effect=capture_metadata,
            ) as metadata,
            patch.object(
                asset_pipeline,
                "create_document_manifest",
                Mock(side_effect=OSError("manifest defect")),
            ) as manifest,
        ):
            with self.assertRaisesRegex(OSError, "manifest defect"):
                await self.invoke_adapter(
                    message, registry=registry, engine=engine, core=core
                )

        metadata.assert_called_once()
        manifest.assert_called_once()
        registry.register.assert_not_awaited()
        engine.process.assert_not_awaited()
        core.route.assert_not_awaited()
        message.reply_text.assert_not_awaited()
        self.assertEqual(len(observed_metadata), 1)
        self.assertEqual(observed_metadata[0]["file_size_bytes"], len(PNG_BYTES))
        self.assertEqual(len(self.stored_originals()), 1)
        self.assertEqual(self.stored_originals()[0].read_bytes(), PNG_BYTES)
        self.assertEqual(self.manifests(), ())

    async def test_registry_persistence_failure_rolls_back_and_acknowledges_receipt_only(self):
        message = telegram_photo_message()
        registry = ObservedRegistry(PostgresRegistry(self.read_only_url()))
        engine = SimpleNamespace(process=AsyncMock())
        core = SimpleNamespace(route=AsyncMock())

        result = await self.invoke_adapter(
            message, registry=registry, engine=engine, core=core
        )

        self.assertEqual(registry.calls, 1)
        self.assertFalse(result.registration_succeeded)
        self.assertTrue(result.register_handoff_ready)
        self.assertFalse(result.route_handoff_ready)
        self.assertEqual(await self.count_rows(), 0)
        engine.process.assert_not_awaited()
        core.route.assert_not_awaited()
        self.assert_completed_upstream_files()
        message.reply_text.assert_awaited_once()
        self.assertIn("AIOS menerima input", message.acknowledgement)

    async def test_unexpected_registry_exception_propagates_without_acknowledgement(self):
        message = telegram_photo_message()
        registry = SimpleNamespace(
            register=AsyncMock(side_effect=RuntimeError("unexpected registry defect"))
        )
        engine = SimpleNamespace(process=AsyncMock())
        core = SimpleNamespace(route=AsyncMock())

        with self.assertRaisesRegex(RuntimeError, "unexpected registry defect"):
            await self.invoke_adapter(
                message, registry=registry, engine=engine, core=core
            )

        registry.register.assert_awaited_once()
        engine.process.assert_not_awaited()
        core.route.assert_not_awaited()
        message.reply_text.assert_not_awaited()
        self.assertEqual(await self.count_rows(), 0)
        self.assert_completed_upstream_files()

    async def test_invalid_envelope_result_preserves_commit_and_suppresses_core(self):
        message = telegram_photo_message()
        delivery = EventDeliveryResult(
            False,
            0,
            EventDeliveryFailureCode.INVALID_ENVELOPE,
            "injected integration gating evidence; Stage 6 remains primary",
        )
        engine = SimpleNamespace(process=AsyncMock(return_value=delivery))
        core = SimpleNamespace(route=AsyncMock())

        result = await self.invoke_adapter(
            message, registry=self.registry, engine=engine, core=core
        )

        engine.process.assert_awaited_once()
        core.route.assert_not_awaited()
        self.assertIs(
            result.event_delivery_failure_code,
            EventDeliveryFailureCode.INVALID_ENVELOPE,
        )
        self.assertFalse(result.route_handoff_ready)
        self.assertEqual(await self.count_rows(), 1)
        self.assert_completed_upstream_files()
        message.reply_text.assert_awaited_once()

    async def test_no_handler_preserves_commit_and_suppresses_core(self):
        message = telegram_photo_message()
        engine = EventEngine()
        engine.process = AsyncMock(wraps=engine.process)
        core = SimpleNamespace(route=AsyncMock())

        result = await self.invoke_adapter(
            message, registry=self.registry, engine=engine, core=core
        )

        engine.process.assert_awaited_once()
        core.route.assert_not_awaited()
        self.assertIs(
            result.event_delivery_failure_code,
            EventDeliveryFailureCode.NO_HANDLER,
        )
        self.assertFalse(result.route_handoff_ready)
        self.assertEqual(await self.count_rows(), 1)
        self.assert_completed_upstream_files()
        message.reply_text.assert_awaited_once()

    async def test_handler_failure_preserves_commit_and_prior_handler_effect(self):
        message = telegram_photo_message()
        engine = EventEngine()
        effects = []

        async def successful_handler(envelope):
            effects.append(("completed", envelope))

        async def failing_handler(envelope):
            effects.append(("failed", envelope))
            raise RuntimeError("bounded handler defect")

        engine.register(self.event.event_name, successful_handler)
        engine.register(self.event.event_name, failing_handler)
        engine.process = AsyncMock(wraps=engine.process)
        core = SimpleNamespace(route=AsyncMock())

        result = await self.invoke_adapter(
            message, registry=self.registry, engine=engine, core=core
        )

        engine.process.assert_awaited_once()
        core.route.assert_not_awaited()
        self.assertEqual([effect[0] for effect in effects], ["completed", "failed"])
        self.assertIs(effects[0][1], effects[1][1])
        self.assertIs(
            result.event_delivery_failure_code,
            EventDeliveryFailureCode.HANDLER_FAILURE,
        )
        self.assertFalse(result.route_handoff_ready)
        self.assertEqual(await self.count_rows(), 1)
        self.assert_completed_upstream_files()
        message.reply_text.assert_awaited_once()

    async def test_unexpected_event_exception_preserves_commit_without_acknowledgement(self):
        message = telegram_photo_message()
        engine = SimpleNamespace(
            process=AsyncMock(side_effect=RuntimeError("unexpected event defect"))
        )
        core = SimpleNamespace(route=AsyncMock())

        with self.assertRaisesRegex(RuntimeError, "unexpected event defect"):
            await self.invoke_adapter(
                message, registry=self.registry, engine=engine, core=core
            )

        engine.process.assert_awaited_once()
        core.route.assert_not_awaited()
        message.reply_text.assert_not_awaited()
        self.assertEqual(await self.count_rows(), 1)
        self.assert_completed_upstream_files()

    async def test_core_bounded_failure_preserves_event_and_acknowledges_receipt_only(self):
        message = telegram_photo_message()
        engine = EventEngine()

        async def handler(_envelope):
            return None

        engine.register(self.event.event_name, handler)
        real_process = engine.process
        completed_results = []

        async def capture_process(envelope):
            result = await real_process(envelope)
            completed_results.append(result)
            return result

        engine.process = AsyncMock(side_effect=capture_process)
        core_result = CoreRouteResult(
            False,
            None,
            CoreRouteFailureCode.INVALID_INPUT,
            "projection-only bounded Core evidence",
        )
        core = SimpleNamespace(route=AsyncMock(return_value=core_result))

        result = await self.invoke_adapter(
            message, registry=self.registry, engine=engine, core=core
        )

        engine.process.assert_awaited_once()
        core.route.assert_awaited_once()
        self.assertIs(
            engine.process.await_args.args[0], core.route.await_args.args[0]
        )
        self.assertEqual(len(completed_results), 1)
        self.assertTrue(completed_results[0].success)
        self.assertTrue(result.event_delivery_succeeded)
        self.assertFalse(result.route_handoff_ready)
        self.assertEqual(await self.count_rows(), 1)
        self.assert_completed_upstream_files()
        message.reply_text.assert_awaited_once()

    async def test_unexpected_core_exception_preserves_event_without_acknowledgement(self):
        message = telegram_photo_message()
        engine = EventEngine()

        async def handler(_envelope):
            return None

        engine.register(self.event.event_name, handler)
        real_process = engine.process
        completed_results = []

        async def capture_process(envelope):
            result = await real_process(envelope)
            completed_results.append(result)
            return result

        engine.process = AsyncMock(side_effect=capture_process)
        core = SimpleNamespace(
            route=AsyncMock(side_effect=RuntimeError("unexpected core defect"))
        )

        with self.assertRaisesRegex(RuntimeError, "unexpected core defect"):
            await self.invoke_adapter(
                message, registry=self.registry, engine=engine, core=core
            )

        engine.process.assert_awaited_once()
        core.route.assert_awaited_once()
        self.assertIs(
            engine.process.await_args.args[0], core.route.await_args.args[0]
        )
        self.assertEqual(len(completed_results), 1)
        self.assertTrue(completed_results[0].success)
        message.reply_text.assert_not_awaited()
        self.assertEqual(await self.count_rows(), 1)
        self.assert_completed_upstream_files()

    def test_static_matrix_has_no_retry_compensation_dedupe_or_cross_transaction(self):
        adapter_source = inspect.getsource(telegram_adapter)
        ingestion_source = inspect.getsource(universal_ingestion)
        pipeline_source = inspect.getsource(asset_pipeline)
        registry_source = inspect.getsource(
            __import__("core.registry.postgres_registry", fromlist=["unused"])
        )
        engine_source = inspect.getsource(
            __import__("core.event.event_engine", fromlist=["unused"])
        )
        core_source = inspect.getsource(
            __import__("core.aios_core.core", fromlist=["unused"])
        )

        self.assertIn("if not ingestion.register_handoff_ready", adapter_source)
        self.assertNotIn("route_handoff_ready", adapter_source)
        self.assertEqual(ingestion_source.count("registry_client.register("), 1)
        self.assertEqual(ingestion_source.count("event_engine.process("), 1)
        self.assertEqual(ingestion_source.count("aios_core.route("), 1)
        self.assertEqual(pipeline_source.count("save_telegram_attachment("), 2)
        self.assertEqual(registry_source.count("INSERT INTO registry_records"), 1)
        self.assertIn("SET TRANSACTION ISOLATION LEVEL READ COMMITTED", registry_source)
        self.assertNotIn("psycopg", ingestion_source)
        self.assertNotIn("core.registry", engine_source)
        self.assertNotIn("core.aios_core", engine_source)
        self.assertNotIn("core.brain", core_source.lower())
        self.assertNotIn("await brain", core_source.lower())
        for source in (
            adapter_source,
            ingestion_source,
            pipeline_source,
            registry_source,
            engine_source,
            core_source,
        ):
            for prohibited in (
                "backoff",
                "idempotency",
                "processed_event",
                "route_ledger",
                "duplicate_suppression",
                "compensat",
                "create_task",
                "asyncio.gather",
            ):
                self.assertNotIn(prohibited, source.lower())


if __name__ == "__main__":
    unittest.main()
