from __future__ import annotations

from core.event.event import Event
from core.event.registry import EventRegistry


class EventDispatcher:
    """Dispatches events to registered handlers."""

    def __init__(self, registry: EventRegistry) -> None:
        self._registry = registry

    def dispatch(self, event: Event) -> None:
        handlers = self._registry.get_handlers(event.event_name)

        for handler in handlers:
            handler(event)

