import base64
import inspect
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
from core.aios_core import (
    AIOSCore,
    CoreRouteFailureCode,
    CoreRouteResult,
)
from core.domain.domain_event import DomainEvent
from core.event import EventDeliveryFailureCode, EventEngine
from core.ingestion import universal_ingestion
from core.pipeline import asset_pipeline
from core.registry import PostgresRegistry, RegistryPersistenceError
from core.storage import document_manifest, file_storage, metadata_engine
from core.storage import telegram_storage


TEST_DATABASE_URL = os.environ.get("AIOS_REGISTRY_TEST_DATABASE_URL")
ROOT = Path(__file__).resolve().parents[3]
UP = (ROOT / "migrations/postgres/0001_create_registry_records.up.sql").read_text()
PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


class ApprovedPipelineEvent(DomainEvent):
    __slots__ = ()

    def __init__(self, event_id="stage-8-2-1-event"):
        super().__init__(
            event_id,
            datetime(2026, 8, 20, 4, 0, tzinfo=timezone.utc),
            "document.registered",
        )


class FakeTelegramFile:
    def __init__(self, content):
        self.content = content
        self.download_calls = 0

    async def download_to_drive(self, destination):
        self.download_calls += 1
        Path(destination).write_bytes(self.content)


def fake_message(*, photo=False, text=None, observations=None):
    observations = observations if observations is not None else []

    async def reply_text(payload):
        observations.append("respond")
        message.acknowledgement = payload

    message = SimpleNamespace(
        photo=[SimpleNamespace(file_id="photo-file-id")] if photo else None,
        voice=None,
        document=None,
        video=None,
        audio=None,
        text=text,
        caption=None,
        from_user=SimpleNamespace(id=8201, username="stage-owner"),
        chat=SimpleNamespace(id=-8202),
        message_id=8203,
        media_group_id=None,
        reply_text=AsyncMock(side_effect=reply_text),
        acknowledgement=None,
    )
    return message


def fake_update(message):
    return SimpleNamespace(
        update_id=8204,
        message=message,
        effective_user=None if message is None else message.from_user,
        effective_chat=None if message is None else message.chat,
    )


@unittest.skipUnless(
    TEST_DATABASE_URL,
    "AIOS_REGISTRY_TEST_DATABASE_URL is required for isolated PostgreSQL tests",
)
class OfficialPipelineOwnershipSequenceIntegrationTests(
    unittest.IsolatedAsyncioTestCase
):
    async def asyncSetUp(self):
        self.schema = "aios_stage_8_2_1_" + uuid.uuid4().hex
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
        self.telegram_file = FakeTelegramFile(PNG_BYTES)
        self.bot = SimpleNamespace(
            get_file=AsyncMock(return_value=self.telegram_file)
        )
        self.context = SimpleNamespace(bot=self.bot)
        self.event = ApprovedPipelineEvent()

    async def asyncTearDown(self):
        async with await psycopg.AsyncConnection.connect(
            TEST_DATABASE_URL, autocommit=True
        ) as admin:
            await admin.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(
                    sql.Identifier(self.schema)
                )
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

    async def invoke_adapter(
        self,
        message,
        *,
        registry=None,
        engine=None,
        core=None,
        event=None,
        observations=None,
    ):
        captured = {}
        observations = observations if observations is not None else []

        async def injected_ingestion(received_message, received_context):
            observations.append("ingestion_accept")
            result = await universal_ingestion.ingest_telegram_message(
                received_message,
                received_context,
                registry=self.registry if registry is None else registry,
                domain_event=self.event if event is None else event,
                event_engine=engine,
                event_schema_version=21,
                aios_core=core,
            )
            captured["result"] = result
            observations.append("ingestion_return")
            return result

        with (
            patch.object(
                telegram_adapter,
                "ingest_telegram_message",
                AsyncMock(side_effect=injected_ingestion),
            ) as adapter_ingestion,
            patch.dict(
                file_storage.STORAGE_ROOTS,
                {"image": self.storage_root},
            ),
            patch.object(document_manifest, "MANIFEST_ROOT", self.manifest_root),
        ):
            await telegram_adapter.handle_update(
                fake_update(message), self.context
            )

        captured["adapter_ingestion"] = adapter_ingestion
        return captured

    async def test_full_file_lifecycle_has_exact_owners_order_and_commit_visibility(self):
        observations = ["receive"]
        message = fake_message(photo=True, observations=observations)
        context_calls = 0
        original_context_factory = universal_ingestion.RequestContext.from_telegram

        def observe_context(**kwargs):
            nonlocal context_calls
            context_calls += 1
            observations.append("request_context")
            return original_context_factory(**kwargs)

        original_pipeline = asset_pipeline.run_asset_pipeline

        async def observe_pipeline(**kwargs):
            observations.append("asset_pipeline")
            return await original_pipeline(**kwargs)

        original_store = telegram_storage.save_telegram_attachment

        async def observe_store(*args, **kwargs):
            observations.append("store_original")
            return await original_store(*args, **kwargs)

        original_metadata = metadata_engine.extract_basic_metadata

        def observe_metadata(**kwargs):
            observations.append("metadata")
            return original_metadata(**kwargs)

        original_manifest = document_manifest.create_document_manifest

        def observe_manifest(**kwargs):
            observations.append("manifest")
            return original_manifest(**kwargs)

        class ObservedRegistry:
            async def register(inner_self, persistence_input):
                observations.append("registry")
                self.assertTrue(Path(persistence_input.manifest_ref).is_file())
                row = await self.registry.register(persistence_input)
                observations.append("registry_commit")
                return row

        engine = EventEngine()
        handler_observations = []

        async def commit_observing_handler(envelope):
            observations.append("event_handler")
            async with await psycopg.AsyncConnection.connect(
                self.scoped_url
            ) as connection:
                visible = await (
                    await connection.execute(
                        "SELECT record_id, metadata FROM registry_records"
                    )
                ).fetchone()
            handler_observations.append((envelope, visible))

        engine.register(self.event.event_name, commit_observing_handler)
        original_process = engine.process

        async def observe_process(envelope):
            observations.append("process")
            result = await original_process(envelope)
            observations.append("event_success")
            return result

        engine.process = AsyncMock(side_effect=observe_process)
        real_core = AIOSCore()

        async def observe_route(envelope):
            observations.append("route")
            result = await real_core.route(envelope)
            observations.append("route_complete")
            return result

        core = SimpleNamespace(route=AsyncMock(side_effect=observe_route))

        with (
            patch.object(
                universal_ingestion.RequestContext,
                "from_telegram",
                side_effect=observe_context,
            ) as request_context_factory,
            patch.object(
                universal_ingestion,
                "run_asset_pipeline",
                AsyncMock(side_effect=observe_pipeline),
            ) as pipeline_call,
            patch.object(
                asset_pipeline,
                "save_telegram_attachment",
                AsyncMock(side_effect=observe_store),
            ) as storage_call,
            patch.object(
                asset_pipeline,
                "extract_basic_metadata",
                side_effect=observe_metadata,
            ) as metadata_call,
            patch.object(
                asset_pipeline,
                "create_document_manifest",
                side_effect=observe_manifest,
            ) as manifest_call,
        ):
            captured = await self.invoke_adapter(
                message,
                registry=ObservedRegistry(),
                engine=engine,
                core=core,
                observations=observations,
            )

        result = captured["result"]
        request_context_factory.assert_called_once()
        self.assertEqual(context_calls, 1)
        pipeline_call.assert_awaited_once()
        storage_call.assert_awaited_once()
        metadata_call.assert_called_once()
        manifest_call.assert_called_once()
        engine.process.assert_awaited_once()
        core.route.assert_awaited_once()
        self.assertEqual(self.telegram_file.download_calls, 1)
        self.assertTrue(Path(result.stored_path).is_file())
        self.assertEqual(Path(result.stored_path).read_bytes(), PNG_BYTES)
        self.assertTrue(Path(result.manifest_path).is_file())
        self.assertEqual(await self.count_rows(), 1)
        self.assertEqual(len(handler_observations), 1)
        engine_envelope = engine.process.await_args.args[0]
        core_envelope = core.route.await_args.args[0]
        self.assertIs(engine_envelope, core_envelope)
        self.assertIs(handler_observations[0][0], core_envelope)
        self.assertIs(core_envelope.event, self.event)
        self.assertIsNotNone(handler_observations[0][1])
        self.assertEqual(
            handler_observations[0][1][0], result.registry_record_id
        )
        self.assertTrue(result.event_delivery_succeeded)
        self.assertTrue(result.route_handoff_ready)
        self.assertIn("AIOS menerima input", message.acknowledgement)
        self.assertNotIn(
            str(result.registry_record_id),
            message.acknowledgement.splitlines(),
        )
        for left, right in zip(
            (
                "receive",
                "ingestion_accept",
                "request_context",
                "asset_pipeline",
                "store_original",
                "metadata",
                "manifest",
                "registry",
                "registry_commit",
                "process",
                "event_success",
                "route",
                "route_complete",
                "ingestion_return",
            ),
            (
                "ingestion_accept",
                "request_context",
                "asset_pipeline",
                "store_original",
                "metadata",
                "manifest",
                "registry",
                "registry_commit",
                "process",
                "event_success",
                "route",
                "route_complete",
                "ingestion_return",
                "respond",
            ),
        ):
            self.assertLess(observations.index(left), observations.index(right))

    async def test_text_and_url_paths_skip_storage_without_remote_retrieval(self):
        cases = (
            ("plain lifecycle text", None),
            ("https://example.test/Exact?Q=Preserved", "web_link"),
            ("https://youtu.be/ExactIdentifier", "youtube_link"),
        )
        for index, (text, expected_type) in enumerate(cases):
            with self.subTest(expected_type=expected_type or "text"):
                message = fake_message(text=text)
                engine = EventEngine()

                async def handler(_envelope):
                    return None

                engine.register(self.event.event_name, handler)
                core = SimpleNamespace(route=AsyncMock(wraps=AIOSCore().route))
                with patch.object(
                    asset_pipeline,
                    "save_telegram_attachment",
                    AsyncMock(),
                ) as storage_call:
                    captured = await self.invoke_adapter(
                        message,
                        engine=engine,
                        core=core,
                        event=ApprovedPipelineEvent(f"variant-{index}"),
                    )

                result = captured["result"]
                storage_call.assert_not_awaited()
                self.bot.get_file.assert_not_awaited()
                core.route.assert_awaited_once()
                message.reply_text.assert_awaited_once()
                self.assertIsNone(result.stored_path)
                self.assertTrue(result.route_handoff_ready)
                persisted = await self.registry.read(result.registry_record_id)
                self.assertIsNotNone(persisted)
                if expected_type is None:
                    self.assertIsNone(persisted.source_url)
                else:
                    self.assertEqual(persisted.source_url, text)
                    self.assertEqual(persisted.metadata["source_url"], text)

    async def test_invalid_receive_stops_every_lifecycle_owner(self):
        ingestion = AsyncMock()
        with patch.object(
            telegram_adapter, "ingest_telegram_message", ingestion
        ):
            await telegram_adapter.handle_update(
                fake_update(None), self.context
            )
        ingestion.assert_not_awaited()
        self.bot.get_file.assert_not_awaited()
        self.assertEqual(await self.count_rows(), 0)

    async def test_storage_failure_stops_before_metadata_manifest_and_downstream(self):
        message = fake_message(photo=True)
        engine = SimpleNamespace(process=AsyncMock())
        core = SimpleNamespace(route=AsyncMock())
        with (
            patch.object(
                asset_pipeline,
                "save_telegram_attachment",
                AsyncMock(return_value=None),
            ) as storage_call,
            patch.object(
                asset_pipeline, "extract_basic_metadata", Mock()
            ) as metadata_call,
            patch.object(
                asset_pipeline, "create_document_manifest", Mock()
            ) as manifest_call,
            patch.object(self.registry, "register", AsyncMock()) as register_call,
        ):
            captured = await self.invoke_adapter(
                message, engine=engine, core=core
            )

        storage_call.assert_awaited_once()
        metadata_call.assert_not_called()
        manifest_call.assert_not_called()
        register_call.assert_not_awaited()
        engine.process.assert_not_awaited()
        core.route.assert_not_awaited()
        message.reply_text.assert_not_awaited()
        self.assertFalse(captured["result"].register_handoff_ready)

    async def test_registry_failure_preserves_upstream_and_stops_process_and_route(self):
        message = fake_message(photo=True)
        registry = SimpleNamespace(
            register=AsyncMock(side_effect=RegistryPersistenceError("failed"))
        )
        engine = SimpleNamespace(process=AsyncMock())
        core = SimpleNamespace(route=AsyncMock())

        captured = await self.invoke_adapter(
            message, registry=registry, engine=engine, core=core
        )

        result = captured["result"]
        registry.register.assert_awaited_once()
        engine.process.assert_not_awaited()
        core.route.assert_not_awaited()
        self.assertFalse(result.registration_succeeded)
        self.assertTrue(Path(result.stored_path).is_file())
        self.assertTrue(Path(result.manifest_path).is_file())
        self.assertTrue(result.metadata)
        message.reply_text.assert_awaited_once()

    async def test_bounded_event_failure_preserves_commit_and_never_routes(self):
        message = fake_message(photo=True)
        engine = EventEngine()
        engine.process = AsyncMock(wraps=engine.process)
        core = SimpleNamespace(route=AsyncMock())

        captured = await self.invoke_adapter(
            message, engine=engine, core=core
        )

        result = captured["result"]
        engine.process.assert_awaited_once()
        core.route.assert_not_awaited()
        self.assertIs(
            result.event_delivery_failure_code,
            EventDeliveryFailureCode.NO_HANDLER,
        )
        self.assertFalse(result.route_handoff_ready)
        self.assertEqual(await self.count_rows(), 1)
        self.assertTrue(Path(result.stored_path).is_file())
        self.assertTrue(Path(result.manifest_path).is_file())
        message.reply_text.assert_awaited_once()

    async def test_bounded_core_failure_preserves_upstream_and_acknowledges_receipt(self):
        message = fake_message(photo=True)
        engine = EventEngine()

        async def handler(_envelope):
            return None

        engine.register(self.event.event_name, handler)
        core = SimpleNamespace(
            route=AsyncMock(
                return_value=CoreRouteResult(
                    False,
                    None,
                    CoreRouteFailureCode.INVALID_INPUT,
                    "projection-only bounded failure",
                )
            )
        )

        captured = await self.invoke_adapter(
            message, engine=engine, core=core
        )

        result = captured["result"]
        core.route.assert_awaited_once()
        self.assertTrue(result.event_delivery_succeeded)
        self.assertFalse(result.route_handoff_ready)
        self.assertEqual(await self.count_rows(), 1)
        self.assertTrue(Path(result.stored_path).is_file())
        message.reply_text.assert_awaited_once()

    async def test_unexpected_core_exception_propagates_without_acknowledgement(self):
        message = fake_message(photo=True)
        engine = EventEngine()

        async def handler(_envelope):
            return None

        engine.register(self.event.event_name, handler)
        engine.process = AsyncMock(wraps=engine.process)
        core = SimpleNamespace(
            route=AsyncMock(side_effect=RuntimeError("unexpected core defect"))
        )

        with self.assertRaisesRegex(RuntimeError, "unexpected core defect"):
            await self.invoke_adapter(message, engine=engine, core=core)

        engine.process.assert_awaited_once()
        core.route.assert_awaited_once()
        message.reply_text.assert_not_awaited()
        self.assertEqual(await self.count_rows(), 1)
        self.assertEqual(self.telegram_file.download_calls, 1)
        self.assertEqual(len(tuple(self.storage_root.iterdir())), 1)
        self.assertEqual(len(tuple(self.manifest_root.iterdir())), 1)

    def test_static_ownership_retry_transaction_and_brain_boundaries(self):
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
        for marker in (
            "RequestContext",
            "classify_telegram_message",
            "save_telegram_attachment",
            "extract_basic_metadata",
            "create_document_manifest",
        ):
            self.assertNotIn(marker, adapter_source)
        self.assertNotIn("RequestContext.from_telegram(", pipeline_source)
        self.assertNotIn("DomainEvent(", registry_source)
        self.assertNotIn("core.aios_core", engine_source)
        self.assertNotIn("core.brain", core_source.lower())
        self.assertNotIn("await brain", core_source.lower())
        self.assertEqual(ingestion_source.count("event_engine.process("), 1)
        self.assertEqual(ingestion_source.count("aios_core.route("), 1)
        for source in (adapter_source, ingestion_source, pipeline_source):
            for prohibited in (
                "retry",
                "backoff",
                "idempotency",
                "dedup",
                "create_task",
                "asyncio.gather",
            ):
                self.assertNotIn(prohibited, source.lower())
        for sql_marker in ("psycopg", "transaction(", ".commit(", ".rollback("):
            self.assertNotIn(sql_marker, ingestion_source.lower())


if __name__ == "__main__":
    unittest.main()
