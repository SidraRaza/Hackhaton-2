"""
Audit Service for Phase V: Advanced Cloud Deployment
Handles audit logging for all system events and user actions
"""
from typing import List, Optional, Dict, Any
from sqlmodel import SQLModel, Field, Session, select
from datetime import datetime
import logging
from enum import Enum


class AuditAction(str, Enum):
    """Enumeration of audit actions"""
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    TASK_DELETED = "task.deleted"
    TASK_RECURRING_CREATED = "task.recurrence_created"
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_PREFERENCES_UPDATED = "user.preferences_updated"
    REMINDER_TRIGGERED = "reminder.triggered"
    NOTIFICATION_SENT = "notification.sent"


class AuditLog(SQLModel, table=True):
    """Model for audit log entries"""
    __tablename__ = "audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    action: str = Field(index=True)  # Audit action type
    user_id: str = Field(index=True)  # User who performed the action
    resource_type: str = Field(index=True)  # Type of resource (task, user, etc.)
    resource_id: str  # ID of the resource
    action_details: Dict[str, Any] = Field(default={}, sa_column_kwargs={
        "server_default": "'{}'::jsonb",
        "nullable": False
    })  # Details about the action
    ip_address: Optional[str] = Field(default=None)  # IP address of the user
    user_agent: Optional[str] = Field(default=None)  # User agent string
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow())  # When action occurred
    correlation_id: Optional[str] = Field(default=None, index=True)  # For tracking related events


class AuditService:
    """Service for handling audit logging"""

    @staticmethod
    def log_action(
        session: Session,
        action: AuditAction,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action_details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> Optional[AuditLog]:
        """
        Log an action to the audit trail

        Args:
            session: Database session
            action: Type of action being audited
            user_id: ID of the user performing the action
            resource_type: Type of resource affected (task, user, etc.)
            resource_id: ID of the specific resource
            action_details: Additional details about the action
            ip_address: IP address of the user
            user_agent: User agent string
            correlation_id: ID to correlate related events

        Returns:
            Created AuditLog entry or None if failed
        """
        audit_entry = AuditLog(
            action=action.value if isinstance(action, AuditAction) else action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action_details=action_details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            correlation_id=correlation_id
        )

        try:
            session.add(audit_entry)
            session.commit()
            session.refresh(audit_entry)
            return audit_entry
        except Exception as e:
            logging.error(f"Failed to log audit action {action}: {str(e)}")
            session.rollback()
            return None

    @staticmethod
    def log_task_action(
        session: Session,
        action: AuditAction,
        user_id: str,
        task_id: int,
        changes: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> Optional[AuditLog]:
        """
        Log a task-related action to the audit trail

        Args:
            session: Database session
            action: Task-related audit action
            user_id: ID of the user performing the action
            task_id: ID of the task being operated on
            changes: Dictionary of changes made (for update actions)
            ip_address: IP address of the user
            user_agent: User agent string
            correlation_id: ID to correlate related events

        Returns:
            Created AuditLog entry or None if failed
        """
        details = {
            "task_id": task_id,
            "changes": changes or {}
        }

        return AuditService.log_action(
            session=session,
            action=action,
            user_id=user_id,
            resource_type="task",
            resource_id=str(task_id),
            action_details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            correlation_id=correlation_id
        )

    @staticmethod
    def get_user_audit_logs(
        session: Session,
        user_id: str,
        action_filter: Optional[List[AuditAction]] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[AuditLog]:
        """
        Get audit logs for a specific user with optional filters

        Args:
            session: Database session
            user_id: User ID to filter logs for
            action_filter: List of specific actions to filter for
            resource_type: Filter by specific resource type
            start_date: Filter logs after this date
            end_date: Filter logs before this date
            limit: Number of results to return
            offset: Offset for pagination

        Returns:
            List of audit logs matching the criteria
        """
        statement = select(AuditLog).where(AuditLog.user_id == user_id)

        if action_filter:
            action_values = [action.value if isinstance(action, AuditAction) else action for action in action_filter]
            statement = statement.where(AuditLog.action.in_(action_values))

        if resource_type:
            statement = statement.where(AuditLog.resource_type == resource_type)

        if start_date:
            statement = statement.where(AuditLog.timestamp >= start_date)

        if end_date:
            statement = statement.where(AuditLog.timestamp <= end_date)

        statement = statement.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit)

        return session.exec(statement).all()

    @staticmethod
    def get_task_audit_logs(
        session: Session,
        task_id: int,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[AuditLog]:
        """
        Get audit logs for a specific task

        Args:
            session: Database session
            task_id: Task ID to filter logs for
            user_id: User ID for authorization
            limit: Number of results to return
            offset: Offset for pagination

        Returns:
            List of audit logs for the task
        """
        statement = select(AuditLog).where(
            AuditLog.resource_id == str(task_id),
            AuditLog.resource_type == "task",
            AuditLog.user_id == user_id
        ).order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit)

        return session.exec(statement).all()

    @staticmethod
    def get_recent_audit_logs(
        session: Session,
        hours: int = 24,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Get recent audit logs within the specified time window

        Args:
            session: Database session
            hours: Number of hours to look back (default: 24)
            limit: Maximum number of results to return

        Returns:
            List of recent audit logs
        """
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        statement = select(AuditLog).where(
            AuditLog.timestamp >= cutoff_time
        ).order_by(AuditLog.timestamp.desc()).limit(limit)

        return session.exec(statement).all()

    @staticmethod
    def get_audit_statistics(
        session: Session,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get audit statistics for reporting

        Args:
            session: Database session
            user_id: Optional user ID to filter for specific user
            start_date: Optional start date for time range
            end_date: Optional end date for time range

        Returns:
            Dictionary with audit statistics
        """
        from sqlalchemy import func

        # Base query
        statement = select(
            AuditLog.action,
            func.count(AuditLog.id).label('count')
        )

        # Apply filters if provided
        if user_id:
            statement = statement.where(AuditLog.user_id == user_id)

        if start_date:
            statement = statement.where(AuditLog.timestamp >= start_date)

        if end_date:
            statement = statement.where(AuditLog.timestamp <= end_date)

        statement = statement.group_by(AuditLog.action)

        results = session.exec(statement).all()

        stats = {
            "actions": {},
            "total_logs": 0,
            "by_resource_type": {},
            "by_date": {}
        }

        for action, count in results:
            stats["actions"][action] = count
            stats["total_logs"] += count

        # Additional resource type statistics
        resource_statement = select(
            AuditLog.resource_type,
            func.count(AuditLog.id).label('count')
        )

        if user_id:
            resource_statement = resource_statement.where(AuditLog.user_id == user_id)

        if start_date:
            resource_statement = resource_statement.where(AuditLog.timestamp >= start_date)

        if end_date:
            resource_statement = resource_statement.where(AuditLog.timestamp <= end_date)

        resource_statement = resource_statement.group_by(AuditLog.resource_type)
        resource_results = session.exec(resource_statement).all()

        for resource_type, count in resource_results:
            stats["by_resource_type"][resource_type] = count

        return stats

    @staticmethod
    def purge_old_audit_logs(
        session: Session,
        days_to_keep: int = 90
    ) -> int:
        """
        Purge audit logs older than specified days

        Args:
            session: Database session
            days_to_keep: Number of days to keep audit logs (default: 90)

        Returns:
            Number of logs purged
        """
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        # First count logs to be purged
        count_statement = select(func.count(AuditLog.id)).where(AuditLog.timestamp < cutoff_date)
        logs_to_purge = session.exec(count_statement).one()

        # Then delete them
        delete_statement = select(AuditLog).where(AuditLog.timestamp < cutoff_date)
        logs = session.exec(delete_statement).all()

        for log in logs:
            session.delete(log)

        session.commit()
        return logs_to_purge


class AuditMiddleware:
    """Middleware for automatic audit logging of API requests"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Log request if it's an HTTP request
        if scope["type"] == "http":
            # Extract user info, request details, etc.
            # This would be implemented with actual middleware framework
            pass

        await self.app(scope, receive, send)


# Event consumer for audit service
class AuditEventConsumer:
    """Consumer service for processing events and creating audit logs"""

    @staticmethod
    async def process_task_created_event(
        session: Session,
        event_data: Dict[str, Any]
    ) -> Optional[AuditLog]:
        """
        Process task.created event and create audit log

        Args:
            session: Database session
            event_data: Event data containing task information

        Returns:
            Created audit log or None if failed
        """
        try:
            task_id = event_data.get("task_id")
            user_id = event_data.get("user_id", "system")
            correlation_id = event_data.get("metadata", {}).get("correlation_id")

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
                session=session,
                action=AuditAction.TASK_CREATED,
                user_id=user_id,
                task_id=task_id,
                changes=task_details,
                correlation_id=correlation_id
            )
        except Exception as e:
            logging.error(f"Failed to process task.created event: {str(e)}")
            return None

    @staticmethod
    async def process_task_updated_event(
        session: Session,
        event_data: Dict[str, Any]
    ) -> Optional[AuditLog]:
        """
        Process task.updated event and create audit log

        Args:
            session: Database session
            event_data: Event data containing task update information

        Returns:
            Created audit log or None if failed
        """
        try:
            task_id = event_data.get("task_id")
            user_id = event_data.get("user_id", "system")
            changes = event_data.get("changes", {})
            updated_fields = event_data.get("updated_fields", [])
            correlation_id = event_data.get("metadata", {}).get("correlation_id")

            update_details = {
                "changes": changes,
                "updated_fields": updated_fields,
                "updated_at": event_data.get("updated_at")
            }

            return AuditService.log_task_action(
                session=session,
                action=AuditAction.TASK_UPDATED,
                user_id=user_id,
                task_id=task_id,
                changes=update_details,
                correlation_id=correlation_id
            )
        except Exception as e:
            logging.error(f"Failed to process task.updated event: {str(e)}")
            return None

    @staticmethod
    async def process_task_completed_event(
        session: Session,
        event_data: Dict[str, Any]
    ) -> Optional[AuditLog]:
        """
        Process task.completed event and create audit log

        Args:
            session: Database session
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
            correlation_id = event_data.get("metadata", {}).get("correlation_id")

            completion_details = {
                "completed_at": completed_at,
                "was_recurring": was_recurring,
                "mark_series_complete": mark_series_complete
            }

            return AuditService.log_task_action(
                session=session,
                action=AuditAction.TASK_COMPLETED,
                user_id=user_id,
                task_id=task_id,
                changes=completion_details,
                correlation_id=correlation_id
            )
        except Exception as e:
            logging.error(f"Failed to process task.completed event: {str(e)}")
            return None

    @staticmethod
    async def process_task_deleted_event(
        session: Session,
        event_data: Dict[str, Any]
    ) -> Optional[AuditLog]:
        """
        Process task.deleted event and create audit log

        Args:
            session: Database session
            event_data: Event data containing task deletion information

        Returns:
            Created audit log or None if failed
        """
        try:
            task_id = event_data.get("task_id")
            user_id = event_data.get("user_id", "system")
            deleted_at = event_data.get("deleted_at")
            correlation_id = event_data.get("metadata", {}).get("correlation_id")

            deletion_details = {
                "deleted_at": deleted_at,
                "was_recurring": event_data.get("was_recurring", False)
            }

            return AuditService.log_task_action(
                session=session,
                action=AuditAction.TASK_DELETED,
                user_id=user_id,
                task_id=task_id,
                changes=deletion_details,
                correlation_id=correlation_id
            )
        except Exception as e:
            logging.error(f"Failed to process task.deleted event: {str(e)}")
            return None

    @staticmethod
    async def process_recurrence_created_event(
        session: Session,
        event_data: Dict[str, Any]
    ) -> Optional[AuditLog]:
        """
        Process task.recurrence_created event and create audit log

        Args:
            session: Database session
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
            correlation_id = event_data.get("metadata", {}).get("correlation_id")

            recurrence_details = {
                "original_task_id": original_task_id,
                "new_task_id": new_task_id,
                "recurrence_sequence": recurrence_sequence,
                "next_due_date": next_due_date,
                "pattern": event_data.get("pattern"),
                "config": event_data.get("config")
            }

            return AuditService.log_action(
                session=session,
                action=AuditAction.TASK_RECURRING_CREATED,
                user_id=user_id,
                resource_type="task",
                resource_id=str(original_task_id),
                action_details=recurrence_details,
                correlation_id=correlation_id
            )
        except Exception as e:
            logging.error(f"Failed to process task.recurrence_created event: {str(e)}")
            return None

    @staticmethod
    async def process_user_login_event(
        session: Session,
        event_data: Dict[str, Any]
    ) -> Optional[AuditLog]:
        """
        Process user logged in event and create audit log

        Args:
            session: Database session
            event_data: Event data containing login information

        Returns:
            Created audit log or None if failed
        """
        try:
            user_id = event_data.get("user_id", "system")
            session_id = event_data.get("session_id")
            ip_address = event_data.get("ip_address")
            user_agent = event_data.get("user_agent")
            correlation_id = event_data.get("metadata", {}).get("correlation_id")

            login_details = {
                "session_id": session_id,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "login_time": event_data.get("login_time"),
                "source": event_data.get("source")
            }

            return AuditService.log_action(
                session=session,
                action=AuditAction.USER_LOGIN,
                user_id=user_id,
                resource_type="user",
                resource_id=user_id,
                action_details=login_details,
                ip_address=ip_address,
                user_agent=user_agent,
                correlation_id=correlation_id
            )
        except Exception as e:
            logging.error(f"Failed to process user logged in event: {str(e)}")
            return None

    @staticmethod
    async def process_generic_event(
        session: Session,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> Optional[AuditLog]:
        """
        Process any generic event and create audit log

        Args:
            session: Database session
            event_type: Type of event
            event_data: Event data

        Returns:
            Created audit log or None if failed
        """
        try:
            user_id = event_data.get("user_id", "system")
            resource_type = event_data.get("resource_type", "system")
            resource_id = event_data.get("resource_id", "system")
            correlation_id = event_data.get("metadata", {}).get("correlation_id")
            source = event_data.get("source", "system")

            # Determine resource type based on event type
            if event_type.startswith("task."):
                resource_type = "task"
                resource_id = str(event_data.get("task_id", resource_id))
            elif event_type.startswith("user."):
                resource_type = "user"
                resource_id = str(event_data.get("user_id", resource_id))
            elif event_type.startswith("tag."):
                resource_type = "tag"
                resource_id = str(event_data.get("tag_id", resource_id))

            return AuditService.log_action(
                session=session,
                action=event_type,
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                action_details=event_data,
                correlation_id=correlation_id
            )
        except Exception as e:
            logging.error(f"Failed to process generic event {event_type}: {str(e)}")
            return None

    @staticmethod
    async def process_event_stream(
        session: Session,
        events: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Process a stream of events and create audit logs

        Args:
            session: Database session
            events: List of events to process

        Returns:
            Dictionary with processing results (success/failure counts)
        """
        results = {
            "processed": 0,
            "failed": 0,
            "success": 0
        }

        for event in events:
            event_type = event.get("event_type", "")
            event_data = event.get("data", {})
            event_metadata = event.get("metadata", {})

            # Add metadata to event data for audit processing
            if event_metadata:
                event_data["metadata"] = event_metadata

            audit_log = None
            if event_type == "task.created":
                audit_log = await AuditEventConsumer.process_task_created_event(session, event_data)
            elif event_type == "task.updated":
                audit_log = await AuditEventConsumer.process_task_updated_event(session, event_data)
            elif event_type == "task.completed":
                audit_log = await AuditEventConsumer.process_task_completed_event(session, event_data)
            elif event_type == "task.deleted":
                audit_log = await AuditEventConsumer.process_task_deleted_event(session, event_data)
            elif event_type == "task.recurrence_created":
                audit_log = await AuditEventConsumer.process_recurrence_created_event(session, event_data)
            elif event_type == "user.logged_in":
                audit_log = await AuditEventConsumer.process_user_login_event(session, event_data)
            else:
                # Process as generic event
                audit_log = await AuditEventConsumer.process_generic_event(session, event_type, event_data)

            if audit_log:
                results["success"] += 1
            else:
                results["failed"] += 1

            results["processed"] += 1

        return results

    @staticmethod
    def start_audit_consumer_service():
        """
        Start the audit consumer service that listens for events and creates audit logs

        This would typically be run as a background service in production
        """
        import asyncio
        from dapr.clients import DaprClient
        import logging

        logger = logging.getLogger(__name__)

        async def audit_consumer_loop():
            """Main loop for consuming events and creating audit logs"""
            try:
                # Initialize Dapr client
                dapr_client = DaprClient()

                # Subscribe to task events for audit logging
                # This uses Dapr pub/sub to listen for events from the task-events topic
                from dapr.ext.pubsub import AsyncAppChannel

                logger.info("Audit consumer service started and listening for events...")

                # In a real implementation, we would use Dapr's pub/sub subscription
                # For now, this is a conceptual implementation
                while True:
                    try:
                        # Listen for events from the task-events topic
                        # This would be implemented with proper Dapr subscription
                        # await dapr_client.subscribe_to_pubsub_event(
                        #     pubsub_name="kafka-pubsub",
                        #     topic_name="task-events",
                        #     callback=process_task_event
                        # )

                        # For demonstration, we'll just log that the service is running
                        await asyncio.sleep(60)  # Check every minute

                    except Exception as e:
                        logger.error(f"Error in audit consumer loop: {str(e)}")
                        await asyncio.sleep(10)  # Wait before retrying

            except Exception as e:
                logger.error(f"Audit consumer service error: {str(e)}")
                raise e

        # In a real implementation, we would start this as a background task
        # asyncio.create_task(audit_consumer_loop())
        return "Audit consumer service initialized"

    @staticmethod
    def process_task_event(event_data: Dict[str, Any], session: Session) -> bool:
        """
        Process a task event and create audit log entry

        Args:
            event_data: Dictionary containing the event data
            session: Database session for storing audit logs

        Returns:
            bool: True if audit log was created successfully
        """
        try:
            from models import AuditLog
            from datetime import datetime

            # Extract event information
            event_type = event_data.get("event_type", "")
            user_id = event_data.get("user_id", "")
            task_id = event_data.get("task_id", "")
            action_details = event_data.get("data", {})
            timestamp = event_data.get("timestamp", datetime.utcnow())

            # Create audit log entry
            audit_log = AuditLog(
                user_id=user_id,
                action=event_type,
                resource_type="task",
                resource_id=str(task_id),
                action_details=action_details,
                timestamp=timestamp
            )

            session.add(audit_log)
            session.commit()

            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Audit log created for event {event_type} on task {task_id}")
            return True

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to process task event for audit: {str(e)}")
            return False

    @staticmethod
    def process_user_event(event_data: Dict[str, Any], session: Session) -> bool:
        """
        Process a user event and create audit log entry

        Args:
            event_data: Dictionary containing the event data
            session: Database session for storing audit logs

        Returns:
            bool: True if audit log was created successfully
        """
        try:
            from models import AuditLog
            from datetime import datetime

            # Extract event information
            event_type = event_data.get("event_type", "")
            user_id = event_data.get("user_id", "")
            action_details = event_data.get("data", {})
            timestamp = event_data.get("timestamp", datetime.utcnow())

            # Create audit log entry
            audit_log = AuditLog(
                user_id=user_id,
                action=event_type,
                resource_type="user",
                resource_id=user_id,
                action_details=action_details,
                timestamp=timestamp
            )

            session.add(audit_log)
            session.commit()

            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Audit log created for user event {event_type} for user {user_id}")
            return True

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to process user event for audit: {str(e)}")
            return False

    @staticmethod
    def process_system_event(event_data: Dict[str, Any], session: Session) -> bool:
        """
        Process a system event and create audit log entry

        Args:
            event_data: Dictionary containing the event data
            session: Database session for storing audit logs

        Returns:
            bool: True if audit log was created successfully
        """
        try:
            from models import AuditLog
            from datetime import datetime

            # Extract event information
            event_type = event_data.get("event_type", "")
            user_id = event_data.get("user_id", "")
            action_details = event_data.get("data", {})
            timestamp = event_data.get("timestamp", datetime.utcnow())

            # Create audit log entry
            audit_log = AuditLog(
                user_id=user_id,
                action=event_type,
                resource_type="system",
                resource_id=event_type,
                action_details=action_details,
                timestamp=timestamp
            )

            session.add(audit_log)
            session.commit()

            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Audit log created for system event {event_type}")
            return True

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to process system event for audit: {str(e)}")
            return False

    @staticmethod
    def bulk_process_events(events: List[Dict[str, Any]], session: Session) -> Dict[str, int]:
        """
        Process multiple events in bulk for audit logging

        Args:
            events: List of event dictionaries to process
            session: Database session for storing audit logs

        Returns:
            Dictionary with processing statistics
        """
        processed = 0
        failed = 0
        skipped = 0

        for event in events:
            try:
                event_type = event.get("event_type", "")

                if event_type.startswith("task."):
                    success = AuditService.process_task_event(event, session)
                elif event_type.startswith("user."):
                    success = AuditService.process_user_event(event, session)
                elif event_type.startswith("audit.") or event_type.startswith("reminder.") or event_type.startswith("notification."):
                    success = AuditService.process_system_event(event, session)
                else:
                    # Unknown event type, skip
                    skipped += 1
                    continue

                if success:
                    processed += 1
                else:
                    failed += 1

            except Exception as e:
                logging.error(f"Failed to process event {event.get('event_id', 'unknown')}: {str(e)}")
                failed += 1

        return {
            "processed": processed,
            "failed": failed,
            "skipped": skipped,
            "total": len(events)
        }