from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4


class ConversationBase(SQLModel):
    """Base model for Conversation with common fields"""
    title: Optional[str] = Field(default=None, max_length=200)
    is_active: bool = Field(default=True)


class Conversation(ConversationBase, table=True):
    """
    Conversation model representing a user's chat session with the AI assistant.
    Contains metadata like user_id and creation timestamp.
    """
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True)  # Foreign key to user
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to messages
    messages: list["Message"] = Relationship(back_populates="conversation", cascade_delete=True)

    def __setattr__(self, name, value):
        """Override to automatically update updated_at when fields change"""
        if name != "updated_at":
            self.updated_at = datetime.utcnow()
        super().__setattr__(name, value)


class ConversationCreate(ConversationBase):
    """Model for creating a new conversation"""
    pass


class ConversationRead(ConversationBase):
    """Model for reading conversation data"""
    id: UUID
    user_id: str
    created_at: datetime
    updated_at: datetime