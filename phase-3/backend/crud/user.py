from sqlmodel import Session, select
from models.user import User, UserCreate
from utils.auth import get_password_hash


def create_user(session: Session, user_create: UserCreate) -> User:
    # Check if user already exists
    statement = select(User).where(User.email == user_create.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        return None  # User already exists

    # Create new user
    hashed_password = get_password_hash(user_create.password)
    db_user = User(
        email=user_create.email,
        password_hash=hashed_password
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def authenticate_user(session: Session, email: str, password: str) -> User:
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def get_user_by_email(session: Session, email: str) -> User:
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)