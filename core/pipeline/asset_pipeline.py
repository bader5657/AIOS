from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.pipeline.state import AssetPipelineStatus
from core.storage.document_manifest import create_document_manifest
from core.storage.file_storage import save_file
from core.storage.metadata_engine import extract_basic_metadata


@dataclass(slots=True)
class AssetPipelineResult:
    status: AssetPipelineStatus
    storage_path: str
    metadata: dict[str, Any]
    manifest_path: str


class AssetPipeline:
    """Orchestrates storage, metadata extraction, and manifest creation."""

    def process(
        self,
        source_path: str,
        *,
        media_type: str,
        original_filename: str,
        telegram_user_id: int,
        telegram_chat_id: int,
        telegram_message_id: int,
    ) -> AssetPipelineResult:
        source = Path(source_path)

        if not source.exists():
            raise FileNotFoundError(source_path)

        storage_path = save_file(str(source))
        metadata = extract_basic_metadata(storage_path)

        manifest_path = create_document_manifest(
            media_type=media_type,
            storage_path=storage_path,
            original_filename=original_filename,
            telegram_user_id=telegram_user_id,
            telegram_chat_id=telegram_chat_id,
            telegram_message_id=telegram_message_id,
        )

        return AssetPipelineResult(
            status=AssetPipelineStatus.COMPLETED,
            storage_path=storage_path,
            metadata=metadata,
            manifest_path=manifest_path,
        )
