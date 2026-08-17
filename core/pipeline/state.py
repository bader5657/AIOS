from enum import Enum


class AssetPipelineStatus(str, Enum):
    RECEIVED = "received"
    STORED = "stored"
    METADATA_EXTRACTED = "metadata_extracted"
    MANIFEST_CREATED = "manifest_created"
    COMPLETED = "completed"
    FAILED = "failed"
