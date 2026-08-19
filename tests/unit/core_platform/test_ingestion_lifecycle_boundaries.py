import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]

with patch.dict(
    sys.modules,
    {
        "telegram": SimpleNamespace(Message=object),
        "telegram.ext": SimpleNamespace(
            ContextTypes=SimpleNamespace(DEFAULT_TYPE=object)
        ),
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
    from core.ingestion import universal_ingestion
    from core.pipeline import asset_pipeline

def telegram_message(**overrides):
    fields = {
        "photo": None,
        "voice": None,
        "document": None,
        "video": None,
        "audio": None,
        "text": None,
        "caption": None,
        "from_user": SimpleNamespace(id=7),
        "chat": SimpleNamespace(id=8),
        "message_id": 9,
    }
    fields.update(overrides)
    return SimpleNamespace(**fields)

class IngestionLifecycleBoundaryTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.registry = SimpleNamespace(
            register=AsyncMock(return_value=SimpleNamespace(record_id=101))
        )
        self.registry_factory = patch.object(
            universal_ingestion.PostgresRegistry,
            "from_environment",
            return_value=self.registry,
        )
        self.registry_factory_mock = self.registry_factory.start()
        self.addCleanup(self.registry_factory.stop)
    async def test_manifest_exposes_only_register_handoff_and_acknowledgement(self):
        calls = []
        save_attachment = AsyncMock(
            side_effect=lambda *_, **__: calls.append("store") or "/stored/image.jpg"
        )
        extract_metadata = Mock(
            side_effect=lambda **_: calls.append("metadata")
            or {"mime_type": "image/jpeg"}
        )
        create_manifest = Mock(
            side_effect=lambda **_: calls.append("manifest")
            or "/stored/manifest.json"
        )

        with (
            patch.object(
                universal_ingestion,
                "recognize_telegram_message",
                return_value=InputType.IMAGE,
            ),
            patch.object(
                universal_ingestion,
                "classify_telegram_message",
                return_value=InputType.IMAGE,
            ),
            patch.object(
                asset_pipeline,
                "save_telegram_attachment",
                save_attachment,
            ),
            patch.object(
                asset_pipeline,
                "extract_basic_metadata",
                extract_metadata,
            ),
            patch.object(
                asset_pipeline,
                "create_document_manifest",
                create_manifest,
            ),
        ):
            result = await universal_ingestion.ingest_telegram_message(
                telegram_message(photo=[object()]),
                SimpleNamespace(),
            )

        self.assertEqual(calls, ["store", "metadata", "manifest"])
        self.assertTrue(result.register_handoff_ready)
        self.assertFalse(result.process_handoff_ready)
        self.assertFalse(result.route_handoff_ready)
        self.assertTrue(result.respond_acknowledgement_ready)

    async def test_metadata_failure_stops_before_manifest(self):
        create_manifest = Mock()
        with (
            patch.object(
                universal_ingestion,
                "recognize_telegram_message",
                return_value=InputType.IMAGE,
            ),
            patch.object(
                universal_ingestion,
                "classify_telegram_message",
                return_value=InputType.IMAGE,
            ),
            patch.object(
                asset_pipeline,
                "save_telegram_attachment",
                AsyncMock(return_value="/stored/image.jpg"),
            ),
            patch.object(
                asset_pipeline,
                "extract_basic_metadata",
                Mock(side_effect=ValueError("invalid required metadata")),
            ),
            patch.object(
                asset_pipeline,
                "create_document_manifest",
                create_manifest,
            ),
        ):
            with self.assertRaisesRegex(ValueError, "invalid required metadata"):
                await universal_ingestion.ingest_telegram_message(
                    telegram_message(photo=[object()]),
                    SimpleNamespace(),
                )

        create_manifest.assert_not_called()
        self.registry_factory_mock.assert_not_called()
        self.registry.register.assert_not_awaited()

    async def test_manifest_failure_propagates_and_cannot_reach_register_readiness(self):
        create_manifest = Mock(side_effect=OSError("manifest write failed"))
        with (
            patch.object(
                universal_ingestion,
                "recognize_telegram_message",
                return_value=InputType.IMAGE,
            ),
            patch.object(
                universal_ingestion,
                "classify_telegram_message",
                return_value=InputType.IMAGE,
            ),
            patch.object(
                asset_pipeline,
                "save_telegram_attachment",
                AsyncMock(return_value="/stored/image.jpg"),
            ),
            patch.object(
                asset_pipeline,
                "extract_basic_metadata",
                Mock(return_value={"media_type": "image", "file_size_bytes": 1}),
            ),
            patch.object(
                asset_pipeline,
                "create_document_manifest",
                create_manifest,
            ),
        ):
            with self.assertRaisesRegex(OSError, "manifest write failed"):
                await universal_ingestion.ingest_telegram_message(
                    telegram_message(photo=[object()]),
                    SimpleNamespace(),
                )

        create_manifest.assert_called_once()
        self.registry_factory_mock.assert_not_called()
        self.registry.register.assert_not_awaited()

    async def test_failed_storage_stops_before_downstream_handoffs(self):
        extract_metadata = Mock()
        create_manifest = Mock()

        with (
            patch.object(
                universal_ingestion,
                "recognize_telegram_message",
                return_value=InputType.IMAGE,
            ),
            patch.object(
                universal_ingestion,
                "classify_telegram_message",
                return_value=InputType.IMAGE,
            ),
            patch.object(
                asset_pipeline,
                "save_telegram_attachment",
                AsyncMock(return_value=None),
            ),
            patch.object(
                asset_pipeline,
                "extract_basic_metadata",
                extract_metadata,
            ),
            patch.object(
                asset_pipeline,
                "create_document_manifest",
                create_manifest,
            ),
        ):
            result = await universal_ingestion.ingest_telegram_message(
                telegram_message(photo=[object()]),
                SimpleNamespace(),
            )

        extract_metadata.assert_not_called()
        create_manifest.assert_not_called()
        self.registry_factory_mock.assert_not_called()
        self.registry.register.assert_not_awaited()
        self.assertFalse(result.register_handoff_ready)
        self.assertFalse(result.process_handoff_ready)
        self.assertFalse(result.route_handoff_ready)
        self.assertTrue(result.respond_acknowledgement_ready)

    async def test_aggregate_storage_readiness_distinguishes_all_success(self):
        message = telegram_message(
            photo=[object()], voice=object(), audio=object()
        )
        save_attachment = AsyncMock(
            side_effect=["/stored/image", "/stored/voice", "/stored/audio"]
        )
        with patch.object(
            asset_pipeline, "save_telegram_attachment", save_attachment
        ):
            ready = await asset_pipeline._store_file_originals(
                message,
                SimpleNamespace(),
                ("image", "voice", "audio"),
            )

        self.assertTrue(ready)
        self.assertEqual(save_attachment.await_count, 3)

    async def test_aggregate_storage_readiness_distinguishes_failure_positions(self):
        message = telegram_message(
            photo=[object()], voice=object(), audio=object()
        )
        original_types = ("image", "voice", "audio")
        for failed_index in range(3):
            with self.subTest(failed_index=failed_index):
                paths = ["/stored/image", "/stored/voice", "/stored/audio"]
                paths[failed_index] = None
                save_attachment = AsyncMock(side_effect=paths)
                with patch.object(
                    asset_pipeline,
                    "save_telegram_attachment",
                    save_attachment,
                ):
                    ready = await asset_pipeline._store_file_originals(
                        message, SimpleNamespace(), original_types
                    )

                self.assertFalse(ready)
                self.assertEqual(save_attachment.await_count, 3)
                self.assertEqual(
                    [
                        call.kwargs["media_type"]
                        for call in save_attachment.await_args_list
                    ],
                    list(original_types),
                )


    async def test_multiple_originals_store_once_then_stop_at_aggregate_readiness(self):
        calls = []
        save_attachment = AsyncMock(
            side_effect=lambda *_, **kwargs: calls.append(
                ("store", kwargs["media_type"])
            ) or "/stored/" + kwargs["media_type"]
        )
        extract_metadata = Mock()
        create_manifest = Mock()
        message = telegram_message(
            photo=[object()],
            voice=object(),
            document=SimpleNamespace(file_name="report.PDF"),
            video=object(),
            audio=object(),
            caption="mixed",
        )

        with (
            patch.object(asset_pipeline, "save_telegram_attachment", save_attachment),
            patch.object(asset_pipeline, "extract_basic_metadata", extract_metadata),
            patch.object(asset_pipeline, "create_document_manifest", create_manifest),
        ):
            result = await universal_ingestion.ingest_telegram_message(
                message, SimpleNamespace()
            )

        self.assertEqual(
            calls,
            [("store", media_type) for media_type in (
                "image", "voice", "pdf", "video", "audio",
            )],
        )
        extract_metadata.assert_not_called()
        create_manifest.assert_not_called()
        self.registry_factory_mock.assert_not_called()
        self.registry.register.assert_not_awaited()
        self.assertIsNone(result.stored_path)
        self.assertIsNone(result.manifest_path)
        self.assertFalse(result.register_handoff_ready)

    async def test_member_failure_positions_attempt_each_original_once(self):
        message = telegram_message(
            photo=[object()],
            voice=object(),
            audio=object(),
        )
        for failed_index in range(3):
            with self.subTest(failed_index=failed_index):
                paths = ["/stored/image", "/stored/voice", "/stored/audio"]
                paths[failed_index] = None
                save_attachment = AsyncMock(side_effect=paths)
                extract_metadata = Mock()
                create_manifest = Mock()
                with (
                    patch.object(asset_pipeline, "save_telegram_attachment", save_attachment),
                    patch.object(asset_pipeline, "extract_basic_metadata", extract_metadata),
                    patch.object(asset_pipeline, "create_document_manifest", create_manifest),
                ):
                    result = await universal_ingestion.ingest_telegram_message(
                        message, SimpleNamespace()
                    )

                self.assertEqual(save_attachment.await_count, 3)
                self.assertEqual(
                    [call.kwargs["media_type"] for call in save_attachment.await_args_list],
                    ["image", "voice", "audio"],
                )
                extract_metadata.assert_not_called()
                create_manifest.assert_not_called()
                self.assertIsNone(result.stored_path)
                self.assertFalse(result.register_handoff_ready)

    async def test_registry_is_not_constructed_or_called_before_all_readiness_gates(self):
        cases = (
            asset_pipeline.AssetPipelineResult(
                success=False,
                manifest_path="/manifests/exact.json",
                register_handoff_ready=True,
            ),
            asset_pipeline.AssetPipelineResult(
                success=True,
                manifest_path="/manifests/exact.json",
                register_handoff_ready=False,
            ),
            asset_pipeline.AssetPipelineResult(
                success=True,
                manifest_path=None,
                register_handoff_ready=True,
            ),
            asset_pipeline.AssetPipelineResult(
                success=True,
                manifest_path="",
                register_handoff_ready=True,
            ),
        )
        for pipeline_result in cases:
            with self.subTest(pipeline_result=pipeline_result):
                registry = SimpleNamespace(register=AsyncMock())
                with (
                    patch.object(
                        universal_ingestion,
                        "recognize_telegram_message",
                        return_value=InputType.TEXT,
                    ),
                    patch.object(
                        universal_ingestion,
                        "classify_telegram_message",
                        return_value=InputType.TEXT,
                    ),
                    patch.object(
                        universal_ingestion,
                        "run_asset_pipeline",
                        AsyncMock(return_value=pipeline_result),
                    ),
                ):
                    result = await universal_ingestion.ingest_telegram_message(
                        telegram_message(text="exact"),
                        SimpleNamespace(),
                        registry=registry,
                    )

                registry.register.assert_not_awaited()
                self.assertFalse(result.registration_succeeded)
                self.assertIsNone(result.registry_record_id)

        self.registry_factory_mock.assert_not_called()

    def test_registry_caller_and_transaction_boundaries_are_static(self):
        ingestion_source = (
            REPOSITORY_ROOT / "core/ingestion/universal_ingestion.py"
        ).read_text(encoding="utf-8")
        pipeline_source = (
            REPOSITORY_ROOT / "core/pipeline/asset_pipeline.py"
        ).read_text(encoding="utf-8")
        manifest_source = (
            REPOSITORY_ROOT / "core/storage/document_manifest.py"
        ).read_text(encoding="utf-8")

        self.assertEqual(ingestion_source.count(".register("), 1)
        for source in (pipeline_source, manifest_source):
            self.assertNotIn("core.registry", source)
            self.assertNotIn(".register(", source)
        for marker in (
            "psycopg",
            "transaction(",
            ".commit(",
            ".rollback(",
            "retry",
        ):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, ingestion_source.lower())

    def test_runtime_has_only_approved_core_boundary_integration(self):
        source = (
            REPOSITORY_ROOT / "core/ingestion/universal_ingestion.py"
        ).read_text(encoding="utf-8")

        self.assertIn("await aios_core.route(envelope)", source)
        self.assertIn("CoreRouteTarget.AIOS_BRAIN_BOUNDARY", source)
        prohibited = (
            "from core.brain",
            "import brain",
            "specialist",
            "class response",
            "route_to",
            "create_task",
            "gather(",
            "retry",
        )
        for marker in prohibited:
            with self.subTest(marker=marker):
                self.assertNotIn(marker, source.lower())


    def test_stage_6_3_2_publisher_and_dependency_boundaries_are_static(self):
        ingestion_source = (
            REPOSITORY_ROOT / "core/ingestion/universal_ingestion.py"
        ).read_text(encoding="utf-8")
        registry_source = (
            REPOSITORY_ROOT / "core/registry/postgres_registry.py"
        ).read_text(encoding="utf-8")
        engine_source = (
            REPOSITORY_ROOT / "core/event/event_engine.py"
        ).read_text(encoding="utf-8")
        domain_sources = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (REPOSITORY_ROOT / "core/domain").rglob("*.py")
        )

        self.assertIn("EventEnvelope(", ingestion_source)
        self.assertIn("await event_engine.process(envelope)", ingestion_source)
        self.assertEqual(ingestion_source.count("EventEnvelope("), 1)
        self.assertEqual(ingestion_source.count("event_engine.process("), 1)
        self.assertNotIn("record_id,\n                    aggregate_id", ingestion_source)
        self.assertNotIn("DomainEvent(", ingestion_source)
        for marker in (
            "create_task", "asyncio.gather", "retry", "broker", "kafka", "rabbitmq"
        ):
            self.assertNotIn(marker, ingestion_source.lower())
        self.assertNotIn("core.event", registry_source)
        self.assertNotIn("core.registry", engine_source)
        self.assertNotIn("core.event", domain_sources)


if __name__ == "__main__":
    unittest.main()
