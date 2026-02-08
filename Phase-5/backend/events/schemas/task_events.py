"""
Event schemas for task operations in the Todo application
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
import uuid


class EventType(str, Enum):
    """Enumeration of all event types in the system"""
    # Task events
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    TASK_DELETED = "task.deleted"
    TASK_RECURRENCE_CREATED = "task.recurrence_created"

    # User events
    USER_REGISTERED = "user.registered"
    USER_LOGGED_IN = "user.logged_in"
    USER_PREFERENCES_UPDATED = "user.preferences_updated"

    # System events
    REMINDER_TRIGGERED = "reminder.triggered"
    NOTIFICATION_SENT = "notification.sent"
    AUDIT_LOG_CREATED = "audit.log_created"


class EventMetadata(BaseModel):
    """Common metadata for all events"""
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    trace_id: Optional[str] = None
    source_service: str = "todo-service"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TaskEventEnvelope(BaseModel):
    """Standardized event envelope for task-related events"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    event_version: str = "1.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = "todo-service"
    data: Dict[str, Any]
    metadata: Optional[EventMetadata] = Field(default_factory=EventMetadata)


class TaskCreatedEventData(BaseModel):
    """Data schema for task.created events"""
    task_id: int
    user_id: str
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    due_date: Optional[datetime] = None
    recurrence_pattern: Optional[str] = None
    recurrence_config: Optional[Dict[str, Any]] = None
    tag_ids: Optional[list[int]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCreatedEvent(TaskEventEnvelope):
    """Event emitted when a task is created"""
    event_type: EventType = EventType.TASK_CREATED
    data: TaskCreatedEventData


class TaskUpdatedEventData(BaseModel):
    """Data schema for task.updated events"""
    task_id: int
    user_id: str
    changes: Dict[str, Any]
    updated_fields: list[str]
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskUpdatedEvent(TaskEventEnvelope):
    """Event emitted when a task is updated"""
    event_type: EventType = EventType.TASK_UPDATED
    data: TaskUpdatedEventData


class TaskCompletedEventData(BaseModel):
    """Data schema for task.completed events"""
    task_id: int
    user_id: str
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    was_recurring: bool = False
    has_next_occurrence: bool = False
    next_occurrence_date: Optional[datetime] = None


class TaskCompletedEvent(TaskEventEnvelope):
    """Event emitted when a task is completed"""
    event_type: EventType = EventType.TASK_COMPLETED
    data: TaskCompletedEventData


class TaskDeletedEventData(BaseModel):
    """Data schema for task.deleted events"""
    task_id: int
    user_id: str
    deleted_at: datetime = Field(default_factory=datetime.utcnow)


class TaskDeletedEvent(TaskEventEnvelope):
    """Event emitted when a task is deleted"""
    event_type: EventType = EventType.TASK_DELETED
    data: TaskDeletedEventData


class TaskRecurrenceCreatedEventData(BaseModel):
    """Data schema for task.recurrence_created events"""
    original_task_id: int
    new_task_id: int
    user_id: str
    recurrence_sequence: int
    next_due_date: Optional[datetime] = None


class TaskRecurrenceCreatedEvent(TaskEventEnvelope):
    """Event emitted when a recurring task instance is created"""
    event_type: EventType = EventType.TASK_RECURRENCE_CREATED
    data: TaskRecurrenceCreatedEventData


class EventValidator:
    """Validator for event schemas"""

    @staticmethod
    def validate_task_created_event(data: Dict[str, Any]) -> bool:
        """Validate task.created event data"""
        try:
            TaskCreatedEventData(**data)
            return True
        except Exception:
            return False

    @staticmethod
    def validate_task_updated_event(data: Dict[str, Any]) -> bool:
        """Validate task.updated event data"""
        try:
            TaskUpdatedEventData(**data)
            return True
        except Exception:
            return False

    @staticmethod
    def validate_task_completed_event(data: Dict[str, Any]) -> bool:
        """Validate task.completed event data"""
        try:
            TaskCompletedEventData(**data)
            return True
        except Exception:
            return False

    @staticmethod
    def validate_task_deleted_event(data: Dict[str, Any]) -> bool:
        """Validate task.deleted event data"""
        try:
            TaskDeletedEventData(**data)
            return True
        except Exception:
            return False

    @staticmethod
    def validate_task_recurrence_created_event(data: Dict[str, Any]) -> bool:
        """Validate task.recurrence_created event data"""
        try:
            TaskRecurrenceCreatedEventData(**data)
            return True
        except Exception:
            return False

    @staticmethod
    def validate_event_envelope(event: Dict[str, Any]) -> bool:
        """Validate complete event envelope"""
        try:
            TaskEventEnvelope(**event)
            return True
        except Exception:
            return False