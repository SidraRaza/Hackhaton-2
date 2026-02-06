from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, Dict

from utils.auth import get_current_user as utils_get_current_user
from models.user import User, UserCreate, UserLogin
from database import get_session
from app.services.auth_service import AuthService

# Create router
router = APIRouter(prefix="/auth", tags=["auth"])

# Initialize service
auth_service = AuthService()


@router.post("/register")
def register_user(
    user_create: UserCreate,
    db_session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Register a new user.
    """
    try:
        user = auth_service.register_user(db_session, user_create)
        return {
            "id": str(user.id),
            "email": user.email,
            "name": user.full_name
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.post("/login")
def login_user(
    user_login: UserLogin,
    db_session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Login user and return authentication token.
    """
    try:
        result = auth_service.login_user(db_session, user_login)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
def logout_user() -> Dict[str, str]:
    """
    Logout user.
    """
    # In a real implementation, this might involve blacklisting the token
    # For now, we just return a success message
    return {"message": "Successfully logged out"}


def get_current_user(session: Session = Depends(get_session)) -> User:
    """
    Get current user based on authentication token.
    This function wraps the utility function to provide proper dependency injection.
    """
    return utils_get_current_user(session=session)