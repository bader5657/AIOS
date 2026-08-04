from dataclasses import dataclass

from telegram import Message
from telegram.ext import ContextTypes

from core.app.input_classifier import (
    InputType,
    classify_telegram_message,
    recognize_telegram_message,
)
from core.storage.document_manifest import create_document_manifest
from core.storage.metadata_engine import extract_basic_metadata
from core.storage.telegram_storage import save_telegram_attachment


@dataclass(slots=True)
class IngestionResult:
    input_type: InputType
    recognized_input_type: InputType
    stored_path: str | None
    manifest_path: str | None
    metadata: dict
    text: str


async def ingest_telegram_message(
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
) -> IngestionResult:
    recognized_input_type = recognize_telegram_message(message)
    input_type = classify_telegram_message(message)

    stored_path = None
    manifest_path = None
    metadata = {}

    if input_type != InputType.TEXT:
        stored_path = await save_telegram_attachment(message, context)

        if stored_path:
            metadata = extract_basic_metadata(stored_path)

            manifest_path = create_document_manifest(
                media_type=input_type.value,
                storage_path=stored_path,
                original_filename="telegram",
                telegram_user_id=message.from_user.id if message.from_user else 0,
                telegram_chat_id=message.chat.id,
                telegram_message_id=message.message_id,
            )

    text = message.text or message.caption or ""

    return IngestionResult(
        input_type=input_type,
        recognized_input_type=recognized_input_type,
        stored_path=stored_path,
        manifest_path=manifest_path,
        metadata=metadata,
        text=text,
    )
