from sqlmodel import create_engine, Session
from sqlalchemy import event
from sqlalchemy.pool import StaticPool
from .settings import settings
import os

# Use sqlite in-memory for testing, otherwise use the configured database
if os.getenv("TESTING"):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(settings.DATABASE_URL, echo=settings.DB_ECHO)


def get_session():
    with Session(engine) as session:
        yield session


# Create tables on startup
from models.user import User  # noqa: F401
from models.task import Task  # noqa: F401

from sqlmodel import SQLModel

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)