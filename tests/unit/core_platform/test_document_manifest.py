import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import UUID

from jsonschema import Draft202012Validator, FormatChecker

from core.storage import document_manifest


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = REPOSITORY_ROOT / "config/ingestion-manifest.schema.json"
FIXED_ID = UUID("12345678-1234-4abc-8def-1234567890ab")
RECEIVED_AT = "2026-08-18T10:11:12.123456Z"


def metadata_for(media_type, size=5, source_url=None):
    if media_type == "text":
        return {"media_type": "text", "character_count": 5}
    if media_type in document_manifest.URL_MEDIA_TYPES:
        return {"media_type": media_type, "source_url": source_url}
    return {"media_type": media_type, "file_size_bytes": size}


class DocumentManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(
            cls.schema, format_checker=FormatChecker()
        )

    def create(self, root, generated_id=FIXED_ID, **arguments):
        with (
            patch.object(document_manifest, "MANIFEST_ROOT", root),
            patch.object(document_manifest, "uuid4", return_value=generated_id),
        ):
            path = document_manifest.create_document_manifest(**arguments)
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        self.validator.validate(payload)
        return Path(path), payload

    def test_schema_is_closed_normative_schema_with_exact_ten_classes(self):
        self.assertEqual(self.schema["type"], "object")
        self.assertFalse(self.schema["additionalProperties"])
        self.assertIn("$schema", self.schema)
        self.assertEqual(
            self.schema["properties"]["represented_media_type"]["enum"],
            [
                "text", "image", "voice", "audio", "video", "pdf", "doc",
                "spreadsheet", "web_link", "youtube_link",
            ],
        )
        self.assertNotIn(
            "manifest",
            self.schema["properties"]["represented_media_type"]["enum"],
        )

    def test_all_ten_classes_create_schema_valid_manifests(self):
        classes = (
            "text", "image", "voice", "audio", "video", "pdf", "doc",
            "spreadsheet", "web_link", "youtube_link",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "manifests"
            original = Path(directory) / "original.bin"
            original.write_bytes(b"exact")
            for index, media_type in enumerate(classes, start=1):
                with self.subTest(media_type=media_type):
                    source_url = (
                        f"https://example.com/{media_type}?Exact=Yes"
                        if media_type in document_manifest.URL_MEDIA_TYPES else None
                    )
                    arguments = {
                        "represented_media_type": media_type,
                        "received_at": RECEIVED_AT,
                        "metadata": metadata_for(media_type, source_url=source_url),
                    }
                    if media_type in document_manifest.FILE_BACKED_MEDIA_TYPES:
                        arguments["storage_path"] = str(original)
                    if source_url:
                        arguments["source_url"] = source_url
                    _, payload = self.create(
                        root, generated_id=UUID(int=index), **arguments
                    )
                    self.assertEqual(payload["represented_media_type"], media_type)
                    self.assertEqual(payload["manifest_status"], "created")

    def test_file_checksum_size_and_path_are_exact_stored_original_facts(self):
        exact_bytes = b"\x00exact-stored-original\xff"
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory) / "stored.bin"
            original.write_bytes(exact_bytes)
            _, payload = self.create(
                Path(directory) / "manifests",
                represented_media_type="audio",
                received_at=RECEIVED_AT,
                metadata=metadata_for("audio", size=len(exact_bytes)),
                storage_path=str(original),
            )
        self.assertEqual(payload["storage_path"], str(original))
        self.assertEqual(payload["file_size_bytes"], len(exact_bytes))
        self.assertEqual(
            payload["checksum_sha256"], hashlib.sha256(exact_bytes).hexdigest()
        )

    def test_non_file_text_omits_all_file_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            _, payload = self.create(
                Path(directory) / "manifests",
                represented_media_type="text",
                received_at=RECEIVED_AT,
                metadata=metadata_for("text"),
            )
        for field in document_manifest._FILE_FIELDS:
            self.assertNotIn(field, payload)

    def test_exact_url_has_no_file_placeholders(self):
        exact_url = "https://youtu.be/AbC?feature=Exact#Here"
        with tempfile.TemporaryDirectory() as directory:
            _, payload = self.create(
                Path(directory) / "manifests",
                represented_media_type="youtube_link",
                received_at=RECEIVED_AT,
                metadata=metadata_for("youtube_link", source_url=exact_url),
                source_url=exact_url,
            )
        self.assertEqual(payload["source_url"], exact_url)
        for field in document_manifest._FILE_FIELDS:
            self.assertNotIn(field, payload)

    def test_metadata_semantics_and_utf8_json_round_trip_are_preserved(self):
        metadata = {"media_type": "text", "character_count": 4}
        with tempfile.TemporaryDirectory() as directory:
            path, payload = self.create(
                Path(directory) / "manifests",
                represented_media_type="text",
                received_at=RECEIVED_AT,
                metadata=metadata,
            )
            self.assertEqual(path.read_bytes().decode("utf-8"), path.read_text("utf-8"))
        self.assertEqual(payload["metadata"], metadata)
        self.assertIsInstance(payload["metadata"]["character_count"], int)

    def test_active_stage_3_3_optional_metadata_is_preserved_without_narrowing(self):
        cases = (
            ("image", {"orientation": "landscape", "width_pixels": 10}),
            (
                "audio",
                {
                    "duration_seconds": 1.25,
                    "codec": "opus",
                    "sample_rate_hz": 48000,
                    "channel_count": 2,
                    "bit_rate_bps": 128000,
                    "title": "Exact title",
                    "artist": "Exact artist",
                },
            ),
            (
                "spreadsheet",
                {
                    "sheet_count": 2,
                    "sheet_names": ["Exact One", "Exact Two"],
                    "author": "Exact author",
                    "created_at": "embedded-value",
                },
            ),
        )
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory) / "stored"
            original.write_bytes(b"exact")
            for index, (media_type, optional) in enumerate(cases, start=1):
                with self.subTest(media_type=media_type):
                    metadata = {
                        "media_type": media_type,
                        "file_size_bytes": 5,
                        **optional,
                    }
                    _, payload = self.create(
                        Path(directory) / "manifests",
                        generated_id=UUID(int=index),
                        represented_media_type=media_type,
                        received_at=RECEIVED_AT,
                        metadata=metadata,
                        storage_path=str(original),
                        telegram_chat_id=-100123456789,
                    )
                    self.assertEqual(payload["metadata"], metadata)
                    self.assertEqual(payload["telegram_chat_id"], -100123456789)

    def test_invalid_contract_values_and_unknown_fields_are_rejected(self):
        base = {
            "manifest_id": str(FIXED_ID),
            "represented_media_type": "text",
            "received_at": RECEIVED_AT,
            "manifest_status": "created",
            "metadata": {"media_type": "text"},
        }
        invalid = (
            {**base, "represented_media_type": "manifest", "metadata": {"media_type": "manifest"}},
            {**base, "received_at": "2026-08-18T10:11:12"},
            {**base, "received_at": "2026-08-18 10:11:12Z"},
            {**base, "unknown": "forbidden"},
            {**base, "metadata": {"media_type": "text", "title": "invented"}},
            {**base, "manifest_status": "stored"},
        )
        for candidate in invalid:
            with self.subTest(candidate=candidate):
                with self.assertRaises(ValueError):
                    document_manifest.validate_manifest(candidate)
                self.assertFalse(self.validator.is_valid(candidate))

    def test_schema_rejects_mismatched_bounded_metadata_representation(self):
        candidate = {
            "manifest_id": str(FIXED_ID),
            "represented_media_type": "text",
            "received_at": RECEIVED_AT,
            "manifest_status": "created",
            "metadata": {"media_type": "audio", "file_size_bytes": 1},
        }
        self.assertFalse(self.validator.is_valid(candidate))
        with self.assertRaises(ValueError):
            document_manifest.validate_manifest(candidate)

    def test_malformed_checksum_and_partial_file_combinations_are_rejected(self):
        base = {
            "manifest_id": str(FIXED_ID),
            "represented_media_type": "audio",
            "received_at": RECEIVED_AT,
            "manifest_status": "created",
            "metadata": {"media_type": "audio", "file_size_bytes": 1},
            "storage_path": "/stored/original",
            "file_size_bytes": 1,
        }
        for checksum in (None, "A" * 64, "0" * 63, "g" * 64):
            candidate = dict(base)
            if checksum is not None:
                candidate["checksum_sha256"] = checksum
            with self.subTest(checksum=checksum), self.assertRaises(ValueError):
                document_manifest.validate_manifest(candidate)

    def test_validation_and_replace_failures_leave_no_completed_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "manifests"
            with (
                patch.object(document_manifest, "MANIFEST_ROOT", root),
                patch.object(document_manifest, "uuid4", return_value=FIXED_ID),
                self.assertRaises(ValueError),
            ):
                document_manifest.create_document_manifest(
                    represented_media_type="manifest",
                    received_at=RECEIVED_AT,
                    metadata={"media_type": "manifest"},
                )
            self.assertFalse(root.exists())

            original = Path(directory) / "original"
            original.write_bytes(b"x")
            with (
                patch.object(document_manifest, "MANIFEST_ROOT", root),
                patch.object(document_manifest, "uuid4", return_value=FIXED_ID),
                patch.object(document_manifest.os, "replace", side_effect=OSError("replace failed")),
                self.assertRaisesRegex(OSError, "replace failed"),
            ):
                document_manifest.create_document_manifest(
                    represented_media_type="audio",
                    received_at=RECEIVED_AT,
                    metadata=metadata_for("audio", size=1),
                    storage_path=str(original),
                )
            self.assertFalse((root / f"{FIXED_ID}.json").exists())
            self.assertEqual(list(root.iterdir()), [])

    def test_serialization_failure_leaves_no_completed_or_temporary_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "manifests"
            with (
                patch.object(document_manifest, "MANIFEST_ROOT", root),
                patch.object(document_manifest, "uuid4", return_value=FIXED_ID),
                patch.object(
                    document_manifest.json,
                    "dump",
                    side_effect=OSError("serialization write failed"),
                ),
                self.assertRaisesRegex(OSError, "serialization write failed"),
            ):
                document_manifest.create_document_manifest(
                    represented_media_type="text",
                    received_at=RECEIVED_AT,
                    metadata={"media_type": "text"},
                )
            self.assertEqual(list(root.iterdir()), [])

    def test_manifest_id_collision_preserves_existing_artifact_exactly(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "manifests"
            root.mkdir()
            existing_path = root / f"{FIXED_ID}.json"
            existing_bytes = b'{"existing":"must remain exact"}\n'
            existing_path.write_bytes(existing_bytes)
            with (
                patch.object(document_manifest, "MANIFEST_ROOT", root),
                patch.object(document_manifest, "uuid4", return_value=FIXED_ID),
                self.assertRaises(FileExistsError),
            ):
                document_manifest.create_document_manifest(
                    represented_media_type="text",
                    received_at=RECEIVED_AT,
                    metadata={"media_type": "text"},
                )
            self.assertEqual(existing_path.read_bytes(), existing_bytes)
            self.assertEqual(list(root.iterdir()), [existing_path])

    def test_manifest_module_has_no_metadata_or_network_authority(self):
        source = Path(document_manifest.__file__).read_text(encoding="utf-8").lower()
        for prohibited in (
            "metadata_engine", "requests", "urllib", "urlopen", "httpx", "socket"
        ):
            with self.subTest(prohibited=prohibited):
                self.assertNotIn(prohibited, source)


if __name__ == "__main__":
    unittest.main()
