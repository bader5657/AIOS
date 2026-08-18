import ast
import sys
import unittest
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
    },
):
    from core.app.input_classifier import (
        InputType,
        classify_telegram_message,
        recognize_telegram_message,
    )
    from core.storage import telegram_storage


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


def telegram_message(**overrides):
    fields = {
        "photo": None,
        "voice": None,
        "document": None,
        "video": None,
        "audio": None,
        "text": None,
    }
    fields.update(overrides)
    return SimpleNamespace(**fields)


class TestTelegramInputClassifier(unittest.TestCase):
    def test_classifies_native_telegram_input_forms(self):
        cases = (
            (telegram_message(text="hello"), InputType.TEXT),
            (telegram_message(photo=[object()]), InputType.IMAGE),
            (telegram_message(voice=object()), InputType.VOICE),
            (telegram_message(audio=object()), InputType.AUDIO),
            (telegram_message(video=object()), InputType.VIDEO),
            (telegram_message(document=object()), InputType.DOCUMENT),
        )

        for message, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(classify_telegram_message(message), expected)

    def test_document_transport_covers_blueprint_file_inputs(self):
        cases = (
            ("report.pdf", InputType.PDF),
            ("letter.doc", InputType.DOC),
            ("letter.docx", InputType.DOC),
            ("ledger.xls", InputType.SPREADSHEET),
            ("ledger.xlsx", InputType.SPREADSHEET),
            ("export.csv", InputType.SPREADSHEET),
            ("workbook.ods", InputType.SPREADSHEET),
        )

        for filename, expected in cases:
            message = telegram_message(
                document=SimpleNamespace(file_name=filename)
            )
            with self.subTest(filename=filename, expected=expected):
                self.assertEqual(
                    recognize_telegram_message(message),
                    expected,
                )

    def test_unrecognized_document_remains_generic_document(self):
        for filename in (None, "notes.txt", "archive.zip"):
            with self.subTest(filename=filename):
                message = telegram_message(
                    document=SimpleNamespace(file_name=filename)
                )
                self.assertEqual(
                    recognize_telegram_message(message),
                    InputType.DOCUMENT,
                )

    def test_classifies_web_link_and_complete_youtube_host_set(self):
        cases = (
            ("https://example.com/article", InputType.WEB_LINK),
            ("https://youtube.com/watch?v=example", InputType.YOUTUBE_LINK),
            ("https://www.youtube.com/watch?v=example", InputType.YOUTUBE_LINK),
            ("https://m.youtube.com/watch?v=example", InputType.YOUTUBE_LINK),
            ("https://youtu.be/example", InputType.YOUTUBE_LINK),
        )

        for value, expected in cases:
            with self.subTest(value=value, expected=expected):
                self.assertEqual(
                    recognize_telegram_message(telegram_message(text=value)),
                    expected,
                )

    def test_non_url_and_unsupported_youtube_host_remain_bounded(self):
        cases = (
            ("hello", InputType.TEXT),
            ("youtube.com/watch?v=example", InputType.TEXT),
            ("https://music.youtube.com/watch?v=example", InputType.WEB_LINK),
            ("https://youtube.com.example/watch?v=example", InputType.WEB_LINK),
            ("https://example.com bad", InputType.TEXT),
        )

        for value, expected in cases:
            with self.subTest(value=value, expected=expected):
                self.assertEqual(
                    recognize_telegram_message(telegram_message(text=value)),
                    expected,
                )

    def test_pipeline_classifier_preserves_existing_dispatch_categories(self):
        cases = (
            (
                telegram_message(document=SimpleNamespace(file_name="a.pdf")),
                InputType.DOCUMENT,
            ),
            (
                telegram_message(document=SimpleNamespace(file_name="a.docx")),
                InputType.DOCUMENT,
            ),
            (
                telegram_message(document=SimpleNamespace(file_name="a.ods")),
                InputType.DOCUMENT,
            ),
            (telegram_message(text="https://example.com"), InputType.TEXT),
            (telegram_message(text="https://youtu.be/example"), InputType.TEXT),
        )

        for message, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(classify_telegram_message(message), expected)

    def test_classifier_uses_no_parser_normalizer_or_url_decomposition(self):
        source = (REPOSITORY_ROOT / "core/app/input_classifier.py").read_text(
            encoding="utf-8"
        )

        prohibited = (
            "urllib.parse",
            "urlparse",
            "urlsplit",
            "parse_url",
            ".lower(",
            ".casefold(",
        )
        for marker in prohibited:
            with self.subTest(marker=marker):
                self.assertNotIn(marker, source)

    def test_downstream_dispatch_contract_remains_unchanged(self):
        ingestion_source = (
            REPOSITORY_ROOT / "core/ingestion/universal_ingestion.py"
        ).read_text(encoding="utf-8")
        storage_source = (
            REPOSITORY_ROOT / "core/storage/telegram_storage.py"
        ).read_text(encoding="utf-8")

        self.assertIn("if input_type != InputType.TEXT:", ingestion_source)
        self.assertIn(
            'elif media_type == "document" and message.document:',
            storage_source,
        )

    def test_unsupported_message_is_unknown(self):
        self.assertEqual(
            classify_telegram_message(telegram_message()),
            InputType.UNKNOWN,
        )

    def test_media_precedes_text_caption_fallback(self):
        message = telegram_message(document=object(), text="caption")
        self.assertEqual(
            classify_telegram_message(message),
            InputType.DOCUMENT,
        )


class TestTelegramAdapterDependencyBoundary(unittest.TestCase):
    def test_adapter_delegates_without_importing_classifier_or_storage(self):
        source_path = REPOSITORY_ROOT / "core/adapters/telegram/main.py"
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        imported_modules = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        }

        self.assertIn("core.ingestion.universal_ingestion", imported_modules)
        self.assertIn("core.app.request_context", imported_modules)
        self.assertNotIn("core.app.input_classifier", imported_modules)
        self.assertFalse(
            any(module.startswith("core.storage") for module in imported_modules)
        )

    def test_adapter_contains_no_input_type_decision_tree(self):
        source_path = REPOSITORY_ROOT / "core/adapters/telegram/main.py"
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        referenced_attributes = {
            node.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Attribute)
        }

        self.assertTrue(
            {"photo", "voice", "document", "video", "audio"}.isdisjoint(
                referenced_attributes
            )
        )


class TestTelegramStorageDependencyBoundary(unittest.IsolatedAsyncioTestCase):
    def test_storage_has_no_app_classification_dependency(self):
        source_path = REPOSITORY_ROOT / "core/storage/telegram_storage.py"
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported_modules = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        }
        referenced_names = {
            node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
        }

        self.assertNotIn("core.app.input_classifier", imported_modules)
        self.assertNotIn("InputType", referenced_names)
        self.assertNotIn("recognize_telegram_message", referenced_names)
        self.assertNotIn("InputType", source)
        self.assertNotIn("recognize_telegram_message", source)

    def test_storage_package_has_no_disguised_app_dependency(self):
        for source_path in (REPOSITORY_ROOT / "core/storage").glob("*.py"):
            with self.subTest(source_path=source_path):
                tree = ast.parse(source_path.read_text(encoding="utf-8"))
                imported_modules = {
                    node.module
                    for node in ast.walk(tree)
                    if isinstance(node, ast.ImportFrom)
                    and node.module is not None
                }
                imported_modules.update(
                    alias.name
                    for node in ast.walk(tree)
                    if isinstance(node, ast.Import)
                    for alias in node.names
                )
                self.assertFalse(
                    any(
                        module == "core.app" or module.startswith("core.app.")
                        for module in imported_modules
                    )
                )

    async def test_neutral_media_value_preserves_attachment_and_storage_behavior(self):
        cases = (
            ("image", telegram_message(photo=[SimpleNamespace(file_id="image")]), "image", ".jpg", None),
            ("voice", telegram_message(voice=SimpleNamespace(file_id="voice")), "voice", ".ogg", None),
            ("document", telegram_message(document=SimpleNamespace(file_id="document", file_name="notes.txt")), "document", ".txt", "notes.txt"),
            ("pdf", telegram_message(document=SimpleNamespace(file_id="pdf", file_name="report.PDF")), "pdf", ".PDF", "report.PDF"),
            ("doc", telegram_message(document=SimpleNamespace(file_id="doc", file_name="letter.docx")), "doc", ".docx", "letter.docx"),
            ("spreadsheet", telegram_message(document=SimpleNamespace(file_id="sheet", file_name="ledger.xlsx")), "sheet", ".xlsx", "ledger.xlsx"),
            ("video", telegram_message(video=SimpleNamespace(file_id="video", file_name=None)), "video", ".mp4", None),
            ("audio", telegram_message(audio=SimpleNamespace(file_id="audio", file_name=None)), "audio", ".mp3", None),
        )

        for media_type, message, file_id, suffix, original_filename in cases:
            with self.subTest(media_type=media_type):
                telegram_file = SimpleNamespace(download_to_drive=AsyncMock())
                bot = SimpleNamespace(get_file=AsyncMock(return_value=telegram_file))
                temporary_file = Mock()
                temporary_file.__enter__ = Mock(
                    return_value=SimpleNamespace(name="/tmp/aios-stage-3-5-1")
                )
                temporary_file.__exit__ = Mock(return_value=False)
                with (
                    patch.object(
                        telegram_storage,
                        "NamedTemporaryFile",
                        return_value=temporary_file,
                    ) as named_temporary_file,
                    patch.object(
                        telegram_storage,
                        "save_file",
                        return_value=f"/stored/{media_type}",
                    ) as save_file,
                ):
                    result = await telegram_storage.save_telegram_attachment(
                        message,
                        SimpleNamespace(bot=bot),
                        media_type=media_type,
                    )

                bot.get_file.assert_awaited_once_with(file_id)
                named_temporary_file.assert_called_once_with(
                    suffix=suffix,
                    delete=False,
                )
                save_file.assert_called_once_with(
                    "/tmp/aios-stage-3-5-1",
                    storage_class=media_type,
                    original_filename=original_filename,
                )
                self.assertEqual(result, f"/stored/{media_type}")


if __name__ == "__main__":
    unittest.main()
