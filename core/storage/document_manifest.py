import hashlib
import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4


MANIFEST_ROOT = Path("/opt/aios/data/documents/manifests")

FILE_BACKED_MEDIA_TYPES = frozenset(
    {"image", "voice", "audio", "video", "pdf", "doc", "spreadsheet"}
)
URL_MEDIA_TYPES = frozenset({"web_link", "youtube_link"})
APPROVED_MEDIA_TYPES = FILE_BACKED_MEDIA_TYPES | URL_MEDIA_TYPES | {"text"}

_UNIVERSAL_FIELDS = frozenset(
    {
        "manifest_id",
        "represented_media_type",
        "received_at",
        "manifest_status",
        "metadata",
    }
)
_FILE_FIELDS = frozenset({"storage_path", "file_size_bytes", "checksum_sha256"})
_OPTIONAL_FIELDS = frozenset(
    {"source_url", "telegram_user_id", "telegram_chat_id", "telegram_message_id"}
)
_METADATA_FIELDS = frozenset(
    {
        "media_type",
        "character_count",
        "source_url",
        "file_size_bytes",
        "original_filename",
        "mime_type",
        "format",
        "width_pixels",
        "height_pixels",
        "color_mode",
        "orientation",
        "duration_seconds",
        "codec",
        "sample_rate_hz",
        "channel_count",
        "bit_rate_bps",
        "title",
        "artist",
        "video_codec",
        "audio_codec",
        "frame_rate_fps",
        "page_count",
        "author",
        "created_at",
        "modified_at",
        "word_count",
        "sheet_count",
        "sheet_names",
    }
)
_UTC_RFC3339_PATTERN = re.compile(
    r"\A\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z\Z"
)


@dataclass(frozen=True, slots=True)
class DocumentManifest:
    manifest_id: str
    represented_media_type: str
    received_at: str
    manifest_status: str
    metadata: dict[str, Any]
    storage_path: str | None = None
    file_size_bytes: int | None = None
    checksum_sha256: str | None = None
    source_url: str | None = None
    telegram_user_id: int | None = None
    telegram_chat_id: int | None = None
    telegram_message_id: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            key: value
            for key, value in asdict(self).items()
            if value is not None
        }


def calculate_sha256(file_path: str) -> str:
    digest = hashlib.sha256()
    with open(file_path, "rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value)


def _validate_utc_rfc3339(value: object, field_name: str) -> None:
    if not isinstance(value, str) or _UTC_RFC3339_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{field_name} must be a UTC RFC3339 timestamp")
    try:
        parsed = datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a UTC RFC3339 timestamp") from exc
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise ValueError(f"{field_name} must be a UTC RFC3339 timestamp")


def _validate_metadata(metadata: object, represented_media_type: str) -> None:
    if not isinstance(metadata, dict) or not metadata:
        raise ValueError("metadata must be a non-empty object")
    unknown = set(metadata) - _METADATA_FIELDS
    if unknown:
        raise ValueError(f"unknown metadata fields: {sorted(unknown)!r}")
    if metadata.get("media_type") != represented_media_type:
        raise ValueError("metadata media_type must match represented_media_type")

    string_fields = {
        "source_url", "original_filename", "mime_type", "format", "color_mode",
        "orientation", "codec", "title", "artist", "video_codec", "audio_codec",
        "author", "created_at", "modified_at",
    }
    integer_fields = {
        "character_count", "file_size_bytes", "width_pixels", "height_pixels",
        "sample_rate_hz", "channel_count", "bit_rate_bps", "page_count",
        "word_count", "sheet_count",
    }
    number_fields = {"duration_seconds", "frame_rate_fps"}
    for field in string_fields & metadata.keys():
        if not _is_non_empty_string(metadata[field]):
            raise ValueError(f"metadata {field} must be a non-empty string")
    for field in integer_fields & metadata.keys():
        value = metadata[field]
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"metadata {field} must be a non-negative integer")
    for field in number_fields & metadata.keys():
        value = metadata[field]
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
            raise ValueError(f"metadata {field} must be a non-negative number")
    if "sheet_names" in metadata and (
        not isinstance(metadata["sheet_names"], list)
        or any(not _is_non_empty_string(name) for name in metadata["sheet_names"])
    ):
        raise ValueError("metadata sheet_names must be an array of non-empty strings")

    if represented_media_type == "text":
        allowed = {"media_type", "character_count"}
    elif represented_media_type in URL_MEDIA_TYPES:
        allowed = {"media_type", "source_url"}
        if "source_url" not in metadata:
            raise ValueError("URL metadata requires source_url")
    else:
        allowed = {
            "media_type", "file_size_bytes", "original_filename", "mime_type", "format"
        }
        if represented_media_type == "image":
            allowed |= {"width_pixels", "height_pixels", "orientation", "color_mode"}
        elif represented_media_type == "voice":
            allowed |= {
                "duration_seconds", "codec", "sample_rate_hz", "channel_count",
                "bit_rate_bps",
            }
        elif represented_media_type == "audio":
            allowed |= {
                "duration_seconds", "codec", "sample_rate_hz", "channel_count",
                "bit_rate_bps", "title", "artist",
            }
        elif represented_media_type == "video":
            allowed |= {
                "duration_seconds", "width_pixels", "height_pixels", "video_codec",
                "audio_codec", "frame_rate_fps", "bit_rate_bps",
            }
        elif represented_media_type == "pdf":
            allowed |= {"page_count", "title", "author", "created_at", "modified_at"}
        elif represented_media_type == "doc":
            allowed |= {
                "page_count", "word_count", "title", "author", "created_at",
                "modified_at",
            }
        elif represented_media_type == "spreadsheet":
            allowed |= {
                "sheet_count", "sheet_names", "author", "created_at", "modified_at"
            }
        if "file_size_bytes" not in metadata:
            raise ValueError("file-backed metadata requires file_size_bytes")
    disallowed = set(metadata) - allowed
    if disallowed:
        raise ValueError(f"metadata fields invalid for represented type: {sorted(disallowed)!r}")


def validate_manifest(manifest: Mapping[str, Any]) -> None:
    if not isinstance(manifest, dict):
        raise ValueError("Document Manifest must be an object")
    unknown = set(manifest) - _UNIVERSAL_FIELDS - _FILE_FIELDS - _OPTIONAL_FIELDS
    if unknown:
        raise ValueError(f"unknown Document Manifest fields: {sorted(unknown)!r}")
    missing = _UNIVERSAL_FIELDS - set(manifest)
    if missing:
        raise ValueError(f"missing Document Manifest fields: {sorted(missing)!r}")

    if not _is_non_empty_string(manifest["manifest_id"]):
        raise ValueError("manifest_id must be a non-empty string")
    media_type = manifest["represented_media_type"]
    if media_type not in APPROVED_MEDIA_TYPES:
        raise ValueError(f"unsupported represented_media_type: {media_type!r}")
    _validate_utc_rfc3339(manifest["received_at"], "received_at")
    if manifest["manifest_status"] != "created":
        raise ValueError("manifest_status must be 'created'")
    _validate_metadata(manifest["metadata"], media_type)

    for field in ("telegram_user_id", "telegram_message_id"):
        if field in manifest:
            value = manifest[field]
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{field} must be a non-negative integer")
    if "telegram_chat_id" in manifest and (
        not isinstance(manifest["telegram_chat_id"], int)
        or isinstance(manifest["telegram_chat_id"], bool)
    ):
        raise ValueError("telegram_chat_id must be an integer")

    present_file_fields = _FILE_FIELDS & set(manifest)
    if media_type in FILE_BACKED_MEDIA_TYPES or (
        media_type == "text" and present_file_fields
    ):
        if present_file_fields != _FILE_FIELDS:
            raise ValueError("file-backed inputs require all stored-original fields")
        if not _is_non_empty_string(manifest["storage_path"]):
            raise ValueError("storage_path must be a non-empty string")
        size = manifest["file_size_bytes"]
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise ValueError("file_size_bytes must be a non-negative integer")
        checksum = manifest["checksum_sha256"]
        if not isinstance(checksum, str) or len(checksum) != 64 or any(
            character not in "0123456789abcdef" for character in checksum
        ):
            raise ValueError("checksum_sha256 must be lowercase 64-hex")
        if manifest["metadata"].get("file_size_bytes") != size:
            raise ValueError("metadata file_size_bytes must match the stored original")
    elif present_file_fields:
        raise ValueError("URL-only inputs cannot contain stored-original fields")

    if media_type in URL_MEDIA_TYPES:
        if not _is_non_empty_string(manifest.get("source_url")):
            raise ValueError("URL-only inputs require source_url")
        if manifest["source_url"] != manifest["metadata"]["source_url"]:
            raise ValueError("source_url must preserve exact metadata source_url")
    elif "source_url" in manifest:
        raise ValueError("source_url is valid only for URL-only inputs")


def _write_manifest_atomically(manifest: dict[str, Any], manifest_path: Path) -> None:
    temporary_path: Path | None = None
    destination_reserved = False
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=manifest_path.parent,
            prefix=f".{manifest_path.stem}-",
            suffix=".tmp",
            delete=False,
        ) as file_handle:
            temporary_path = Path(file_handle.name)
            json.dump(manifest, file_handle, ensure_ascii=False, indent=2)
            file_handle.write("\n")
            file_handle.flush()
            os.fsync(file_handle.fileno())
        descriptor = os.open(
            manifest_path,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            0o600,
        )
        os.close(descriptor)
        destination_reserved = True
        os.replace(temporary_path, manifest_path)
    except Exception:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        if destination_reserved:
            manifest_path.unlink(missing_ok=True)
        raise


def create_document_manifest(
    *,
    represented_media_type: str,
    received_at: str,
    metadata: dict[str, Any],
    storage_path: str | None = None,
    source_url: str | None = None,
    telegram_user_id: int | None = None,
    telegram_chat_id: int | None = None,
    telegram_message_id: int | None = None,
) -> str:
    manifest_id = str(uuid4())
    file_size_bytes = None
    checksum_sha256 = None
    if storage_path is not None:
        path = Path(storage_path)
        if not path.is_file():
            raise ValueError(f"stored original is not an existing file: {storage_path!r}")
        file_size_bytes = path.stat().st_size
        checksum_sha256 = calculate_sha256(str(path))

    manifest = DocumentManifest(
        manifest_id=manifest_id,
        represented_media_type=represented_media_type,
        received_at=received_at,
        manifest_status="created",
        metadata=metadata,
        storage_path=storage_path,
        file_size_bytes=file_size_bytes,
        checksum_sha256=checksum_sha256,
        source_url=source_url,
        telegram_user_id=telegram_user_id,
        telegram_chat_id=telegram_chat_id,
        telegram_message_id=telegram_message_id,
    ).to_dict()
    validate_manifest(manifest)

    MANIFEST_ROOT.mkdir(parents=True, exist_ok=True)
    manifest_path = MANIFEST_ROOT / f"{manifest_id}.json"
    _write_manifest_atomically(manifest, manifest_path)
    return str(manifest_path)
