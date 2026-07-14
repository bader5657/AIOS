import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MANIFEST_ROOT = Path("/opt/aios/data/documents/manifests")


@dataclass(slots=True)
class DocumentManifest:
    document_id: str
    media_type: str
    storage_path: str
    original_filename: str
    file_size_bytes: int
    checksum_sha256: str
    source: str
    telegram_user_id: int
    telegram_chat_id: int
    telegram_message_id: int
    received_at: str
    status: str = "stored"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def calculate_sha256(file_path: str) -> str:
    digest = hashlib.sha256()

    with open(file_path, "rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def create_document_manifest(
    *,
    media_type: str,
    storage_path: str,
    original_filename: str,
    telegram_user_id: int,
    telegram_chat_id: int,
    telegram_message_id: int,
) -> str:
    path = Path(storage_path)

    timestamp = datetime.now(timezone.utc)
    document_id = f"DOC-{timestamp.strftime('%Y%m%d-%H%M%S-%f')}"

    manifest = DocumentManifest(
        document_id=document_id,
        media_type=media_type,
        storage_path=str(path),
        original_filename=original_filename,
        file_size_bytes=path.stat().st_size,
        checksum_sha256=calculate_sha256(str(path)),
        source="telegram",
        telegram_user_id=telegram_user_id,
        telegram_chat_id=telegram_chat_id,
        telegram_message_id=telegram_message_id,
        received_at=timestamp.isoformat(),
    )

    MANIFEST_ROOT.mkdir(parents=True, exist_ok=True)
    manifest_path = MANIFEST_ROOT / f"{document_id}.json"

    with open(manifest_path, "w", encoding="utf-8") as file_handle:
        json.dump(manifest.to_dict(), file_handle, ensure_ascii=False, indent=2)

    return str(manifest_path)
