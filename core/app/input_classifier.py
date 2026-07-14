from enum import StrEnum

from telegram import Message


class InputType(StrEnum):
    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"
    DOCUMENT = "document"
    VIDEO = "video"
    AUDIO = "audio"
    UNKNOWN = "unknown"


def classify_telegram_message(message: Message) -> InputType:
    if message.photo:
        return InputType.IMAGE

    if message.voice:
        return InputType.VOICE

    if message.document:
        return InputType.DOCUMENT

    if message.video:
        return InputType.VIDEO

    if message.audio:
        return InputType.AUDIO

    if message.text:
        return InputType.TEXT

    return InputType.UNKNOWN
