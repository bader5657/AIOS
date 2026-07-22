from pathlib import Path

from PIL import Image

from core.pipeline.asset_pipeline import AssetPipeline
from core.pipeline.state import AssetPipelineStatus
from core.storage import document_manifest, file_storage


def test_asset_pipeline_process(
    tmp_path: Path,
    monkeypatch,
) -> None:
    image_root = tmp_path / "storage" / "images"
    manifest_root = tmp_path / "storage" / "manifests"

    monkeypatch.setattr(file_storage, "IMAGE_ROOT", image_root)
    monkeypatch.setattr(document_manifest, "MANIFEST_ROOT", manifest_root)

    source = tmp_path / "photo.jpg"

    image = Image.new("RGB", (32, 24))
    image.save(source, format="JPEG")

    pipeline = AssetPipeline()

    result = pipeline.process(
        str(source),
        media_type="image",
        original_filename="photo.jpg",
        telegram_user_id=1,
        telegram_chat_id=2,
        telegram_message_id=3,
    )

    assert result.status is AssetPipelineStatus.COMPLETED
    assert Path(result.storage_path).exists()
    assert Path(result.manifest_path).exists()
    assert result.metadata["file_name"].endswith(".jpg")
    assert result.metadata["mime_type"] == "image/jpeg"
    assert result.metadata["width"] == 32
    assert result.metadata["height"] == 24
