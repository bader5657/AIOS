"""Base event envelope contract."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from core.domain.domain_event import DomainEvent
from core.domain.exceptions import DomainValidationError


class EventEnvelope:
    """Immutable wrapper for one published domain event."""

    __slots__ = (
        "_event",
        "_aggregate_id",
        "_correlation_id",
        "_causation_id",
        "_schema_version",
    )

    def __init__(
        self,
        event: DomainEvent,
        aggregate_id: Any = None,
        correlation_id: Any = None,
        causation_id: Any = None,
        *,
        schema_version: int,
    ) -> None:
        if not isinstance(event, DomainEvent):
            raise DomainValidationError("event must be a DomainEvent")
        if isinstance(schema_version, bool) or not isinstance(
            schema_version, int
        ):
            raise DomainValidationError("schema_version must be an integer")
        if schema_version < 1:
            raise DomainValidationError("schema_version must be at least 1")

        self._event = event
        self._aggregate_id = aggregate_id
        self._correlation_id = correlation_id
        self._causation_id = causation_id
        self._schema_version = schema_version

    @property
    def event(self) -> DomainEvent:
        return self._event

    @property
    def event_id(self) -> Any:
        return self._event.id

    @property
    def event_name(self) -> str:
        return self._event.event_name

    @property
    def occurred_at(self) -> datetime:
        return self._event.occurred_at

    @property
    def aggregate_id(self) -> Any:
        return self._aggregate_id

    @property
    def correlation_id(self) -> Any:
        return self._correlation_id

    @property
    def causation_id(self) -> Any:
        return self._causation_id

    @property
    def schema_version(self) -> int:
        return self._schema_version

    def __setattr__(self, name: str, value: object) -> None:
        if name in EventEnvelope.__slots__ and hasattr(self, name):
            raise AttributeError(f"{name[1:]} cannot be changed")

        object.__setattr__(self, name, value)

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return False

        return (
            self.event == other.event
            and self.aggregate_id == other.aggregate_id
            and self.correlation_id == other.correlation_id
            and self.causation_id == other.causation_id
            and self.schema_version == other.schema_version
        )

    def __hash__(self) -> int:
        return hash(
            (
                type(self),
                self.event,
                self.aggregate_id,
                self.correlation_id,
                self.causation_id,
                self.schema_version,
            )
        )
