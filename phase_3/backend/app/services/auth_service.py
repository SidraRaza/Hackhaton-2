from sqlmodel import Session, select
from typing import Optional
from datetime import timedelta
import uuid

from ..models.user import User, UserCreate, UserLogin, get_password_hash
from ..utils.auth import create_access_token, verify_token
from ...config.settings import settings


class AuthService:
    def register_user(self, session: Session, user_data: UserCreate) -> User:
        """
        Register a new user with the provided data
        """
        # Check if user with email already exists
        existing_user_by_email = session.exec(
            select(User).where(User.email == user_data.email)
        ).first()

        if existing_user_by_email:
            raise ValueError("A user with this email already exists")

        # Check if user with username already exists
        existing_user_by_username = session.exec(
            select(User).where(User.username == user_data.username)
        ).first()

        if existing_user_by_username:
            raise ValueError("A user with this username already exists")

        # Hash the password
        hashed_password = get_password_hash(user_data.password)

        # Create new user
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        return user

    def authenticate_user(self, session: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password
        """
        # Find user by email
        user = session.exec(
            select(User).where(User.email == email)
        ).first()

        if not user or not user.verify_password(password):
            return None

        if not user.is_active:
            raise ValueError("Inactive user account")

        return user

    def login_user(self, session: Session, user_login: UserLogin) -> dict:
        """
        Login user and return access token
        """
        user = self.authenticate_user(session, user_login.email, user_login.password)

        if not user:
            raise ValueError("Incorrect email or password")

        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "created_at": user.created_at.isoformat()
            }
        }

    def get_current_user(self, session: Session, token: str) -> User:
        """
        Get current user based on authentication token
        """
        payload = verify_token(token)
        user_id = payload.get("sub")

        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise ValueError("Invalid user ID format")

        user = session.exec(select(User).where(User.id == user_uuid)).first()
        if not user:
            raise ValueError("User not found")
        if not user.is_active:
            raise ValueError("Inactive user")

        return user