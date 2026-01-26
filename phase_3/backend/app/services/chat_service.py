from typing import List, Optional, Dict, Any
from sqlmodel import Session
from uuid import UUID

from app.models.conversation import Conversation
from app.models.message import Message
from app.services.conversation_service import conversation_service


class ChatService:
    """
    Service for managing chat interactions between the API layer and AI service.
    Handles loading conversation context and coordinating with AI processing.
    """

    def __init__(self):
        pass

    def prepare_conversation_context(
        self,
        db_session: Session,
        conversation_id: UUID,
        user_id: str,
        max_messages: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Prepare conversation context by loading recent messages.

        Args:
            db_session: Database session
            conversation_id: ID of the conversation
            user_id: ID of the user requesting context
            max_messages: Maximum number of messages to load

        Returns:
            List of message dictionaries formatted for AI consumption
        """
        # Get recent messages from the conversation
        messages = conversation_service.get_recent_messages(
            db_session=db_session,
            conversation_id=conversation_id,
            user_id=user_id,
            limit=max_messages
        )

        # Format messages for AI consumption
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                "id": str(msg.id)
            })

        return formatted_messages

    def load_conversation_history(
        self,
        db_session: Session,
        conversation_id: UUID,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Load full conversation history with metadata.

        Args:
            db_session: Database session
            conversation_id: ID of the conversation
            user_id: ID of the user requesting history

        Returns:
            Dictionary with conversation metadata and messages
        """
        # Get conversation
        conversation = conversation_service.get_conversation_by_id(
            db_session=db_session,
            conversation_id=conversation_id,
            user_id=user_id
        )

        if not conversation:
            raise ValueError("Conversation not found or unauthorized access")

        # Get all messages for the conversation
        all_messages = conversation_service.get_messages_for_conversation(
            db_session=db_session,
            conversation_id=conversation_id,
            user_id=user_id,
            limit=None  # Get all messages
        )

        return {
            "conversation": {
                "id": str(conversation.id),
                "title": conversation.title,
                "created_at": conversation.created_at.isoformat(),
                "updated_at": conversation.updated_at.isoformat(),
                "is_active": conversation.is_active
            },
            "messages": [
                {
                    "id": str(msg.id),
                    "role": msg.role.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "tool_call_id": msg.tool_call_id,
                    "tool_response": msg.tool_response
                }
                for msg in all_messages
            ]
        }

    def save_message_interaction(
        self,
        db_session: Session,
        conversation_id: UUID,
        user_id: str,
        user_message: str,
        ai_response: str,
        tool_call_results: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Save a complete message interaction (user message + AI response + tool calls).

        Args:
            db_session: Database session
            conversation_id: ID of the conversation
            user_id: ID of the user
            user_message: Original user message
            ai_response: AI-generated response
            tool_call_results: Optional results from tool calls

        Returns:
            Dictionary with saved message IDs
        """
        # Add user message to conversation
        user_msg = conversation_service.add_message_to_conversation(
            db_session=db_session,
            conversation_id=conversation_id,
            user_id=user_id,
            role="user",
            content=user_message
        )

        # Add AI response to conversation
        ai_msg = conversation_service.add_message_to_conversation(
            db_session=db_session,
            conversation_id=conversation_id,
            user_id=user_id,
            role="assistant",
            content=ai_response
        )

        # If there were tool calls, add them as well
        tool_msgs = []
        if tool_call_results:
            for result in tool_call_results:
                tool_msg = conversation_service.add_message_to_conversation(
                    db_session=db_session,
                    conversation_id=conversation_id,
                    user_id=user_id,
                    role="tool",
                    content=str(result.get('result', '')),
                    tool_call_id=result.get('tool_call_id'),
                    tool_response=str(result.get('result', ''))
                )
                tool_msgs.append(tool_msg)

        return {
            "user_message_id": str(user_msg.id),
            "ai_message_id": str(ai_msg.id),
            "tool_message_ids": [str(tm.id) for tm in tool_msgs],
            "conversation_updated_at": user_msg.conversation.updated_at
        }

    def validate_user_conversation_access(
        self,
        db_session: Session,
        conversation_id: UUID,
        user_id: str
    ) -> bool:
        """
        Validate that a user has access to a specific conversation.

        Args:
            db_session: Database session
            conversation_id: ID of the conversation
            user_id: ID of the user

        Returns:
            Boolean indicating if user has access
        """
        try:
            conversation = conversation_service.get_conversation_by_id(
                db_session=db_session,
                conversation_id=conversation_id,
                user_id=user_id
            )
            return conversation is not None
        except:
            return False


# Global chat service instance
chat_service = ChatService()