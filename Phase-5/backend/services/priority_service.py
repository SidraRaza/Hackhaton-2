"""
Priority Service Module
Handles validation and business logic for task priorities
"""
from typing import Optional, List
from enum import Enum
from datetime import datetime, timedelta
from sqlmodel import Session, select

from models.task import Task, PriorityEnum


class PriorityService:
    """Service class for handling priority-related operations"""

    @staticmethod
    def validate_priority_value(priority: Optional[str]) -> bool:
        """
        Validates if the provided priority value is valid

        Args:
            priority: Priority value to validate (low, medium, high)

        Returns:
            bool: True if valid, raises exception if invalid
        """
        if priority is None:
            return True  # None is acceptable for optional fields

        if priority not in [e.value for e in PriorityEnum]:
            raise ValueError(f"Invalid priority value: {priority}. Must be one of: {[e.value for e in PriorityEnum]}")

        return True

    @staticmethod
    def get_valid_priorities() -> List[str]:
        """
        Returns list of all valid priority values

        Returns:
            List of valid priority values
        """
        return [priority.value for priority in PriorityEnum]

    @staticmethod
    def validate_priority_change(
        current_priority: PriorityEnum,
        new_priority: Optional[PriorityEnum]
    ) -> bool:
        """
        Validates priority change based on business rules

        Args:
            current_priority: Current priority of the task
            new_priority: New priority to change to

        Returns:
            bool: True if change is valid
        """
        if new_priority is None:
            # No change requested
            return True

        # For now, any priority change is valid
        # Additional business rules can be added here
        return True

    @staticmethod
    def get_tasks_by_priority(
        session: Session,
        user_id: str,
        priority: PriorityEnum
    ) -> List[Task]:
        """
        Get all tasks for a user with a specific priority

        Args:
            session: Database session
            user_id: User ID to filter tasks
            priority: Priority level to filter by

        Returns:
            List of tasks with specified priority
        """
        statement = select(Task).where(
            Task.user_id == user_id,
            Task.priority == priority
        )
        return session.exec(statement).all()

    @staticmethod
    def get_tasks_by_multiple_priorities(
        session: Session,
        user_id: str,
        priorities: List[PriorityEnum]
    ) -> List[Task]:
        """
        Get all tasks for a user with any of the specified priorities

        Args:
            session: Database session
            user_id: User ID to filter tasks
            priorities: List of priority levels to filter by

        Returns:
            List of tasks with any of the specified priorities
        """
        statement = select(Task).where(
            Task.user_id == user_id,
            Task.priority.in_(priorities)
        )
        return session.exec(statement).all()

    @staticmethod
    def get_priority_statistics(
        session: Session,
        user_id: str
    ) -> dict[str, int]:
        """
        Get statistics for tasks by priority for a user (only counts pending tasks)

        Args:
            session: Database session
            user_id: User ID to get stats for

        Returns:
            Dictionary with priority counts
        """
        stats = {}
        for priority in PriorityEnum:
            statement = select(Task).where(
                Task.user_id == user_id,
                Task.priority == priority,
                Task.completed == False  # Only count pending tasks
            )
            count = len(session.exec(statement).all())
            stats[priority.value] = count

        return stats

    @staticmethod
    def calculate_priority_impact_score(task: Task) -> float:
        """
        Calculate a numeric impact score based on priority and due date

        Args:
            task: Task to calculate impact for

        Returns:
            Float representing impact score (higher = more impactful)
        """
        # Base scores for priorities
        priority_scores = {
            PriorityEnum.low: 1.0,
            PriorityEnum.medium: 2.0,
            PriorityEnum.high: 3.0
        }

        base_score = priority_scores.get(task.priority, 2.0)

        # Adjust score based on proximity to due date
        if task.due_date:
            now = datetime.utcnow()
            days_until_due = (task.due_date - now).days

            if days_until_due < 0:  # Overdue
                base_score *= 2.0  # Double impact for overdue tasks
            elif days_until_due <= 1:  # Due today or tomorrow
                base_score *= 1.5  # 50% more impact for imminent tasks
            elif days_until_due <= 7:  # Due within a week
                base_score *= 1.2  # 20% more impact for near-term tasks

        # Reduce score if already completed
        if task.completed:
            base_score *= 0.1  # Much lower score for completed tasks

        return base_score