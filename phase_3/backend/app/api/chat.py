from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import asyncio
from uuid import UUID

from database import get_session
from utils.auth import get_current_user
from models.user import User
from sqlmodel import Session, select
from datetime import datetime

from models.conversation import Conversation
from models.message import Message, MessageRole

# Create router
router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/")
async def chat_endpoint(
    request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Main chat endpoint that handles user messages and returns AI responses.
    """
    # Extract message and conversation_id from request
    message_content = request.get("message")
    if not message_content:
        raise HTTPException(status_code=400, detail="Message content is required")

    conversation_id = request.get("conversation_id")

    # If no conversation_id provided, create a new conversation
    if not conversation_id:
        # Create new conversation
        new_conversation = Conversation(
            user_id=str(current_user.id),
            title=message_content[:50] + "..." if len(message_content) > 50 else message_content
        )
        db_session.add(new_conversation)
        db_session.commit()
        db_session.refresh(new_conversation)
        conversation_id = str(new_conversation.id)
    else:
        # Verify conversation belongs to user
        conversation = db_session.get(Conversation, conversation_id)
        if not conversation or str(conversation.user_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied to this conversation")

    # Add user message to conversation
    user_message = Message(
        conversation_id=UUID(conversation_id),
        role=MessageRole.USER,  # Use the correct enum value
        content=message_content
    )
    db_session.add(user_message)
    db_session.commit()

    # Placeholder AI response - in real implementation, this would come from AI service
    ai_response = f"I received your message: '{message_content}'. This is a placeholder response from the AI assistant."

    # Add AI response to conversation
    ai_message = Message(
        conversation_id=UUID(conversation_id),
        role=MessageRole.ASSISTANT,  # Use the correct enum value
        content=ai_response
    )
    db_session.add(ai_message)
    db_session.commit()

    return {
        "response": ai_response,
        "conversation_id": conversation_id,
        "success": True
    }


@router.get("/conversations")
def get_user_conversations(
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Get all conversations for the current user.
    """
    statement = select(Conversation).where(Conversation.user_id == str(current_user.id))
    conversations = db_session.exec(statement).all()

    conversations_list = []
    for conv in conversations:
        conversations_list.append({
            "id": str(conv.id),
            "title": conv.title,
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat(),
            "is_active": conv.is_active
        })

    return {
        "conversations": conversations_list,
        "count": len(conversations_list),
        "success": True
    }


@router.get("/conversations/{conversation_id}")
def get_conversation_with_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Get a specific conversation with its messages.
    """
    # Verify conversation belongs to user
    conversation = db_session.get(Conversation, conversation_id)
    if not conversation or str(conversation.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied to this conversation")

    # Get messages for the conversation
    statement = select(Message).where(Message.conversation_id == UUID(conversation_id)).order_by(Message.timestamp)
    messages = db_session.exec(statement).all()

    messages_list = []
    for msg in messages:
        messages_list.append({
            "id": str(msg.id),
            "role": msg.role.value,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat()
        })

    return {
        "conversation": {
            "id": str(conversation.id),
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "is_active": conversation.is_active
        },
        "messages": messages_list,
        "success": True
    }


@router.post("/conversations")
def create_new_conversation(
    request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Create a new conversation.
    """
    title = request.get("title", "New Conversation")

    new_conversation = Conversation(
        user_id=str(current_user.id),
        title=title
    )
    db_session.add(new_conversation)
    db_session.commit()
    db_session.refresh(new_conversation)

    return {
        "conversation": {
            "id": str(new_conversation.id),
            "title": new_conversation.title,
            "created_at": new_conversation.created_at.isoformat(),
            "updated_at": new_conversation.updated_at.isoformat(),
            "is_active": new_conversation.is_active
        },
        "success": True
    }