import inspect
import os
import unittest
from dataclasses import FrozenInstanceError, fields
from unittest.mock import AsyncMock, patch

import psycopg

from core.registry import postgres_registry
from core.registry.postgres_registry import (
    PostgresRegistry,
    RegistryPersistenceError,
    RegistryPersistenceInput,
    RegistryPersistenceRow,
    RegistryUpdate,
)


ROW = (
    1,
    "identity:1",
    "text",
    {"kind": "text"},
    [],
    "manifest:1",
    None,
    None,
    None,
)


class AsyncContext:
    def __init__(self, value):
        self.value = value

    async def __aenter__(self):
        return self.value

    async def __aexit__(self, *_):
        return False


class FakeConnection(AsyncContext):
    def __init__(self, row=ROW):
        self.cursor_value = FakeCursor(row)
        self.execute = AsyncMock()
        super().__init__(self)

    def transaction(self):
        return AsyncContext(None)

    def cursor(self):
        return AsyncContext(self.cursor_value)


class FakeCursor:
    def __init__(self, row):
        self.row = row
        self.execute = AsyncMock()

    async def fetchone(self):
        return self.row


def persistence_input(**overrides):
    values = {
        "identity_ref": "identity:1",
        "represented_media_type": "text",
        "metadata": {"kind": "text"},
        "relationships": [],
        "manifest_ref": "manifest:1",
    }
    values.update(overrides)
    return RegistryPersistenceInput(**values)


class RegistryDtoTests(unittest.TestCase):
    def test_input_requires_and_accepts_relationships(self):
        self.assertEqual(persistence_input().relationships, [])
        with self.assertRaises(TypeError):
            RegistryPersistenceInput(
                identity_ref="identity:1",
                represented_media_type="text",
                metadata={},
                manifest_ref="manifest:1",
            )

    def test_input_validates_only_minimum_structure(self):
        for name, value in (
            ("identity_ref", ""),
            ("represented_media_type", None),
            ("manifest_ref", 4),
            ("metadata", []),
            ("relationships", {}),
        ):
            with self.subTest(name=name), self.assertRaises(ValueError):
                persistence_input(**{name: value})

    def test_dtos_are_frozen_and_have_exact_fields(self):
        self.assertEqual(
            [item.name for item in fields(RegistryPersistenceInput)],
            [
                "identity_ref",
                "represented_media_type",
                "metadata",
                "relationships",
                "manifest_ref",
                "registration_status",
                "storage_path",
                "source_url",
            ],
        )
        self.assertEqual(
            [item.name for item in fields(RegistryUpdate)],
            [
                "metadata",
                "relationships",
                "registration_status",
                "storage_path",
                "source_url",
            ],
        )
        with self.assertRaises(FrozenInstanceError):
            persistence_input().identity_ref = "changed"

    def test_update_accepts_only_mutable_fields_and_explicit_null(self):
        patch_value = RegistryUpdate(metadata={}, registration_status=None)
        self.assertEqual(
            patch_value.values(), {"metadata": {}, "registration_status": None}
        )
        with self.assertRaises(TypeError):
            RegistryUpdate(identity_ref="changed")
        with self.assertRaises(ValueError):
            RegistryUpdate(metadata=[])
        with self.assertRaises(ValueError):
            RegistryUpdate(relationships={})


class RegistryRuntimeTests(unittest.IsolatedAsyncioTestCase):
    async def test_register_uses_parameterized_insert_and_maps_row(self):
        connection = FakeConnection()
        with patch.object(
            postgres_registry.psycopg.AsyncConnection,
            "connect",
            AsyncMock(return_value=connection),
        ):
            result = await PostgresRegistry("postgresql://test").register(
                persistence_input()
            )
        statement, parameters = connection.cursor_value.execute.await_args.args
        self.assertIn("VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", statement)
        self.assertNotIn("identity:1", statement)
        self.assertEqual(len(parameters), 8)
        self.assertEqual(result, RegistryPersistenceRow(*ROW))

    async def test_read_not_found_is_none_and_parameterized(self):
        connection = FakeConnection(None)
        with patch.object(
            postgres_registry.psycopg.AsyncConnection,
            "connect",
            AsyncMock(return_value=connection),
        ):
            result = await PostgresRegistry("postgresql://test").read(91)
        statement, parameters = connection.cursor_value.execute.await_args.args
        self.assertEqual(parameters, (91,))
        self.assertIn("record_id = %s", statement)
        self.assertIsNone(result)

    async def test_update_not_found_is_none_and_parameterized(self):
        connection = FakeConnection(None)
        with patch.object(
            postgres_registry.psycopg.AsyncConnection,
            "connect",
            AsyncMock(return_value=connection),
        ):
            result = await PostgresRegistry("postgresql://test").update(
                91, RegistryUpdate(storage_path="/new")
            )
        statement, parameters = connection.cursor_value.execute.await_args.args
        self.assertIn("storage_path = %s", statement)
        self.assertNotIn("/new", statement)
        self.assertEqual(parameters, ["/new", 91])
        self.assertIsNone(result)

    async def test_empty_update_fails_before_connection(self):
        connect = AsyncMock()
        with patch.object(
            postgres_registry.psycopg.AsyncConnection, "connect", connect
        ):
            with self.assertRaisesRegex(ValueError, "must not be empty"):
                await PostgresRegistry("postgresql://test").update(
                    1, RegistryUpdate()
                )
        connect.assert_not_awaited()

    async def test_database_error_is_registry_local(self):
        with patch.object(
            postgres_registry.psycopg.AsyncConnection,
            "connect",
            AsyncMock(side_effect=psycopg.OperationalError("unavailable")),
        ):
            with self.assertRaises(RegistryPersistenceError):
                await PostgresRegistry("postgresql://test").register(
                    persistence_input()
                )

    def test_configuration_fails_closed_without_runtime_dsn(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(
                ValueError, "AIOS_REGISTRY_DATABASE_URL is required"
            ):
                PostgresRegistry.from_environment()

    def test_prohibited_surfaces_are_absent(self):
        runtime_source = inspect.getsource(postgres_registry).lower()
        for method_name in ("delete", "up" + "sert", "save"):
            self.assertFalse(hasattr(PostgresRegistry, method_name))
        self.assertFalse(
            hasattr(postgres_registry, "Registry" + "Entry")
        )
        for marker in (
            "sqlalchemy",
            "asyncpg",
            "psycopg_" + "pool",
            "de" + "dupe",
            "re" + "try",
            "original_" + "binary",
            "base" + "64",
        ):
            self.assertNotIn(marker, runtime_source)


if __name__ == "__main__":
    unittest.main()
