from dataclasses import dataclass
from datetime import datetime

from core.conversation.state import ConversationStatus


class ConversationValidationError(ValueError):
    """Raised when a Conversation is invalid."""


@dataclass(slots=True)
class Conversation:
    conversation_id: str
    status: ConversationStatus
    context: dict[str, object]
    created_at: datetime
    updated_at: datetime

    def validate(self) -> None:
        if not self.conversation_id.strip():
            raise ConversationValidationError(
                "conversation_id must not be empty."
            )

        if not isinstance(self.status, ConversationStatus):
            raise ConversationValidationError(
                "status must be a ConversationStatus."
            )

        if not isinstance(self.context, dict):
            raise ConversationValidationError(
                "context must be a dictionary."
            )

        if self.updated_at < self.created_at:
            raise ConversationValidationError(
                "updated_at cannot be earlier than created_at."
            )

    def to_dict(self) -> dict[str, object]:
        return {
            "conversation_id": self.conversation_id,
            "status": self.status.value,
            "context": self.context.copy(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    def complete(self, completed_at: datetime) -> None:
        self.status = ConversationStatus.COMPLETED
        self.updated_at = completed_at
        self.validate()
    def cancel(self, cancelled_at: datetime) -> None:
        self.status = ConversationStatus.CANCELLED
        self.updated_at = cancelled_at
        self.validate()
    def resume(self, resumed_at: datetime) -> None:
        self.status = ConversationStatus.ACTIVE
        self.updated_at = resumed_at
        self.validate()
