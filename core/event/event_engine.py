"""Fresh, bounded, in-memory Event Engine runtime."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import Enum

from core.domain.event_envelope import EventEnvelope


EventHandler = Callable[[EventEnvelope], Awaitable[None]]


class EventEngineRegistrationError(ValueError):
    """Reject an invalid in-memory handler registration boundary."""


class EventDeliveryFailureCode(str, Enum):
    """Complete set of bounded Event Engine failure dispositions."""

    INVALID_ENVELOPE = "invalid_envelope"
    NO_HANDLER = "no_handler"
    HANDLER_FAILURE = "handler_failure"


@dataclass(frozen=True, slots=True)
class EventDeliveryResult:
    """Runtime-local result of one Event Engine process invocation."""

    success: bool
    delivered_handler_count: int
    failure_code: EventDeliveryFailureCode | None
    failure_reason: str | None


class EventEngine:
    """Route immutable envelopes to explicit in-memory async handlers."""

    _MAX_FAILURE_REASON_LENGTH = 256

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = {}

    def register(self, event_name: str, handler: EventHandler) -> None:
        """Register a handler in deterministic registration order."""
        if not isinstance(event_name, str):
            raise EventEngineRegistrationError("event_name must be a string")
        if not event_name.strip():
            raise EventEngineRegistrationError("event_name cannot be blank")
        if not callable(handler):
            raise EventEngineRegistrationError("handler must be callable")

        self._handlers.setdefault(event_name, []).append(handler)

    async def process(self, envelope: EventEnvelope) -> EventDeliveryResult:
        """Attempt each snapshotted matching handler at most once, sequentially."""
        if not isinstance(envelope, EventEnvelope):
            return EventDeliveryResult(
                success=False,
                delivered_handler_count=0,
                failure_code=EventDeliveryFailureCode.INVALID_ENVELOPE,
                failure_reason="process input must be an EventEnvelope",
            )

        handlers = tuple(self._handlers.get(envelope.event_name, ()))
        if not handlers:
            return EventDeliveryResult(
                success=False,
                delivered_handler_count=0,
                failure_code=EventDeliveryFailureCode.NO_HANDLER,
                failure_reason="no handler is registered for the event",
            )

        delivered_handler_count = 0
        for handler in handlers:
            try:
                await handler(envelope)
            except Exception as exc:
                reason = str(exc) or type(exc).__name__
                return EventDeliveryResult(
                    success=False,
                    delivered_handler_count=delivered_handler_count,
                    failure_code=EventDeliveryFailureCode.HANDLER_FAILURE,
                    failure_reason=reason[: self._MAX_FAILURE_REASON_LENGTH],
                )
            delivered_handler_count += 1

        return EventDeliveryResult(
            success=True,
            delivered_handler_count=delivered_handler_count,
            failure_code=None,
            failure_reason=None,
        )
