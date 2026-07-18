import unittest
from types import SimpleNamespace

from core.app.input_classifier import InputType, classify_telegram_message
from core.app.request_context import RequestContext


def make_message(**overrides):
    defaults = {
        "photo": None,
        "voice": None,
        "document": None,
        "video": None,
        "audio": None,
        "text": None,
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


class InputClassifierTests(unittest.TestCase):
    def test_image_is_classified(self):
        self.assertEqual(
            classify_telegram_message(make_message(photo=[object()])),
            InputType.IMAGE,
        )

    def test_voice_is_classified(self):
        self.assertEqual(
            classify_telegram_message(make_message(voice=object())),
            InputType.VOICE,
        )

    def test_document_is_classified(self):
        self.assertEqual(
            classify_telegram_message(make_message(document=object())),
            InputType.DOCUMENT,
        )

    def test_video_is_classified(self):
        self.assertEqual(
            classify_telegram_message(make_message(video=object())),
            InputType.VIDEO,
        )

    def test_audio_is_classified(self):
        self.assertEqual(
            classify_telegram_message(make_message(audio=object())),
            InputType.AUDIO,
        )

    def test_text_is_classified(self):
        self.assertEqual(
            classify_telegram_message(make_message(text="catat order")),
            InputType.TEXT,
        )

    def test_unknown_is_classified(self):
        self.assertEqual(
            classify_telegram_message(make_message()),
            InputType.UNKNOWN,
        )


class RequestContextTests(unittest.TestCase):
    def test_context_from_telegram(self):
        context = RequestContext.from_telegram(
            user_id=101,
            chat_id=202,
            message_id=303,
            username="bagus",
            text="catat order baru",
        )

        self.assertEqual(context.source, "telegram")
        self.assertEqual(context.user_id, 101)
        self.assertEqual(context.chat_id, 202)
        self.assertEqual(context.message_id, 303)
        self.assertEqual(context.username, "bagus")
        self.assertEqual(context.text, "catat order baru")
        self.assertIsNotNone(context.received_at.tzinfo)

    def test_context_can_be_serialized(self):
        context = RequestContext.from_telegram(
            user_id=1,
            chat_id=2,
            message_id=3,
            username="tester",
            text="test",
        )

        data = context.to_dict()

        self.assertEqual(data["source"], "telegram")
        self.assertEqual(data["message_id"], 3)
        self.assertIsInstance(data["received_at"], str)


if __name__ == "__main__":
    unittest.main()
