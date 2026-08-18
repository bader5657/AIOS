import inspect
import sys
import unittest
from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

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
    from core.app.request_context import RequestContext
    from core.pipeline import asset_pipeline


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


def request_context(text: str = "") -> RequestContext:
    return RequestContext(
        source="telegram",
        user_id=7,
        chat_id=8,
        message_id=9,
        username="operator",
        text=text,
        received_at=datetime(2026, 8, 18, tzinfo=timezone.utc),
    )


def pipeline_arguments(media_type: str, *, text: str = "") -> dict:
    file_types = () if media_type in {"text", "web_link", "youtube_link"} else (media_type,)
    return {
        "request_context": request_context(text),
        "recognized_input_type": media_type,
        "message": SimpleNamespace(),
        "telegram_context": SimpleNamespace(),
        "file_original_types": file_types,
        "original_filename": "original.bin" if file_types else None,
        "text": text,
    }


class AssetPipelineContractTests(unittest.IsolatedAsyncioTestCase):
    async def test_single_file_orders_delegation_and_returns_bounded_success(self):
        calls = []
        storage = AsyncMock(side_effect=lambda *_, **__: calls.append("store") or "/stored/file")
        metadata = Mock(side_effect=lambda **_: calls.append("metadata") or {"media_type": "image"})
        manifest = Mock(side_effect=lambda **_: calls.append("manifest") or "/manifest.json")
        with (
            patch.object(asset_pipeline, "save_telegram_attachment", storage),
            patch.object(asset_pipeline, "extract_basic_metadata", metadata),
            patch.object(asset_pipeline, "create_document_manifest", manifest),
        ):
            result = await asset_pipeline.run_asset_pipeline(**pipeline_arguments("image"))

        self.assertEqual(calls, ["store", "metadata", "manifest"])
        self.assertTrue(result.success)
        self.assertTrue(result.register_handoff_ready)
        self.assertEqual(result.stored_path, "/stored/file")
        self.assertEqual(result.manifest_path, "/manifest.json")

    async def test_storage_failure_stops_metadata_and_manifest(self):
        metadata = Mock()
        manifest = Mock()
        with (
            patch.object(asset_pipeline, "save_telegram_attachment", AsyncMock(return_value=None)),
            patch.object(asset_pipeline, "extract_basic_metadata", metadata),
            patch.object(asset_pipeline, "create_document_manifest", manifest),
        ):
            result = await asset_pipeline.run_asset_pipeline(**pipeline_arguments("image"))
        metadata.assert_not_called()
        manifest.assert_not_called()
        self.assertFalse(result.success)
        self.assertFalse(result.register_handoff_ready)

    async def test_metadata_failure_stops_manifest(self):
        manifest = Mock()
        with (
            patch.object(asset_pipeline, "save_telegram_attachment", AsyncMock(return_value="/stored/file")),
            patch.object(asset_pipeline, "extract_basic_metadata", Mock(side_effect=ValueError("metadata failed"))),
            patch.object(asset_pipeline, "create_document_manifest", manifest),
        ):
            with self.assertRaisesRegex(ValueError, "metadata failed"):
                await asset_pipeline.run_asset_pipeline(**pipeline_arguments("image"))
        manifest.assert_not_called()

    async def test_manifest_failure_cannot_produce_success(self):
        with (
            patch.object(asset_pipeline, "save_telegram_attachment", AsyncMock(return_value="/stored/file")),
            patch.object(asset_pipeline, "extract_basic_metadata", Mock(return_value={"media_type": "image"})),
            patch.object(asset_pipeline, "create_document_manifest", Mock(side_effect=OSError("manifest failed"))),
        ):
            with self.assertRaisesRegex(OSError, "manifest failed"):
                await asset_pipeline.run_asset_pipeline(**pipeline_arguments("image"))

    async def test_text_and_url_flows_never_use_storage_or_network(self):
        cases = (
            ("text", "exact text", {"media_type": "text", "text": "exact text"}),
            ("web_link", "https://example.com/x", {"media_type": "web_link", "source_url": "https://example.com/x"}),
            ("youtube_link", "https://youtu.be/x", {"media_type": "youtube_link", "source_url": "https://youtu.be/x"}),
        )
        for media_type, text, expected_metadata_call in cases:
            with self.subTest(media_type=media_type):
                storage = AsyncMock()
                metadata = Mock(return_value={"media_type": media_type})
                manifest = Mock(return_value="/manifest.json")
                with (
                    patch.object(asset_pipeline, "save_telegram_attachment", storage),
                    patch.object(asset_pipeline, "extract_basic_metadata", metadata),
                    patch.object(asset_pipeline, "create_document_manifest", manifest),
                ):
                    result = await asset_pipeline.run_asset_pipeline(**pipeline_arguments(media_type, text=text))
                storage.assert_not_awaited()
                metadata.assert_called_once_with(**expected_metadata_call)
                self.assertTrue(result.success)

    async def test_all_ten_approved_input_classes_reach_existing_capabilities(self):
        approved = ("text", "image", "voice", "audio", "video", "pdf", "doc", "spreadsheet", "web_link", "youtube_link")
        observed = set()
        for media_type in approved:
            text = "https://example.com/x" if media_type in {"web_link", "youtube_link"} else "plain"
            with (
                patch.object(asset_pipeline, "save_telegram_attachment", AsyncMock(return_value="/stored/file")),
                patch.object(asset_pipeline, "extract_basic_metadata", Mock(return_value={"media_type": media_type})),
                patch.object(asset_pipeline, "create_document_manifest", Mock(return_value="/manifest.json")),
            ):
                result = await asset_pipeline.run_asset_pipeline(**pipeline_arguments(media_type, text=text))
            self.assertTrue(result.success)
            observed.add(media_type)
        self.assertEqual(observed, set(approved))

    async def test_multi_file_stores_each_primitive_then_stops_before_metadata(self):
        storage = AsyncMock(side_effect=["/image", None, "/audio"])
        metadata = Mock()
        manifest = Mock()
        arguments = pipeline_arguments("image")
        arguments["file_original_types"] = ("image", "voice", "audio")
        with (
            patch.object(asset_pipeline, "save_telegram_attachment", storage),
            patch.object(asset_pipeline, "extract_basic_metadata", metadata),
            patch.object(asset_pipeline, "create_document_manifest", manifest),
        ):
            result = await asset_pipeline.run_asset_pipeline(**arguments)
        self.assertEqual([call.kwargs["media_type"] for call in storage.await_args_list], ["image", "voice", "audio"])
        metadata.assert_not_called()
        manifest.assert_not_called()
        self.assertFalse(result.success)

    def test_result_is_frozen_noncanonical_transport_only(self):
        self.assertEqual(
            [item.name for item in fields(asset_pipeline.AssetPipelineResult)],
            ["success", "stored_path", "metadata", "manifest_path", "register_handoff_ready"],
        )
        result = asset_pipeline.AssetPipelineResult()
        with self.assertRaises(FrozenInstanceError):
            result.success = True

    def test_runtime_has_no_historical_or_prohibited_dependency(self):
        source = inspect.getsource(asset_pipeline).lower()
        prohibited = (
            "completed",
            "stateenum",
            "core.registry",
            "postgres",
            "sqlalchemy",
            "event_engine",
            "brain",
            "specialist",
            "requests",
            "urlopen",
            "input_classifier",
            "dedup",
            "retry",
        )
        for marker in prohibited:
            with self.subTest(marker=marker):
                self.assertNotIn(marker, source)
        self.assertFalse((REPOSITORY_ROOT / "core/pipeline/state.py").exists())


if __name__ == "__main__":
    unittest.main()
