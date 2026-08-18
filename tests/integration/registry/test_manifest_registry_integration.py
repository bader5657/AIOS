import os
import tempfile
import unittest
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import psycopg
from PIL import Image
from psycopg import conninfo, sql

from core.app.input_classifier import InputType
from core.ingestion import universal_ingestion
from core.pipeline import asset_pipeline
from core.registry import PostgresRegistry
from core.storage import document_manifest


TEST_DATABASE_URL = os.environ.get("AIOS_REGISTRY_TEST_DATABASE_URL")
ROOT = Path(__file__).resolve().parents[3]
UP = (ROOT / "migrations/postgres/0001_create_registry_records.up.sql").read_text()


def telegram_message(**overrides):
    fields = {
        "photo": None,
        "voice": None,
        "document": None,
        "video": None,
        "audio": None,
        "text": None,
        "caption": None,
        "from_user": SimpleNamespace(id=7, username="stage541"),
        "chat": SimpleNamespace(id=8),
        "message_id": 9,
    }
    fields.update(overrides)
    return SimpleNamespace(**fields)


class CountingRegistry:
    def __init__(self, registry):
        self.registry = registry
        self.calls = 0

    async def register(self, persistence_input):
        self.calls += 1
        return await self.registry.register(persistence_input)


@unittest.skipUnless(
    TEST_DATABASE_URL,
    "AIOS_REGISTRY_TEST_DATABASE_URL is required for isolated PostgreSQL tests",
)
class ManifestRegistryIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.schema = "aios_manifest_registry_" + uuid.uuid4().hex
        async with await psycopg.AsyncConnection.connect(
            TEST_DATABASE_URL, autocommit=True
        ) as admin:
            await admin.execute(
                sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.schema))
            )
        self.scoped_url = conninfo.make_conninfo(
            TEST_DATABASE_URL, options=f"-csearch_path={self.schema}"
        )
        async with await psycopg.AsyncConnection.connect(
            self.scoped_url, autocommit=True
        ) as connection:
            await connection.execute(UP)
        self.registry = PostgresRegistry(self.scoped_url)
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        self.manifest_root = self.root / "manifests"

    async def asyncTearDown(self):
        async with await psycopg.AsyncConnection.connect(
            TEST_DATABASE_URL, autocommit=True
        ) as admin:
            await admin.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(
                    sql.Identifier(self.schema)
                )
            )

    async def ingest(self, recognized, message, *, registry=None, stored_path=None):
        patches = [
            patch.object(
                universal_ingestion,
                "recognize_telegram_message",
                return_value=recognized,
            ),
            patch.object(
                universal_ingestion,
                "classify_telegram_message",
                return_value=(
                    InputType.TEXT
                    if recognized
                    in (InputType.TEXT, InputType.WEB_LINK, InputType.YOUTUBE_LINK)
                    else recognized
                ),
            ),
            patch.object(document_manifest, "MANIFEST_ROOT", self.manifest_root),
        ]
        if stored_path is not None:
            patches.append(
                patch.object(
                    asset_pipeline,
                    "save_telegram_attachment",
                    AsyncMock(return_value=str(stored_path)),
                )
            )
        with patches[0], patches[1], patches[2]:
            if len(patches) == 4:
                with patches[3]:
                    return await universal_ingestion.ingest_telegram_message(
                        message,
                        SimpleNamespace(),
                        registry=registry or self.registry,
                    )
            return await universal_ingestion.ingest_telegram_message(
                message,
                SimpleNamespace(),
                registry=registry or self.registry,
            )

    async def test_file_backed_lifecycle_persists_exact_registry_row(self):
        original = self.root / "exact.png"
        Image.new("RGB", (1, 1), color="red").save(original)
        counting_registry = CountingRegistry(self.registry)

        result = await self.ingest(
            InputType.IMAGE,
            telegram_message(photo=[object()]),
            registry=counting_registry,
            stored_path=original,
        )

        self.assertEqual(counting_registry.calls, 1)
        self.assertTrue(result.registration_succeeded)
        self.assertIsInstance(result.registry_record_id, int)
        row = await self.registry.read(result.registry_record_id)
        self.assertEqual(row.identity_ref, result.manifest_path)
        self.assertEqual(row.manifest_ref, result.manifest_path)
        self.assertEqual(row.represented_media_type, "image")
        self.assertEqual(row.metadata, result.metadata)
        self.assertEqual(row.relationships, [])
        self.assertIsNone(row.registration_status)
        self.assertEqual(row.storage_path, str(original))
        self.assertIsNone(row.source_url)
        self.assertTrue(original.is_file())
        self.assertTrue(Path(result.manifest_path).is_file())

    async def test_text_lifecycle_persists_nullable_references(self):
        result = await self.ingest(
            InputType.TEXT,
            telegram_message(text="exact text"),
        )

        self.assertTrue(result.registration_succeeded)
        row = await self.registry.read(result.registry_record_id)
        self.assertEqual(row.identity_ref, result.manifest_path)
        self.assertEqual(row.manifest_ref, result.manifest_path)
        self.assertEqual(row.represented_media_type, "text")
        self.assertEqual(row.metadata, result.metadata)
        self.assertEqual(row.relationships, [])
        self.assertIsNone(row.registration_status)
        self.assertIsNone(row.storage_path)
        self.assertIsNone(row.source_url)

    async def test_url_lifecycles_preserve_exact_source_without_storage(self):
        cases = (
            (InputType.WEB_LINK, "https://example.test/Exact?A=1"),
            (InputType.YOUTUBE_LINK, "https://youtu.be/Exact?A=1"),
        )
        for recognized, source_url in cases:
            with self.subTest(recognized=recognized):
                result = await self.ingest(
                    recognized,
                    telegram_message(text=source_url),
                )
                row = await self.registry.read(result.registry_record_id)
                self.assertTrue(result.registration_succeeded)
                self.assertEqual(row.represented_media_type, recognized.value)
                self.assertEqual(row.source_url, source_url)
                self.assertEqual(row.metadata, result.metadata)
                self.assertIsNone(row.storage_path)

    async def test_registry_failure_preserves_original_and_manifest_without_retry(self):
        original = self.root / "failure.png"
        Image.new("RGB", (1, 1), color="blue").save(original)
        missing_table_url = conninfo.make_conninfo(
            TEST_DATABASE_URL,
            options="-csearch_path=aios_stage_5_4_1_missing",
        )
        counting_registry = CountingRegistry(PostgresRegistry(missing_table_url))

        result = await self.ingest(
            InputType.IMAGE,
            telegram_message(photo=[object()]),
            registry=counting_registry,
            stored_path=original,
        )

        self.assertEqual(counting_registry.calls, 1)
        self.assertFalse(result.registration_succeeded)
        self.assertIsNone(result.registry_record_id)
        self.assertTrue(original.is_file())
        self.assertTrue(Path(result.manifest_path).is_file())
        self.assertEqual(result.stored_path, str(original))
        self.assertEqual(result.metadata["media_type"], "image")


if __name__ == "__main__":
    unittest.main()
