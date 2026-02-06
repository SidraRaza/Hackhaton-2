from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID

from database import get_session
from utils.auth import get_current_user
from models.user import User
from models.task import Task, TaskCreate, TaskUpdate, TaskRead
from sqlmodel import Session
from app.services.task_service import TaskService

# Create router
router = APIRouter(prefix="/todos", tags=["todos"])

# Initialize service
task_service = TaskService()


@router.get("/", response_model=List[TaskRead])
def get_user_tasks(
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100
) -> List[TaskRead]:
    """
    Get all tasks for the current user with optional pagination.
    """
    tasks = task_service.get_tasks(db_session, current_user.id, skip=skip, limit=limit)
    return tasks


@router.post("/", response_model=TaskRead)
def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
) -> TaskRead:
    """
    Create a new task for the current user.
    """
    task = task_service.create_task(db_session, task_data, current_user.id)
    if not task:
        raise HTTPException(status_code=400, detail="Could not create task")
    return task


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
) -> TaskRead:
    """
    Get a specific task by ID for the current user.
    """
    task = task_service.get_task(db_session, task_id, current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskRead.model_validate(task)


@router.put("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
) -> TaskRead:
    """
    Update a specific task for the current user.
    """
    updated_task = task_service.update_task(db_session, task_id, task_data, current_user.id)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found or not authorized")
    return updated_task


@router.delete("/{task_id}")
def delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
) -> dict:
    """
    Delete a specific task for the current user.
    """
    success = task_service.delete_task(db_session, task_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found or not authorized")
    return {"success": True, "message": "Task deleted successfully"}