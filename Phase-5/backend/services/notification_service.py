"""
Notification Service for Browser Notifications
Handles browser notifications for task reminders
UPDATED: Integrated with WebSocket ConnectionManager
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from fastapi import WebSocket
import asyncio

from models import Task
from services.timezone_service import TimezoneService
from ws_manager import manager as ws_manager  # Import the WebSocket connection manager


logger = logging.getLogger(__name__)


class NotificationService:
    """Service for handling browser and other notifications"""

    # DEPRECATED: Use ws_manager instead
    # Keep for backward compatibility
    active_connections: List[WebSocket] = []

    @classmethod
    async def connect_websocket(cls, websocket: WebSocket):
        """
        DEPRECATED: Use ws_manager.connect() instead
        Add a new WebSocket connection for real-time notifications
        """
        logger.warning("Using deprecated connect_websocket. Use ws_manager.connect() instead")
        await websocket.accept()
        cls.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(cls.active_connections)}")

    @classmethod
    def disconnect_websocket(cls, websocket: WebSocket):
        """
        DEPRECATED: Use ws_manager.disconnect() instead
        Remove a WebSocket connection
        """
        logger.warning("Using deprecated disconnect_websocket. Use ws_manager.disconnect() instead")
        if websocket in cls.active_connections:
            cls.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total connections: {len(cls.active_connections)}")

    @classmethod
    async def broadcast_notification(cls, notification_data: Dict[str, Any]):
        """
        UPDATED: Now uses ws_manager for broadcasting
        Broadcast a notification to all connected WebSockets
        """
        # Use the new WebSocket manager for broadcasting
        await ws_manager.broadcast(notification_data)
        logger.info(f"Broadcast notification sent to {ws_manager.get_total_connections()} connections")

    @staticmethod
    async def send_browser_notification(
        user_id: str,
        title: str,
        message: str,
        task_id: Optional[int] = None,
        priority: str = "medium"
    ) -> bool:
        """
        Send browser notification via WebSocket to specific user

        Args:
            user_id: ID of the user to notify
            title: Notification title
            message: Notification message
            task_id: Optional task ID for task-specific notifications
            priority: Notification priority level

        Returns:
            bool: True if notification was sent successfully
        """
        try:
            notification_payload = {
                "type": "notification",
                "data": {
                    "id": f"notif_{datetime.utcnow().timestamp()}",
                    "type": "browser_notification",
                    "user_id": user_id,
                    "title": title,
                    "message": message,
                    "task_id": task_id,
                    "priority": priority,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

            # Send to specific user using WebSocket manager
            await ws_manager.send_to_user(notification_payload, user_id)

            logger.info(f"Browser notification sent to user {user_id}: {title}")
            return True

        except Exception as e:
            logger.error(f"Failed to send browser notification: {str(e)}")
            return False

    @staticmethod
    async def send_task_reminder_notification(
        user_id: str,
        task: Task,
        reminder_type: str = "due_soon"
    ) -> bool:
        """
        Send a task reminder notification

        Args:
            user_id: ID of the user to notify
            task: Task object to remind about
            reminder_type: Type of reminder ('due_soon', 'overdue', 'due_now')

        Returns:
            bool: True if notification was sent successfully
        """
        try:
            # Determine message based on reminder type
            if reminder_type == "due_soon":
                title = "Task Reminder ⏰"
                message = f"'{task.title}' is due soon"
            elif reminder_type == "overdue":
                title = "Overdue Task ⚠️"
                message = f"'{task.title}' is overdue"
            elif reminder_type == "due_now":
                title = "Task Due Now 🔔"
                message = f"'{task.title}' is due now"
            else:
                title = "Task Reminder"
                message = f"'{task.title}' reminder"

            # Include priority information
            priority_emoji = {
                "low": "🟢",
                "medium": "🟡",
                "high": "🔴"
            }.get(task.priority, "🟡")

            enhanced_message = f"{priority_emoji} {message}"
            if task.due_date:
                user_timezone = "UTC"  # Would come from user preferences
                local_due_date = TimezoneService.convert_to_user_timezone(task.due_date, user_timezone)
                enhanced_message += f" at {local_due_date.strftime('%H:%M')}"

            return await NotificationService.send_browser_notification(
                user_id=user_id,
                title=title,
                message=enhanced_message,
                task_id=task.id,
                priority=task.priority
            )
        except Exception as e:
            logger.error(f"Failed to send task reminder notification: {str(e)}")
            return False

    @staticmethod
    async def send_task_completion_notification(
        user_id: str,
        task: Task
    ) -> bool:
        """
        Send notification about task completion

        Args:
            user_id: ID of the user who completed the task
            task: Task object that was completed

        Returns:
            bool: True if notification was sent successfully
        """
        try:
            title = "Task Completed ✅"
            message = f"You've completed '{task.title}'"
            priority = "low"

            return await NotificationService.send_browser_notification(
                user_id=user_id,
                title=title,
                message=message,
                task_id=task.id,
                priority=priority
            )
        except Exception as e:
            logger.error(f"Failed to send task completion notification: {str(e)}")
            return False

    @staticmethod
    async def send_task_creation_notification(
        user_id: str,
        task: Task
    ) -> bool:
        """
        Send notification about task creation

        Args:
            user_id: ID of the user who created the task
            task: Task object that was created

        Returns:
            bool: True if notification was sent successfully
        """
        try:
            title = "Task Created 📝"
            message = f"New task '{task.title}' created successfully"
            priority = "low"

            return await NotificationService.send_browser_notification(
                user_id=user_id,
                title=title,
                message=message,
                task_id=task.id,
                priority=priority
            )
        except Exception as e:
            logger.error(f"Failed to send task creation notification: {str(e)}")
            return False

    @staticmethod
    async def send_task_updated_notification(
        user_id: str,
        task: Task
    ) -> bool:
        """
        Send notification about task update

        Args:
            user_id: ID of the user who updated the task
            task: Task object that was updated

        Returns:
            bool: True if notification was sent successfully
        """
        try:
            title = "Task Updated 🔄"
            message = f"Task '{task.title}' has been updated"
            priority = "low"

            return await NotificationService.send_browser_notification(
                user_id=user_id,
                title=title,
                message=message,
                task_id=task.id,
                priority=priority
            )
        except Exception as e:
            logger.error(f"Failed to send task update notification: {str(e)}")
            return False

    @staticmethod
    async def send_task_deleted_notification(
        user_id: str,
        task_title: str,
        task_id: int
    ) -> bool:
        """
        Send notification about task deletion

        Args:
            user_id: ID of the user who deleted the task
            task_title: Title of the deleted task
            task_id: ID of the deleted task

        Returns:
            bool: True if notification was sent successfully
        """
        try:
            title = "Task Deleted 🗑️"
            message = f"Task '{task_title}' has been deleted"
            priority = "low"

            return await NotificationService.send_browser_notification(
                user_id=user_id,
                title=title,
                message=message,
                task_id=task_id,
                priority=priority
            )
        except Exception as e:
            logger.error(f"Failed to send task deletion notification: {str(e)}")
            return False

    @staticmethod
    def can_send_notification(user_id: str, notification_type: str) -> bool:
        """
        Check if user can receive notifications of this type

        Args:
            user_id: ID of the user
            notification_type: Type of notification to check

        Returns:
            bool: True if user can receive this notification type
        """
        # Check if user is connected via WebSocket
        if not ws_manager.is_user_connected(user_id):
            logger.warning(f"User {user_id} not connected via WebSocket")
            return False

        # In a real implementation, this would check user preferences
        # For now, we'll assume all users can receive all notification types
        return True

    @staticmethod
    def get_notification_preferences(user_id: str) -> Dict[str, Any]:
        """
        Get user's notification preferences

        Args:
            user_id: ID of the user

        Returns:
            Dictionary with user's notification preferences
        """
        # In a real implementation, this would fetch from the database
        # For now, return default preferences
        return {
            "browser_notifications": True,
            "email_notifications": False,
            "push_notifications": False,
            "reminder_lead_times": ["1h", "1d"],  # 1 hour, 1 day before
            "notification_types": {
                "task_created": True,
                "task_completed": True,
                "task_updated": True,
                "task_deleted": True,
                "task_due_soon": True,
                "task_overdue": True,
                "recurring_task_generated": True
            }
        }

    @staticmethod
    async def schedule_reminder_notification(
        user_id: str,
        task_id: int,
        reminder_time: datetime,
        notification_channels: List[str] = ["browser"]
    ) -> bool:
        """
        Schedule a reminder notification for a future time

        Args:
            user_id: ID of the user to notify
            task_id: ID of the task to remind about
            reminder_time: When to send the reminder
            notification_channels: List of channels to send notification through

        Returns:
            bool: True if scheduling was successful
        """
        try:
            # In a real implementation, this would schedule with a task queue like Celery
            # or use a scheduler service. For now, we'll just log the scheduled notification.
            logger.info(f"Scheduled reminder for user {user_id}, task {task_id} at {reminder_time}")

            # Calculate time until reminder
            time_diff = reminder_time - datetime.utcnow()
            seconds_until = int(time_diff.total_seconds())

            if seconds_until > 0:
                # In production, use proper task queue (Celery/Redis)
                # For demo, we could use asyncio (not recommended for production)
                logger.info(f"Reminder will fire in {seconds_until} seconds")
            else:
                logger.warning(f"Attempted to schedule past reminder for {reminder_time}")
                return False

            return True
        except Exception as e:
            logger.error(f"Failed to schedule reminder notification: {str(e)}")
            return False

    @staticmethod
    async def process_reminder_queue():
        """
        Process the reminder queue and send notifications for due tasks

        This would typically be called by a scheduled job or cron
        """
        try:
            # In a real implementation, this would:
            # 1. Query the database for tasks with reminders due now
            # 2. Check user preferences for notification types
            # 3. Send notifications via appropriate channels
            # 4. Update reminder status in database

            logger.info("Processing reminder queue...")
            # Placeholder implementation
            pass
        except Exception as e:
            logger.error(f"Failed to process reminder queue: {str(e)}")

    @staticmethod
    def validate_notification_payload(payload: Dict[str, Any]) -> bool:
        """
        Validate notification payload

        Args:
            payload: Notification payload to validate

        Returns:
            bool: True if payload is valid
        """
        required_fields = ["user_id", "title", "message"]
        for field in required_fields:
            if field not in payload:
                return False

        # Validate field types
        if not isinstance(payload["user_id"], str):
            return False
        if not isinstance(payload["title"], str) or len(payload["title"]) > 100:
            return False
        if not isinstance(payload["message"], str) or len(payload["message"]) > 500:
            return False

        return True

    @staticmethod
    def get_connection_status(user_id: str) -> Dict[str, Any]:
        """
        Get WebSocket connection status for a user

        Args:
            user_id: ID of the user

        Returns:
            Dictionary with connection status information
        """
        return {
            "user_id": user_id,
            "connected": ws_manager.is_user_connected(user_id),
            "connection_count": ws_manager.get_user_connection_count(user_id),
            "total_connections": ws_manager.get_total_connections()
        }