from pathlib import Path
import shutil
from typing import Callable
from uuid import UUID, uuid4


DOCUMENT_ROOT = Path("/opt/aios/data/documents")
STORAGE_ROOTS = {
    "image": DOCUMENT_ROOT / "images",
    "voice": DOCUMENT_ROOT / "voice",
    "audio": DOCUMENT_ROOT / "voice",
    "video": DOCUMENT_ROOT / "images",
    "pdf": DOCUMENT_ROOT / "pdf",
    "doc": DOCUMENT_ROOT / "docs",
    "spreadsheet": DOCUMENT_ROOT / "docs",
    "document": DOCUMENT_ROOT / "docs",
    "web_link": DOCUMENT_ROOT / "links",
    "youtube_link": DOCUMENT_ROOT / "links",
    "manifest": DOCUMENT_ROOT / "manifests",
}


def storage_root(storage_class: str) -> Path:
    try:
        return STORAGE_ROOTS[storage_class]
    except KeyError as error:
        raise ValueError(f"unsupported storage class: {storage_class}") from error


def _accepted_extension(original_filename: str | None) -> str:
    if not original_filename:
        return ""
    extension = Path(original_filename).suffix.removeprefix(".")
    if not 1 <= len(extension) <= 16 or not extension.isascii():
        return ""
    if not extension.isalnum():
        return ""
    return f".{extension.lower()}"


def generate_storage_name(
    original_filename: str | None,
    *,
    uuid_factory: Callable[[], UUID] = uuid4,
) -> str:
    candidate = uuid_factory()
    if candidate.version != 4:
        raise ValueError("storage filename requires a UUID v4 candidate")
    return f"{str(candidate).lower()}{_accepted_extension(original_filename)}"


def save_file(
    source_path: str | Path,
    *,
    storage_class: str = "image",
    original_filename: str | None = None,
    uuid_factory: Callable[[], UUID] = uuid4,
) -> str:
    """Persist exact source bytes once without overwrite, rename, or retry."""
    source = Path(source_path)
    target_root = storage_root(storage_class)
    target_root.mkdir(parents=True, exist_ok=True)
    destination = target_root / generate_storage_name(
        original_filename,
        uuid_factory=uuid_factory,
    )

    with source.open("rb") as source_file, destination.open("xb") as target_file:
        shutil.copyfileobj(source_file, target_file)

    return str(destination)
