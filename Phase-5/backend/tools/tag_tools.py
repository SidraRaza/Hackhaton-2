"""MCP Tools for Tag Operations"""
from typing import Dict, Any, List
from sqlmodel import Session, select
from datetime import datetime

from models import Tag
from services.tag_service import TagService


class TagMCPTools:
    """Collection of MCP tools for tag operations"""

    @staticmethod
    def create_tag(
        session: Session,
        user_id: str,
        name: str,
        color: str = "#3B82F6"
    ) -> Dict[str, Any]:
        """Create a new tag for the user"""
        try:
            # Validate color format
            if color and not color.startswith("#") or len(color) != 7:
                return {
                    "success": False,
                    "error": "Color must be a valid hex color code (e.g., #3B82F6)"
                }

            # Check if tag already exists for user
            existing_tag = session.exec(
                select(Tag).where(
                    Tag.user_id == user_id,
                    Tag.name == name
                )
            ).first()

            if existing_tag:
                return {
                    "success": False,
                    "error": f"Tag with name '{name}' already exists"
                }

            tag = Tag(
                user_id=user_id,
                name=name,
                color=color
            )

            created_tag = TagService.create_tag(session, tag)
            return {
                "success": True,
                "tag": {
                    "id": created_tag.id,
                    "name": created_tag.name,
                    "color": created_tag.color,
                    "created_at": created_tag.created_at.isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def get_tags(session: Session, user_id: str) -> Dict[str, Any]:
        """Get all tags for a user"""
        try:
            tags = TagService.get_tags_by_user(session, user_id)
            tag_list = [
                {
                    "id": tag.id,
                    "name": tag.name,
                    "color": tag.color,
                    "created_at": tag.created_at.isoformat()
                }
                for tag in tags
            ]

            return {
                "success": True,
                "tags": tag_list,
                "count": len(tag_list)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def update_tag(
        session: Session,
        user_id: str,
        tag_id: int,
        name: str = None,
        color: str = None
    ) -> Dict[str, Any]:
        """Update a tag"""
        try:
            # First get the tag to check if it belongs to the user
            tag = TagService.get_tag_by_id(session, tag_id, user_id)
            if not tag:
                return {
                    "success": False,
                    "error": "Tag not found or doesn't belong to user"
                }

            update_data = {}
            if name is not None:
                update_data["name"] = name
            if color is not None:
                update_data["color"] = color

            updated_tag = TagService.update_tag(session, tag_id, user_id, update_data)
            if updated_tag:
                return {
                    "success": True,
                    "tag": {
                        "id": updated_tag.id,
                        "name": updated_tag.name,
                        "color": updated_tag.color,
                        "created_at": updated_tag.created_at.isoformat()
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to update tag"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def delete_tag(session: Session, user_id: str, tag_id: int) -> Dict[str, Any]:
        """Delete a tag"""
        try:
            success = TagService.delete_tag(session, tag_id, user_id)
            if success:
                return {
                    "success": True,
                    "message": "Tag deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Tag not found or doesn't belong to user"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def get_tasks_by_tag(session: Session, user_id: str, tag_id: int) -> Dict[str, Any]:
        """Get all tasks associated with a specific tag"""
        try:
            # First verify the tag belongs to the user
            tag = TagService.get_tag_by_id(session, tag_id, user_id)
            if not tag:
                return {
                    "success": False,
                    "error": "Tag not found or doesn't belong to user"
                }

            tasks = TagService.get_tasks_for_tag(session, tag_id, user_id)
            task_list = [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "priority": task.priority,
                    "due_date": task.due_date.isoformat() if task.due_date else None
                }
                for task in tasks
            ]

            return {
                "success": True,
                "tasks": task_list,
                "count": len(task_list),
                "tag_name": tag.name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }