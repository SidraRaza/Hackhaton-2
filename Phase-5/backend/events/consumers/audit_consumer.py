"""
Audit Consumer Service for Phase V: Advanced Cloud Deployment
Consumes task events and creates audit logs in the database
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from sqlmodel import Session, create_engine, SQLModel
from dapr.clients import DaprClient
from dapr.ext.grpc import App
from dapr.clients.grpc._helpers import MetadataTuple

from models import AuditLog, Task
from events.schemas.event_envelope import EventEnvelope, EventType
from services.audit_service import AuditService, AuditAction
from database import get_session


logger = logging.getLogger(__name__)


class AuditEventConsumer:
    """Consumer service for processing events and creating audit logs"""

    def __init__(self, db_session: Session):
        self.session = db_session

    async def process_task_created_event(self, event_data: Dict[str, Any]) -> Optional[AuditLog]:
        """
        Process task.created event and create audit log

        Args:
            event_data: Event data containing task information

        Returns:
            Created audit log or None if failed
        """
        try:
            task_id = event_data.get("task_id")
            user_id = event_data.get("user_id", "system")

            task_details = {
                "title": event_data.get("title"),
                "priority": event_data.get("priority"),
                "due_date": event_data.get("due_date"),
                "recurrence_pattern": event_data.get("recurrence_pattern"),
                "recurrence_config": event_data.get("recurrence_config"),
                "tag_ids": event_data.get("tag_ids"),
                "created_at": event_data.get("created_at")
            }

            return AuditService.log_task_action(
                session=self.session,
                action=AuditAction.TASK_CREATED,
                user_id=user_id,
                task_id=task_id,
                changes=task_details
            )
        except Exception as e:
            logger.error(f"Failed to process task.created event: {str(e)}")
            return None

    async def process_task_updated_event(self, event_data: Dict[str, Any]) -> Optional[AuditLog]:
        """
        Process task.updated event and create audit log

        Args:
            event_data: Event data containing task update information

        Returns:
            Created audit log or None if failed
        """
        try:
            task_id = event_data.get("task_id")
            user_id = event_data.get("user_id", "system")
            changes = event_data.get("changes", {})
            updated_fields = event_data.get("updated_fields", [])

            update_details = {
                "changes": changes,
                "updated_fields": updated_fields,
                "updated_at": event_data.get("updated_at")
            }

            return AuditService.log_task_action(
                session=self.session,
                action=AuditAction.TASK_UPDATED,
                user_id=user_id,
                task_id=task_id,
                changes=update_details
            )
        except Exception as e:
            logger.error(f"Failed to process task.updated event: {str(e)}")
            return None

    async def process_task_completed_event(self, event_data: Dict[str, Any]) -> Optional[AuditLog]:
        """
        Process task.completed event and create audit log

        Args:
            event_data: Event data containing task completion information

        Returns:
            Created audit log or None if failed
        """
        try:
            task_id = event_data.get("task_id")
            user_id = event_data.get("user_id", "system")
            completed_at = event_data.get("completed_at")
            was_recurring = event_data.get("was_recurring", False)
            mark_series_complete = event_data.get("mark_series_complete", False)

            completion_details = {
                "completed_at": completed_at,
                "was_recurring": was_recurring,
                "mark_series_complete": mark_series_complete
            }

            return AuditService.log_task_action(
                session=self.session,
                action=AuditAction.TASK_COMPLETED,
                user_id=user_id,
                task_id=task_id,
                changes=completion_details
            )
        except Exception as e:
            logger.error(f"Failed to process task.completed event: {str(e)}")
            return None

    async def process_task_deleted_event(self, event_data: Dict[str, Any]) -> Optional[AuditLog]:
        """
        Process task.deleted event and create audit log

        Args:
            event_data: Event data containing task deletion information

        Returns:
            Created audit log or None if failed
        """
        try:
            task_id = event_data.get("task_id")
            user_id = event_data.get("user_id", "system")
            deleted_at = event_data.get("deleted_at")

            deletion_details = {
                "deleted_at": deleted_at,
                "was_recurring": event_data.get("was_recurring", False)
            }

            return AuditService.log_task_action(
                session=self.session,
                action=AuditAction.TASK_DELETED,
                user_id=user_id,
                task_id=task_id,
                changes=deletion_details
            )
        except Exception as e:
            logger.error(f"Failed to process task.deleted event: {str(e)}")
            return None

    async def process_recurrence_created_event(self, event_data: Dict[str, Any]) -> Optional[AuditLog]:
        """
        Process task.recurrence_created event and create audit log

        Args:
            event_data: Event data containing recurrence creation information

        Returns:
            Created audit log or None if failed
        """
        try:
            original_task_id = event_data.get("original_task_id")
            user_id = event_data.get("user_id", "system")
            new_task_id = event_data.get("new_task_id")
            recurrence_sequence = event_data.get("recurrence_sequence")
            next_due_date = event_data.get("next_due_date")

            recurrence_details = {
                "original_task_id": original_task_id,
                "new_task_id": new_task_id,
                "recurrence_sequence": recurrence_sequence,
                "next_due_date": next_due_date,
                "pattern": event_data.get("pattern"),
                "config": event_data.get("config")
            }

            return AuditService.log_action(
                session=self.session,
                action=AuditAction.TASK_RECURRING_CREATED,
                user_id=user_id,
                resource_type="task",
                resource_id=str(original_task_id),
                action_details=recurrence_details
            )
        except Exception as e:
            logger.error(f"Failed to process task.recurrence_created event: {str(e)}")
            return None

    async def consume_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Consume a single event and create appropriate audit log

        Args:
            event_data: Dictionary containing event information

        Returns:
            bool: True if event was processed successfully
        """
        try:
            event_type = event_data.get("event_type", "")

            if event_type == "task.created":
                result = await self.process_task_created_event(event_data)
            elif event_type == "task.updated":
                result = await self.process_task_updated_event(event_data)
            elif event_type == "task.completed":
                result = await self.process_task_completed_event(event_data)
            elif event_type == "task.deleted":
                result = await self.process_task_deleted_event(event_data)
            elif event_type == "task.recurrence_created":
                result = await self.process_recurrence_created_event(event_data)
            else:
                # Log unknown event types
                logger.warning(f"Unknown event type received: {event_type}")
                return False

            return result is not None
        except Exception as e:
            logger.error(f"Error consuming event: {str(e)}")
            return False

    async def start_consuming(self):
        """
        Start consuming events from the task-events topic
        This would typically be called by a background process
        """
        logger.info("Starting audit event consumer...")

        try:
            # Subscribe to Dapr pub/sub for task events
            from dapr.ext.grpc import App
            from dapr.clients import DaprClient

            app = App()

            # Subscribe to task events topic
            @app.subscribe(pubsub='kafka-pubsub', topic='task-events')
            async def task_events_handler(event_data: bytes):
                try:
                    # Deserialize the event data
                    import json
                    event_dict = json.loads(event_data.decode('utf-8'))

                    # Process the event
                    success = await self.consume_event(event_dict)

                    if success:
                        logger.info(f"Audit consumer processed event: {event_dict.get('event_type', 'unknown')}")
                    else:
                        logger.error(f"Audit consumer failed to process event: {event_dict.get('event_type', 'unknown')}")

                except Exception as e:
                    logger.error(f"Error in audit consumer handler: {str(e)}")

            # Run the app - this would normally be handled by the Dapr runtime
            # In practice, this would be run as part of the Dapr sidecar
            await app.run()

        except Exception as e:
            logger.error(f"Audit event consumer error: {str(e)}")
            raise


def create_audit_consumer(db_session: Session) -> AuditEventConsumer:
    """
    Factory function to create an audit event consumer

    Args:
        db_session: Database session to use for audit logging

    Returns:
        AuditEventConsumer instance
    """
    return AuditEventConsumer(db_session)