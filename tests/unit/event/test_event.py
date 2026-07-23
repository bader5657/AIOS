from datetime import datetime

import pytest

from core.event.event import Event


def test_create_event() -> None:
    event = Event(
        event_id="EVT001",
        event_name="asset.stored",
        payload={"file": "photo.jpg"},
    )

    assert event.event_id == "EVT001"
    assert event.event_name == "asset.stored"
    assert event.payload["file"] == "photo.jpg"
    assert isinstance(event.created_at, datetime)


def test_empty_event_id_is_rejected() -> None:
    with pytest.raises(ValueError):
        Event(
            event_id="",
            event_name="asset.stored",
            payload={},
        )


def test_empty_event_name_is_rejected() -> None:
    with pytest.raises(ValueError):
        Event(
            event_id="EVT001",
            event_name="",
            payload={},
        )
