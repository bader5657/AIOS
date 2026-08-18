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
    async def test_manifest_exposes_only_register_handoff_and_acknowledgement(self):
        calls = []
        save_attachment = AsyncMock(
            side_effect=lambda *_: calls.append("store") or "/stored/image.jpg"
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
                universal_ingestion,
                "save_telegram_attachment",
                save_attachment,
            ),
            patch.object(
                universal_ingestion,
                "extract_basic_metadata",
                extract_metadata,
            ),
            patch.object(
                universal_ingestion,
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
                universal_ingestion,
                "save_telegram_attachment",
                AsyncMock(return_value="/stored/image.jpg"),
            ),
            patch.object(
                universal_ingestion,
                "extract_basic_metadata",
                Mock(side_effect=ValueError("invalid required metadata")),
            ),
            patch.object(
                universal_ingestion,
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
                universal_ingestion,
                "save_telegram_attachment",
                AsyncMock(return_value=None),
            ),
            patch.object(
                universal_ingestion,
                "extract_basic_metadata",
                extract_metadata,
            ),
            patch.object(
                universal_ingestion,
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
            universal_ingestion, "save_telegram_attachment", save_attachment
        ):
            ready = await universal_ingestion._store_file_originals(
                message,
                SimpleNamespace(),
                (InputType.IMAGE, InputType.VOICE, InputType.AUDIO),
            )

        self.assertTrue(ready)
        self.assertEqual(save_attachment.await_count, 3)

    async def test_aggregate_storage_readiness_distinguishes_failure_positions(self):
        message = telegram_message(
            photo=[object()], voice=object(), audio=object()
        )
        original_types = (InputType.IMAGE, InputType.VOICE, InputType.AUDIO)
        for failed_index in range(3):
            with self.subTest(failed_index=failed_index):
                paths = ["/stored/image", "/stored/voice", "/stored/audio"]
                paths[failed_index] = None
                save_attachment = AsyncMock(side_effect=paths)
                with patch.object(
                    universal_ingestion,
                    "save_telegram_attachment",
                    save_attachment,
                ):
                    ready = await universal_ingestion._store_file_originals(
                        message, SimpleNamespace(), original_types
                    )

                self.assertFalse(ready)
                self.assertEqual(save_attachment.await_count, 3)
                self.assertEqual(
                    [
                        call.kwargs["input_type"]
                        for call in save_attachment.await_args_list
                    ],
                    list(original_types),
                )


    async def test_multiple_originals_store_once_then_stop_at_aggregate_readiness(self):
        calls = []
        save_attachment = AsyncMock(
            side_effect=lambda *_, **kwargs: calls.append(
                ("store", kwargs["input_type"])
            ) or "/stored/" + kwargs["input_type"].value
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
            patch.object(universal_ingestion, "save_telegram_attachment", save_attachment),
            patch.object(universal_ingestion, "extract_basic_metadata", extract_metadata),
            patch.object(universal_ingestion, "create_document_manifest", create_manifest),
        ):
            result = await universal_ingestion.ingest_telegram_message(
                message, SimpleNamespace()
            )

        self.assertEqual(
            calls,
            [("store", input_type) for input_type in (
                InputType.IMAGE, InputType.VOICE, InputType.PDF,
                InputType.VIDEO, InputType.AUDIO,
            )],
        )
        extract_metadata.assert_not_called()
        create_manifest.assert_not_called()
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
                    patch.object(universal_ingestion, "save_telegram_attachment", save_attachment),
                    patch.object(universal_ingestion, "extract_basic_metadata", extract_metadata),
                    patch.object(universal_ingestion, "create_document_manifest", create_manifest),
                ):
                    result = await universal_ingestion.ingest_telegram_message(
                        message, SimpleNamespace()
                    )

                self.assertEqual(save_attachment.await_count, 3)
                self.assertEqual(
                    [call.kwargs["input_type"] for call in save_attachment.await_args_list],
                    [InputType.IMAGE, InputType.VOICE, InputType.AUDIO],
                )
                extract_metadata.assert_not_called()
                create_manifest.assert_not_called()
                self.assertIsNone(result.stored_path)
                self.assertFalse(result.register_handoff_ready)

    def test_runtime_has_no_downstream_owner_or_response_implementation(self):
        source = (
            REPOSITORY_ROOT / "core/ingestion/universal_ingestion.py"
        ).read_text(encoding="utf-8")

        prohibited = (
            "core.registry",
            "event_engine",
            "aios_core",
            "brain",
            "specialist",
            "class response",
            "route_to",
        )
        for marker in prohibited:
            with self.subTest(marker=marker):
                self.assertNotIn(marker, source.lower())

if __name__ == "__main__":
    unittest.main()
