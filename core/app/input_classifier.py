import re
from enum import StrEnum

from telegram import Message


class InputType(StrEnum):
    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"
    DOCUMENT = "document"
    PDF = "pdf"
    DOC = "doc"
    SPREADSHEET = "spreadsheet"
    VIDEO = "video"
    AUDIO = "audio"
    WEB_LINK = "web_link"
    YOUTUBE_LINK = "youtube_link"
    UNKNOWN = "unknown"


_PDF_PATTERN = re.compile(r".+\.pdf\Z", re.IGNORECASE)
_DOC_PATTERN = re.compile(r".+\.docx?\Z", re.IGNORECASE)
_SPREADSHEET_PATTERN = re.compile(r".+\.(?:xls|xlsx|csv|ods)\Z", re.IGNORECASE)
_WEB_LINK_PATTERN = re.compile(
    r"https?://[^\s/?#]+(?:[/?#][^\s]*)?\Z",
    re.IGNORECASE,
)
_YOUTUBE_LINK_PATTERN = re.compile(
    r"https?://(?:youtube\.com|www\.youtube\.com|m\.youtube\.com|youtu\.be)"
    r"(?:[/?#][^\s]*)?\Z",
    re.IGNORECASE,
)

_PIPELINE_COMPATIBILITY = {
    InputType.PDF: InputType.DOCUMENT,
    InputType.DOC: InputType.DOCUMENT,
    InputType.SPREADSHEET: InputType.DOCUMENT,
    InputType.WEB_LINK: InputType.TEXT,
    InputType.YOUTUBE_LINK: InputType.TEXT,
}


def _classify_document(filename: str | None) -> InputType:
    candidate = filename or ""

    if _PDF_PATTERN.fullmatch(candidate):
        return InputType.PDF

    if _DOC_PATTERN.fullmatch(candidate):
        return InputType.DOC

    if _SPREADSHEET_PATTERN.fullmatch(candidate):
        return InputType.SPREADSHEET

    return InputType.DOCUMENT


def _classify_text(candidate: str) -> InputType:
    if _YOUTUBE_LINK_PATTERN.fullmatch(candidate):
        return InputType.YOUTUBE_LINK

    if _WEB_LINK_PATTERN.fullmatch(candidate):
        return InputType.WEB_LINK

    return InputType.TEXT


def recognize_telegram_message(message: Message) -> InputType:
    if message.photo:
        return InputType.IMAGE

    if message.voice:
        return InputType.VOICE

    if message.document:
        return _classify_document(getattr(message.document, "file_name", None))

    if message.video:
        return InputType.VIDEO

    if message.audio:
        return InputType.AUDIO

    if message.text:
        return _classify_text(message.text)

    return InputType.UNKNOWN


def classify_telegram_message(message: Message) -> InputType:
    recognized = recognize_telegram_message(message)
    return _PIPELINE_COMPATIBILITY.get(recognized, recognized)
