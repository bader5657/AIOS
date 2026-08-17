from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

from core.event.event import Event


EventHandler = Callable[[Event], None]


class EventRegistry:
    """Stores event handlers."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def register(self, event_name: str, handler: EventHandler) -> None:
        self._handlers[event_name].append(handler)

    def get_handlers(self, event_name: str) -> list[EventHandler]:
        return list(self._handlers.get(event_name, []))

