"""PostgreSQL-backed Registry persistence boundary."""

from .postgres_registry import (
    PostgresRegistry,
    RegistryPersistenceError,
    RegistryPersistenceInput,
    RegistryPersistenceRow,
    RegistryUpdate,
)

__all__ = (
    "PostgresRegistry",
    "RegistryPersistenceError",
    "RegistryPersistenceInput",
    "RegistryPersistenceRow",
    "RegistryUpdate",
)
