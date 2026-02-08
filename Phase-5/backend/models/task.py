from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from datetime import datetime
from enum import Enum


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


class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)


class Task(TaskBase, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    priority: PriorityEnum = Field(default=PriorityEnum.medium)
    due_date: Optional[datetime] = Field(default=None)
    recurrence_pattern: Optional[RecurrencePatternEnum] = Field(default=None)
    
    # Dict field - JSON column use karo
    recurrence_config: Optional[Dict[str, Any]] = Field(
        default=None, 
        sa_column=Column(JSON, nullable=True)
    )
    
    parent_task_id: Optional[int] = Field(default=None, foreign_key="tasks.id")
    next_occurrence: Optional[datetime] = Field(default=None)
    occurrences_remaining: Optional[int] = Field(default=None)
    
    # List field - JSON column use karo
    reminder_times: Optional[List[datetime]] = Field(
        default=None, 
        sa_column=Column(JSON, nullable=True)
    )
    
    last_reminder_sent: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCreate(TaskBase):
    priority: Optional[PriorityEnum] = Field(default=PriorityEnum.medium)
    due_date: Optional[datetime] = Field(default=None)
    recurrence_pattern: Optional[RecurrencePatternEnum] = Field(default=None)
    recurrence_config: Optional[Dict[str, Any]] = Field(default=None)
    tag_ids: Optional[List[int]] = Field(default_factory=list)
    reminder_times: Optional[List[datetime]] = Field(default=None)


class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = None
    priority: Optional[PriorityEnum] = Field(default=None)
    due_date: Optional[datetime] = Field(default=None)
    recurrence_pattern: Optional[RecurrencePatternEnum] = Field(default=None)
    recurrence_config: Optional[Dict[str, Any]] = Field(default=None)
    tag_ids: Optional[List[int]] = Field(default=None)
    reminder_times: Optional[List[datetime]] = Field(default=None)


class TaskPublic(TaskBase):
    id: int
    user_id: str
    priority: PriorityEnum
    due_date: Optional[datetime] = None
    recurrence_pattern: Optional[RecurrencePatternEnum] = None
    recurrence_config: Optional[Dict[str, Any]] = None
    parent_task_id: Optional[int] = None
    next_occurrence: Optional[datetime] = None
    occurrences_remaining: Optional[int] = None
    reminder_times: Optional[List[datetime]] = None
    last_reminder_sent: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime