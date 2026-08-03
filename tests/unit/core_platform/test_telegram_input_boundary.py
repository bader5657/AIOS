import ast
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

with patch.dict(sys.modules, {"telegram": SimpleNamespace(Message=object)}):
    from core.app.input_classifier import InputType, classify_telegram_message


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
        for filename in (
            "report.pdf",
            "letter.doc",
            "letter.docx",
            "ledger.xls",
            "ledger.xlsx",
            "export.csv",
        ):
            message = telegram_message(
                document=SimpleNamespace(file_name=filename)
            )
            with self.subTest(filename=filename):
                self.assertEqual(
                    classify_telegram_message(message),
                    InputType.DOCUMENT,
                )

    def test_link_inputs_remain_text_at_the_adapter_boundary(self):
        for value in (
            "https://example.com/article",
            "https://www.youtube.com/watch?v=example",
        ):
            with self.subTest(value=value):
                self.assertEqual(
                    classify_telegram_message(telegram_message(text=value)),
                    InputType.TEXT,
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
