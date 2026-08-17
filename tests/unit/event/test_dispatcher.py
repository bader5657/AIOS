from core.event.dispatcher import EventDispatcher
from core.event.event import Event
from core.event.registry import EventRegistry


def test_dispatch_calls_registered_handler() -> None:
    registry = EventRegistry()

    received: list[Event] = []

    def handler(event: Event) -> None:
        received.append(event)

    registry.register("asset.stored", handler)

    dispatcher = EventDispatcher(registry)

    event = Event(
        event_id="EVT001",
        event_name="asset.stored",
        payload={"file": "photo.jpg"},
    )

    dispatcher.dispatch(event)

    assert len(received) == 1
    assert received[0] is event


def test_dispatch_unknown_event() -> None:
    registry = EventRegistry()

    dispatcher = EventDispatcher(registry)

    event = Event(
        event_id="EVT002",
        event_name="unknown.event",
        payload={},
    )

    dispatcher.dispatch(event)

