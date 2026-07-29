from datetime import datetime

import pytest

from core.conversation.conversation import (
    Conversation,
    ConversationValidationError,
)
from core.conversation.repository_impl import InMemoryConversationRepository
from core.conversation.state import ConversationStatus


NOW = datetime(2026, 7, 19, 10, 0, 0)


def create_conversation(
    conversation_id: str,
    status: ConversationStatus = ConversationStatus.ACTIVE,
) -> Conversation:
    return Conversation(
        conversation_id=conversation_id,
        status=status,
        context={},
        created_at=NOW,
        updated_at=NOW,
    )


def test_save_and_get_conversation() -> None:
    repository = InMemoryConversationRepository()
    conversation = create_conversation("conv-001")

    repository.save(conversation)

    assert repository.get("conv-001") is conversation


def test_save_updates_existing_conversation() -> None:
    repository = InMemoryConversationRepository()
    conversation = create_conversation("conv-001")
    repository.save(conversation)

    conversation.context["topic"] = "updated"
    repository.save(conversation)

    stored = repository.get("conv-001")

    assert stored is conversation
    assert stored.context == {"topic": "updated"}


def test_save_rejects_invalid_conversation() -> None:
    repository = InMemoryConversationRepository()
    conversation = create_conversation("")

    with pytest.raises(ConversationValidationError):
        repository.save(conversation)


def test_get_missing_conversation_returns_none() -> None:
    repository = InMemoryConversationRepository()

    assert repository.get("missing") is None


def test_delete_existing_conversation() -> None:
    repository = InMemoryConversationRepository()
    conversation = create_conversation("conv-001")
    repository.save(conversation)

    assert repository.delete("conv-001") is True
    assert repository.get("conv-001") is None


def test_delete_missing_conversation_returns_false() -> None:
    repository = InMemoryConversationRepository()

    assert repository.delete("missing") is False


def test_list_active_returns_only_active_conversations() -> None:
    repository = InMemoryConversationRepository()

    active = create_conversation("active")
    completed = create_conversation(
        "completed",
        ConversationStatus.COMPLETED,
    )
    cancelled = create_conversation(
        "cancelled",
        ConversationStatus.CANCELLED,
    )

    repository.save(active)
    repository.save(completed)
    repository.save(cancelled)

    result = repository.list_active()

    assert result == [active]


def test_list_active_returns_empty_list_when_none_exist() -> None:
    repository = InMemoryConversationRepository()

    assert repository.list_active() == []
