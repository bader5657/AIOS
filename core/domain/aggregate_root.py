"""Base aggregate root contract."""

from __future__ import annotations

from abc import abstractmethod

from core.domain.domain_event import DomainEvent
from core.domain.entity import Entity, EntityId
from core.domain.exceptions import DomainValidationError


class AggregateRoot(Entity[EntityId]):
    """Entity that marks the consistency boundary of an aggregate."""

    __slots__ = ("__pending_events",)

    @abstractmethod
    def __init__(self, entity_id: EntityId) -> None:
        super().__init__(entity_id)
        self.__pending_events: list[DomainEvent] = []

    def record_event(self, event: DomainEvent) -> None:
        """Record a pending domain event."""
        if not isinstance(event, DomainEvent):
            raise DomainValidationError("event must be a DomainEvent")

        self.__pending_events.append(event)

    def pending_events(self) -> tuple[DomainEvent, ...]:
        """Return an immutable snapshot of pending domain events."""
        return tuple(self.__pending_events)

    def pull_events(self) -> tuple[DomainEvent, ...]:
        """Return and clear all pending domain events."""
        events = tuple(self.__pending_events)
        self.__pending_events.clear()
        return events

    def clear_events(self) -> None:
        """Clear all pending domain events."""
        self.__pending_events.clear()
