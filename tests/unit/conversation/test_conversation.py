from datetime import datetime

from core.conversation.conversation import Conversation
from core.conversation.state import ConversationStatus


def test_create_valid_conversation() -> None:
    conversation = Conversation(
        conversation_id="conv-001",
        status=ConversationStatus.ACTIVE,
        context={},
        created_at=datetime(2026, 7, 19, 10, 0, 0),
        updated_at=datetime(2026, 7, 19, 10, 0, 0),
    )

    conversation.validate()

    assert conversation.conversation_id == "conv-001"
    assert conversation.status == ConversationStatus.ACTIVE
