from sqlmodel import create_engine, Session
from typing import Generator
import os
from dotenv import load_dotenv

# Import models to ensure they are registered with SQLModel
from models.user import User
from models.task import Task
from models.conversation import Conversation
from models.message import Message

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_app.db")

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session