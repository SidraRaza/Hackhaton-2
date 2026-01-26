from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(SQLModel):
    """Base model for User with common fields"""
    email: str
    username: str
    full_name: Optional[str] = None


class User(UserBase, table=True):
    """
    User model representing application users with authentication.
    """
    id: UUID
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    hashed_password: str

    def verify_password(self, plain_password: str) -> bool:
        """Verify a plain password against the hashed password"""
        # This would use the actual password verification logic
        # For now, using a placeholder implementation
        from utils.security import verify_password
        return verify_password(plain_password, self.hashed_password)


class UserRead(UserBase):
    """Schema for reading user data"""
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str


class UserLogin(SQLModel):
    """Schema for user login"""
    email: str
    password: str