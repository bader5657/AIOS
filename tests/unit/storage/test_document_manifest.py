from pathlib import Path

from core.storage.document_manifest import (
    calculate_sha256,
    create_document_manifest,
)


def test_calculate_sha256_returns_hash(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.txt"
    file_path.write_text("AIOS", encoding="utf-8")

    digest = calculate_sha256(str(file_path))

    assert len(digest) == 64
    assert digest.isalnum()


def test_create_document_manifest(tmp_path: Path) -> None:
    storage_file = tmp_path / "image.jpg"
    storage_file.write_bytes(b"hello")

    manifest_path = create_document_manifest(
        media_type="image",
        storage_path=str(storage_file),
        original_filename="photo.jpg",
        telegram_user_id=1,
        telegram_chat_id=2,
        telegram_message_id=3,
    )

    manifest = Path(manifest_path)

    assert manifest.exists()
    assert manifest.suffix == ".json"
