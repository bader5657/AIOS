import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import UUID

from core.storage import file_storage


UUID_V4 = UUID("12345678-1234-4abc-8def-1234567890ab")


class StoragePathContractTests(unittest.TestCase):
    def test_complete_published_storage_mapping(self):
        expected = {
            "image": "images",
            "voice": "voice",
            "audio": "voice",
            "video": "images",
            "pdf": "pdf",
            "doc": "docs",
            "spreadsheet": "docs",
            "document": "docs",
            "web_link": "links",
            "youtube_link": "links",
            "manifest": "manifests",
        }
        for storage_class, leaf in expected.items():
            with self.subTest(storage_class=storage_class):
                self.assertEqual(
                    file_storage.storage_root(storage_class),
                    Path("/opt/aios/data/documents") / leaf,
                )

    def test_uuid_v4_name_uses_only_an_accepted_lowercase_extension(self):
        cases = (
            ("../../Exact Name.PDF", f"{UUID_V4}.pdf"),
            ("name.tar.gz", f"{UUID_V4}.gz"),
            ("name.bad-ext", str(UUID_V4)),
            ("name.abcdefghijklmnopq", str(UUID_V4)),
            ("name.é", str(UUID_V4)),
            (None, str(UUID_V4)),
        )
        for original_filename, expected in cases:
            with self.subTest(original_filename=original_filename):
                self.assertEqual(
                    file_storage.generate_storage_name(
                        original_filename,
                        uuid_factory=lambda: UUID_V4,
                    ),
                    expected,
                )

    def test_non_v4_candidate_is_rejected(self):
        candidate = UUID("12345678-1234-1abc-8def-1234567890ab")
        with self.assertRaises(ValueError):
            file_storage.generate_storage_name(
                "original.pdf", uuid_factory=lambda: candidate
            )

    def test_exact_bytes_are_written_to_the_explicit_root(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            source = temporary_root / "received.tmp"
            source.write_bytes(b"\x00exact-original\xff")
            roots = dict(file_storage.STORAGE_ROOTS)
            roots["audio"] = temporary_root / "voice"
            with patch.object(file_storage, "STORAGE_ROOTS", roots):
                stored_path = file_storage.save_file(
                    source,
                    storage_class="audio",
                    original_filename="Exact Original.MP3",
                    uuid_factory=lambda: UUID_V4,
                )
            destination = Path(stored_path)
            self.assertEqual(destination.parent, temporary_root / "voice")
            self.assertEqual(destination.name, f"{UUID_V4}.mp3")
            self.assertEqual(destination.read_bytes(), source.read_bytes())

    def test_first_collision_fails_without_overwrite_or_retry(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            source = temporary_root / "received.tmp"
            source.write_bytes(b"new")
            image_root = temporary_root / "images"
            image_root.mkdir()
            destination = image_root / f"{UUID_V4}.jpg"
            destination.write_bytes(b"existing")
            roots = dict(file_storage.STORAGE_ROOTS)
            roots["image"] = image_root
            calls = 0

            def candidate():
                nonlocal calls
                calls += 1
                return UUID_V4

            with (
                patch.object(file_storage, "STORAGE_ROOTS", roots),
                self.assertRaises(FileExistsError),
            ):
                file_storage.save_file(
                    source,
                    storage_class="image",
                    original_filename="photo.jpg",
                    uuid_factory=candidate,
                )
            self.assertEqual(calls, 1)
            self.assertEqual(destination.read_bytes(), b"existing")

    def test_unknown_class_fails_without_inferred_root(self):
        with self.assertRaises(ValueError):
            file_storage.storage_root("unknown")


if __name__ == "__main__":
    unittest.main()
