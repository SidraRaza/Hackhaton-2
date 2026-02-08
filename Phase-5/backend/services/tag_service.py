from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime

from models import Tag, Task, TaskTag


class TagService:
    """Service class for handling tag operations"""

    @staticmethod
    def get_tags_by_user(session: Session, user_id: str) -> List[Tag]:
        """
        Get all tags for a specific user

        Args:
            session: Database session
            user_id: User ID to filter tags

        Returns:
            List of tags belonging to the user
        """
        statement = select(Tag).where(Tag.user_id == user_id).order_by(Tag.name)
        return session.exec(statement).all()

    @staticmethod
    def get_tag_by_id(session: Session, tag_id: int, user_id: str) -> Optional[Tag]:
        """
        Get a specific tag by ID for a user

        Args:
            session: Database session
            tag_id: Tag ID to retrieve
            user_id: User ID for authorization

        Returns:
            Tag object if found and belongs to user, None otherwise
        """
        statement = select(Tag).where(
            Tag.id == tag_id,
            Tag.user_id == user_id
        )
        return session.exec(statement).first()

    @staticmethod
    def create_tag(session: Session, tag: Tag) -> Tag:
        """
        Create a new tag

        Args:
            session: Database session
            tag: Tag object to create

        Returns:
            Created Tag object
        """
        session.add(tag)
        session.commit()
        session.refresh(tag)
        return tag

    @staticmethod
    def update_tag(
        session: Session,
        tag_id: int,
        user_id: str,
        tag_data: dict
    ) -> Optional[Tag]:
        """
        Update a tag with new data

        Args:
            session: Database session
            tag_id: ID of the tag to update
            user_id: User ID for authorization
            tag_data: Dictionary with fields to update

        Returns:
            Updated Tag object if successful, None if tag not found
        """
        existing_tag = session.exec(
            select(Tag).where(
                Tag.id == tag_id,
                Tag.user_id == user_id
            )
        ).first()

        if not existing_tag:
            return None

        # Update fields
        for field, value in tag_data.items():
            if hasattr(existing_tag, field) and field not in ["id", "user_id", "created_at"]:
                setattr(existing_tag, field, value)

        existing_tag.updated_at = datetime.utcnow()
        session.add(existing_tag)
        session.commit()
        session.refresh(existing_tag)
        return existing_tag

    @staticmethod
    def delete_tag(session: Session, tag_id: int, user_id: str) -> bool:
        """
        Delete a tag and its associations

        Args:
            session: Database session
            tag_id: ID of the tag to delete
            user_id: User ID for authorization

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        # First delete associations
        stmt_delete_associations = select(TaskTag).where(
            TaskTag.tag_id == tag_id
        )
        associations = session.exec(stmt_delete_associations).all()

        for assoc in associations:
            session.delete(assoc)

        # Then delete the tag
        existing_tag = session.exec(
            select(Tag).where(
                Tag.id == tag_id,
                Tag.user_id == user_id
            )
        ).first()

        if not existing_tag:
            return False

        session.delete(existing_tag)
        session.commit()
        return True

    @staticmethod
    def get_tasks_for_tag(session: Session, tag_id: int, user_id: str) -> List[Task]:
        """
        Get all tasks associated with a specific tag for a user

        Args:
            session: Database session
            tag_id: ID of the tag
            user_id: User ID for authorization

        Returns:
            List of tasks associated with the tag
        """
        statement = select(Task).join(TaskTag).join(Tag).where(
            Tag.id == tag_id,
            Tag.user_id == user_id
        )
        return session.exec(statement).all()

    @staticmethod
    def associate_task_with_tag(session: Session, task_id: int, tag_id: int) -> bool:
        """
        Associate a task with a tag

        Args:
            session: Database session
            task_id: ID of the task
            tag_id: ID of the tag

        Returns:
            bool: True if association was created, False if already exists
        """
        # Check if association already exists
        existing_assoc = session.exec(
            select(TaskTag).where(
                TaskTag.task_id == task_id,
                TaskTag.tag_id == tag_id
            )
        ).first()

        if existing_assoc:
            return False  # Association already exists

        # Create new association
        task_tag = TaskTag(task_id=task_id, tag_id=tag_id)
        session.add(task_tag)
        session.commit()
        return True

    @staticmethod
    def remove_task_from_tag(session: Session, task_id: int, tag_id: int) -> bool:
        """
        Remove a task from a tag (remove association)

        Args:
            session: Database session
            task_id: ID of the task
            tag_id: ID of the tag

        Returns:
            bool: True if association was removed, False if not found
        """
        task_tag = session.exec(
            select(TaskTag).where(
                TaskTag.task_id == task_id,
                TaskTag.tag_id == tag_id
            )
        ).first()

        if not task_tag:
            return False

        session.delete(task_tag)
        session.commit()
        return True

    @staticmethod
    def get_popular_tags(session: Session, user_id: str, limit: int = 10) -> List[Tag]:
        """
        Get the most popular tags for a user (by number of associated tasks)

        Args:
            session: Database session
            user_id: User ID to filter tags
            limit: Maximum number of tags to return

        Returns:
            List of most popular tags with counts
        """
        from sqlalchemy import func

        statement = (
            select(Tag, func.count(TaskTag.task_id).label('task_count'))
            .join(TaskTag, Tag.id == TaskTag.tag_id)
            .join(Task, Task.id == TaskTag.task_id)
            .where(Tag.user_id == user_id)
            .group_by(Tag.id)
            .order_by(func.count(TaskTag.task_id).desc())
            .limit(limit)
        )

        results = session.exec(statement).all()
        return [result[0] for result in results]  # Return only the tags, not the counts