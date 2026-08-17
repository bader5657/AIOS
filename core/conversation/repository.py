from __future__ import annotations

from abc import ABC, abstractmethod

from core.conversation.conversation import Conversation


class ConversationRepository(ABC):
    """Abstract repository contract for Conversation entities."""

    @abstractmethod
    def save(self, conversation: Conversation) -> None:
        """Create or update a conversation."""
        raise NotImplementedError

    @abstractmethod
    def get(self, conversation_id: str) -> Conversation | None:
        """Return a conversation by ID."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, conversation_id: str) -> bool:
        """Delete a conversation."""
        raise NotImplementedError

    @abstractmethod
    def list_active(self) -> list[Conversation]:
        """Return all active conversations."""
        raise NotImplementedError
