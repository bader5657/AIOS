from datetime import datetime

import pytest

from core.conversation.conversation import (
    Conversation,
    ConversationValidationError,
)
from core.conversation.state import ConversationStatus


CREATED_AT = datetime(2026, 7, 19, 10, 0, 0)


def create_conversation() -> Conversation:
    return Conversation(
        conversation_id="conv-001",
        status=ConversationStatus.ACTIVE,
        context={"source": "telegram"},
        created_at=CREATED_AT,
        updated_at=CREATED_AT,
    )


def test_create_valid_conversation() -> None:
    conversation = create_conversation()

    conversation.validate()

    assert conversation.conversation_id == "conv-001"
    assert conversation.status is ConversationStatus.ACTIVE
    assert conversation.context == {"source": "telegram"}
    assert conversation.created_at == CREATED_AT
    assert conversation.updated_at == CREATED_AT


def test_empty_conversation_id_is_rejected() -> None:
    conversation = create_conversation()
    conversation.conversation_id = "   "

    with pytest.raises(
        ConversationValidationError,
        match="conversation_id must not be empty",
    ):
        conversation.validate()


def test_invalid_status_is_rejected() -> None:
    conversation = create_conversation()
    conversation.status = "active"  # type: ignore[assignment]

    with pytest.raises(
        ConversationValidationError,
        match="status must be a ConversationStatus",
    ):
        conversation.validate()


def test_invalid_context_is_rejected() -> None:
    conversation = create_conversation()
    conversation.context = []  # type: ignore[assignment]

    with pytest.raises(
        ConversationValidationError,
        match="context must be a dictionary",
    ):
        conversation.validate()


def test_updated_at_before_created_at_is_rejected() -> None:
    conversation = create_conversation()
    conversation.updated_at = datetime(2026, 7, 19, 9, 59, 59)

    with pytest.raises(
        ConversationValidationError,
        match="updated_at cannot be earlier than created_at",
    ):
        conversation.validate()


def test_complete_conversation() -> None:
    conversation = create_conversation()
    completed_at = datetime(2026, 7, 19, 11, 0, 0)

    conversation.complete(completed_at)

    assert conversation.status is ConversationStatus.COMPLETED
    assert conversation.updated_at == completed_at


def test_cancel_conversation() -> None:
    conversation = create_conversation()
    cancelled_at = datetime(2026, 7, 19, 11, 0, 0)

    conversation.cancel(cancelled_at)

    assert conversation.status is ConversationStatus.CANCELLED
    assert conversation.updated_at == cancelled_at


def test_resume_conversation() -> None:
    conversation = create_conversation()
    cancelled_at = datetime(2026, 7, 19, 11, 0, 0)
    resumed_at = datetime(2026, 7, 19, 12, 0, 0)

    conversation.cancel(cancelled_at)
    conversation.resume(resumed_at)

    assert conversation.status is ConversationStatus.ACTIVE
    assert conversation.updated_at == resumed_at


def test_conversation_to_dict() -> None:
    conversation = create_conversation()

    result = conversation.to_dict()

    assert result == {
        "conversation_id": "conv-001",
        "status": "active",
        "context": {"source": "telegram"},
        "created_at": "2026-07-19T10:00:00",
        "updated_at": "2026-07-19T10:00:00",
    }


def test_to_dict_returns_context_copy() -> None:
    conversation = create_conversation()

    result = conversation.to_dict()
    result["context"]["source"] = "modified"  # type: ignore[index]

    assert conversation.context == {"source": "telegram"}
