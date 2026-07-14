import os
from datetime import datetime
from pathlib import Path


IMAGE_ROOT = Path("/opt/aios/data/documents/images")
MANIFEST_ROOT = Path("/opt/aios/data/documents/manifests")


def mission_status() -> str:
    environment = os.getenv("AIOS_ENV", "unknown")

    image_count = len(list(IMAGE_ROOT.glob("*")))
    manifest_count = len(list(MANIFEST_ROOT.glob("*.json")))

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return (
        "🤖 AIOS Mission Control\n\n"
        "Status      : Running\n"
        "Version     : 0.1.0-alpha\n"
        f"Environment : {environment}\n\n"
        "Storage\n"
        f"Images      : {image_count}\n"
        f"Manifest    : {manifest_count}\n\n"
        f"Time        : {now}"
    )
