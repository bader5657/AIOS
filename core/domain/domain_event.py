"""Base domain event contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import TypeVar

from core.domain.exceptions import DomainValidationError


EventId = TypeVar("EventId")


class DomainEvent(ABC):
    """Immutable domain record identifying a fact that occurred."""

    __slots__ = ("_id", "_occurred_at", "_event_name")

    @abstractmethod
    def __init__(
        self,
        id: EventId,
        occurred_at: datetime,
        event_name: str,
    ) -> None:
        if id is None:
            raise DomainValidationError("id cannot be None")
        if not isinstance(occurred_at, datetime):
            raise DomainValidationError("occurred_at must be a datetime")
        if occurred_at.tzinfo is None or occurred_at.utcoffset() is None:
            raise DomainValidationError("occurred_at must be timezone-aware")
        if not isinstance(event_name, str):
            raise DomainValidationError("event_name must be a string")
        if not event_name.strip():
            raise DomainValidationError("event_name cannot be blank")

        self._id = id
        self._occurred_at = occurred_at
        self._event_name = event_name

    @property
    def id(self) -> EventId:
        """Return the event identity."""
        return self._id

    @property
    def occurred_at(self) -> datetime:
        """Return when the event occurred."""
        return self._occurred_at

    @property
    def event_name(self) -> str:
        """Return the published event identifier."""
        return self._event_name

    def __setattr__(self, name: str, value: object) -> None:
        if name in DomainEvent.__slots__ and hasattr(self, name):
            raise AttributeError(f"{name[1:]} cannot be changed")

        object.__setattr__(self, name, value)

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return False

        return (
            self.id == other.id
            and self.occurred_at == other.occurred_at
            and self.event_name == other.event_name
        )

    def __hash__(self) -> int:
        return hash(
            (type(self), self.id, self.occurred_at, self.event_name)
        )
