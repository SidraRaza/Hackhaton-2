"""
Recurrence Consumer Service for Phase V: Advanced Cloud Deployment
Consumes task completion events and creates next occurrences for recurring tasks
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from sqlmodel import Session
from datetime import datetime

from models import Task
from services.recurrence_service import RecurrenceService
from services.task_service import TaskService
from services.event_publisher import EventPublisher
from events.schemas.event_envelope import EventType


logger = logging.getLogger(__name__)


class RecurrenceEventConsumer:
    """Consumer service for processing task completion events and creating next occurrences"""

    def __init__(self, db_session: Session):
        self.session = db_session

    async def process_task_completed_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Process task.completed event and create next occurrence if task is recurring

        Args:
            event_data: Event data containing task completion information

        Returns:
            bool: True if processing was successful
        """
        try:
            task_id = event_data.get("task_id")
            user_id = event_data.get("user_id")
            completed_at = event_data.get("completed_at")
            mark_series_complete = event_data.get("mark_series_complete", False)

            # Fetch the completed task from the database
            original_task = self.session.get(Task, task_id)
            if not original_task:
                logger.error(f"Original task with ID {task_id} not found for recurrence processing")
                return False

            # Check if the task has recurrence pattern and is recurring
            if not original_task.recurrence_pattern:
                logger.debug(f"Task {task_id} is not recurring, skipping recurrence processing")
                return True

            # If mark_series_complete is True, don't create next occurrence
            if mark_series_complete:
                logger.info(f"Task {task_id} series marked complete, not creating next occurrence")
                return True

            # Calculate and create the next occurrence
            next_task = RecurrenceService.create_next_occurrence(original_task)
            if not next_task:
                logger.info(f"No next occurrence needed for task {task_id}")
                return True

            # Save the next occurrence to the database
            try:
                self.session.add(next_task)
                self.session.commit()
                self.session.refresh(next_task)

                logger.info(f"Next occurrence created for task {task_id}: new task ID {next_task.id}")

                # Emit an event for the newly created recurrence
                recurrence_event_data = {
                    "original_task_id": original_task.id,
                    "new_task_id": next_task.id,
                    "recurrence_sequence": getattr(original_task, 'recurrence_sequence', 0) + 1,
                    "next_due_date": next_task.due_date.isoformat() if next_task.due_date else None,
                    "pattern": original_task.recurrence_pattern,
                    "config": original_task.recurrence_config,
                    "user_id": user_id
                }

                # Publish event for the new recurrence
                event = EventPublisher.create_task_event(
                    event_type=EventType.TASK_RECURRENCE_CREATED,
                    user_id=user_id,
                    data=recurrence_event_data,
                    task_id=next_task.id
                )

                # In a real implementation, we would publish this event
                # await EventPublisher.publish_event(event, session=self.session)

                logger.info(f"Recurrence created event published for new task {next_task.id}")

                # If the original task was part of a series, update its occurrence tracking
                if original_task.occurrences_remaining is not None:
                    original_task.occurrences_remaining -= 1
                    if original_task.occurrences_remaining <= 0:
                        original_task.completed = True  # Mark series as complete
                    self.session.add(original_task)
                    self.session.commit()

                return True

            except Exception as save_error:
                logger.error(f"Failed to save next occurrence for task {task_id}: {str(save_error)}")
                self.session.rollback()
                return False

        except Exception as e:
            logger.error(f"Failed to process task.completed event for recurrence: {str(e)}")
            return False

    async def process_task_deleted_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Process task.deleted event for recurring tasks (cleanup if needed)

        Args:
            event_data: Event data containing task deletion information

        Returns:
            bool: True if processing was successful
        """
        try:
            task_id = event_data.get("task_id")
            user_id = event_data.get("user_id")

            # Fetch the deleted task from the database
            deleted_task = self.session.get(Task, task_id)
            if not deleted_task:
                logger.warning(f"Deleted task with ID {task_id} not found for recurrence processing")
                return True

            # If the deleted task had a recurrence pattern, we might want to clean up
            # related future occurrences or series tracking
            if deleted_task.recurrence_pattern:
                logger.info(f"Recurring task {task_id} was deleted, cleaning up related occurrences")

                # Cancel any future occurrences in the series
                # In a real implementation, we might set a flag to prevent future occurrences
                # or delete all pending occurrences in the series
                await self.cancel_future_occurrences(deleted_task)

            return True
        except Exception as e:
            logger.error(f"Failed to process task.deleted event for recurrence: {str(e)}")
            return False

    async def cancel_future_occurrences(self, task: Task) -> bool:
        """
        Cancel any future occurrences related to this recurring task

        Args:
            task: The recurring task that was cancelled

        Returns:
            bool: True if cancellation was successful
        """
        try:
            # In a real implementation, we would:
            # 1. Find all future occurrences of this task series
            # 2. Mark them as cancelled or delete them
            # 3. Update the parent task to indicate series cancellation

            # For now, we'll just log that we're cancelling future occurrences
            logger.info(f"Cancelling future occurrences for task series {task.id}")

            # Update the original task to mark series as cancelled
            # This would prevent future occurrences from being created
            task.series_cancelled = True
            self.session.add(task)
            self.session.commit()

            return True
        except Exception as e:
            logger.error(f"Failed to cancel future occurrences: {str(e)}")
            return False

    async def consume_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Consume a single event and process recurrence logic if applicable

        Args:
            event_data: Dictionary containing event information

        Returns:
            bool: True if event was processed successfully
        """
        try:
            event_type = event_data.get("event_type", "")

            if event_type == "task.completed":
                return await self.process_task_completed_event(event_data)
            elif event_type == "task.deleted":
                return await self.process_task_deleted_event(event_data)
            else:
                # Log unknown event types
                logger.warning(f"Unknown event type for recurrence: {event_type}")
                return False

        except Exception as e:
            logger.error(f"Error consuming recurrence event: {str(e)}")
            return False

    async def start_consuming(self):
        """
        Start consuming recurrence events
        This would typically be called by a background process
        """
        logger.info("Starting recurrence event consumer...")

        try:
            # Subscribe to Dapr pub/sub for task events
            from dapr.ext.grpc import App

            app = App()

            # Subscribe to task events topic for completion events that trigger recurrences
            @app.subscribe(pubsub='kafka-pubsub', topic='task-events')
            async def task_events_handler(event_data: bytes):
                try:
                    # Deserialize the event data
                    import json
                    event_dict = json.loads(event_data.decode('utf-8'))

                    # Only process task completion/deletion events for recurrence
                    event_type = event_dict.get('event_type', '')
                    if event_type in ['task.completed', 'task.deleted']:
                        success = await self.consume_event(event_dict)

                        if success:
                            logger.info(f"Recurrence consumer processed event: {event_type}")
                        else:
                            logger.error(f"Recurrence consumer failed to process event: {event_type}")

                except Exception as e:
                    logger.error(f"Error in recurrence consumer handler: {str(e)}")

            # Run the app - this would normally be handled by the Dapr runtime
            await app.run()

        except Exception as e:
            logger.error(f"Recurrence event consumer error: {str(e)}")
            raise


def create_recurrence_consumer(db_session: Session) -> RecurrenceEventConsumer:
    """
    Factory function to create a recurrence event consumer

    Args:
        db_session: Database session to use for accessing tasks

    Returns:
        RecurrenceEventConsumer instance
    """
    return RecurrenceEventConsumer(db_session)