import mimetypes
from pathlib import Path
from typing import Any

from PIL import Image


def extract_basic_metadata(file_path: str) -> dict[str, Any]:
    path = Path(file_path)

    metadata: dict[str, Any] = {
        "file_name": path.name,
        "file_extension": path.suffix.lower(),
        "file_size_bytes": path.stat().st_size,
        "mime_type": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
    }

    if metadata["mime_type"].startswith("image/"):
        with Image.open(path) as image:
            metadata["width"] = image.width
            metadata["height"] = image.height
            metadata["image_format"] = image.format or ""

    return metadata
