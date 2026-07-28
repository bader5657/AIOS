"""Generic aggregate-root repository contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from core.domain.aggregate_root import AggregateRoot
from core.domain.entity import EntityId


AggregateType = TypeVar("AggregateType", bound=AggregateRoot)


class Repository(ABC, Generic[AggregateType, EntityId]):
    """Abstract interface for storing and retrieving aggregate roots."""

    __slots__ = ()

    @abstractmethod
    def save(self, aggregate: AggregateType) -> None:
        """Store an aggregate root for creation or update."""

    @abstractmethod
    def get(self, entity_id: EntityId) -> AggregateType | None:
        """Return the matching aggregate root, or None when absent."""

    @abstractmethod
    def exists(self, entity_id: EntityId) -> bool:
        """Return whether a matching aggregate root exists."""

    @abstractmethod
    def delete(self, entity_id: EntityId) -> bool:
        """Remove a matching aggregate root and report whether it existed."""

    @abstractmethod
    def list(self) -> tuple[AggregateType, ...]:
        """Return all stored aggregate roots as an immutable tuple."""
