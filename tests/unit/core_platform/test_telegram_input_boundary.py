import ast
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

with patch.dict(sys.modules, {"telegram": SimpleNamespace(Message=object)}):
    from core.app.input_classifier import (
        InputType,
        classify_telegram_message,
        recognize_telegram_message,
    )


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
            "elif input_type == InputType.DOCUMENT and message.document:",
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


if __name__ == "__main__":
    unittest.main()
