from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, create_engine, Session, select
from datetime import datetime
import json
from dapr_state_service import DaprStateService, get_dapr_state_service


class UserPreferences(SQLModel, table=True):
    """User preferences model for storing filter states and UI preferences"""
    __tablename__ = "user_preferences"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(unique=True, index=True)
    preferences: Dict[str, Any] = Field(default={}, sa_column_kwargs={
        "server_default": "'{}'::jsonb",
        "nullable": False
    })
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())

    class Config:
        arbitrary_types_allowed = True


class PreferenceService:
    """Service for managing user preferences including filter states using Dapr state store"""

    @staticmethod
    def get_user_preferences(session: Session, user_id: str) -> Dict[str, Any]:
        """
        Get user preferences using Dapr state store as cache, falling back to database
        Creates default if not exists

        Args:
            session: Database session
            user_id: User ID to get preferences for

        Returns:
            Dictionary of user preferences with defaults
        """
        # First try to get from Dapr state store cache
        dapr_service = get_dapr_state_service()
        cached_prefs = dapr_service.get_user_preferences(user_id)

        if cached_prefs:
            return cached_prefs

        # If not in cache, get from database
        statement = select(UserPreferences).where(UserPreferences.user_id == user_id)
        user_pref = session.exec(statement).first()

        if user_pref:
            # Cache in Dapr state store
            dapr_service.save_user_preferences(user_id, user_pref.preferences)
            return user_pref.preferences
        else:
            # Create default preferences for user
            default_prefs = {
                "task_filters": {
                    "priority": [],
                    "status": "all",
                    "search": "",
                    "sort": "created_at",
                    "sort_order": "desc",
                    "tags": [],
                    "due_date_from": None,
                    "due_date_to": None,
                    "recurrence_pattern": None
                },
                "ui_settings": {
                    "theme": "light",
                    "language": "en",
                    "timezone": "UTC"
                },
                "notifications": {
                    "email_enabled": True,
                    "browser_notifications": True,
                    "reminder_lead_times": ["1d", "1h"]  # 1 day, 1 hour before
                }
            }

            # Save to database
            pref_record = UserPreferences(user_id=user_id, preferences=default_prefs)
            session.add(pref_record)
            session.commit()

            # Also save to Dapr state store cache
            dapr_service.save_user_preferences(user_id, default_prefs)

            return default_prefs

    @staticmethod
    def update_user_preferences(session: Session, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user preferences using Dapr state store for caching

        Args:
            session: Database session
            user_id: User ID to update preferences for
            updates: Dictionary of preference updates

        Returns:
            Updated preferences dictionary
        """
        statement = select(UserPreferences).where(UserPreferences.user_id == user_id)
        user_pref = session.exec(statement).first()

        if user_pref:
            # Deep merge the updates
            merged_prefs = PreferenceService._deep_merge(user_pref.preferences, updates)
            user_pref.preferences = merged_prefs
            user_pref.updated_at = datetime.now()
            session.add(user_pref)
            session.commit()
            session.refresh(user_pref)

            # Update Dapr state store cache
            dapr_service = get_dapr_state_service()
            dapr_service.save_user_preferences(user_id, user_pref.preferences)

            return user_pref.preferences
        else:
            # Create new preferences record
            default_prefs = {
                "task_filters": {
                    "priority": [],
                    "status": "all",
                    "search": "",
                    "sort": "created_at",
                    "sort_order": "desc",
                    "tags": [],
                    "due_date_from": None,
                    "due_date_to": None,
                    "recurrence_pattern": None
                },
                "ui_settings": {
                    "theme": "light",
                    "language": "en",
                    "timezone": "UTC"
                },
                "notifications": {
                    "email_enabled": True,
                    "browser_notifications": True,
                    "reminder_lead_times": ["1d", "1h"]  # 1 day, 1 hour before
                }
            }
            merged_prefs = PreferenceService._deep_merge(default_prefs, updates)

            # Save to database
            pref_record = UserPreferences(user_id=user_id, preferences=merged_prefs)
            session.add(pref_record)
            session.commit()
            session.refresh(pref_record)

            # Also save to Dapr state store cache
            dapr_service = get_dapr_state_service()
            dapr_service.save_user_preferences(user_id, pref_record.preferences)

            return pref_record.preferences

    @staticmethod
    def _deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries

        Args:
            dict1: Base dictionary
            dict2: Dictionary to merge

        Returns:
            Merged dictionary
        """
        result = dict1.copy()

        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = PreferenceService._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    @staticmethod
    def get_task_filter_preferences(session: Session, user_id: str) -> Dict[str, Any]:
        """
        Get only task filter preferences for a user using Dapr cache

        Args:
            session: Database session
            user_id: User ID to get task filter preferences for

        Returns:
            Dictionary of task filter preferences
        """
        prefs = PreferenceService.get_user_preferences(session, user_id)
        return prefs.get("task_filters", {})

    @staticmethod
    def get_sort_preferences(session: Session, user_id: str) -> Dict[str, Any]:
        """
        Get sort preferences for a user using Dapr cache

        Args:
            session: Database session
            user_id: User ID to get sort preferences for

        Returns:
            Dictionary with primary and secondary sort preferences
        """
        prefs = PreferenceService.get_user_preferences(session, user_id)
        task_filters = prefs.get("task_filters", {})

        # Return sort preferences with defaults
        return {
            "primary": {
                "field": task_filters.get("sort", "created_at"),
                "order": task_filters.get("sort_order", "desc")
            },
            "secondary": {
                "field": task_filters.get("secondary_sort", "created_at"),
                "order": task_filters.get("secondary_sort_order", "desc")
            }
        }

    @staticmethod
    def update_sort_preferences(session: Session, user_id: str, sort_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update sort preferences for a user using Dapr cache

        Args:
            session: Database session
            user_id: User ID to update sort preferences for
            sort_config: Dictionary with primary and secondary sort configuration

        Returns:
            Updated sort preferences
        """
        # Prepare update structure for task filters
        filter_updates = {}

        if "primary" in sort_config:
            primary = sort_config["primary"]
            if "field" in primary:
                filter_updates["sort"] = primary["field"]
            if "order" in primary:
                filter_updates["sort_order"] = primary["order"]

        if "secondary" in sort_config:
            secondary = sort_config["secondary"]
            if "field" in secondary:
                filter_updates["secondary_sort"] = secondary["field"]
            if "order" in secondary:
                filter_updates["secondary_sort_order"] = secondary["order"]

        # Update task filter preferences which includes sort settings
        updated_filters = PreferenceService.update_task_filter_preferences(session, user_id, filter_updates)

        # Return the sort preferences in the expected format
        return {
            "primary": {
                "field": updated_filters.get("sort", "created_at"),
                "order": updated_filters.get("sort_order", "desc")
            },
            "secondary": {
                "field": updated_filters.get("secondary_sort", "created_at"),
                "order": updated_filters.get("secondary_sort_order", "desc")
            }
        }

    @staticmethod
    def update_task_filter_preferences(session: Session, user_id: str, filter_updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update only task filter preferences for a user using Dapr cache

        Args:
            session: Database session
            user_id: User ID to update task filter preferences for
            filter_updates: Dictionary of task filter updates

        Returns:
            Updated task filter preferences
        """
        updates = {"task_filters": filter_updates}
        prefs = PreferenceService.update_user_preferences(session, user_id, updates)
        return prefs.get("task_filters", {})

    @staticmethod
    def get_ui_settings(session: Session, user_id: str) -> Dict[str, Any]:
        """
        Get UI settings for a user using Dapr cache

        Args:
            session: Database session
            user_id: User ID to get UI settings for

        Returns:
            Dictionary of UI settings
        """
        prefs = PreferenceService.get_user_preferences(session, user_id)
        return prefs.get("ui_settings", {})

    @staticmethod
    def update_ui_settings(session: Session, user_id: str, ui_updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update UI settings for a user using Dapr cache

        Args:
            session: Database session
            user_id: User ID to update UI settings for
            ui_updates: Dictionary of UI setting updates

        Returns:
            Updated UI settings
        """
        updates = {"ui_settings": ui_updates}
        prefs = PreferenceService.update_user_preferences(session, user_id, updates)
        return prefs.get("ui_settings", {})