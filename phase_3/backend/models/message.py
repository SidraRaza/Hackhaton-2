from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
import json


class MessageRole(str, Enum):
    """Enumeration for message roles"""
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class MessageBase(SQLModel):
    """Base model for Message with common fields"""
    role: MessageRole = Field(index=True)
    content: str = Field(max_length=5000)  # Reasonable limit for message content
    timestamp: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    tool_call_id: Optional[str] = Field(default=None)
    tool_response: Optional[str] = Field(default=None, max_length=10000)  # Store as JSON string


class Message(MessageBase, table=True):
    """
    Message model representing individual messages within a conversation.
    Includes role (user, assistant, tool) and content.
    """
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(index=True, foreign_key="conversation.id")  # Foreign key to conversation

    # Relationship to conversation
    conversation: "Conversation" = Relationship(back_populates="messages")

    def __setattr__(self, name, value):
        """Override to automatically update timestamp when content changes"""
        if name == "content" and hasattr(self, 'timestamp'):
            self.timestamp = datetime.utcnow()
        super().__setattr__(name, value)


class MessageCreate(MessageBase):
    """Model for creating a new message"""
    conversation_id: UUID


class MessageRead(MessageBase):
    """Model for reading message data"""
    id: UUID
    conversation_id: UUID
    timestamp: datetime