from dataclasses import dataclass


@dataclass(slots=True)
class RegistryRecord:
    id: str
    media_type: str
    storage_path: str
    manifest_path: str

