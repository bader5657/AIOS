import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]

save_attachment = AsyncMock(return_value=None)

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
            save_telegram_attachment=save_attachment
        ),
    },
):
    from core.app.input_classifier import InputType
    from core.ingestion.universal_ingestion import ingest_telegram_message


def telegram_message(**overrides):
    fields = {
        "photo": None,
        "voice": None,
        "document": None,
        "video": None,
        "audio": None,
        "text": None,
        "caption": None,
        "from_user": SimpleNamespace(id=1),
        "chat": SimpleNamespace(id=2),
        "message_id": 3,
    }
    fields.update(overrides)
    return SimpleNamespace(**fields)


class IngestionCapabilityMatrixTests(unittest.IsolatedAsyncioTestCase):
    async def test_complete_blueprint_input_and_compatibility_matrix(self):
        cases = (
            (
                "Text",
                telegram_message(text="plain"),
                InputType.TEXT,
                InputType.TEXT,
            ),
            (
                "Image",
                telegram_message(photo=[object()]),
                InputType.IMAGE,
                InputType.IMAGE,
            ),
            (
                "Voice",
                telegram_message(voice=object()),
                InputType.VOICE,
                InputType.VOICE,
            ),
            (
                "Audio",
                telegram_message(audio=object()),
                InputType.AUDIO,
                InputType.AUDIO,
            ),
            (
                "Video",
                telegram_message(video=object()),
                InputType.VIDEO,
                InputType.VIDEO,
            ),
            (
                "PDF",
                telegram_message(document=SimpleNamespace(file_name="a.pdf")),
                InputType.PDF,
                InputType.DOCUMENT,
            ),
            (
                "DOC/DOCX",
                telegram_message(document=SimpleNamespace(file_name="a.doc")),
                InputType.DOC,
                InputType.DOCUMENT,
            ),
            (
                "DOC/DOCX",
                telegram_message(document=SimpleNamespace(file_name="a.docx")),
                InputType.DOC,
                InputType.DOCUMENT,
            ),
            (
                "Spreadsheet",
                telegram_message(document=SimpleNamespace(file_name="a.ods")),
                InputType.SPREADSHEET,
                InputType.DOCUMENT,
            ),
            (
                "Web Link",
                telegram_message(text="https://example.com"),
                InputType.WEB_LINK,
                InputType.TEXT,
            ),
            (
                "YouTube Link",
                telegram_message(text="https://youtu.be/id"),
                InputType.YOUTUBE_LINK,
                InputType.TEXT,
            ),
        )
        expected_capabilities = {
            "Text",
            "Image",
            "Voice",
            "Audio",
            "Video",
            "PDF",
            "DOC/DOCX",
            "Spreadsheet",
            "Web Link",
            "YouTube Link",
        }

        self.assertEqual({name for name, *_ in cases}, expected_capabilities)

        for name, message, recognized, pipeline in cases:
            with self.subTest(capability=name, recognized=recognized):
                previous_dispatches = save_attachment.await_count
                result = await ingest_telegram_message(message, SimpleNamespace())

                self.assertEqual(result.recognized_input_type, recognized)
                self.assertEqual(result.input_type, pipeline)
                expected_dispatches = (
                    previous_dispatches
                    if pipeline == InputType.TEXT
                    else previous_dispatches + 1
                )
                self.assertEqual(save_attachment.await_count, expected_dispatches)

    async def test_unknown_recognition_preserves_unknown_pipeline_fallback(self):
        result = await ingest_telegram_message(
            telegram_message(),
            SimpleNamespace(),
        )

        self.assertEqual(result.recognized_input_type, InputType.UNKNOWN)
        self.assertEqual(result.input_type, InputType.UNKNOWN)

    def test_task_c_changes_no_runtime_boundary(self):
        ingestion_source = (
            REPOSITORY_ROOT / "core/ingestion/universal_ingestion.py"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "recognized_input_type = recognize_telegram_message",
            ingestion_source,
        )
        self.assertIn("input_type = classify_telegram_message", ingestion_source)
        self.assertIn("if input_type != InputType.TEXT:", ingestion_source)
        self.assertIn("media_type=input_type.value", ingestion_source)


if __name__ == "__main__":
    unittest.main()
