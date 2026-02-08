"""MCP Tools for Task Operations"""

from typing import Dict, Any, List
from services.task_service import TaskService
from models import Task
from sqlmodel import Session


class TaskMCPTools:
    """Collection of MCP tools for task operations"""

    @staticmethod
    def add_task(
        session: Session,
        user_id: str,
        title: str,
        description: str = None,
        priority: str = "medium",
        due_date: str = None,
        tag_ids: List[int] = None,
        recurrence_pattern: str = None,
        recurrence_config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a new task with advanced features and emit events"""
        try:
            from datetime import datetime
            from dateutil.parser import parse
            from services.event_publisher import EventPublisher
            from events.schemas.event_envelope import EventType, TaskCreatedEventData

            # Parse due_date if provided
            parsed_due_date = None
            if due_date:
                parsed_due_date = parse(due_date)

            # Validate priority
            if priority not in ["low", "medium", "high"]:
                return {
                    "success": False,
                    "error": "Priority must be one of: low, medium, high"
                }

            # Validate recurrence pattern if provided
            if recurrence_pattern:
                valid_patterns = ["daily", "weekly", "monthly", "yearly", "custom"]
                if recurrence_pattern not in valid_patterns:
                    return {
                        "success": False,
                        "error": f"Recurrence pattern must be one of: {valid_patterns}"
                    }

            task = Task(
                user_id=user_id,
                title=title,
                description=description,
                priority=priority,
                due_date=parsed_due_date,
                recurrence_pattern=recurrence_pattern,
                recurrence_config=recurrence_config,
                completed=False
            )

            created_task = TaskService.create_task(session, task, tag_ids)

            # Emit task created event
            event_data = TaskCreatedEventData(
                task_id=created_task.id,
                user_id=user_id,
                title=title,
                description=description,
                priority=priority,
                due_date=parsed_due_date,
                recurrence_pattern=recurrence_pattern,
                tag_ids=tag_ids,
                created_at=created_task.created_at
            )

            event = EventPublisher.create_task_event(
                event_type=EventType.TASK_CREATED,
                user_id=user_id,
                data=event_data.dict()
            )

            # Publish the event asynchronously
            import asyncio
            asyncio.create_task(EventPublisher.publish_event(event))

            return {
                "success": True,
                "task": {
                    "id": created_task.id,
                    "title": created_task.title,
                    "description": created_task.description,
                    "completed": created_task.completed,
                    "priority": created_task.priority,
                    "due_date": created_task.due_date.isoformat() if created_task.due_date else None,
                    "recurrence_pattern": created_task.recurrence_pattern,
                    "tags": [tag.name for tag in created_task.tags]
                },
                "event_published": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def list_tasks(
        session: Session,
        user_id: str,
        status: str = "all",
        priority: List[str] = None,
        tags: List[int] = None,
        search: str = None,
        due_date_from: str = None,
        due_date_to: str = None,
        sort: str = "created_at",
        sort_order: str = "desc",
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """List user's tasks with advanced filtering and sorting"""
        try:
            from dateutil.parser import parse
            from datetime import datetime

            # Prepare filters
            filters = {
                "status": status,
                "priority": priority,
                "tags": tags,
                "search": search,
                "sort": sort,
                "sort_order": sort_order,
                "limit": limit,
                "offset": offset
            }

            # Parse due dates if provided
            if due_date_from:
                filters["due_date_from"] = parse(due_date_from)
            if due_date_to:
                filters["due_date_to"] = parse(due_date_to)

            # Get tasks with filters
            tasks = TaskService.get_tasks_by_user(session, user_id, filters)

            task_list = [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "completed": t.completed,
                    "priority": t.priority,
                    "due_date": t.due_date.isoformat() if t.due_date else None,
                    "tags": [tag.name for tag in t.tags] if hasattr(t, 'tags') else [],
                    "recurrence_pattern": t.recurrence_pattern
                }
                for t in tasks
            ]

            return {
                "success": True,
                "tasks": task_list,
                "count": len(task_list),
                "filters_applied": filters
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def search_tasks(
        session: Session,
        user_id: str,
        query: str,
        priority: List[str] = None,
        tags: List[int] = None,
        status: str = "all",
        due_date_from: str = None,
        due_date_to: str = None,
        sort: str = "relevance",
        sort_order: str = "desc",
        limit: int = 50
    ) -> Dict[str, Any]:
        """Search tasks with natural language query and advanced filters"""
        try:
            from dateutil.parser import parse
            from services.search_service import SearchService

            # Prepare filters
            filters = {
                "priority": priority,
                "tags": tags,
                "status": status,
                "due_date_from": parse(due_date_from) if due_date_from else None,
                "due_date_to": parse(due_date_to) if due_date_to else None,
                "sort": sort,
                "sort_order": sort_order
            }

            # Perform search with advanced filters
            search_results = SearchService.search_tasks_with_filters(
                session=session,
                user_id=user_id,
                query=query,
                filters=filters
            )

            result_list = [
                {
                    "id": result["task"].id,
                    "title": result["task"].title,
                    "description": result["task"].description,
                    "completed": result["task"].completed,
                    "priority": result["task"].priority,
                    "due_date": result["task"].due_date.isoformat() if result["task"].due_date else None,
                    "tags": [tag.name for tag in result["task"].tags] if hasattr(result["task"], 'tags') else [],
                    "recurrence_pattern": result["task"].recurrence_pattern,
                    "relevance_score": result.get("rank", 0.0)
                }
                for result in search_results
            ]

            return {
                "success": True,
                "tasks": result_list,
                "count": len(result_list),
                "query": query,
                "filters_applied": filters
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def complete_task(session: Session, user_id: str, task_id: int, completed: bool = True) -> Dict[str, Any]:
        """Mark a task as complete or pending with event emission"""
        try:
            from services.event_publisher import EventPublisher
            from events.schemas.event_envelope import EventType

            # First get the task to check if it belongs to the user
            task = TaskService.get_task_by_id(session, task_id, user_id)
            if not task:
                return {
                    "success": False,
                    "error": "Task not found or doesn't belong to user"
                }

            updated_task = TaskService.toggle_task_completion(session, task_id, user_id, completed)
            if updated_task:
                # Emit task completion event
                event_data = {
                    "task_id": updated_task.id,
                    "user_id": user_id,
                    "completed": completed,
                    "was_recurring": updated_task.is_recurring if hasattr(updated_task, 'is_recurring') else False,
                    "completed_at": updated_task.updated_at,
                    "has_next_occurrence": updated_task.next_occurrence is not None if hasattr(updated_task, 'next_occurrence') else False
                }

                event = EventPublisher.create_task_event(
                    event_type=EventType.TASK_COMPLETED if completed else EventType.TASK_UPDATED,
                    user_id=user_id,
                    data=event_data,
                    task_id=updated_task.id
                )

                # Publish the event asynchronously
                import asyncio
                asyncio.create_task(EventPublisher.publish_event(event))

                return {
                    "success": True,
                    "task": {
                        "id": updated_task.id,
                        "title": updated_task.title,
                        "description": updated_task.description,
                        "completed": updated_task.completed
                    },
                    "event_published": True
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to update task"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def update_task(
        session: Session,
        user_id: str,
        task_id: int,
        title: str = None,
        description: str = None,
        priority: str = None,
        due_date: str = None,
        completed: bool = None,
        tag_ids: List[int] = None,
        recurrence_pattern: str = None,
        recurrence_config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Update a task with advanced features and emit events"""
        try:
            from dateutil.parser import parse
            from services.event_publisher import EventPublisher
            from events.schemas.event_envelope import EventType

            # First get the task to check if it belongs to the user
            existing_task = TaskService.get_task_by_id(session, task_id, user_id)
            if not existing_task:
                return {
                    "success": False,
                    "error": "Task not found or doesn't belong to user"
                }

            # Validate priority if provided
            if priority and priority not in ["low", "medium", "high"]:
                return {
                    "success": False,
                    "error": "Priority must be one of: low, medium, high"
                }

            # Validate recurrence pattern if provided
            if recurrence_pattern:
                valid_patterns = ["daily", "weekly", "monthly", "yearly", "custom"]
                if recurrence_pattern not in valid_patterns:
                    return {
                        "success": False,
                        "error": f"Recurrence pattern must be one of: {valid_patterns}"
                    }

            # Parse due_date if provided
            parsed_due_date = None
            if due_date:
                parsed_due_date = parse(due_date)

            # Prepare update data and track changes
            update_data = {}
            changes = {}
            if title is not None and title != existing_task.title:
                update_data['title'] = title
                changes['title'] = {'old': existing_task.title, 'new': title}
            if description is not None and description != existing_task.description:
                update_data['description'] = description
                changes['description'] = {'old': existing_task.description, 'new': description}
            if priority is not None and priority != existing_task.priority:
                update_data['priority'] = priority
                changes['priority'] = {'old': existing_task.priority, 'new': priority}
            if due_date is not None and parsed_due_date != existing_task.due_date:
                update_data['due_date'] = parsed_due_date
                changes['due_date'] = {
                    'old': existing_task.due_date.isoformat() if existing_task.due_date else None,
                    'new': parsed_due_date.isoformat() if parsed_due_date else None
                }
            if completed is not None and completed != existing_task.completed:
                update_data['completed'] = completed
                changes['completed'] = {'old': existing_task.completed, 'new': completed}
            if recurrence_pattern is not None and recurrence_pattern != existing_task.recurrence_pattern:
                update_data['recurrence_pattern'] = recurrence_pattern
                changes['recurrence_pattern'] = {'old': existing_task.recurrence_pattern, 'new': recurrence_pattern}
            if recurrence_config is not None and recurrence_config != existing_task.recurrence_config:
                update_data['recurrence_config'] = recurrence_config
                changes['recurrence_config'] = {'old': existing_task.recurrence_config, 'new': recurrence_config}

            updated_task = TaskService.update_task(session, task_id, user_id, update_data, tag_ids)
            if updated_task:
                # Emit task updated event if there were actual changes
                if changes:
                    event_data = {
                        "task_id": updated_task.id,
                        "user_id": user_id,
                        "changes": changes,
                        "updated_fields": list(changes.keys()),
                        "updated_at": updated_task.updated_at
                    }

                    event = EventPublisher.create_task_event(
                        event_type=EventType.TASK_UPDATED,
                        user_id=user_id,
                        data=event_data,
                        task_id=updated_task.id
                    )

                    # Publish the event asynchronously
                    import asyncio
                    asyncio.create_task(EventPublisher.publish_event(event))

                return {
                    "success": True,
                    "task": {
                        "id": updated_task.id,
                        "title": updated_task.title,
                        "description": updated_task.description,
                        "completed": updated_task.completed,
                        "priority": updated_task.priority,
                        "due_date": updated_task.due_date.isoformat() if updated_task.due_date else None,
                        "recurrence_pattern": updated_task.recurrence_pattern,
                        "tags": [tag.name for tag in updated_task.tags]
                    },
                    "changes_made": len(changes) > 0,
                    "changed_fields": list(changes.keys())
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to update task"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def delete_task(session: Session, user_id: str, task_id: int) -> Dict[str, Any]:
        """Delete a task with event emission"""
        from datetime import datetime
        from services.event_publisher import EventPublisher
        from events.schemas.event_envelope import EventType

        try:
            # First get the task to emit event with its details
            task = TaskService.get_task_by_id(session, task_id, user_id)
            if not task:
                return {
                    "success": False,
                    "error": "Task not found or doesn't belong to user"
                }

            success = TaskService.delete_task(session, task_id, user_id)
            if success:
                # Emit task deletion event
                event_data = {
                    "task_id": task_id,
                    "user_id": user_id,
                    "title": task.title,
                    "deleted_at": datetime.utcnow()
                }

                event = EventPublisher.create_task_event(
                    event_type=EventType.TASK_DELETED,
                    user_id=user_id,
                    data=event_data,
                    task_id=task_id
                )

                # Publish the event asynchronously
                import asyncio
                asyncio.create_task(EventPublisher.publish_event(event))

                return {
                    "success": True,
                    "message": "Task deleted successfully",
                    "event_published": True
                }
            else:
                return {
                    "success": False,
                    "error": "Task not found or doesn't belong to user"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }