"""
Event schemas for system operations in the Todo application
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid

from task_events import EventType, EventMetadata


class ReminderTriggeredEventData(BaseModel):
    """Data schema for reminder.triggered events"""
    task_id: int
    user_id: str
    reminder_time: datetime
    notification_channel: str = "browser"  # browser, email, sms, push
    scheduled_time: datetime
    actual_trigger_time: datetime = Field(default_factory=datetime.utcnow)


class ReminderTriggeredEvent(BaseModel):
    """Event emitted when a reminder is triggered"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.REMINDER_TRIGGERED
    event_version: str = "1.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = "reminder-service"
    data: ReminderTriggeredEventData
    metadata: Optional[EventMetadata] = Field(default_factory=EventMetadata)


class NotificationSentEventData(BaseModel):
    """Data schema for notification.sent events"""
    notification_id: str
    user_id: str
    task_id: Optional[int] = None
    channel: str  # browser, email, sms, push
    message: str
    sent_time: datetime = Field(default_factory=datetime.utcnow)
    success: bool = True
    retry_count: int = 0


class NotificationSentEvent(BaseModel):
    """Event emitted when a notification is sent"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.NOTIFICATION_SENT
    event_version: str = "1.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = "notification-service"
    data: NotificationSentEventData
    metadata: Optional[EventMetadata] = Field(default_factory=EventMetadata)


class AuditLogCreatedEventData(BaseModel):
    """Data schema for audit.log_created events"""
    user_id: str
    action: str  # create_task, update_task, complete_task, etc.
    resource_type: str  # task, tag, user, etc.
    resource_id: str
    action_details: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogCreatedEvent(BaseModel):
    """Event emitted when an audit log is created"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.AUDIT_LOG_CREATED
    event_version: str = "1.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = "audit-service"
    data: AuditLogCreatedEventData
    metadata: Optional[EventMetadata] = Field(default_factory=EventMetadata)


class TaskDueSoonEventData(BaseModel):
    """Data schema for task.due_soon events"""
    task_id: int
    user_id: str
    title: str
    due_date: datetime
    priority: str
    hours_until_due: int
    scheduled_reminder_time: datetime


class TaskDueSoonEvent(BaseModel):
    """Event emitted when a task is due soon"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.REMINDER_TRIGGERED
    event_version: str = "1.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = "reminder-service"
    data: TaskDueSoonEventData
    metadata: Optional[EventMetadata] = Field(default_factory=EventMetadata)


class SystemEventEnvelope(BaseModel):
    """Generic event envelope for all system events"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    event_version: str = "1.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str
    data: Dict[str, Any]
    metadata: Optional[EventMetadata] = Field(default_factory=EventMetadata)

    class Config:
        # Allow extra fields for flexibility
        extra = "allow"


class SystemEventValidator:
    """Validator for system event schemas"""

    @staticmethod
    def validate_reminder_triggered_event(data: Dict[str, Any]) -> bool:
        """Validate reminder.triggered event data"""
        try:
            ReminderTriggeredEventData(**data)
            return True
        except Exception:
            return False

    @staticmethod
    def validate_notification_sent_event(data: Dict[str, Any]) -> bool:
        """Validate notification.sent event data"""
        try:
            NotificationSentEventData(**data)
            return True
        except Exception:
            return False

    @staticmethod
    def validate_audit_log_created_event(data: Dict[str, Any]) -> bool:
        """Validate audit.log_created event data"""
        try:
            AuditLogCreatedEventData(**data)
            return True
        except Exception:
            return False

    @staticmethod
    def validate_task_due_soon_event(data: Dict[str, Any]) -> bool:
        """Validate task.due_soon event data"""
        try:
            TaskDueSoonEventData(**data)
            return True
        except Exception:
            return False

    @staticmethod
    def validate_system_event_envelope(event: Dict[str, Any]) -> bool:
        """Validate complete system event envelope"""
        try:
            SystemEventEnvelope(**event)
            return True
        except Exception:
            return False