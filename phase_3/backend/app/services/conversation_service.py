from datetime import datetime
from typing import List, Optional
from sqlmodel import Session, select
from uuid import UUID

from app.models.conversation import Conversation
from app.models.message import Message, MessageCreate
from app.models.user import User


class ConversationService:
    """
    Service for managing conversations and messages.
    Handles conversation creation, retrieval, and message management.
    """

    def __init__(self):
        pass

    def create_conversation(self, db_session: Session, user_id: str, title: Optional[str] = None) -> Conversation:
        """Create a new conversation for a user"""
        # Create a default title if none provided
        if not title:
            title = f"Conversation on {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        conversation = Conversation(
            user_id=user_id,
            title=title
        )

        db_session.add(conversation)
        db_session.commit()
        db_session.refresh(conversation)

        return conversation

    def get_conversation_by_id(self, db_session: Session, conversation_id: UUID, user_id: str) -> Optional[Conversation]:
        """Get a conversation by ID for a specific user"""
        conversation = db_session.get(Conversation, conversation_id)

        # Verify the user owns this conversation
        if conversation and str(conversation.user_id) == user_id:
            return conversation

        return None

    def get_user_conversations(self, db_session: Session, user_id: str) -> List[Conversation]:
        """Get all conversations for a user"""
        statement = select(Conversation).where(Conversation.user_id == user_id)
        conversations = db_session.exec(statement).all()
        return conversations

    def add_message_to_conversation(
        self,
        db_session: Session,
        conversation_id: UUID,
        user_id: str,
        role: str,
        content: str,
        tool_call_id: Optional[str] = None,
        tool_response: Optional[str] = None
    ) -> Message:
        """Add a message to a conversation"""
        # Verify the user can add to this conversation
        conversation = self.get_conversation_by_id(db_session, conversation_id, user_id)
        if not conversation:
            raise ValueError("User does not have access to this conversation")

        # Create message
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_call_id=tool_call_id,
            tool_response=tool_response
        )

        db_session.add(message)
        db_session.commit()
        db_session.refresh(message)

        # Update conversation's updated_at timestamp
        conversation.updated_at = datetime.utcnow()
        db_session.add(conversation)
        db_session.commit()

        return message

    def get_messages_for_conversation(
        self,
        db_session: Session,
        conversation_id: UUID,
        user_id: str,
        limit: Optional[int] = 50,
        offset: int = 0
    ) -> List[Message]:
        """Get messages for a conversation with pagination"""
        # Verify the user has access to this conversation
        conversation = self.get_conversation_by_id(db_session, conversation_id, user_id)
        if not conversation:
            raise ValueError("User does not have access to this conversation")

        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp.desc())
        )

        if limit:
            statement = statement.offset(offset).limit(limit)

        messages = db_session.exec(statement).all()
        return messages

    def update_conversation_title(
        self,
        db_session: Session,
        conversation_id: UUID,
        user_id: str,
        title: str
    ) -> Optional[Conversation]:
        """Update a conversation's title"""
        conversation = self.get_conversation_by_id(db_session, conversation_id, user_id)
        if not conversation:
            return None

        conversation.title = title
        conversation.updated_at = datetime.utcnow()

        db_session.add(conversation)
        db_session.commit()
        db_session.refresh(conversation)

        return conversation

    def get_recent_messages(
        self,
        db_session: Session,
        conversation_id: UUID,
        user_id: str,
        limit: int = 10
    ) -> List[Message]:
        """Get the most recent messages from a conversation"""
        # Verify the user has access to this conversation
        conversation = self.get_conversation_by_id(db_session, conversation_id, user_id)
        if not conversation:
            raise ValueError("User does not have access to this conversation")

        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp.desc())
            .limit(limit)
        )

        messages = db_session.exec(statement).all()
        # Reverse to return in chronological order (oldest first)
        return list(reversed(messages))


# Global conversation service instance
conversation_service = ConversationService()