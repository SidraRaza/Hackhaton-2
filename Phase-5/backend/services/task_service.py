from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from sqlalchemy import text
from models import Task, PriorityEnum
from datetime import datetime


class TaskService:
    @staticmethod
    def get_tasks_by_user(
        session: Session,
        user_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Task]:
        """
        Get all tasks for a specific user with advanced filtering and sorting

        Args:
            session: Database session
            user_id: User ID to filter tasks
            filters: Optional dictionary with filtering parameters:
                - priority: List of priority levels to filter by
                - tags: List of tag IDs to filter by
                - search: Full-text search term
                - due_date_from: Filter tasks with due date after this date
                - due_date_to: Filter tasks with due date before this date
                - recurrence_pattern: Filter by recurrence pattern
                - status: Filter by task status ('pending', 'completed', 'all')
                - sort: Sort field ('priority', 'due_date', 'created_at', 'title', 'completed')
                - sort_order: Sort order ('asc', 'desc')
                - limit: Number of results to return
                - offset: Offset for pagination

        Returns:
            List of tasks matching the criteria
        """
        statement = select(Task).where(Task.user_id == user_id)

        # Apply filters if provided
        if filters:
            # Combine multiple filter conditions
            filter_conditions = []

            # Priority filter
            if filters.get("priority"):
                priorities = filters["priority"]
                if isinstance(priorities, list):
                    filter_conditions.append(Task.priority.in_(priorities))
                else:
                    filter_conditions.append(Task.priority == priorities)

            # Tag filter - need to join with TaskTag table
            if filters.get("tags"):
                tag_ids = filters["tags"]
                if isinstance(tag_ids, list) and len(tag_ids) > 0:
                    # For tag filtering, we need to join with TaskTag table
                    # This requires a more complex query that will be handled differently
                    pass  # Tags are handled separately in a different method

            # Status filter
            if filters.get("status") and filters["status"] != "all":
                if filters["status"] == "pending":
                    filter_conditions.append(Task.completed == False)
                elif filters["status"] == "completed":
                    filter_conditions.append(Task.completed == True)

            # Due date filters
            if filters.get("due_date_from"):
                filter_conditions.append(Task.due_date >= filters["due_date_from"])
            if filters.get("due_date_to"):
                filter_conditions.append(Task.due_date <= filters["due_date_to"])

            # Recurrence pattern filter
            if filters.get("recurrence_pattern"):
                filter_conditions.append(Task.recurrence_pattern == filters["recurrence_pattern"])

            # Apply all collected filter conditions
            for condition in filter_conditions:
                statement = statement.where(condition)

            # Search filter (full-text search) - needs to be handled separately as it's more complex
            if filters.get("search"):
                search_term = filters["search"]
                # Use PostgreSQL full-text search if available, otherwise fallback to LIKE
                try:
                    # Try full-text search with proper parameter binding
                    statement = statement.where(
                        text("to_tsvector('english', coalesce(tasks.title, '') || ' ' || coalesce(tasks.description, '')) @@ plainto_tsquery('english', :search_term)")
                    ).params(search_term=search_term)
                except:
                    # Fallback to basic LIKE search
                    statement = statement.where(
                        (Task.title.ilike(f"%{search_term}%")) |
                        (Task.description.is_not(None) & Task.description.ilike(f"%{search_term}%"))
                    )

            # Handle tags separately with join (since it's a many-to-many relationship)
            if filters.get("tags"):
                tag_ids = filters["tags"]
                if isinstance(tag_ids, list) and len(tag_ids) > 0:
                    from models import TaskTag
                    # Join with TaskTag and filter by tag IDs
                    statement = statement.join(TaskTag).where(TaskTag.tag_id.in_(tag_ids))

        # Apply sorting
        sort_field = filters.get("sort", "created_at") if filters else "created_at"
        sort_order = filters.get("sort_order", "desc") if filters else "desc"
        secondary_sort = filters.get("secondary_sort", "created_at") if filters else "created_at"
        secondary_sort_order = filters.get("secondary_sort_order", "desc") if filters else "desc"

        # Primary sort
        if sort_field == "priority":
            if sort_order == "desc":
                statement = statement.order_by(Task.priority.desc())
            else:
                statement = statement.order_by(Task.priority.asc())
        elif sort_field == "due_date":
            if sort_order == "desc":
                statement = statement.order_by(Task.due_date.desc())
            else:
                statement = statement.order_by(Task.due_date.asc())
        elif sort_field == "title":
            if sort_order == "desc":
                statement = statement.order_by(Task.title.desc())
            else:
                statement = statement.order_by(Task.title.asc())
        elif sort_field == "completed":
            if sort_order == "desc":
                statement = statement.order_by(Task.completed.desc())
            else:
                statement = statement.order_by(Task.completed.asc())
        else:  # Default to created_at
            if sort_order == "desc":
                statement = statement.order_by(Task.created_at.desc())
            else:
                statement = statement.order_by(Task.created_at.asc())

        # Secondary sort (for tie-breaking)
        if secondary_sort and secondary_sort != sort_field:
            if secondary_sort == "priority":
                if secondary_sort_order == "desc":
                    statement = statement.order_by(Task.priority.desc())
                else:
                    statement = statement.order_by(Task.priority.asc())
            elif secondary_sort == "due_date":
                if secondary_sort_order == "desc":
                    statement = statement.order_by(Task.due_date.desc())
                else:
                    statement = statement.order_by(Task.due_date.asc())
            elif secondary_sort == "title":
                if secondary_sort_order == "desc":
                    statement = statement.order_by(Task.title.desc())
                else:
                    statement = statement.order_by(Task.title.asc())
            elif secondary_sort == "completed":
                if secondary_sort_order == "desc":
                    statement = statement.order_by(Task.completed.desc())
                else:
                    statement = statement.order_by(Task.completed.asc())
            elif secondary_sort == "created_at":
                if secondary_sort_order == "desc":
                    statement = statement.order_by(Task.created_at.desc())
                else:
                    statement = statement.order_by(Task.created_at.asc())

        # Apply pagination
        limit = filters.get("limit", 50) if filters else 50
        offset = filters.get("offset", 0) if filters else 0

        statement = statement.offset(offset).limit(limit)

        return session.exec(statement).all()

    @staticmethod
    def get_task_by_id(session: Session, task_id: int, user_id: str) -> Optional[Task]:
        """Get a specific task by ID for a user"""
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        return session.exec(statement).first()

    @staticmethod
    def create_task(session: Session, task: Task, tag_ids: Optional[List[int]] = None) -> Task:
        """
        Create a new task with optional tag associations

        Args:
            session: Database session
            task: Task object to create
            tag_ids: Optional list of tag IDs to associate with the task

        Returns:
            Created Task object
        """
        session.add(task)
        session.commit()
        session.refresh(task)

        # Associate tags if provided
        if tag_ids:
            from models import TaskTag
            for tag_id in tag_ids:
                task_tag = TaskTag(task_id=task.id, tag_id=tag_id)
                session.add(task_tag)
            session.commit()
            session.refresh(task)

        # Create audit log for task creation
        TaskService.create_audit_log(
            session=session,
            user_id=task.user_id,
            action="task.created",
            resource_type="task",
            resource_id=str(task.id),
            action_details={
                "task_id": task.id,
                "title": task.title,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "recurrence_pattern": task.recurrence_pattern,
                "tags_added": tag_ids
            }
        )

        return task

    @staticmethod
    def update_task(
        session: Session,
        task_id: int,
        user_id: str,
        task_data: dict,
        tag_ids: Optional[List[int]] = None
    ) -> Optional[Task]:
        """
        Update a task with optional tag association updates

        Args:
            session: Database session
            task_id: ID of the task to update
            user_id: User ID for authorization
            task_data: Dictionary of fields to update
            tag_ids: Optional list of tag IDs to associate with the task (replaces existing)

        Returns:
            Updated Task object or None if not found
        """
        existing_task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if existing_task:
            # Store original values for audit
            original_values = {
                "title": existing_task.title,
                "description": existing_task.description,
                "priority": existing_task.priority,
                "due_date": existing_task.due_date,
                "completed": existing_task.completed,
                "recurrence_pattern": existing_task.recurrence_pattern
            }

            # Update task fields
            for key, value in task_data.items():
                if hasattr(existing_task, key):
                    setattr(existing_task, key, value)

            existing_task.updated_at = datetime.utcnow()
            session.add(existing_task)

            # Update tag associations if provided
            if tag_ids is not None:
                from models import TaskTag
                # Remove existing tag associations
                stmt_delete = select(TaskTag).where(TaskTag.task_id == task_id)
                existing_task_tags = session.exec(stmt_delete).all()
                for task_tag in existing_task_tags:
                    session.delete(task_tag)

                # Add new tag associations
                for tag_id in tag_ids:
                    task_tag = TaskTag(task_id=task_id, tag_id=tag_id)
                    session.add(task_tag)

            session.commit()
            session.refresh(existing_task)

            # Create audit log for task update
            changes = {}
            for key, new_value in task_data.items():
                if key in original_values and original_values[key] != new_value:
                    changes[key] = {
                        "old": str(original_values[key]) if original_values[key] else None,
                        "new": str(new_value) if new_value else None
                    }

            TaskService.create_audit_log(
                session=session,
                user_id=user_id,
                action="task.updated",
                resource_type="task",
                resource_id=str(task_id),
                action_details={
                    "task_id": task_id,
                    "updated_fields": list(changes.keys()),
                    "changes": changes,
                    "updated_at": existing_task.updated_at.isoformat()
                }
            )

            return existing_task
        return None

    @staticmethod
    def delete_task(session: Session, task_id: int, user_id: str) -> bool:
        """
        Delete a task and its associated tags

        Args:
            session: Database session
            task_id: ID of the task to delete
            user_id: User ID for authorization

        Returns:
            bool: True if task was deleted, False otherwise
        """
        # First delete associated task-tag relationships
        from models import TaskTag
        task_tag_stmt = select(TaskTag).where(TaskTag.task_id == task_id)
        task_tags = session.exec(task_tag_stmt).all()

        for task_tag in task_tags:
            session.delete(task_tag)

        # Then delete the task itself
        existing_task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if existing_task:
            task_title = existing_task.title
            session.delete(existing_task)
            session.commit()

            # Create audit log for task deletion
            TaskService.create_audit_log(
                session=session,
                user_id=user_id,
                action="task.deleted",
                resource_type="task",
                resource_id=str(task_id),
                action_details={
                    "task_id": task_id,
                    "title": task_title,
                    "deleted_at": datetime.utcnow().isoformat()
                }
            )

            return True
        return False

    @staticmethod
    def toggle_task_completion(session: Session, task_id: int, user_id: str, completed: bool) -> Optional[Task]:
        """
        Toggle task completion status with recurrence handling

        Args:
            session: Database session
            task_id: ID of the task to update
            user_id: User ID for authorization
            completed: New completion status

        Returns:
            Updated Task object or None if not found
        """
        existing_task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if existing_task:
            # Store original values for audit
            original_completed = existing_task.completed

            existing_task.completed = completed
            existing_task.updated_at = datetime.utcnow()

            next_task = None
            # Handle recurring task completion
            if existing_task.recurrence_pattern and completed and existing_task.next_occurrence:
                # For recurring tasks, create next occurrence when completed
                try:
                    from services.recurrence_service import RecurrenceService
                    next_task = RecurrenceService.create_next_occurrence(existing_task)
                    if next_task:
                        session.add(next_task)
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Failed to create next occurrence: {str(e)}")

            session.add(existing_task)
            session.commit()
            session.refresh(existing_task)

            # Create audit log for task completion
            TaskService.create_audit_log(
                session=session,
                user_id=user_id,
                action="task.completed" if completed else "task.updated",
                resource_type="task",
                resource_id=str(task_id),
                action_details={
                    "task_id": task_id,
                    "previous_status": original_completed,
                    "new_status": completed,
                    "completed_at": datetime.utcnow().isoformat() if completed else None,
                    "is_recurring": bool(existing_task.recurrence_pattern),
                    "next_occurrence_created": next_task.id if next_task else None
                }
            )

            return existing_task
        return None

    @staticmethod
    def complete_task(
        session: Session,
        task_id: int,
        user_id: str,
        mark_series_complete: bool = False
    ) -> Optional[Task]:
        """
        Complete a task with options for recurring tasks

        Args:
            session: Database session
            task_id: ID of the task to complete
            user_id: User ID for authorization
            mark_series_complete: For recurring tasks, whether to complete the entire series

        Returns:
            Completed Task object or None if not found
        """
        existing_task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if existing_task:
            # Store original values for audit
            original_completed = existing_task.completed
            original_occurrences_remaining = existing_task.occurrences_remaining

            existing_task.completed = True
            existing_task.updated_at = datetime.utcnow()

            next_task = None
            # Handle recurring task completion
            if existing_task.recurrence_pattern and not mark_series_complete:
                # Create next occurrence for series
                try:
                    from services.recurrence_service import RecurrenceService
                    next_task = RecurrenceService.create_next_occurrence(existing_task)
                    if next_task:
                        session.add(next_task)
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Failed to create next occurrence: {str(e)}")
            elif existing_task.recurrence_pattern and mark_series_complete:
                # Mark entire series as completed (for recurring tasks with parent_id)
                # This would update the parent task to mark series complete
                if existing_task.parent_task_id is None:
                    # This is the parent task - mark all future occurrences as completed
                    existing_task.occurrences_remaining = 0
                    existing_task.recurrence_pattern = None  # Stop recurrence

            session.add(existing_task)
            session.commit()
            session.refresh(existing_task)

            # Create audit log for task completion
            TaskService.create_audit_log(
                session=session,
                user_id=user_id,
                action="task.completed",
                resource_type="task",
                resource_id=str(task_id),
                action_details={
                    "task_id": task_id,
                    "previous_status": original_completed,
                    "completed_at": datetime.utcnow().isoformat(),
                    "mark_series_complete": mark_series_complete,
                    "was_recurring": bool(existing_task.recurrence_pattern),
                    "next_occurrence_created": next_task.id if next_task else None,
                    "occurrences_remaining_after": existing_task.occurrences_remaining if hasattr(existing_task, 'occurrences_remaining') else None
                }
            )

            return existing_task
        return None

    @staticmethod
    def complete_recurring_task(
        session: Session,
        task_id: int,
        user_id: str,
        mark_series_complete: bool = False,
        modify_future_occurrences: bool = False,
        skip_next_occurrence: bool = False,
        recurrence_action: str = "create_next",
        create_next_occurrence: bool = True
    ) -> Optional[Task]:
        """
        Complete a recurring task with advanced options

        Args:
            session: Database session
            task_id: ID of the task to complete
            user_id: User ID for authorization
            mark_series_complete: Whether to complete the entire series
            modify_future_occurrences: Whether to modify future occurrences
            skip_next_occurrence: Whether to skip creating the next occurrence
            recurrence_action: Action to take ("create_next", "skip", "end_series")
            create_next_occurrence: Whether to create next occurrence

        Returns:
            Completed Task object or None if not found
        """
        # Get the task to complete
        existing_task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if not existing_task:
            return None

        # Store original values for audit
        original_completed = existing_task.completed
        original_occurrences_remaining = existing_task.occurrences_remaining

        # Mark as completed
        existing_task.completed = True
        existing_task.updated_at = datetime.utcnow()

        next_task = None
        # Handle recurrence based on action
        if existing_task.recurrence_pattern and not mark_series_complete:
            if recurrence_action == "create_next" and create_next_occurrence:
                # Create next occurrence based on recurrence pattern
                try:
                    from services.recurrence_service import RecurrenceService
                    next_task = RecurrenceService.create_next_occurrence(existing_task)
                    if next_task:
                        session.add(next_task)
                        # Update occurrences_remaining if applicable
                        if existing_task.occurrences_remaining is not None:
                            existing_task.occurrences_remaining -= 1
                            if existing_task.occurrences_remaining <= 0:
                                # No more occurrences, mark series as complete
                                existing_task.completed = True
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Failed to create next occurrence: {str(e)}")
            elif recurrence_action == "skip" or skip_next_occurrence:
                # Skip creating next occurrence but update recurrence data
                if existing_task.occurrences_remaining is not None:
                    existing_task.occurrences_remaining -= 1
                    if existing_task.occurrences_remaining <= 0:
                        existing_task.completed = True
            elif recurrence_action == "end_series":
                # Mark the series as completed by preventing future occurrences
                existing_task.occurrences_remaining = 0
                existing_task.completed = True
                existing_task.recurrence_pattern = None  # Stop recurrence
        elif existing_task.recurrence_pattern and mark_series_complete:
            # Mark entire series as completed
            # For recurring tasks, update parent task to mark series complete
            if existing_task.parent_task_id:
                # Update parent task to prevent future occurrences
                parent_task = session.exec(
                    select(Task).where(Task.id == existing_task.parent_task_id)
                ).first()
                if parent_task:
                    parent_task.occurrences_remaining = 0
                    parent_task.completed = True
                    session.add(parent_task)
            else:
                # This is a parent task, mark all future occurrences as cancelled
                existing_task.occurrences_remaining = 0
                existing_task.recurrence_pattern = None  # Stop recurrence

        session.add(existing_task)
        session.commit()
        session.refresh(existing_task)

        # Create audit log for recurring task completion
        TaskService.create_audit_log(
            session=session,
            user_id=user_id,
            action="task.completed",
            resource_type="task",
            resource_id=str(task_id),
            action_details={
                "task_id": task_id,
                "previous_status": original_completed,
                "completed_at": datetime.utcnow().isoformat(),
                "mark_series_complete": mark_series_complete,
                "modify_future_occurrences": modify_future_occurrences,
                "skip_next_occurrence": skip_next_occurrence,
                "recurrence_action": recurrence_action,
                "was_recurring": bool(existing_task.recurrence_pattern),
                "next_occurrence_created": next_task.id if next_task else None,
                "occurrences_remaining_after": existing_task.occurrences_remaining,
                "is_parent_task": existing_task.parent_task_id is None and bool(existing_task.recurrence_pattern)
            }
        )

        return existing_task

    @staticmethod
    def create_audit_log(session: Session, user_id: str, action: str, resource_type: str, resource_id: str, action_details: Dict[str, Any]):
        """
        Create an audit log entry for the action performed

        Args:
            session: Database session
            user_id: User ID performing the action
            action: Action performed (e.g., task.created, task.updated)
            resource_type: Type of resource (task, user, etc.)
            resource_id: ID of the resource
            action_details: Details about the action
        """
        try:
            from models import AuditLog

            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=str(resource_id),
                action_details=action_details,
                timestamp=datetime.utcnow()
            )

            session.add(audit_log)
            session.commit()
            return audit_log
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to create audit log: {str(e)}")
            return None
        