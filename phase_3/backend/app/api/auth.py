from fastapi import Depends
from sqlalchemy.orm import Session

from utils.auth import get_current_user as utils_get_current_user
from models.user import User
from database import get_session


def get_current_user(session: Session = Depends(get_session)) -> User:
    """
    Get current user based on authentication token.
    This function wraps the utility function to provide proper dependency injection.
    """
    return utils_get_current_user(session=session)