import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from core.mission import status


class FixedDateTime(datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2026, 8, 3, 14, 5, 6, tzinfo=tz)


class MissionStatusTests(unittest.TestCase):
    def test_reports_exact_evidenced_status_fields(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            image_root = root / "images"
            manifest_root = root / "manifests"
            image_root.mkdir()
            manifest_root.mkdir()
            (image_root / "first.jpg").touch()
            (image_root / "second.png").touch()
            (manifest_root / "first.json").touch()

            with (
                patch.object(status, "IMAGE_ROOT", image_root),
                patch.object(status, "MANIFEST_ROOT", manifest_root),
                patch.object(status, "datetime", FixedDateTime),
                patch.dict(os.environ, {"AIOS_ENV": "verification"}),
            ):
                result = status.mission_status()

        self.assertEqual(
            result,
            "🤖 AIOS Mission Control\n\n"
            "Status      : Running\n"
            "Version     : 0.1.0-alpha\n"
            "Environment : verification\n\n"
            "Storage\n"
            "Images      : 2\n"
            "Manifest    : 1\n\n"
            "Time        : 2026-08-03 14:05:06",
        )

    def test_uses_unknown_when_environment_is_absent(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            image_root = root / "images"
            manifest_root = root / "manifests"
            image_root.mkdir()
            manifest_root.mkdir()

            environment = os.environ.copy()
            environment.pop("AIOS_ENV", None)
            with (
                patch.object(status, "IMAGE_ROOT", image_root),
                patch.object(status, "MANIFEST_ROOT", manifest_root),
                patch.object(status, "datetime", FixedDateTime),
                patch.dict(os.environ, environment, clear=True),
            ):
                result = status.mission_status()

        self.assertIn("Environment : unknown", result)

    def test_counts_only_top_level_entries_and_json_manifests(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            image_root = root / "images"
            manifest_root = root / "manifests"
            image_root.mkdir()
            manifest_root.mkdir()

            (image_root / "image.jpg").touch()
            (image_root / "nested").mkdir()
            (image_root / "nested" / "not_top_level.jpg").touch()
            (manifest_root / "included.json").touch()
            (manifest_root / "excluded.txt").touch()
            (manifest_root / "nested").mkdir()
            (manifest_root / "nested" / "not_top_level.json").touch()

            with (
                patch.object(status, "IMAGE_ROOT", image_root),
                patch.object(status, "MANIFEST_ROOT", manifest_root),
                patch.object(status, "datetime", FixedDateTime),
            ):
                result = status.mission_status()

        self.assertIn("Images      : 2", result)
        self.assertIn("Manifest    : 1", result)


if __name__ == "__main__":
    unittest.main()
