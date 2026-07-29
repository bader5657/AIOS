from core.registry.models import RegistryRecord
from core.registry.registry import Registry


def test_registry_save_returns_record() -> None:
    registry = Registry()

    record = RegistryRecord(
        id="DOC-001",
        media_type="image",
        storage_path="/tmp/image.jpg",
        manifest_path="/tmp/image.json",
    )

    result = registry.save(record)

    assert result == record
