import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]

telegram_module = SimpleNamespace(Message=object)
telegram_ext_module = SimpleNamespace(
    ContextTypes=SimpleNamespace(DEFAULT_TYPE=object)
)
manifest_module = SimpleNamespace(create_document_manifest=Mock())
metadata_module = SimpleNamespace(extract_basic_metadata=Mock())
storage_module = SimpleNamespace(save_telegram_attachment=AsyncMock())

with patch.dict(
    sys.modules,
    {
        "telegram": telegram_module,
        "telegram.ext": telegram_ext_module,
        "core.storage.document_manifest": manifest_module,
        "core.storage.metadata_engine": metadata_module,
        "core.storage.telegram_storage": storage_module,
    },
):
    from core.app.input_classifier import InputType
    from core.domain.domain_event import DomainEvent
    from core.domain.exceptions import DomainValidationError
    from core.event import EventDeliveryFailureCode, EventDeliveryResult
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


class UniversalIngestionRecognitionTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.registry = SimpleNamespace(
            register=AsyncMock(return_value=SimpleNamespace(record_id=101))
        )
        self.registry_factory = patch.object(
            universal_ingestion.PostgresRegistry,
            "from_environment",
            return_value=self.registry,
        )
        self.registry_factory.start()
        self.addCleanup(self.registry_factory.stop)
    async def test_canonical_recognition_is_exposed_with_legacy_pipeline_type(self):
        cases = (
            (InputType.PDF, InputType.DOCUMENT),
            (InputType.DOC, InputType.DOCUMENT),
            (InputType.SPREADSHEET, InputType.DOCUMENT),
            (InputType.WEB_LINK, InputType.TEXT),
            (InputType.YOUTUBE_LINK, InputType.TEXT),
        )

        for recognized, pipeline in cases:
            with self.subTest(recognized=recognized, pipeline=pipeline):
                save_attachment = AsyncMock(return_value=None)
                with (
                    patch.object(
                        universal_ingestion,
                        "recognize_telegram_message",
                        return_value=recognized,
                    ),
                    patch.object(
                        universal_ingestion,
                        "classify_telegram_message",
                        return_value=pipeline,
                    ),
                    patch.object(
                        asset_pipeline,
                        "save_telegram_attachment",
                        save_attachment,
                    ),
                ):
                    result = await universal_ingestion.ingest_telegram_message(
                        telegram_message(
                            document=SimpleNamespace(file_name="candidate.bin")
                        )
                        if pipeline == InputType.DOCUMENT
                        else telegram_message(text="candidate"),
                        SimpleNamespace(),
                    )

                self.assertEqual(result.recognized_input_type, recognized)
                self.assertEqual(result.input_type, pipeline)
                if pipeline == InputType.TEXT:
                    save_attachment.assert_not_awaited()
                else:
                    save_attachment.assert_awaited_once_with(
                        unittest.mock.ANY,
                        unittest.mock.ANY,
                        media_type=recognized.value,
                    )

    async def test_existing_storage_metadata_and_manifest_flow_is_unchanged(self):
        save_attachment = AsyncMock(return_value="/existing/path/image.jpg")
        extract_metadata = Mock(return_value={"mime_type": "image/jpeg"})
        create_manifest = Mock(return_value="/existing/path/manifest.json")
        message = telegram_message(photo=[object()], caption="caption")

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
                message,
                SimpleNamespace(),
            )

        save_attachment.assert_awaited_once_with(
            message,
            unittest.mock.ANY,
            media_type="image",
        )
        extract_metadata.assert_called_once_with(
            media_type="image",
            file_path="/existing/path/image.jpg",
            original_filename=None,
        )
        create_manifest.assert_called_once_with(
            represented_media_type="image",
            received_at=unittest.mock.ANY,
            metadata={"mime_type": "image/jpeg"},
            storage_path="/existing/path/image.jpg",
            telegram_user_id=7,
            telegram_chat_id=8,
            telegram_message_id=9,
        )
        self.assertEqual(result.input_type, InputType.IMAGE)
        self.assertEqual(result.recognized_input_type, InputType.IMAGE)
        self.assertEqual(result.text, "caption")

    async def test_text_and_links_create_manifest_without_storage(self):
        cases = (
            (
                InputType.TEXT,
                telegram_message(text="exact text"),
                {"media_type": "text", "text": "exact text"},
            ),
            (
                InputType.WEB_LINK,
                telegram_message(text="https://example.com/Exact"),
                {
                    "media_type": "web_link",
                    "source_url": "https://example.com/Exact",
                },
            ),
            (
                InputType.YOUTUBE_LINK,
                telegram_message(text="https://youtu.be/Exact"),
                {
                    "media_type": "youtube_link",
                    "source_url": "https://youtu.be/Exact",
                },
            ),
        )
        for recognized, message, expected_call in cases:
            with self.subTest(recognized=recognized):
                extract_metadata = Mock(
                    return_value={"media_type": recognized.value}
                )
                create_manifest = Mock()
                save_attachment = AsyncMock()
                with (
                    patch.object(
                        universal_ingestion,
                        "recognize_telegram_message",
                        return_value=recognized,
                    ),
                    patch.object(
                        universal_ingestion,
                        "classify_telegram_message",
                        return_value=InputType.TEXT,
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
                    patch.object(
                        asset_pipeline,
                        "save_telegram_attachment",
                        save_attachment,
                    ),
                ):
                    result = await universal_ingestion.ingest_telegram_message(
                        message,
                        SimpleNamespace(),
                    )

                extract_metadata.assert_called_once_with(**expected_call)
                save_attachment.assert_not_awaited()
                expected_manifest = {
                    "represented_media_type": recognized.value,
                    "received_at": unittest.mock.ANY,
                    "metadata": {"media_type": recognized.value},
                    "telegram_user_id": 7,
                    "telegram_chat_id": 8,
                    "telegram_message_id": 9,
                }
                if recognized in (InputType.WEB_LINK, InputType.YOUTUBE_LINK):
                    expected_manifest["source_url"] = message.text
                create_manifest.assert_called_once_with(**expected_manifest)
                self.assertEqual(result.metadata, {"media_type": recognized.value})
                self.assertIs(result.manifest_path, create_manifest.return_value)
                self.assertTrue(result.register_handoff_ready)

    async def test_original_filename_remains_stage_3_3_metadata_input_only(self):
        message = telegram_message(
            document=SimpleNamespace(file_name="Exact Received Name.PDF")
        )
        create_manifest = Mock(return_value="/stored/manifest.json")
        extract_metadata = Mock(
            return_value={"media_type": "pdf", "file_size_bytes": 1}
        )
        with (
            patch.object(
                universal_ingestion,
                "recognize_telegram_message",
                return_value=InputType.PDF,
            ),
            patch.object(
                universal_ingestion,
                "classify_telegram_message",
                return_value=InputType.DOCUMENT,
            ),
            patch.object(
                asset_pipeline,
                "save_telegram_attachment",
                AsyncMock(return_value="/stored/generated.pdf"),
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
            await universal_ingestion.ingest_telegram_message(
                message,
                SimpleNamespace(),
            )
        self.assertEqual(
            extract_metadata.call_args.kwargs["original_filename"],
            "Exact Received Name.PDF",
        )
        self.assertNotIn("original_filename", create_manifest.call_args.kwargs)

    def test_task_b_adds_no_prohibited_runtime_behavior(self):
        source = (
            REPOSITORY_ROOT / "core/ingestion/universal_ingestion.py"
        ).read_text(encoding="utf-8")

        prohibited = (
            "urllib.parse",
            "urlsplit",
            "urlparse",
            "redirect",
            "normalize",
            "canonicalize",
            "re.compile",
        )
        for marker in prohibited:
            with self.subTest(marker=marker):
                self.assertNotIn(marker, source)


    async def test_registry_mapping_and_success_for_all_non_file_inputs(self):
        cases = (
            (InputType.TEXT, "exact text", None),
            (InputType.WEB_LINK, "https://example.test/Exact", "https://example.test/Exact"),
            (InputType.YOUTUBE_LINK, "https://youtu.be/Exact", "https://youtu.be/Exact"),
        )
        for recognized, text, expected_source_url in cases:
            with self.subTest(recognized=recognized):
                metadata = {"media_type": recognized.value}
                pipeline_result = asset_pipeline.AssetPipelineResult(
                    success=True,
                    metadata=metadata,
                    manifest_path="/manifests/exact.json",
                    register_handoff_ready=True,
                )
                registry = SimpleNamespace(
                    register=AsyncMock(return_value=SimpleNamespace(record_id=202))
                )
                with (
                    patch.object(
                        universal_ingestion,
                        "recognize_telegram_message",
                        return_value=recognized,
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
                        telegram_message(text=text),
                        SimpleNamespace(),
                        registry=registry,
                    )

                registry.register.assert_awaited_once()
                persistence_input = registry.register.await_args.args[0]
                self.assertEqual(
                    persistence_input.identity_ref, "/manifests/exact.json"
                )
                self.assertEqual(
                    persistence_input.manifest_ref, "/manifests/exact.json"
                )
                self.assertEqual(
                    persistence_input.represented_media_type, recognized.value
                )
                self.assertIs(persistence_input.metadata, metadata)
                self.assertEqual(persistence_input.relationships, [])
                self.assertIsNone(persistence_input.registration_status)
                self.assertIsNone(persistence_input.storage_path)
                self.assertEqual(persistence_input.source_url, expected_source_url)
                self.assertTrue(result.registration_succeeded)
                self.assertEqual(result.registry_record_id, 202)

    async def test_file_backed_registry_mapping_preserves_upstream_values(self):
        metadata = {"media_type": "image", "file_size_bytes": 4}
        pipeline_result = asset_pipeline.AssetPipelineResult(
            success=True,
            stored_path="/stored/exact.jpg",
            metadata=metadata,
            manifest_path="/manifests/exact.json",
            register_handoff_ready=True,
        )
        registry = SimpleNamespace(
            register=AsyncMock(return_value=SimpleNamespace(record_id=303))
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
                universal_ingestion,
                "run_asset_pipeline",
                AsyncMock(return_value=pipeline_result),
            ),
        ):
            result = await universal_ingestion.ingest_telegram_message(
                telegram_message(photo=[object()]),
                SimpleNamespace(),
                registry=registry,
            )

        persistence_input = registry.register.await_args.args[0]
        self.assertEqual(persistence_input.storage_path, "/stored/exact.jpg")
        self.assertIsNone(persistence_input.source_url)
        self.assertIs(persistence_input.metadata, metadata)
        self.assertTrue(result.registration_succeeded)
        self.assertEqual(result.registry_record_id, 303)

    async def test_registry_failure_is_bounded_without_retry(self):
        pipeline_result = asset_pipeline.AssetPipelineResult(
            success=True,
            stored_path="/stored/exact.jpg",
            metadata={"media_type": "image", "file_size_bytes": 4},
            manifest_path="/manifests/exact.json",
            register_handoff_ready=True,
        )
        registry = SimpleNamespace(
            register=AsyncMock(
                side_effect=universal_ingestion.RegistryPersistenceError("failed")
            )
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
                universal_ingestion,
                "run_asset_pipeline",
                AsyncMock(return_value=pipeline_result),
            ),
        ):
            result = await universal_ingestion.ingest_telegram_message(
                telegram_message(photo=[object()]),
                SimpleNamespace(),
                registry=registry,
            )

        registry.register.assert_awaited_once()
        self.assertFalse(result.registration_succeeded)
        self.assertIsNone(result.registry_record_id)
        self.assertEqual(result.stored_path, "/stored/exact.jpg")
        self.assertEqual(result.manifest_path, "/manifests/exact.json")
        self.assertIs(result.metadata, pipeline_result.metadata)

    async def test_unexpected_registry_exception_is_not_swallowed(self):
        pipeline_result = asset_pipeline.AssetPipelineResult(
            success=True,
            metadata={"media_type": "text"},
            manifest_path="/manifests/exact.json",
            register_handoff_ready=True,
        )
        registry = SimpleNamespace(register=AsyncMock(side_effect=RuntimeError("bug")))
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
            with self.assertRaisesRegex(RuntimeError, "bug"):
                await universal_ingestion.ingest_telegram_message(
                    telegram_message(text="exact"),
                    SimpleNamespace(),
                    registry=registry,
                )

        registry.register.assert_awaited_once()

class SuppliedDomainEvent(DomainEvent):
    def __init__(self, event_id, occurred_at, event_name):
        super().__init__(event_id, occurred_at, event_name)


class RegistryEventIntegrationUnitTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.pipeline_result = asset_pipeline.AssetPipelineResult(
            success=True,
            stored_path="/stored/original.bin",
            metadata={"media_type": "document"},
            manifest_path="/manifests/exact.json",
            register_handoff_ready=True,
        )
        self.registry = SimpleNamespace(
            register=AsyncMock(return_value=SimpleNamespace(record_id=404))
        )
        self.event = SuppliedDomainEvent(
            "domain-event-1",
            datetime(2026, 8, 19, 4, 5, tzinfo=timezone.utc),
            "document.registered",
        )
        self.core = SimpleNamespace(
            route=AsyncMock(
                return_value=SimpleNamespace(
                    success=True,
                    route_target=(
                        universal_ingestion.CoreRouteTarget.AIOS_BRAIN_BOUNDARY
                    ),
                )
            )
        )
        self.pipeline_patch = patch.object(
            universal_ingestion,
            "run_asset_pipeline",
            AsyncMock(return_value=self.pipeline_result),
        )
        self.recognition_patch = patch.object(
            universal_ingestion, "recognize_telegram_message",
            return_value=InputType.DOCUMENT,
        )
        self.classification_patch = patch.object(
            universal_ingestion, "classify_telegram_message",
            return_value=InputType.DOCUMENT,
        )
        for active_patch in (
            self.pipeline_patch, self.recognition_patch, self.classification_patch
        ):
            active_patch.start()
            self.addCleanup(active_patch.stop)

    async def ingest(self, **kwargs):
        kwargs.setdefault("aios_core", self.core)
        return await universal_ingestion.ingest_telegram_message(
            telegram_message(document=SimpleNamespace(file_name="exact.bin")),
            SimpleNamespace(),
            registry=self.registry,
            **kwargs,
        )

    async def test_registry_failure_constructs_no_envelope_and_makes_no_event_call(self):
        self.registry.register = AsyncMock(
            side_effect=universal_ingestion.RegistryPersistenceError("failed")
        )
        engine = SimpleNamespace(process=AsyncMock())
        with patch.object(
            universal_ingestion, "EventEnvelope", wraps=universal_ingestion.EventEnvelope
        ) as envelope_type:
            result = await self.ingest(
                domain_event=self.event, event_engine=engine, event_schema_version=7
            )

        self.registry.register.assert_awaited_once()
        envelope_type.assert_not_called()
        engine.process.assert_not_awaited()
        self.assertFalse(result.registration_succeeded)
        self.assertFalse(result.event_publication_attempted)

    async def test_registry_success_without_domain_event_does_not_publish(self):
        engine = SimpleNamespace(process=AsyncMock())
        result = await self.ingest(event_engine=engine, event_schema_version=7)

        self.assertTrue(result.registration_succeeded)
        self.assertFalse(result.event_publication_attempted)
        self.assertFalse(result.event_delivery_succeeded)
        self.assertIsNone(result.event_delivery_failure_code)
        self.assertFalse(result.route_handoff_ready)
        self.core.route.assert_not_awaited()
        engine.process.assert_not_awaited()

    async def test_exact_envelope_mapping_uses_one_unchanged_supplied_event(self):
        original_state = (self.event.id, self.event.event_name, self.event.occurred_at)
        engine = SimpleNamespace(
            process=AsyncMock(return_value=EventDeliveryResult(True, 1, None, None))
        )
        result = await self.ingest(
            domain_event=self.event, event_engine=engine, event_schema_version=7
        )

        engine.process.assert_awaited_once()
        envelope = engine.process.await_args.args[0]
        self.assertIs(envelope.event, self.event)
        self.assertEqual(envelope.event_id, self.event.id)
        self.assertEqual(envelope.event_name, self.event.event_name)
        self.assertEqual(envelope.occurred_at, self.event.occurred_at)
        self.assertIsNone(envelope.aggregate_id)
        self.assertIsNone(envelope.correlation_id)
        self.assertIsNone(envelope.causation_id)
        self.assertEqual(envelope.schema_version, 7)
        self.assertNotEqual(envelope.event_id, result.registry_record_id)
        self.assertEqual(
            (self.event.id, self.event.event_name, self.event.occurred_at), original_state
        )
        self.assertTrue(result.event_publication_attempted)
        self.assertTrue(result.event_delivery_succeeded)
        self.assertIsNone(result.event_delivery_failure_code)
        self.assertTrue(result.route_handoff_ready)
        self.core.route.assert_awaited_once_with(envelope)

    async def test_all_bounded_delivery_results_map_once_without_retry(self):
        cases = (
            (True, None),
            (False, EventDeliveryFailureCode.NO_HANDLER),
            (False, EventDeliveryFailureCode.HANDLER_FAILURE),
            (False, EventDeliveryFailureCode.INVALID_ENVELOPE),
        )
        for succeeded, failure_code in cases:
            with self.subTest(failure_code=failure_code):
                engine = SimpleNamespace(
                    process=AsyncMock(
                        return_value=EventDeliveryResult(
                            succeeded, int(succeeded), failure_code,
                            None if succeeded else "bounded",
                        )
                    )
                )
                result = await self.ingest(
                    domain_event=self.event,
                    event_engine=engine,
                    event_schema_version=3,
                )

                self.assertTrue(result.registration_succeeded)
                self.assertEqual(result.registry_record_id, 404)
                self.assertTrue(result.event_publication_attempted)
                self.assertIs(result.event_delivery_succeeded, succeeded)
                self.assertIs(result.event_delivery_failure_code, failure_code)
                engine.process.assert_awaited_once()
                self.assertEqual(len(engine.process.await_args.args), 1)
                if succeeded:
                    self.assertTrue(result.route_handoff_ready)
                else:
                    self.assertFalse(result.route_handoff_ready)

    async def test_publication_contract_requires_explicit_engine_and_schema(self):
        with self.assertRaisesRegex(ValueError, "event_engine is required"):
            await self.ingest(domain_event=self.event, event_schema_version=1)
        with self.assertRaisesRegex(DomainValidationError, "schema_version"):
            await self.ingest(
                domain_event=self.event,
                event_engine=SimpleNamespace(process=AsyncMock()),
            )


if __name__ == "__main__":
    unittest.main()
