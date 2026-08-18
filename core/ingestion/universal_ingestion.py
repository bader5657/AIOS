from dataclasses import dataclass
from pathlib import Path

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
    register_handoff_ready: bool
    process_handoff_ready: bool
    route_handoff_ready: bool
    respond_acknowledgement_ready: bool


def _file_original_types(message: Message) -> tuple[InputType, ...]:
    """Enumerate file originals in deterministic Telegram transport order."""
    originals = []
    if message.photo:
        originals.append(InputType.IMAGE)
    if message.voice:
        originals.append(InputType.VOICE)
    if message.document:
        filename = getattr(message.document, "file_name", None) or ""
        extension = Path(filename).suffix.removeprefix(".").lower()
        if extension == "pdf":
            originals.append(InputType.PDF)
        elif extension in ("doc", "docx"):
            originals.append(InputType.DOC)
        elif extension in ("xls", "xlsx", "csv", "ods"):
            originals.append(InputType.SPREADSHEET)
        else:
            originals.append(InputType.DOCUMENT)
    if message.video:
        originals.append(InputType.VIDEO)
    if message.audio:
        originals.append(InputType.AUDIO)
    return tuple(originals)

async def _store_file_originals(
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
    file_original_types: tuple[InputType, ...],
) -> bool:
    storage_results = []
    for file_original_type in file_original_types:
        storage_results.append(
            await save_telegram_attachment(
                message,
                context,
                input_type=file_original_type,
            )
        )
    return all(stored_path is not None for stored_path in storage_results)


async def ingest_telegram_message(
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
) -> IngestionResult:
    recognized_input_type = recognize_telegram_message(message)
    input_type = classify_telegram_message(message)

    stored_path = None
    manifest_path = None
    metadata = {}
    file_original_types = _file_original_types(message)
    aggregate_storage_ready = True
    text = message.text or message.caption or ""

    if input_type != InputType.TEXT:
        if len(file_original_types) == 1:
            stored_path = await save_telegram_attachment(message, context)

            if stored_path:
                original_filename = None
                if message.document:
                    original_filename = message.document.file_name
                elif message.audio:
                    original_filename = message.audio.file_name
                elif message.video:
                    original_filename = getattr(message.video, "file_name", None)

                metadata = extract_basic_metadata(
                    media_type=recognized_input_type.value,
                    file_path=stored_path,
                    original_filename=original_filename,
                )

                manifest_path = create_document_manifest(
                    media_type=input_type.value,
                    storage_path=stored_path,
                    original_filename=original_filename,
                    telegram_user_id=message.from_user.id if message.from_user else 0,
                    telegram_chat_id=message.chat.id,
                    telegram_message_id=message.message_id,
                )

        elif len(file_original_types) > 1:
            aggregate_storage_ready = await _store_file_originals(
                message,
                context,
                file_original_types,
            )

            # Stage 3.2.2 stops at aggregate storage readiness without selecting a
            # representative path or entering any downstream lifecycle boundary.
        else:
            metadata = extract_basic_metadata(
                media_type=recognized_input_type.value
            )
    elif recognized_input_type == InputType.TEXT:
        metadata = extract_basic_metadata(
            media_type=recognized_input_type.value,
            text=text,
        )
    elif recognized_input_type in (InputType.WEB_LINK, InputType.YOUTUBE_LINK):
        metadata = extract_basic_metadata(
            media_type=recognized_input_type.value,
            source_url=text,
        )
    else:
        metadata = extract_basic_metadata(media_type=recognized_input_type.value)

    return IngestionResult(
        input_type=input_type,
        recognized_input_type=recognized_input_type,
        stored_path=stored_path,
        manifest_path=manifest_path,
        metadata=metadata,
        text=text,
        register_handoff_ready=(
            aggregate_storage_ready and manifest_path is not None
        ),
        process_handoff_ready=False,
        route_handoff_ready=False,
        respond_acknowledgement_ready=True,
    )
