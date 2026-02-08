from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from datetime import datetime


class AuditLog(SQLModel, table=True):
    """Model for audit logging of system events"""
    __tablename__ = "audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # ID of the user who triggered the action
    action: str = Field(index=True)  # Type of action (task.created, user.login, etc.)
    resource_type: str = Field(index=True)  # Type of resource (task, user, tag, etc.)
    resource_id: str = Field(index=True)  # ID of the resource that was acted upon
    
    # Dict field - JSON column use karo
    action_details: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False, server_default='{}')
    )  # Details about the action taken
    
    ip_address: Optional[str] = Field(default=None)  # IP address of the user
    user_agent: Optional[str] = Field(default=None)  # User agent string
    timestamp: datetime = Field(default_factory=datetime.utcnow)  # When the action occurred
    correlation_id: Optional[str] = Field(default=None, index=True)  # For tracking related actions
    
    # "metadata" naam change karo (SQLModel mein reserved hai)
    # Ya phir JSON column use karo
    extra_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True)
    )  # Additional metadata

    class Config:
        arbitrary_types_allowed = True