from pathlib import Path

from core.storage.file_storage import (
    ensure_storage,
    generate_image_name,
    save_file,
)


def test_ensure_storage_creates_directory() -> None:
    ensure_storage()

    assert Path("/opt/aios/data/documents/images").exists()


def test_generate_image_name_uses_extension() -> None:
    filename = generate_image_name(".png")

    assert filename.startswith("IMG-")
    assert filename.endswith(".png")


def test_save_file_returns_existing_destination(tmp_path) -> None:
    source = tmp_path / "image.jpg"
    source.write_bytes(b"AIOS")

    destination = save_file(str(source))

    destination_path = Path(destination)

    assert destination_path.exists()
    assert destination_path.read_bytes() == b"AIOS"
