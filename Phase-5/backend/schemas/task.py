from pydantic import BaseModel
from typing import Optional, List
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


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: Optional[PriorityEnum] = "medium"
    due_date: Optional[datetime] = None
    recurrence_pattern: Optional[RecurrencePatternEnum] = None
    recurrence_config: Optional[dict] = None
    tag_ids: Optional[List[int]] = []


class TaskCreate(TaskBase):
    title: str  # Required for creation
    priority: PriorityEnum = "medium"  # Default to medium priority


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[PriorityEnum] = None
    due_date: Optional[datetime] = None
    recurrence_pattern: Optional[RecurrencePatternEnum] = None
    recurrence_config: Optional[dict] = None
    tag_ids: Optional[List[int]] = None


class TaskResponse(TaskBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    tags: Optional[List[dict]] = []  # Will contain tag objects


class TaskRecurrenceCompleteRequest(BaseModel):
    """Request model for completing recurring tasks with advanced options"""
    mark_series_complete: bool = False
    modify_future_occurrences: bool = False
    skip_next_occurrence: bool = False
    create_next_occurrence: bool = True
    recurrence_action: Optional[str] = "create_next"  # Options: "create_next", "skip", "end_series"


class TaskListQueryParams(BaseModel):
    """Query parameters for task listing with advanced filtering"""
    priority: Optional[List[PriorityEnum]] = None
    tags: Optional[List[int]] = None
    search: Optional[str] = None
    due_date_from: Optional[datetime] = None
    due_date_to: Optional[datetime] = None
    status: Optional[str] = "all"
    sort: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"
    limit: Optional[int] = 50
    offset: Optional[int] = 0