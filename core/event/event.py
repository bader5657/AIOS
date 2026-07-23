from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class Event:
    event_id: str
    event_name: str
    payload: dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if not self.event_id.strip():
            raise ValueError("event_id cannot be empty")

        if not self.event_name.strip():
            raise ValueError("event_name cannot be empty")
