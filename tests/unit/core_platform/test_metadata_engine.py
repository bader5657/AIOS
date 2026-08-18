import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

image_api = SimpleNamespace(open=MagicMock())
with patch.dict(sys.modules, {"PIL": SimpleNamespace(Image=image_api)}):
    from core.storage import metadata_engine


class MetadataEngineTests(unittest.TestCase):
    def test_text_metadata_is_minimum_and_deterministic(self):
        self.assertEqual(
            metadata_engine.extract_basic_metadata(media_type="text", text="AIOS"),
            {"media_type": "text", "character_count": 4},
        )
        self.assertEqual(
            metadata_engine.extract_basic_metadata(media_type="text"),
            {"media_type": "text"},
        )

    def test_image_metadata_uses_exact_local_original(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "stored.bin"
            path.write_bytes(b"png")
            image = MagicMock(width=3, height=2, format="PNG", mode="RGB")
            image.__enter__.return_value = image
            with patch.object(metadata_engine.Image, "open", return_value=image):
                metadata = metadata_engine.extract_basic_metadata(
                    media_type="image",
                    file_path=str(path),
                    original_filename="Exact Name.PNG",
                )

        self.assertEqual(metadata["media_type"], "image")
        self.assertGreater(metadata["file_size_bytes"], 0)
        self.assertEqual(metadata["original_filename"], "Exact Name.PNG")
        self.assertEqual(metadata["mime_type"], "image/png")
        self.assertEqual(metadata["format"], "png")
        self.assertEqual(metadata["width_pixels"], 3)
        self.assertEqual(metadata["height_pixels"], 2)
        self.assertEqual(metadata["color_mode"], "RGB")

    def test_file_backed_classes_emit_only_available_common_fields(self):
        cases = (
            ("voice", "voice.ogg"),
            ("audio", "audio.mp3"),
            ("video", "video.mp4"),
            ("pdf", "report.pdf"),
            ("doc", "report.docx"),
            ("spreadsheet", "sheet.xlsx"),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "preserved"
            path.write_bytes(b"source")
            for media_type, filename in cases:
                with self.subTest(media_type=media_type):
                    metadata = metadata_engine.extract_basic_metadata(
                        media_type=media_type,
                        file_path=str(path),
                        original_filename=filename,
                    )
                    self.assertEqual(metadata["media_type"], media_type)
                    self.assertEqual(metadata["file_size_bytes"], 6)
                    self.assertEqual(metadata["original_filename"], filename)
                    self.assertEqual(metadata["format"], filename.rsplit(".", 1)[1])
                    self.assertNotIn("duration_seconds", metadata)
                    self.assertNotIn("title", metadata)

    def test_unavailable_optional_values_are_omitted(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "preserved"
            path.write_bytes(b"")
            metadata = metadata_engine.extract_basic_metadata(
                media_type="audio",
                file_path=str(path),
            )

        self.assertEqual(
            metadata,
            {"media_type": "audio", "file_size_bytes": 0},
        )

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "preserved"
            path.write_bytes(b"x")
            metadata = metadata_engine.extract_basic_metadata(
                media_type="audio",
                file_path=str(path),
                original_filename=123,
            )
        self.assertEqual(
            metadata,
            {"media_type": "audio", "file_size_bytes": 1},
        )

    def test_url_only_metadata_preserves_exact_url_without_network(self):
        exact_urls = {
            "web_link": "https://example.com/A?x=One#Exact",
            "youtube_link": "https://youtu.be/AbC?feature=Exact",
        }
        with patch("socket.socket", side_effect=AssertionError("network forbidden")):
            for media_type, source_url in exact_urls.items():
                with self.subTest(media_type=media_type):
                    self.assertEqual(
                        metadata_engine.extract_basic_metadata(
                            media_type=media_type,
                            source_url=source_url,
                        ),
                        {"media_type": media_type, "source_url": source_url},
                    )

    def test_invalid_required_inputs_and_media_types_fail(self):
        invalid_calls = (
            {"media_type": "manifest"},
            {"media_type": "unknown"},
            {"media_type": "document"},
            {"media_type": "audio"},
            {"media_type": "web_link", "source_url": ""},
        )
        for arguments in invalid_calls:
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                metadata_engine.extract_basic_metadata(**arguments)

    def test_missing_preserved_original_fails(self):
        with self.assertRaises(ValueError):
            metadata_engine.extract_basic_metadata(
                media_type="pdf",
                file_path="/definitely/not/a/preserved/original.pdf",
            )

    def test_metadata_engine_has_no_manifest_or_network_dependency(self):
        source = Path(metadata_engine.__file__).read_text(encoding="utf-8").lower()
        for prohibited in (
            "manifest",
            "requests",
            "urllib",
            "urlopen",
            "httpx",
            "socket",
        ):
            with self.subTest(prohibited=prohibited):
                self.assertNotIn(prohibited, source)


if __name__ == "__main__":
    unittest.main()
