from pathlib import Path
from datetime import datetime
import shutil

IMAGE_ROOT = Path("/opt/aios/data/documents/images")


def ensure_storage():
    IMAGE_ROOT.mkdir(parents=True, exist_ok=True)


def generate_image_name(extension=".jpg"):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"IMG-{timestamp}{extension}"


def save_file(source_path):
    ensure_storage()

    source = Path(source_path)

    filename = generate_image_name(source.suffix or ".jpg")

    destination = IMAGE_ROOT / filename

    shutil.copy2(source, destination)

    return str(destination)
