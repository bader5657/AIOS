"""Minimal async PostgreSQL persistence for Registry records."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Final

import psycopg
from psycopg.types.json import Jsonb


class RegistryPersistenceError(RuntimeError):
    """A PostgreSQL operation failed inside the Registry boundary."""


def _required_text(name: str, value: object) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a non-empty string")


def _structured(metadata: object, relationships: object) -> None:
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be an object")
    if not isinstance(relationships, list):
        raise ValueError("relationships must be an array")


@dataclass(frozen=True, slots=True)
class RegistryPersistenceInput:
    identity_ref: str
    represented_media_type: str
    metadata: dict[str, Any]
    relationships: list[Any]
    manifest_ref: str
    registration_status: str | None = None
    storage_path: str | None = None
    source_url: str | None = None

    def __post_init__(self) -> None:
        _required_text("identity_ref", self.identity_ref)
        _required_text("represented_media_type", self.represented_media_type)
        _required_text("manifest_ref", self.manifest_ref)
        _structured(self.metadata, self.relationships)


@dataclass(frozen=True, slots=True)
class RegistryPersistenceRow:
    record_id: int
    identity_ref: str
    represented_media_type: str
    metadata: dict[str, Any]
    relationships: list[Any]
    manifest_ref: str
    registration_status: str | None
    storage_path: str | None
    source_url: str | None


_OMITTED: Final = object()


@dataclass(frozen=True, slots=True)
class RegistryUpdate:
    metadata: dict[str, Any] | object = _OMITTED
    relationships: list[Any] | object = _OMITTED
    registration_status: str | None | object = _OMITTED
    storage_path: str | None | object = _OMITTED
    source_url: str | None | object = _OMITTED

    def __post_init__(self) -> None:
        if self.metadata is not _OMITTED and not isinstance(self.metadata, dict):
            raise ValueError("metadata must be an object")
        if self.relationships is not _OMITTED and not isinstance(self.relationships, list):
            raise ValueError("relationships must be an array")

    def values(self) -> dict[str, Any]:
        values = {}
        for name in (
            "metadata",
            "relationships",
            "registration_status",
            "storage_path",
            "source_url",
        ):
            value = getattr(self, name)
            if value is not _OMITTED:
                values[name] = value
        return values


_COLUMNS = (
    "record_id, identity_ref, represented_media_type, metadata, relationships, "
    "manifest_ref, registration_status, storage_path, source_url"
)


def _row(values: tuple[Any, ...]) -> RegistryPersistenceRow:
    return RegistryPersistenceRow(*values)


class PostgresRegistry:
    """Own one direct PostgreSQL connection per bounded operation."""

    def __init__(self, database_url: str) -> None:
        if not isinstance(database_url, str) or not database_url:
            raise ValueError("database_url must be a non-empty string")
        self._database_url = database_url

    @classmethod
    def from_environment(cls) -> PostgresRegistry:
        database_url = os.environ.get("AIOS_REGISTRY_DATABASE_URL")
        if not database_url:
            raise ValueError("AIOS_REGISTRY_DATABASE_URL is required")
        return cls(database_url)

    async def register(
        self, persistence_input: RegistryPersistenceInput
    ) -> RegistryPersistenceRow:
        statement = f"""
            INSERT INTO registry_records (
                identity_ref, represented_media_type, metadata, relationships,
                manifest_ref, registration_status, storage_path, source_url
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING {_COLUMNS}
        """
        parameters = (
            persistence_input.identity_ref,
            persistence_input.represented_media_type,
            Jsonb(persistence_input.metadata),
            Jsonb(persistence_input.relationships),
            persistence_input.manifest_ref,
            persistence_input.registration_status,
            persistence_input.storage_path,
            persistence_input.source_url,
        )
        try:
            async with await psycopg.AsyncConnection.connect(self._database_url) as connection:
                async with connection.transaction():
                    await connection.execute(
                        "SET TRANSACTION ISOLATION LEVEL READ COMMITTED"
                    )
                    async with connection.cursor() as cursor:
                        await cursor.execute(statement, parameters)
                        values = await cursor.fetchone()
            if values is None:
                raise RegistryPersistenceError("register returned no row")
            return _row(values)
        except psycopg.Error as exc:
            raise RegistryPersistenceError("register failed") from exc

    async def read(self, record_id: int) -> RegistryPersistenceRow | None:
        statement = f"SELECT {_COLUMNS} FROM registry_records WHERE record_id = %s"
        try:
            async with await psycopg.AsyncConnection.connect(self._database_url) as connection:
                async with connection.transaction():
                    await connection.execute(
                        "SET TRANSACTION ISOLATION LEVEL READ COMMITTED"
                    )
                    async with connection.cursor() as cursor:
                        await cursor.execute(statement, (record_id,))
                        values = await cursor.fetchone()
            return None if values is None else _row(values)
        except psycopg.Error as exc:
            raise RegistryPersistenceError("read failed") from exc

    async def update(
        self, record_id: int, patch: RegistryUpdate
    ) -> RegistryPersistenceRow | None:
        values = patch.values()
        if not values:
            raise ValueError("update patch must not be empty")

        assignments = ", ".join(f"{name} = %s" for name in values)
        parameters = [
            Jsonb(value) if name in {"metadata", "relationships"} else value
            for name, value in values.items()
        ]
        parameters.append(record_id)
        statement = (
            f"UPDATE registry_records SET {assignments} WHERE record_id = %s "
            f"RETURNING {_COLUMNS}"
        )
        try:
            async with await psycopg.AsyncConnection.connect(self._database_url) as connection:
                async with connection.transaction():
                    await connection.execute(
                        "SET TRANSACTION ISOLATION LEVEL READ COMMITTED"
                    )
                    async with connection.cursor() as cursor:
                        await cursor.execute(statement, parameters)
                        row_values = await cursor.fetchone()
            return None if row_values is None else _row(row_values)
        except psycopg.Error as exc:
            raise RegistryPersistenceError("update failed") from exc
