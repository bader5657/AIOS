import inspect
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from core.app.input_classifier import InputType
from core.app.request_context import RequestContext
from core.ingestion import universal_ingestion
from core.pipeline import asset_pipeline


RECEIVED_AT = datetime(2026, 8, 19, 10, 30, 45, tzinfo=timezone.utc)


def request_context(*, text="context-only text"):
    return RequestContext(
        source="telegram",
        user_id=101,
        chat_id=-202,
        message_id=303,
        username="must-not-reach-manifest",
        text=text,
        received_at=RECEIVED_AT,
    )


def telegram_message(*, text="separate exact text"):
    return SimpleNamespace(
        photo=[SimpleNamespace(file_id="transport-file-id")],
        voice=None,
        document=None,
        video=None,
        audio=None,
        text=text,
        caption=None,
        from_user=SimpleNamespace(id=101, username="operator"),
        chat=SimpleNamespace(id=-202),
        message_id=303,
    )


def pipeline_arguments(*, context=None, text="separate exact text"):
    return {
        "request_context": context or request_context(),
        "recognized_input_type": "image",
        "message": telegram_message(text=text),
        "telegram_context": SimpleNamespace(bot=SimpleNamespace()),
        "file_original_types": ("image",),
        "original_filename": None,
        "text": text,
    }


class RequestContextAssetPipelineManifestIntegrationTests(
    unittest.IsolatedAsyncioTestCase
):
    async def test_authoritative_context_is_handed_to_pipeline_once_by_identity(self):
        calls = []
        created_contexts = []
        real_factory = universal_ingestion.RequestContext.from_telegram

        def construct_context(**kwargs):
            calls.append("request_context")
            created = real_factory(**kwargs)
            created_contexts.append(created)
            return created

        async def observe_pipeline(**kwargs):
            calls.append("asset_pipeline")
            self.assertEqual(len(created_contexts), 1)
            self.assertIs(kwargs["request_context"], created_contexts[0])
            self.assertEqual(kwargs["text"], "separate exact text")
            return asset_pipeline.AssetPipelineResult()

        forbidden_registry = SimpleNamespace(
            register=AsyncMock(side_effect=AssertionError("Registry is out of scope"))
        )
        with (
            patch.object(
                universal_ingestion.RequestContext,
                "from_telegram",
                side_effect=construct_context,
            ) as context_factory,
            patch.object(
                universal_ingestion,
                "run_asset_pipeline",
                AsyncMock(side_effect=observe_pipeline),
            ) as pipeline_call,
        ):
            result = await universal_ingestion.ingest_telegram_message(
                telegram_message(),
                SimpleNamespace(bot=SimpleNamespace()),
                registry=forbidden_registry,
            )

        self.assertEqual(calls, ["request_context", "asset_pipeline"])
        context_factory.assert_called_once()
        pipeline_call.assert_awaited_once()
        self.assertIs(
            pipeline_call.await_args.kwargs["request_context"],
            created_contexts[0],
        )
        forbidden_registry.register.assert_not_awaited()
        self.assertFalse(result.register_handoff_ready)

    async def test_file_lifecycle_maps_only_approved_contextual_values(self):
        calls = []
        context = request_context(text="must not supply pipeline text")
        metadata_result = {
            "media_type": "image",
            "file_size_bytes": 17,
            "mime_type": "image/jpeg",
        }
        storage = AsyncMock(
            side_effect=lambda *_, **__: calls.append("store")
            or "/stored/original.jpg"
        )
        metadata = Mock(
            side_effect=lambda **_: calls.append("metadata") or metadata_result
        )
        manifest = Mock(
            side_effect=lambda **_: calls.append("manifest")
            or "/manifests/manifest.json"
        )

        with (
            patch.object(asset_pipeline, "save_telegram_attachment", storage),
            patch.object(asset_pipeline, "extract_basic_metadata", metadata),
            patch.object(asset_pipeline, "create_document_manifest", manifest),
        ):
            result = await asset_pipeline.run_asset_pipeline(
                **pipeline_arguments(
                    context=context,
                    text="separate exact pipeline text",
                )
            )

        self.assertEqual(calls, ["store", "metadata", "manifest"])
        storage.assert_awaited_once()
        metadata.assert_called_once_with(
            media_type="image",
            file_path="/stored/original.jpg",
            original_filename=None,
        )
        manifest.assert_called_once()
        manifest_values = manifest.call_args.kwargs
        self.assertEqual(
            manifest_values,
            {
                "represented_media_type": "image",
                "received_at": "2026-08-19T10:30:45Z",
                "metadata": metadata_result,
                "storage_path": "/stored/original.jpg",
                "telegram_user_id": 101,
                "telegram_chat_id": -202,
                "telegram_message_id": 303,
            },
        )
        self.assertIs(manifest_values["metadata"], metadata_result)
        self.assertNotIn("request_context", manifest_values)
        self.assertNotIn("username", manifest_values)
        self.assertNotIn("source", manifest_values)
        self.assertNotIn("text", manifest_values)
        self.assertNotIn("manifest_id", manifest_values)
        self.assertNotIn("identity_ref", manifest_values)
        self.assertTrue(result.success)
        self.assertEqual(result.manifest_path, "/manifests/manifest.json")
        self.assertTrue(result.register_handoff_ready)

    async def test_storage_failure_stops_before_metadata_and_manifest(self):
        storage = AsyncMock(return_value=None)
        metadata = Mock()
        manifest = Mock()
        with (
            patch.object(asset_pipeline, "save_telegram_attachment", storage),
            patch.object(asset_pipeline, "extract_basic_metadata", metadata),
            patch.object(asset_pipeline, "create_document_manifest", manifest),
        ):
            result = await asset_pipeline.run_asset_pipeline(**pipeline_arguments())

        storage.assert_awaited_once()
        metadata.assert_not_called()
        manifest.assert_not_called()
        self.assertFalse(result.success)
        self.assertIsNone(result.manifest_path)
        self.assertFalse(result.register_handoff_ready)

    async def test_metadata_failure_propagates_before_manifest_without_retry(self):
        storage = AsyncMock(return_value="/stored/original.jpg")
        metadata = Mock(side_effect=ValueError("metadata failed"))
        manifest = Mock()
        with (
            patch.object(asset_pipeline, "save_telegram_attachment", storage),
            patch.object(asset_pipeline, "extract_basic_metadata", metadata),
            patch.object(asset_pipeline, "create_document_manifest", manifest),
        ):
            with self.assertRaisesRegex(ValueError, "metadata failed"):
                await asset_pipeline.run_asset_pipeline(**pipeline_arguments())

        storage.assert_awaited_once()
        metadata.assert_called_once()
        manifest.assert_not_called()

    async def test_manifest_failure_propagates_without_readiness_or_retry(self):
        storage = AsyncMock(return_value="/stored/original.jpg")
        metadata_result = {"media_type": "image", "file_size_bytes": 17}
        metadata = Mock(return_value=metadata_result)
        manifest = Mock(side_effect=OSError("manifest failed"))
        with (
            patch.object(asset_pipeline, "save_telegram_attachment", storage),
            patch.object(asset_pipeline, "extract_basic_metadata", metadata),
            patch.object(asset_pipeline, "create_document_manifest", manifest),
        ):
            with self.assertRaisesRegex(OSError, "manifest failed"):
                await asset_pipeline.run_asset_pipeline(**pipeline_arguments())

        storage.assert_awaited_once()
        metadata.assert_called_once()
        manifest.assert_called_once()
        self.assertIs(manifest.call_args.kwargs["metadata"], metadata_result)

    def test_focused_boundary_has_no_registry_retry_or_later_stage_execution(self):
        source = inspect.getsource(asset_pipeline).lower()
        for prohibited in (
            "core.registry",
            "postgres",
            "eventengine",
            "aioscore",
            "brain",
            "retry",
            "backoff",
        ):
            with self.subTest(prohibited=prohibited):
                self.assertNotIn(prohibited, source)


if __name__ == "__main__":
    unittest.main()
