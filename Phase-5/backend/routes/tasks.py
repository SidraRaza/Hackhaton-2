from fastapi import APIRouter, Depends, HTTPException, status, Body, Request, Query
from sqlmodel import Session
from typing import Dict, Any, List, Optional
from datetime import datetime
from typing_extensions import Annotated
import logging

from database import get_session
from models import Task, TaskCreate, TaskUpdate, PriorityEnum, RecurrencePatternEnum
from auth import get_current_user
from services.task_service import TaskService
from schemas.task import TaskRecurrenceCompleteRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tasks")


@router.get("")
def list_tasks(
    priority: Optional[List[PriorityEnum]] = Query(None),
    tags: Optional[List[int]] = Query(None),
    search: Optional[str] = Query(None),
    due_date_from: Optional[datetime] = Query(None),
    due_date_to: Optional[datetime] = Query(None),
    recurrence_pattern: Optional[RecurrencePatternEnum] = Query(None),
    status_filter: Annotated[Optional[str], Query(pattern=r"^(pending|completed|all)$")] = "all",
    sort: Annotated[Optional[str], Query(pattern=r"^(priority|due_date|created_at|title|completed)$")] = "created_at",
    sort_order: Annotated[Optional[str], Query(pattern=r"^(asc|desc)$")] = "desc",
    secondary_sort: Annotated[Optional[str], Query(pattern=r"^(priority|due_date|created_at|title|completed)$")] = "created_at",
    secondary_sort_order: Annotated[Optional[str], Query(pattern=r"^(asc|desc)$")] = "desc",
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    use_saved_filters: Optional[bool] = Query(default=False),
    save_filters: Optional[bool] = Query(default=False),
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """Get all tasks for the current user with advanced filtering and sorting"""
    from services.preference_service import PreferenceService

    # Determine which filters to use
    effective_filters = {
        "priority": priority,
        "tags": tags,
        "search": search,
        "due_date_from": due_date_from,
        "due_date_to": due_date_to,
        "recurrence_pattern": recurrence_pattern,
        "status": status_filter,
        "sort": sort,
        "sort_order": sort_order,
        "secondary_sort": secondary_sort,
        "secondary_sort_order": secondary_sort_order,
        "limit": limit,
        "offset": offset
    }

    # Use saved filters if requested
    if use_saved_filters:
        saved_filters = PreferenceService.get_task_filter_preferences(session, current_user)
        # Merge saved filters with query parameters (query params take precedence)
        for key, value in saved_filters.items():
            if effective_filters.get(key) is None and value is not None:
                effective_filters[key] = value

    # Save filters if requested
    if save_filters:
        # Only save non-default values
        filter_updates = {}
        for key, value in effective_filters.items():
            if key not in ["limit", "offset"] and value is not None:
                filter_updates[key] = value
        PreferenceService.update_task_filter_preferences(session, current_user, filter_updates)

    return TaskService.get_tasks_by_user(session, current_user, effective_filters)


@router.post("")
def create_task(
    task_data: TaskCreate,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """Create a new task for the current user with advanced features"""
    # Validate recurrence pattern requirements
    if task_data.recurrence_pattern and not task_data.due_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recurrence pattern requires a due date"
        )

    if task_data.recurrence_pattern == "custom" and not task_data.recurrence_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Custom recurrence pattern requires recurrence_config"
        )

    # Validate recurrence pattern
    if task_data.recurrence_pattern:
        try:
            from services.recurrence_service import RecurrenceService
            RecurrenceService.validate_pattern(
                task_data.recurrence_pattern,
                task_data.recurrence_config
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid recurrence pattern: {str(e)}"
            )
        except:
            pass

    # Create task with current user's ID
    task_dict = task_data.model_dump(exclude={"tag_ids"})
    task = Task(**task_dict, user_id=current_user)

    # Calculate next occurrence if recurring
    if task.recurrence_pattern and task.due_date:
        try:
            from services.recurrence_service import RecurrenceService
            task.next_occurrence = RecurrenceService.calculate_next_occurrence(
                task.recurrence_pattern,
                task.recurrence_config,
                task.due_date
            )
        except:
            pass

    created_task = TaskService.create_task(session, task, task_data.tag_ids)

    return created_task

@router.get("/analytics")  # ✅ YE PEHLE - /{task_id} se PEHLE
def get_task_analytics(
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """Get task analytics for the current user"""
    all_tasks = TaskService.get_tasks_by_user(session, current_user, {"limit": 1000})
    
    total_tasks = len(all_tasks)
    completed_tasks = len([t for t in all_tasks if t.completed])
    pending_tasks = total_tasks - completed_tasks
    
    priority_breakdown = {
        "high": len([t for t in all_tasks if t.priority == PriorityEnum.high]),
        "medium": len([t for t in all_tasks if t.priority == PriorityEnum.medium]),
        "low": len([t for t in all_tasks if t.priority == PriorityEnum.low])
    }
    
    recurring_tasks = len([t for t in all_tasks if t.recurrence_pattern])
    
    now = datetime.utcnow()
    overdue_tasks = len([
        t for t in all_tasks 
        if not t.completed and t.due_date and t.due_date < now
    ])
    
    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "completion_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2),
        "priority_breakdown": priority_breakdown,
        "recurring_tasks": recurring_tasks,
        "overdue_tasks": overdue_tasks
    }


@router.get("/{task_id}")
def get_task(
    task_id: int,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """Get a specific task by ID"""
    task = TaskService.get_task_by_id(session, task_id, current_user)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.put("/{task_id}")
def update_task(
    task_id: int,
    updated_task: TaskUpdate,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """Update a task with advanced features"""
    task = TaskService.get_task_by_id(session, task_id, current_user)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Validate recurrence pattern requirements if being updated
    if updated_task.recurrence_pattern:
        if updated_task.due_date is None and task.due_date is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recurrence pattern requires a due date"
            )

    if updated_task.recurrence_pattern == "custom" and updated_task.recurrence_config is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Custom recurrence pattern requires recurrence_config"
        )

    # Validate recurrence pattern
    if updated_task.recurrence_pattern:
        try:
            from services.recurrence_service import RecurrenceService
            RecurrenceService.validate_pattern(
                updated_task.recurrence_pattern,
                updated_task.recurrence_config
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid recurrence pattern: {str(e)}"
            )
        except:
            pass

    # Update with the new values
    update_data = updated_task.model_dump(exclude_unset=True)
    updated = TaskService.update_task(session, task_id, current_user, update_data, updated_task.tag_ids)

    return updated


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """Delete a task"""
    task = TaskService.get_task_by_id(session, task_id, current_user)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    success = TaskService.delete_task(session, task_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return {"message": "Task deleted successfully"}


@router.post("/{task_id}/complete")
def complete_task(
    task_id: int,
    mark_series_complete: bool = Body(default=False),
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """Complete a task with options for recurring tasks"""
    task = TaskService.get_task_by_id(session, task_id, current_user)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    completed_task = TaskService.complete_task(
        session,
        task_id,
        current_user,
        mark_series_complete=mark_series_complete
    )

    if not completed_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return completed_task


@router.post("/{task_id}/complete-recurrence")
def complete_recurring_task(
    task_id: int,
    request: TaskRecurrenceCompleteRequest,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """Special completion endpoint for recurring tasks with advanced options"""
    task = TaskService.get_task_by_id(session, task_id, current_user)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if not task.recurrence_pattern:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is not recurring"
        )

    completed_task = TaskService.complete_recurring_task(
        session,
        task_id,
        current_user,
        mark_series_complete=request.mark_series_complete,
        modify_future_occurrences=request.modify_future_occurrences,
        skip_next_occurrence=request.skip_next_occurrence,
        recurrence_action=request.recurrence_action,
        create_next_occurrence=request.create_next_occurrence
    )

    if not completed_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return completed_task


@router.patch("/{task_id}/complete")
async def toggle_task_completion(
    task_id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """Toggle task completion status"""
    try:
        body = await request.json()
        logger.info(f"📦 Received body: {body}")

        if "completed" not in body:
            logger.error("❌ 'completed' field missing from body")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="'completed' field is required in request body"
            )

        completed = body.get("completed")
        logger.info(f"✅ Completed value: {completed}, type: {type(completed)}")

        if not isinstance(completed, bool):
            logger.error(f"❌ 'completed' is not boolean: {completed}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="'completed' must be a boolean value"
            )

        task = TaskService.toggle_task_completion(
            session,
            task_id,
            current_user,
            completed
        )
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        logger.info(f"✅ Task {task_id} completion updated to {completed}")
        return task

    except ValueError as e:
        logger.error(f"❌ Invalid JSON: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid JSON in request body"
        )
