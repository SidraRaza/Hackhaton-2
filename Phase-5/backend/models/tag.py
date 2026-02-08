from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class TagBase(SQLModel):
    name: str = Field(max_length=50)
    color: str = Field(max_length=7, default="#3B82F6")


class Tag(TagBase, table=True):
    __tablename__ = "tags"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TaskTag(SQLModel, table=True):
    __tablename__ = "task_tags"
    
    task_id: int = Field(foreign_key="tasks.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)


class TagCreate(TagBase):
    pass


class TagUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=50)
    color: Optional[str] = Field(default=None, max_length=7)


class TagPublic(TagBase):
    id: int
    user_id: str
    created_at: datetime