import mimetypes
from pathlib import Path
from typing import Any

from PIL import Image


_FILE_BACKED_MEDIA_TYPES = frozenset(
    {"image", "voice", "audio", "video", "pdf", "doc", "spreadsheet"}
)
_URL_MEDIA_TYPES = frozenset({"web_link", "youtube_link"})
_APPROVED_MEDIA_TYPES = _FILE_BACKED_MEDIA_TYPES | _URL_MEDIA_TYPES | {"text"}


def _validate_media_type(media_type: str) -> None:
    if media_type not in _APPROVED_MEDIA_TYPES:
        raise ValueError(f"unsupported metadata media_type: {media_type!r}")


def extract_basic_metadata(
    *,
    media_type: str,
    file_path: str | None = None,
    original_filename: str | None = None,
    text: str | None = None,
    source_url: str | None = None,
) -> dict[str, Any]:
    """Extract the active minimum metadata contract from local source facts."""
    _validate_media_type(media_type)
    metadata: dict[str, Any] = {"media_type": media_type}

    if media_type == "text":
        if isinstance(text, str):
            metadata["character_count"] = len(text)
        return metadata

    if media_type in _URL_MEDIA_TYPES:
        if not isinstance(source_url, str) or not source_url:
            raise ValueError(f"source_url is required for {media_type}")
        metadata["source_url"] = source_url
        return metadata

    if not isinstance(file_path, str) or not file_path:
        raise ValueError(f"file_path is required for {media_type}")

    path = Path(file_path)
    if not path.is_file():
        raise ValueError(f"preserved original is not an existing file: {file_path!r}")

    file_size = path.stat().st_size
    if not isinstance(file_size, int) or file_size < 0:
        raise ValueError("file_size_bytes must be a non-negative integer")
    metadata["file_size_bytes"] = file_size

    source_filename = (
        original_filename
        if isinstance(original_filename, str) and original_filename
        else None
    )
    if source_filename:
        metadata["original_filename"] = source_filename

    mime_type = mimetypes.guess_type(source_filename or path.name)[0]
    if mime_type:
        metadata["mime_type"] = mime_type

    source_suffix = Path(source_filename or path.name).suffix
    if source_suffix:
        metadata["format"] = source_suffix.removeprefix(".").lower()

    if media_type == "image":
        with Image.open(path) as image:
            metadata["width_pixels"] = image.width
            metadata["height_pixels"] = image.height
            if image.format:
                metadata["format"] = image.format.lower()
            if image.mode:
                metadata["color_mode"] = image.mode

    return metadata
