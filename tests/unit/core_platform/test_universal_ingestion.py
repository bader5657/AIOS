import sys
import unittest
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


class UniversalIngestionRecognitionTests(unittest.IsolatedAsyncioTestCase):
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
                        universal_ingestion,
                        "save_telegram_attachment",
                        save_attachment,
                    ),
                ):
                    result = await universal_ingestion.ingest_telegram_message(
                        telegram_message(text="candidate"),
                        SimpleNamespace(),
                    )

                self.assertEqual(result.recognized_input_type, recognized)
                self.assertEqual(result.input_type, pipeline)
                if pipeline == InputType.TEXT:
                    save_attachment.assert_not_awaited()
                else:
                    save_attachment.assert_awaited_once()

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
                message,
                SimpleNamespace(),
            )

        save_attachment.assert_awaited_once_with(message, unittest.mock.ANY)
        extract_metadata.assert_called_once_with("/existing/path/image.jpg")
        create_manifest.assert_called_once_with(
            media_type="image",
            storage_path="/existing/path/image.jpg",
            original_filename=None,
            telegram_user_id=7,
            telegram_chat_id=8,
            telegram_message_id=9,
        )
        self.assertEqual(result.input_type, InputType.IMAGE)
        self.assertEqual(result.recognized_input_type, InputType.IMAGE)
        self.assertEqual(result.text, "caption")

    async def test_original_filename_is_preserved_separately_for_manifest(self):
        message = telegram_message(
            document=SimpleNamespace(file_name="Exact Received Name.PDF")
        )
        create_manifest = Mock(return_value="/stored/manifest.json")
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
                universal_ingestion,
                "save_telegram_attachment",
                AsyncMock(return_value="/stored/generated.pdf"),
            ),
            patch.object(
                universal_ingestion,
                "extract_basic_metadata",
                Mock(return_value={}),
            ),
            patch.object(
                universal_ingestion,
                "create_document_manifest",
                create_manifest,
            ),
        ):
            await universal_ingestion.ingest_telegram_message(
                message,
                SimpleNamespace(),
            )
        self.assertEqual(
            create_manifest.call_args.kwargs["original_filename"],
            "Exact Received Name.PDF",
        )

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


if __name__ == "__main__":
    unittest.main()
