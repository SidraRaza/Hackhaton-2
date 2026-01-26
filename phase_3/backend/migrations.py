"""
Simple migration script to create tables for new models.
This is a simplified migration approach for demonstration.
In a real application, you'd use Alembic for proper migrations.
"""
from sqlmodel import SQLModel
from database import engine
from app.models.conversation import Conversation
from app.models.message import Message


def run_migrations():
    """Run migrations to create tables for new models"""
    print("Creating tables for new models...")

    # Create tables for Conversation and Message models
    SQLModel.metadata.create_all(bind=engine)

    print("Migration completed successfully!")


if __name__ == "__main__":
    run_migrations()