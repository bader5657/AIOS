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


if __name__ == "__main__":
    unittest.main()
