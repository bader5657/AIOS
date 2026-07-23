from core.event.event import Event
from core.event.registry import EventRegistry


def dummy_handler(event: Event) -> None:
    pass


def test_register_handler() -> None:
    registry = EventRegistry()

    registry.register("asset.stored", dummy_handler)

    handlers = registry.get_handlers("asset.stored")

    assert len(handlers) == 1
    assert handlers[0] is dummy_handler


def test_unknown_event_returns_empty_list() -> None:
    registry = EventRegistry()

    assert registry.get_handlers("unknown") == []

