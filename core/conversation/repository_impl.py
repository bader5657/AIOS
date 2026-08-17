from __future__ import annotations

from core.conversation.conversation import Conversation
from core.conversation.repository import ConversationRepository
from core.conversation.state import ConversationStatus


class InMemoryConversationRepository(ConversationRepository):
    """In-memory implementation for Foundation."""

    def __init__(self) -> None:
        self._items: dict[str, Conversation] = {}

    def save(self, conversation: Conversation) -> None:
        conversation.validate()
        self._items[conversation.conversation_id] = conversation

    def get(self, conversation_id: str) -> Conversation | None:
        return self._items.get(conversation_id)

    def delete(self, conversation_id: str) -> bool:
        return self._items.pop(conversation_id, None) is not None

    def list_active(self) -> list[Conversation]:
        return [
            item
            for item in self._items.values()
            if item.status is ConversationStatus.ACTIVE
        ]
