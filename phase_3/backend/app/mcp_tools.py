"""
MCP (Model Context Protocol) Tools Implementation
This module implements the actual tools that the AI assistant can call
to perform task management operations.
"""
from typing import Dict, Any, Optional
from sqlmodel import Session
from fastapi import Depends, HTTPException
from ..database import get_session
from ..models.task import Task
from ..models.conversation import Conversation
from ..models.message import Message
from .api.auth import get_current_user
from .schemas.user import User
from datetime import datetime
import logging


# Set up logging
logger = logging.getLogger(__name__)


async def create_task(
    db_session: Session,
    user: User,
    title: str,
    description: str = "",
    due_date: Optional[str] = None,
    priority: str = "medium"
) -> Dict[str, Any]:
    """
    Create a new task for the user

    Args:
        db_session: Database session
        user: Current user
        title: Title of the task
        description: Description of the task
        due_date: Due date in YYYY-MM-DD format
        priority: Priority level (low, medium, high)

    Returns:
        Dictionary with success status and task info
    """
    try:
        # Validate input
        if not title.strip():
            raise HTTPException(status_code=400, detail="Task title is required")

        # Log the operation for security auditing
        logger.info(f"User {user.id} creating task with title: {title}")

        # Prepare task data
        task_data = {
            "user_id": str(user.id),
            "title": title.strip(),
            "description": description.strip() if description else "",
            "completed": False,
            "priority": priority.lower()
        }

        # Validate priority
        if task_data["priority"] not in ["low", "medium", "high"]:
            raise HTTPException(status_code=400, detail="Priority must be low, medium, or high")

        # Handle due_date if provided
        if due_date:
            try:
                task_data["due_date"] = datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        # Create task
        task = Task(**task_data)
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        # Log successful creation
        logger.info(f"Task {task.id} created successfully for user {user.id}")

        return {
            "success": True,
            "task_id": str(task.id),
            "message": f"Task '{task.title}' created successfully"
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error for security auditing
        logger.error(f"Error creating task for user {user.id}: {str(e)}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")


async def update_task(
    db_session: Session,
    user: User,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: Optional[str] = None,
    completed: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Update an existing task

    Args:
        db_session: Database session
        user: Current user
        task_id: ID of the task to update
        title: New title (optional)
        description: New description (optional)
        due_date: New due date (optional)
        priority: New priority (optional)
        completed: New completion status (optional)

    Returns:
        Dictionary with success status and task info
    """
    try:
        # Log the operation for security auditing
        logger.info(f"User {user.id} attempting to update task {task_id}")

        # Get the task
        task = db_session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

        # Check user ownership - SECURITY CHECK
        if str(task.user_id) != str(user.id):
            logger.warning(f"Unauthorized access attempt: User {user.id} tried to update task {task_id} owned by {task.user_id}")
            raise HTTPException(status_code=403, detail="Unauthorized: Cannot modify another user's task")

        # Log the update attempt
        logger.info(f"User {user.id} authorized to update task {task_id}")

        # Update task fields if provided
        update_fields = ["title", "description", "due_date", "priority", "completed"]
        for field in update_fields:
            value = locals().get(field)
            if value is not None:
                if field == "title" and value.strip():
                    setattr(task, field, value.strip())
                elif field == "description":
                    setattr(task, field, value.strip() if value else "")
                elif field == "due_date" and value:
                    try:
                        setattr(task, field, datetime.strptime(value, "%Y-%m-%d"))
                    except ValueError:
                        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
                elif field == "priority" and value:
                    value = value.lower()
                    if value not in ["low", "medium", "high"]:
                        raise HTTPException(status_code=400, detail="Priority must be low, medium, or high")
                    setattr(task, field, value)
                elif field == "completed" and isinstance(value, bool):
                    setattr(task, field, value)

        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        # Log successful update
        logger.info(f"Task {task.id} updated successfully by user {user.id}")

        return {
            "success": True,
            "task_id": str(task.id),
            "message": f"Task '{task.title}' updated successfully"
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error for security auditing
        logger.error(f"Error updating task {task_id} for user {user.id}: {str(e)}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update task: {str(e)}")


async def delete_task(
    db_session: Session,
    user: User,
    task_id: str
) -> Dict[str, Any]:
    """
    Delete a task

    Args:
        db_session: Database session
        user: Current user
        task_id: ID of the task to delete

    Returns:
        Dictionary with success status
    """
    try:
        # Log the operation for security auditing
        logger.info(f"User {user.id} attempting to delete task {task_id}")

        # Get the task
        task = db_session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

        # Check user ownership - SECURITY CHECK
        if str(task.user_id) != str(user.id):
            logger.warning(f"Unauthorized access attempt: User {user.id} tried to delete task {task_id} owned by {task.user_id}")
            raise HTTPException(status_code=403, detail="Unauthorized: Cannot delete another user's task")

        # Log the deletion
        logger.info(f"User {user.id} authorized to delete task {task_id}")

        # Delete the task
        db_session.delete(task)
        db_session.commit()

        # Log successful deletion
        logger.info(f"Task {task_id} deleted successfully by user {user.id}")

        return {
            "success": True,
            "task_id": task_id,
            "message": f"Task deleted successfully"
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error for security auditing
        logger.error(f"Error deleting task {task_id} for user {user.id}: {str(e)}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete task: {str(e)}")


async def get_tasks(
    db_session: Session,
    user: User,
    filter_completed: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Get tasks for the user

    Args:
        db_session: Database session
        user: Current user
        filter_completed: Filter by completion status (optional)

    Returns:
        Dictionary with success status and tasks list
    """
    try:
        # Log the operation for security auditing
        logger.info(f"User {user.id} requesting tasks (filter_completed: {filter_completed})")

        from sqlmodel import select

        # Build query with user filter - SECURITY CHECK
        query = select(Task).where(Task.user_id == str(user.id))

        # Apply completion filter if specified
        if filter_completed is not None:
            query = query.where(Task.completed == filter_completed)

        # Execute query
        tasks = db_session.exec(query).all()

        # Log the number of tasks returned
        logger.info(f"Returning {len(tasks)} tasks for user {user.id}")

        # Format response
        tasks_list = []
        for task in tasks:
            task_dict = {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority
            }
            if task.due_date:
                task_dict["due_date"] = task.due_date.isoformat()
            tasks_list.append(task_dict)

        return {
            "success": True,
            "count": len(tasks_list),
            "tasks": tasks_list
        }
    except Exception as e:
        # Log the error for security auditing
        logger.error(f"Error retrieving tasks for user {user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get tasks: {str(e)}")


async def complete_task(
    db_session: Session,
    user: User,
    task_id: str,
    completed: bool
) -> Dict[str, Any]:
    """
    Mark a task as completed or not completed

    Args:
        db_session: Database session
        user: Current user
        task_id: ID of the task to update
        completed: Whether the task is completed

    Returns:
        Dictionary with success status and task info
    """
    try:
        # Log the operation for security auditing
        logger.info(f"User {user.id} attempting to update completion status of task {task_id} to {completed}")

        # Get the task
        task = db_session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

        # Check user ownership - SECURITY CHECK
        if str(task.user_id) != str(user.id):
            logger.warning(f"Unauthorized access attempt: User {user.id} tried to update completion status of task {task_id} owned by {task.user_id}")
            raise HTTPException(status_code=403, detail="Unauthorized: Cannot modify another user's task")

        # Log the completion update
        logger.info(f"User {user.id} authorized to update completion status of task {task_id}")

        # Update completion status
        task.completed = completed
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        status_str = "completed" if completed else "marked as incomplete"
        logger.info(f"Task {task.id} completion status updated to {status_str} by user {user.id}")

        return {
            "success": True,
            "task_id": str(task.id),
            "message": f"Task '{task.title}' {status_str} successfully"
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error for security auditing
        logger.error(f"Error updating completion status of task {task_id} for user {user.id}: {str(e)}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to complete task: {str(e)}")


# Collection of all MCP tools
MCP_TOOLS = {
    "create_task": create_task,
    "update_task": update_task,
    "delete_task": delete_task,
    "get_tasks": get_tasks,
    "complete_task": complete_task
}