from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Relationship, Column
from datetime import datetime
from enum import Enum


class ReminderChannel(str, Enum):
    BROWSER = "browser"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class ReminderStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Reminder(SQLModel, table=True):
    """Model for task reminders"""
    __tablename__ = "reminders"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", index=True)
    user_id: str = Field(index=True)
    reminder_time: datetime = Field(sa_column_kwargs={"index": True})
    channel: ReminderChannel = Field(default=ReminderChannel.BROWSER)
    status: ReminderStatus = Field(default=ReminderChannel.PENDING)
    message: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    updated_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    sent_at: Optional[datetime] = Field(default=None)

    # Relationships
    task: Optional["Task"] = Relationship(back_populates="reminders")

    class Config:
        arbitrary_types_allowed = True


class TaskReminderConfig(SQLModel):
    """Configuration for task reminders"""
    reminder_times: List[datetime]  # List of reminder times relative to due date
    channels: List[ReminderChannel] = Field(default=[ReminderChannel.BROWSER])
    enabled: bool = Field(default=True)
    snooze_duration: Optional[int] = Field(default=None)  # Minutes to snooze (e.g., 5, 10, 15)


class ReminderSchedule(SQLModel):
    """Model for recurring reminder schedules"""
    __tablename__ = "reminder_schedules"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", index=True)
    user_id: str = Field(index=True)
    schedule_type: str = Field(default="relative")  # "relative" to due date, "absolute" time
    schedule_config: Dict[str, Any] = Field(default={}, sa_column_kwargs={
        "server_default": "'{}'::jsonb",
        "nullable": False
    })
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    updated_at: datetime = Field(default_factory=lambda: datetime.utcnow())

    class Config:
        arbitrary_types_allowed = True