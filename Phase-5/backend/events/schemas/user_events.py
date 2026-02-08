"""
Event schemas for user operations in the Todo application
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid

from task_events import EventType, EventMetadata


class UserRegisteredEventData(BaseModel):
    """Data schema for user.registered events"""
    user_id: str
    email: str
    name: Optional[str] = None
    registration_method: str = "email"  # email, oauth, etc.
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserRegisteredEvent(BaseModel):
    """Event emitted when a user registers"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.USER_REGISTERED
    event_version: str = "1.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = "auth-service"
    data: UserRegisteredEventData
    metadata: Optional[EventMetadata] = Field(default_factory=EventMetadata)


class UserLoggedInEventData(BaseModel):
    """Data schema for user.logged_in events"""
    user_id: str
    session_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    login_time: datetime = Field(default_factory=datetime.utcnow)


class UserLoggedInEvent(BaseModel):
    """Event emitted when a user logs in"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.USER_LOGGED_IN
    event_version: str = "1.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = "auth-service"
    data: UserLoggedInEventData
    metadata: Optional[EventMetadata] = Field(default_factory=EventMetadata)


class UserPreferencesUpdatedEventData(BaseModel):
    """Data schema for user.preferences_updated events"""
    user_id: str
    preferences: Dict[str, Any]
    updated_fields: list[str]
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserPreferencesUpdatedEvent(BaseModel):
    """Event emitted when user preferences are updated"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.USER_PREFERENCES_UPDATED
    event_version: str = "1.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = "user-service"
    data: UserPreferencesUpdatedEventData
    metadata: Optional[EventMetadata] = Field(default_factory=EventMetadata)


class UserProfileUpdatedEventData(BaseModel):
    """Data schema for user.profile_updated events"""
    user_id: str
    changes: Dict[str, Any]
    updated_fields: list[str]
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserProfileUpdatedEvent(BaseModel):
    """Event emitted when user profile is updated"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.USER_PREFERENCES_UPDATED
    event_version: str = "1.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = "user-service"
    data: UserProfileUpdatedEventData
    metadata: Optional[EventMetadata] = Field(default_factory=EventMetadata)