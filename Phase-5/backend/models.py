from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from enum import Enum
import json


class RoleEnum(str, Enum):
    user = "user"
    assistant = "assistant"


class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class RecurrencePatternEnum(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"
    custom = "custom"


class TaskTag(SQLModel, table=True):
    __tablename__ = "task_tags"

    task_id: int = Field(foreign_key="tasks.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    priority: PriorityEnum = Field(default=PriorityEnum.medium)
    due_date: Optional[datetime] = Field(default=None)
    recurrence_pattern: Optional[RecurrencePatternEnum] = Field(default=None)
    recurrence_config: Optional[Dict[str, Any]] = Field(default=None, sa_column_kwargs={
        "server_default": "NULL",
        "nullable": True
    })
    parent_task_id: Optional[int] = Field(default=None, foreign_key="tasks.id")
    next_occurrence: Optional[datetime] = Field(default=None)
    occurrences_remaining: Optional[int] = Field(default=None)
    reminder_times: Optional[List[datetime]] = Field(default=None, sa_column_kwargs={
        "server_default": "NULL",
        "nullable": True
    })
    last_reminder_sent: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tags: List["Tag"] = Relationship(back_populates="tasks", link_model=TaskTag)
    parent_task: Optional["Task"] = Relationship(back_populates="child_tasks", sa_relationship_kwargs={
        "remote_side": "[Task.id]"
    })
    child_tasks: List["Task"] = Relationship(back_populates="parent_task")

    @property
    def is_recurring(self) -> bool:
        return self.recurrence_pattern is not None

    @property
    def is_overdue(self) -> bool:
        if not self.due_date or self.completed:
            return False
        return self.due_date < datetime.utcnow()

    @property
    def days_until_due(self) -> Optional[int]:
        if not self.due_date:
            return None
        delta = self.due_date - datetime.utcnow()
        return delta.days if delta.days >= 0 else 0


class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    name: str = Field(max_length=50)
    color: str = Field(default="#3B82F6", max_length=7)  # Default blue color
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: List[Task] = Relationship(back_populates="tags", link_model=TaskTag)

    class Config:
        arbitrary_types_allowed = True


class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    conversation_id: int = Field(index=True)  # foreign key constraint will be handled by database
    role: RoleEnum
    content: str = Field(max_length=5000)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ProcessedEvent(SQLModel, table=True):
    """Model for tracking processed events to prevent duplicates"""
    __tablename__ = "processed_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: str = Field(index=True, unique=True)  # Reference to the actual event
    idempotency_key: str = Field(index=True, unique=True)  # Unique key to identify duplicate attempts
    event_type: str  # Type of the event for categorization
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = Field(default=None, index=True)  # Associated user (if applicable)

    class Config:
        arbitrary_types_allowed = True


class FailedEvent(SQLModel, table=True):
    """Model for tracking failed events in the dead letter queue"""
    __tablename__ = "failed_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: str = Field(index=True)  # Reference to the original event
    event_type: str = Field(index=True)  # Type of the failed event
    payload: Dict[str, Any] = Field(default={}, sa_column_kwargs={
        "server_default": "'{}'::jsonb",
        "nullable": False
    })  # Event data that failed to publish
    metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column_kwargs={
        "server_default": "NULL",
        "nullable": True
    })  # Event metadata
    error_message: str  # Error that caused the failure
    retry_count: int = Field(default=0)  # Number of retry attempts
    next_retry_at: Optional[datetime] = Field(default=None)  # When to next retry
    permanent_failure: bool = Field(default=False)  # Whether to stop retrying
    processed: bool = Field(default=False)  # Whether the event has been processed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_attempt: Optional[datetime] = Field(default=None)

    class Config:
        arbitrary_types_allowed = True