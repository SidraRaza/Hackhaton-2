from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from datetime import datetime

from database import get_session
from models import Tag, TaskTag, Task, TagCreate, TagUpdate
from auth import get_current_user
from services.tag_service import TagService

router = APIRouter(prefix="/tags", tags=["tags"])  


@router.get("", response_model=List[Tag])
async def list_tags(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Get all tags for the current user"""
    user_id = current_user  
    tags = TagService.get_tags_by_user(session, user_id)
    return tags


@router.post("", response_model=Tag, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Create a new tag for the current user"""
    user_id = current_user["id"]

    # Check if tag with this name already exists for the user
    existing_tag = session.exec(
        select(Tag).where(
            Tag.user_id == user_id,
            Tag.name == tag_data.name
        )
    ).first()

    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag with this name already exists for the user"
        )

    # Create tag with user_id from current user
    tag = Tag(
        user_id=user_id,
        name=tag_data.name,
        color=tag_data.color or "#3B82F6"
    )

    created_tag = TagService.create_tag(session, tag)
    return created_tag


@router.get("/{tag_id}", response_model=Tag)
async def get_tag(
    tag_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific tag by ID"""
    user_id = current_user["id"]
    tag = TagService.get_tag_by_id(session, tag_id, user_id)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found or doesn't belong to user"
        )

    return tag


@router.put("/{tag_id}", response_model=Tag)
async def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Update a tag"""
    user_id = current_user["id"]

    # Verify the tag belongs to the user
    existing_tag = session.exec(
        select(Tag).where(
            Tag.id == tag_id,
            Tag.user_id == user_id
        )
    ).first()

    if not existing_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found or doesn't belong to user"
        )

    # Check if new name conflicts with another tag for the user
    if tag_data.name and tag_data.name != existing_tag.name:
        name_conflict = session.exec(
            select(Tag).where(
                Tag.user_id == user_id,
                Tag.name == tag_data.name,
                Tag.id != tag_id  # Exclude current tag from check
            )
        ).first()

        if name_conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag with this name already exists for the user"
            )

    # Prepare update data
    update_data = {}
    if tag_data.name is not None:
        update_data["name"] = tag_data.name
    if tag_data.color is not None:
        update_data["color"] = tag_data.color

    # Update tag
    updated_tag = TagService.update_tag(session, tag_id, user_id, update_data)
    if not updated_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    return updated_tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Delete a tag and its associations"""
    user_id = current_user["id"]

    success = TagService.delete_tag(session, tag_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found or doesn't belong to user"
        )

    return


@router.get("/{tag_id}/tasks", response_model=List[Task])
async def get_tasks_by_tag(
    tag_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Get all tasks associated with a specific tag"""
    user_id = current_user["id"]

    # First verify the tag belongs to the user
    tag = session.exec(
        select(Tag).where(
            Tag.id == tag_id,
            Tag.user_id == user_id
        )
    ).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found or doesn't belong to user"
        )

    tasks = TagService.get_tasks_for_tag(session, tag_id, user_id)
    return tasks


@router.post("/{tag_id}/tasks/{task_id}", status_code=status.HTTP_201_CREATED)
async def associate_task_with_tag(
    tag_id: int,
    task_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Associate a task with a tag"""
    user_id = current_user["id"]

    # Verify both tag and task belong to the user
    tag = session.exec(
        select(Tag).where(
            Tag.id == tag_id,
            Tag.user_id == user_id
        )
    ).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found or doesn't belong to user"
        )

    task = session.exec(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or doesn't belong to user"
        )

    # Create association
    success = TagService.associate_task_with_tag(session, task_id, tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Association already exists"
        )

    return


@router.delete("/{tag_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_task_from_tag(
    tag_id: int,
    task_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Remove a task from a tag"""
    user_id = current_user["id"]

    # Verify both tag and task belong to the user
    tag = session.exec(
        select(Tag).where(
            Tag.id == tag_id,
            Tag.user_id == user_id
        )
    ).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found or doesn't belong to user"
        )

    task = session.exec(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or doesn't belong to user"
        )

    # Remove association
    success = TagService.remove_task_from_tag(session, task_id, tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Association not found"
        )

    return