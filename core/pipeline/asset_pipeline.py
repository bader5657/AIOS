"""Contract-first, single-execution Asset Pipeline orchestration."""

from dataclasses import dataclass, field
from typing import Any

from telegram import Message
from telegram.ext import ContextTypes

from core.app.request_context import RequestContext
from core.storage.document_manifest import create_document_manifest
from core.storage.metadata_engine import extract_basic_metadata
from core.storage.telegram_storage import save_telegram_attachment


@dataclass(frozen=True, slots=True)
class AssetPipelineResult:
    """Non-canonical transport result for one bounded pipeline execution."""

    success: bool = False
    stored_path: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    manifest_path: str | None = None
    register_handoff_ready: bool = False


async def _store_file_originals(
    message: Message,
    telegram_context: ContextTypes.DEFAULT_TYPE,
    file_original_types: tuple[str, ...],
) -> bool:
    storage_results = []
    for file_original_type in file_original_types:
        storage_results.append(
            await save_telegram_attachment(
                message,
                telegram_context,
                media_type=file_original_type,
            )
        )
    return all(stored_path is not None for stored_path in storage_results)


def _result(
    *,
    stored_path: str | None = None,
    metadata: dict[str, Any] | None = None,
    manifest_path: str | None = None,
) -> AssetPipelineResult:
    handoff_ready = manifest_path is not None
    return AssetPipelineResult(
        success=handoff_ready,
        stored_path=stored_path,
        metadata=metadata or {},
        manifest_path=manifest_path,
        register_handoff_ready=handoff_ready,
    )


async def run_asset_pipeline(
    *,
    request_context: RequestContext,
    recognized_input_type: str,
    message: Message,
    telegram_context: ContextTypes.DEFAULT_TYPE,
    file_original_types: tuple[str, ...],
    original_filename: str | None,
    text: str,
) -> AssetPipelineResult:
    """Coordinate approved capabilities without owning their semantics."""
    if len(file_original_types) > 1:
        await _store_file_originals(message, telegram_context, file_original_types)
        return _result()

    manifest_identity = {
        "telegram_user_id": request_context.user_id,
        "telegram_chat_id": request_context.chat_id,
        "telegram_message_id": request_context.message_id,
    }
    received_at = request_context.received_at.isoformat().replace("+00:00", "Z")

    if len(file_original_types) == 1:
        stored_path = await save_telegram_attachment(
            message,
            telegram_context,
            media_type=recognized_input_type,
        )
        if stored_path is None:
            return _result()

        metadata = extract_basic_metadata(
            media_type=recognized_input_type,
            file_path=stored_path,
            original_filename=original_filename,
        )
        manifest_path = create_document_manifest(
            represented_media_type=recognized_input_type,
            received_at=received_at,
            metadata=metadata,
            storage_path=stored_path,
            **manifest_identity,
        )
        return _result(
            stored_path=stored_path,
            metadata=metadata,
            manifest_path=manifest_path,
        )

    if recognized_input_type == "text":
        metadata = extract_basic_metadata(media_type="text", text=text)
        manifest_path = create_document_manifest(
            represented_media_type="text",
            received_at=received_at,
            metadata=metadata,
            **manifest_identity,
        )
        return _result(metadata=metadata, manifest_path=manifest_path)

    if recognized_input_type in ("web_link", "youtube_link"):
        metadata = extract_basic_metadata(
            media_type=recognized_input_type,
            source_url=text,
        )
        manifest_path = create_document_manifest(
            represented_media_type=recognized_input_type,
            received_at=received_at,
            metadata=metadata,
            source_url=text,
            **manifest_identity,
        )
        return _result(metadata=metadata, manifest_path=manifest_path)

    metadata = extract_basic_metadata(media_type=recognized_input_type)
    return _result(metadata=metadata)
