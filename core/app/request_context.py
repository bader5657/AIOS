from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class RequestContext:
    source: str
    user_id: int
    chat_id: int
    message_id: int
    username: str
    text: str
    received_at: datetime

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["received_at"] = self.received_at.isoformat()
        return data

    @classmethod
    def from_telegram(
        cls,
        *,
        user_id: int,
        chat_id: int,
        message_id: int,
        username: str,
        text: str,
    ) -> "RequestContext":
        return cls(
            source="telegram",
            user_id=user_id,
            chat_id=chat_id,
            message_id=message_id,
            username=username,
            text=text,
            received_at=datetime.now(timezone.utc),
        )
