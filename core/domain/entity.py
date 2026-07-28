"""Base entity contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from core.domain.exceptions import DomainInvariantError, DomainValidationError


EntityId = TypeVar("EntityId")


class Entity(ABC, Generic[EntityId]):
    """Domain object defined by an immutable identity."""

    __slots__ = ("_entity_id",)

    @abstractmethod
    def __init__(self, entity_id: EntityId) -> None:
        if entity_id is None:
            raise DomainValidationError("id cannot be None")

        self._entity_id = entity_id

    @property
    def id(self) -> EntityId:
        """Return the entity identity."""
        return self._entity_id

    def __setattr__(self, name: str, value: object) -> None:
        if name == "_entity_id" and hasattr(self, "_entity_id"):
            raise DomainInvariantError("id cannot be changed")

        object.__setattr__(self, name, value)

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return False

        return self.id == other.id

    def __hash__(self) -> int:
        return hash((type(self), self.id))
