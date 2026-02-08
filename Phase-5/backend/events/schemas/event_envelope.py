"""
Event Envelope Standard for Phase V: Advanced Cloud Deployment
Defines the standard format for all events in the system
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid


class EventMetadata(BaseModel):
    """
    Standard metadata for all events in the system
    Contains correlation and tracing information
    """
    correlation_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="ID to correlate related events across services"
    )
    trace_id: Optional[str] = Field(
        default=None,
        description="Trace ID for distributed tracing"
    )
    user_id: Optional[str] = Field(
        default=None,
        description="ID of the user who triggered the event"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Session ID for the user session"
    )
    source_service: str = Field(
        default="todo-service",
        description="Name of the service that generated the event"
    )
    source_component: Optional[str] = Field(
        default=None,
        description="Component within the service that generated the event"
    )
    client_ip: Optional[str] = Field(
        default=None,
        description="IP address of the client that initiated the action"
    )
    user_agent: Optional[str] = Field(
        default=None,
        description="User agent string of the client"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the event was generated"
    )


class EventEnvelope(BaseModel):
    """
    Standardized event envelope for all events in the system
    Provides consistent structure for event-driven architecture
    """
    # Event identification
    event_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the event"
    )
    event_type: str = Field(
        description="Type of the event (e.g., 'task.created', 'user.logged_in')"
    )
    event_version: str = Field(
        default="1.0",
        description="Version of the event schema for backward compatibility"
    )

    # Event timing and source
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the event occurred"
    )
    source: str = Field(
        default="todo-service",
        description="Source service that generated the event"
    )

    # Event data
    data: Dict[str, Any] = Field(
        default={},
        description="Event-specific data payload"
    )

    # Event metadata
    metadata: Optional[EventMetadata] = Field(
        default_factory=EventMetadata,
        description="Additional metadata for correlation and tracing"
    )

    # Aggregate information for event sourcing
    aggregate_type: Optional[str] = Field(
        default=None,
        description="Type of the aggregate root (for event sourcing)"
    )
    aggregate_id: Optional[str] = Field(
        default=None,
        description="ID of the aggregate root (for event sourcing)"
    )

    class Config:
        """Pydantic configuration for the event envelope"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        # Allow extra fields for flexibility in different event types
        extra = "allow"


class TaskEventEnvelope(EventEnvelope):
    """
    Specialized event envelope for task-related events
    Includes additional fields specific to task operations
    """
    # Task-specific fields
    task_id: Optional[int] = Field(
        default=None,
        description="ID of the task related to this event"
    )
    user_id: Optional[str] = Field(
        default=None,
        description="ID of the user who owns the task"
    )

    # Ensure proper aggregate information for task events
    aggregate_type: str = Field(
        default="task",
        description="Aggregate type for task events"
    )
    aggregate_id: Optional[str] = Field(
        default=None,
        description="ID of the task aggregate"
    )


class UserEventEnvelope(EventEnvelope):
    """
    Specialized event envelope for user-related events
    Includes additional fields specific to user operations
    """
    # User-specific fields
    user_id: Optional[str] = Field(
        default=None,
        description="ID of the user related to this event"
    )

    # Ensure proper aggregate information for user events
    aggregate_type: str = Field(
        default="user",
        description="Aggregate type for user events"
    )
    aggregate_id: Optional[str] = Field(
        default=None,
        description="ID of the user aggregate"
    )


class SystemEventEnvelope(EventEnvelope):
    """
    Specialized event envelope for system events
    Includes additional fields specific to system operations
    """
    # System-specific fields
    service_name: Optional[str] = Field(
        default=None,
        description="Name of the service where the system event occurred"
    )
    component_name: Optional[str] = Field(
        default=None,
        description="Component where the system event occurred"
    )

    # Ensure proper aggregate information for system events
    aggregate_type: str = Field(
        default="system",
        description="Aggregate type for system events"
    )


class EventFactory:
    """
    Factory for creating properly formatted events
    """
    @staticmethod
    def create_task_event(
        event_type: str,
        task_id: int,
        user_id: str,
        data: Dict[str, Any],
        source: str = "todo-service"
    ) -> TaskEventEnvelope:
        """
        Create a properly formatted task event

        Args:
            event_type: Type of the event (e.g., 'task.created')
            task_id: ID of the task
            user_id: ID of the user
            data: Event-specific data
            source: Source service name

        Returns:
            Properly formatted TaskEventEnvelope
        """
        return TaskEventEnvelope(
            event_type=event_type,
            task_id=task_id,
            user_id=user_id,
            data=data,
            source=source,
            aggregate_id=str(task_id)
        )

    @staticmethod
    def create_user_event(
        event_type: str,
        user_id: str,
        data: Dict[str, Any],
        source: str = "auth-service"
    ) -> UserEventEnvelope:
        """
        Create a properly formatted user event

        Args:
            event_type: Type of the event (e.g., 'user.registered')
            user_id: ID of the user
            data: Event-specific data
            source: Source service name

        Returns:
            Properly formatted UserEventEnvelope
        """
        return UserEventEnvelope(
            event_type=event_type,
            user_id=user_id,
            data=data,
            source=source,
            aggregate_id=user_id
        )

    @staticmethod
    def create_system_event(
        event_type: str,
        data: Dict[str, Any],
        source: str = "system-service",
        service_name: Optional[str] = None,
        component_name: Optional[str] = None
    ) -> SystemEventEnvelope:
        """
        Create a properly formatted system event

        Args:
            event_type: Type of the event (e.g., 'system.started')
            data: Event-specific data
            source: Source service name
            service_name: Name of the service where event occurred
            component_name: Name of the component where event occurred

        Returns:
            Properly formatted SystemEventEnvelope
        """
        return SystemEventEnvelope(
            event_type=event_type,
            data=data,
            source=source,
            service_name=service_name,
            component_name=component_name
        )


class EventValidator:
    """
    Validator for event schemas to ensure consistency
    """
    @staticmethod
    def validate_event_structure(event: EventEnvelope) -> bool:
        """
        Validate that an event has the required structure

        Args:
            event: Event to validate

        Returns:
            True if event structure is valid
        """
        required_fields = ['event_id', 'event_type', 'timestamp', 'source', 'data']
        for field in required_fields:
            if not hasattr(event, field) or getattr(event, field) is None:
                return False
        return True

    @staticmethod
    def validate_task_event_structure(event: TaskEventEnvelope) -> bool:
        """
        Validate that a task event has the required structure

        Args:
            event: Task event to validate

        Returns:
            True if task event structure is valid
        """
        if not EventValidator._validate_base_event_structure(event):
            return False

        # Task events should have task_id and user_id
        if event.task_id is None or event.user_id is None:
            return False

        return True

    @staticmethod
    def validate_user_event_structure(event: UserEventEnvelope) -> bool:
        """
        Validate that a user event has the required structure

        Args:
            event: User event to validate

        Returns:
            True if user event structure is valid
        """
        if not EventValidator._validate_base_event_structure(event):
            return False

        # User events should have user_id
        if event.user_id is None:
            return False

        return True

    @staticmethod
    def validate_system_event_structure(event: SystemEventEnvelope) -> bool:
        """
        Validate that a system event has the required structure

        Args:
            event: System event to validate

        Returns:
            True if system event structure is valid
        """
        if not EventValidator._validate_base_event_structure(event):
            return False

        return True

    @staticmethod
    def _validate_base_event_structure(event: EventEnvelope) -> bool:
        """
        Validate the base event structure (helper method)

        Args:
            event: Event to validate

        Returns:
            True if base event structure is valid
        """
        required_fields = ['event_id', 'event_type', 'timestamp', 'source', 'data']
        for field in required_fields:
            if not hasattr(event, field) or getattr(event, field) is None:
                return False
        return True