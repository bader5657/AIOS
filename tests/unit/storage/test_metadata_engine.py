from pathlib import Path

from PIL import Image

from core.storage.metadata_engine import extract_basic_metadata


def test_extract_basic_metadata_for_text_file(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.txt"
    file_path.write_text("AIOS", encoding="utf-8")

    metadata = extract_basic_metadata(str(file_path))

    assert metadata["file_name"] == "sample.txt"
    assert metadata["file_extension"] == ".txt"
    assert metadata["file_size_bytes"] == 4
    assert metadata["mime_type"] == "text/plain"
    assert "width" not in metadata
    assert "height" not in metadata
    assert "image_format" not in metadata


def test_extract_basic_metadata_for_image(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.png"

    image = Image.new("RGB", (32, 24))
    image.save(file_path)

    metadata = extract_basic_metadata(str(file_path))

    assert metadata["file_name"] == "sample.png"
    assert metadata["file_extension"] == ".png"
    assert metadata["file_size_bytes"] > 0
    assert metadata["mime_type"] == "image/png"
    assert metadata["width"] == 32
    assert metadata["height"] == 24
    assert metadata["image_format"] == "PNG"
