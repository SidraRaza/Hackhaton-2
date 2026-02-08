"""
Notification Consumer Service for Phase V: Advanced Cloud Deployment
Consumes reminder events and sends notifications to users
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from sqlmodel import Session
from datetime import datetime

from models import Task
from services.notification_service import NotificationService
from services.reminder_service import ReminderService
from services.timezone_service import TimezoneService


logger = logging.getLogger(__name__)


class NotificationEventConsumer:
    """Consumer service for processing notification events and sending user notifications"""

    def __init__(self, db_session: Session):
        self.session = db_session

    async def process_reminder_triggered_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Process reminder.triggered event and send appropriate notification

        Args:
            event_data: Event data containing reminder information

        Returns:
            bool: True if notification was sent successfully
        """
        try:
            user_id = event_data.get("user_id")
            task_id = event_data.get("task_id")
            reminder_type = event_data.get("reminder_type", "due_soon")

            # Fetch the task from the database
            task = self.session.get(Task, task_id)
            if not task:
                logger.error(f"Task with ID {task_id} not found for reminder notification")
                return False

            # Send the appropriate reminder notification
            success = await NotificationService.send_task_reminder_notification(
                user_id=user_id,
                task=task,
                reminder_type=reminder_type
            )

            if success:
                logger.info(f"Reminder notification sent for task {task_id} to user {user_id}")

                # Update reminder status in database
                await ReminderService.mark_reminder_sent(self.session, task_id, reminder_type)
            else:
                logger.error(f"Failed to send reminder notification for task {task_id}")

            return success
        except Exception as e:
            logger.error(f"Failed to process reminder.triggered event: {str(e)}")
            return False

    async def process_notification_sent_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Process notification.sent event (for logging/tracking purposes)

        Args:
            event_data: Event data containing notification information

        Returns:
            bool: True if event was processed successfully
        """
        try:
            notification_id = event_data.get("notification_id")
            user_id = event_data.get("user_id")
            task_id = event_data.get("task_id")
            channel = event_data.get("channel", "browser")
            sent_at = event_data.get("sent_at", datetime.utcnow())

            logger.info(f"Notification {notification_id} sent to user {user_id} via {channel}")

            # In a real implementation, we might update notification tracking in DB
            # For now, we just log the event

            return True
        except Exception as e:
            logger.error(f"Failed to process notification.sent event: {str(e)}")
            return False

    async def process_task_completed_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Process task.completed event and send completion notification

        Args:
            event_data: Event data containing task completion information

        Returns:
            bool: True if notification was sent successfully
        """
        try:
            user_id = event_data.get("user_id")
            task_id = event_data.get("task_id")

            # Fetch the task from the database
            task = self.session.get(Task, task_id)
            if not task:
                logger.error(f"Task with ID {task_id} not found for completion notification")
                return False

            # Send completion notification
            success = await NotificationService.send_task_completion_notification(
                user_id=user_id,
                task=task
            )

            if success:
                logger.info(f"Completion notification sent for task {task_id} to user {user_id}")
            else:
                logger.error(f"Failed to send completion notification for task {task_id}")

            return success
        except Exception as e:
            logger.error(f"Failed to process task.completed event for notification: {str(e)}")
            return False

    async def process_task_created_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Process task.created event and send creation notification

        Args:
            event_data: Event data containing task creation information

        Returns:
            bool: True if notification was sent successfully
        """
        try:
            user_id = event_data.get("user_id")
            task_id = event_data.get("task_id")

            # Fetch the task from the database
            task = self.session.get(Task, task_id)
            if not task:
                logger.error(f"Task with ID {task_id} not found for creation notification")
                return False

            # Send creation notification
            success = await NotificationService.send_task_creation_notification(
                user_id=user_id,
                task=task
            )

            if success:
                logger.info(f"Creation notification sent for task {task_id} to user {user_id}")
            else:
                logger.error(f"Failed to send creation notification for task {task_id}")

            return success
        except Exception as e:
            logger.error(f"Failed to process task.created event for notification: {str(e)}")
            return False

    async def consume_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Consume a single event and send appropriate notification

        Args:
            event_data: Dictionary containing event information

        Returns:
            bool: True if event was processed successfully
        """
        try:
            event_type = event_data.get("event_type", "")

            if event_type == "reminder.triggered":
                return await self.process_reminder_triggered_event(event_data)
            elif event_type == "notification.sent":
                return await self.process_notification_sent_event(event_data)
            elif event_type == "task.completed":
                return await self.process_task_completed_event(event_data)
            elif event_type == "task.created":
                return await self.process_task_created_event(event_data)
            else:
                # Log unknown event types
                logger.warning(f"Unknown event type for notification: {event_type}")
                return False

        except Exception as e:
            logger.error(f"Error consuming notification event: {str(e)}")
            return False

    async def start_consuming(self):
        """
        Start consuming notification events
        This would typically be called by a background process
        """
        logger.info("Starting notification event consumer...")

        try:
            # Subscribe to Dapr pub/sub for reminder events
            from dapr.ext.grpc import App

            app = App()

            # Subscribe to reminder events topic
            @app.subscribe(pubsub='kafka-pubsub', topic='task-reminders')
            async def reminder_events_handler(event_data: bytes):
                try:
                    # Deserialize the event data
                    import json
                    event_dict = json.loads(event_data.decode('utf-8'))

                    # Process the event
                    success = await self.consume_event(event_dict)

                    if success:
                        logger.info(f"Notification consumer processed reminder event")
                    else:
                        logger.error(f"Notification consumer failed to process reminder event")

                except Exception as e:
                    logger.error(f"Error in notification consumer handler: {str(e)}")

            # Also subscribe to task events that trigger notifications
            @app.subscribe(pubsub='kafka-pubsub', topic='task-events')
            async def task_events_handler(event_data: bytes):
                try:
                    import json
                    event_dict = json.loads(event_data.decode('utf-8'))

                    # Only process certain task events for notifications
                    event_type = event_dict.get('event_type', '')
                    if event_type in ['task.created', 'task.completed']:
                        success = await self.consume_event(event_dict)

                        if success:
                            logger.info(f"Notification consumer processed task event: {event_type}")
                        else:
                            logger.error(f"Notification consumer failed to process task event: {event_type}")

                except Exception as e:
                    logger.error(f"Error in notification consumer task handler: {str(e)}")

            # Run the app - this would normally be handled by the Dapr runtime
            await app.run()

        except Exception as e:
            logger.error(f"Notification event consumer error: {str(e)}")
            raise


def create_notification_consumer(db_session: Session) -> NotificationEventConsumer:
    """
    Factory function to create a notification event consumer

    Args:
        db_session: Database session to use for accessing tasks

    Returns:
        NotificationEventConsumer instance
    """
    return NotificationEventConsumer(db_session)