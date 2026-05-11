"""Phase 2D-1: persistent chat history for the regional analytics chatbot.

Two tables on the bff-backend's async (asyncpg) database:
- chatbot_sessions   — one row per chat thread, owned by a user.
- chatbot_messages   — one row per user/assistant message inside a session.

Schema notes:
- Session id is the SAME UUID the chatbot-api receives as `session_id` for its
  ephemeral per-turn memory. Reusing the id means the upstream chatbot's
  short-term memory continues to work for the active thread.
- Soft cascade on user delete: dropping a user removes their sessions and
  every message that belonged to them.
- Title is set lazily from the first user message (truncated to 200 chars)
  so the sidebar can render the list without an extra query.
- `last_message_at` is updated on every save so the sidebar can sort by
  recency without scanning all messages.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .db_async import BaseAsync


def utcnow():
    return datetime.now(timezone.utc)


class ChatbotSession(BaseAsync):
    __tablename__ = "chatbot_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    last_message_at = Column(
        DateTime(timezone=True), default=utcnow, nullable=False, index=True
    )

    messages = relationship(
        "ChatbotMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatbotMessage.created_at.asc()",
    )


class ChatbotMessage(BaseAsync):
    __tablename__ = "chatbot_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chatbot_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String(16), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    # Assistant-only metadata. NULL on user messages.
    sql_text = Column(Text, nullable=True)
    row_count = Column(Integer, nullable=True)
    kind = Column(String(32), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    session = relationship("ChatbotSession", back_populates="messages")
