"""
Event Publisher Service for Phase V: Advanced Cloud Deployment
Handles publishing events to Kafka/Redpanda via Dapr pub/sub
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional
from sqlmodel import Session
from uuid import uuid4
import logging

from ..models import Task
from ..events.schemas.event_envelope import EventEnvelope, EventType, EventMetadata


logger = logging.getLogger(__name__)


class EventPublisher:
    """Service for publishing events to Kafka/Redpanda via Dapr pub/sub"""

    @staticmethod
    def create_task_event(
        event_type: EventType,
        user_id: str,
        data: Dict[str, Any],
        task_id: Optional[int] = None,
        idempotency_key: Optional[str] = None
    ) -> EventEnvelope:
        """
        Create a standardized task event with idempotency support

        Args:
            event_type: Type of the event (TASK_CREATED, TASK_UPDATED, etc.)
            user_id: User ID associated with the event
            data: Event-specific data
            task_id: Optional task ID for task-specific events
            idempotency_key: Optional key to prevent duplicate processing

        Returns:
            EventEnvelope with standardized structure
        """
        event_metadata = EventMetadata(
            user_id=user_id,
            correlation_id=str(uuid4()),
            trace_id=f"task-{task_id}" if task_id else f"general-{str(uuid4())[:8]}",
            source_service="todo-backend"
        )

        # Generate idempotency key if not provided
        if not idempotency_key:
            idempotency_key = EventPublisher.generate_idempotency_key(event_type.value, user_id, data)

        event = EventEnvelope(
            event_id=str(uuid4()),
            event_type=event_type.value,
            event_version="1.0",
            timestamp=datetime.utcnow(),
            source="todo-backend",
            data=data,
            metadata=event_metadata,
            aggregate_type="task",
            aggregate_id=str(task_id) if task_id else str(user_id),
            idempotency_key=idempotency_key  # Add idempotency key for duplicate prevention
        )

        return event

    @staticmethod
    def generate_idempotency_key(
        event_type: str,
        user_id: str,
        data: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ) -> str:
        """
        Generate an idempotency key to prevent duplicate event processing

        Args:
            event_type: Type of the event
            user_id: User ID associated with the event
            data: Event data for uniqueness
            timestamp: Optional timestamp for additional uniqueness

        Returns:
            str: Unique idempotency key
        """
        import hashlib
        import json

        if timestamp is None:
            timestamp = datetime.utcnow()

        # Create a unique key based on event type, user, and relevant data
        key_parts = [
            event_type,
            user_id,
            json.dumps(data, sort_keys=True, default=str),
            timestamp.isoformat()
        ]

        # Combine all parts and create a hash
        key_string = ":".join(key_parts)
        return hashlib.sha256(key_string.encode()).hexdigest()[:32]

    @staticmethod
    def check_duplicate_event(session: Session, idempotency_key: str) -> bool:
        """
        Check if an event with the same idempotency key has already been processed

        Args:
            session: Database session
            idempotency_key: Idempotency key to check

        Returns:
            bool: True if event is duplicate, False otherwise
        """
        from sqlmodel import select
        from ..models import ProcessedEvent

        # Check if an event with this idempotency key already exists
        existing_event = session.exec(
            select(ProcessedEvent).where(ProcessedEvent.idempotency_key == idempotency_key)
        ).first()

        return existing_event is not None

    @staticmethod
    def record_processed_event(session: Session, idempotency_key: str, event_id: str) -> bool:
        """
        Record that an event has been processed to prevent duplicates

        Args:
            session: Database session
            idempotency_key: Idempotency key of the processed event
            event_id: Event ID that was processed

        Returns:
            bool: True if recording was successful
        """
        from ..models import ProcessedEvent

        processed_event = ProcessedEvent(
            idempotency_key=idempotency_key,
            event_id=event_id,
            processed_at=datetime.utcnow()
        )

        try:
            session.add(processed_event)
            session.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to record processed event: {str(e)}")
            session.rollback()
            return False

    @staticmethod
    def create_user_event(
        event_type: EventType,
        user_id: str,
        data: Dict[str, Any]
    ) -> EventEnvelope:
        """
        Create a standardized user event

        Args:
            event_type: Type of the event (USER_REGISTERED, USER_LOGGED_IN, etc.)
            user_id: User ID associated with the event
            data: Event-specific data

        Returns:
            EventEnvelope with standardized structure
        """
        event_metadata = EventMetadata(
            user_id=user_id,
            correlation_id=str(uuid4()),
            trace_id=f"user-{user_id}",
            source_service="auth-service"
        )

        event = EventEnvelope(
            event_id=str(uuid4()),
            event_type=event_type.value,
            event_version="1.0",
            timestamp=datetime.utcnow(),
            source="auth-service",
            data=data,
            metadata=event_metadata,
            aggregate_type="user",
            aggregate_id=user_id
        )

        return event

    @staticmethod
    async def publish_event(
        event: EventEnvelope,
        topic: Optional[str] = None,
        session: Optional[Session] = None,
        max_retries: int = 3
    ) -> bool:
        """
        Publish an event to Kafka/Redpanda via Dapr pub/sub with idempotency support and retry logic

        Args:
            event: Event to publish
            topic: Optional topic name (defaults based on event type)
            session: Optional database session for audit logging
            max_retries: Maximum number of retry attempts (default: 3)

        Returns:
            bool: True if event published successfully
        """
        import asyncio
        from typing import Awaitable
        from dapr.clients import DaprClient

        for attempt in range(max_retries + 1):
            try:
                # Determine topic based on event type if not provided
                if not topic:
                    if event.event_type.startswith("task."):
                        topic = "task-events"
                    elif event.event_type.startswith("user."):
                        topic = "user-events"
                    elif event.event_type.startswith("reminder."):
                        topic = "task-reminders"
                    elif event.event_type.startswith("notification."):
                        topic = "task-notifications"
                    elif event.event_type.startswith("audit."):
                        topic = "task-audit"
                    else:
                        topic = "system-events"

                # Check for duplicate event if idempotency key exists
                if hasattr(event, 'idempotency_key') and event.idempotency_key and session:
                    if EventPublisher.check_duplicate_event(session, event.idempotency_key):
                        logger.info(f"Duplicate event detected with idempotency key {event.idempotency_key}, skipping publish")
                        return True  # Return success to avoid retries for duplicate events

                # Publish to Dapr pub/sub
                dapr_client = DaprClient()

                # Serialize the event to JSON
                event_json = json.dumps(event.dict(), default=str)

                # Publish the event via Dapr pub/sub
                await dapr_client.publish_event(
                    pubsub_name="kafka-pubsub",
                    topic_name=topic,
                    data=event_json,
                    data_content_type="application/json"
                )

                logger.info(f"Successfully published event {event.event_id} to topic {topic}")

                # Log event as processed to prevent duplicates if session is available
                if session and hasattr(event, 'idempotency_key') and event.idempotency_key:
                    try:
                        EventPublisher.record_processed_event(session, event.idempotency_key, event.event_id)
                    except Exception as e:
                        logger.error(f"Failed to record processed event: {str(e)}")
                        # Continue even if recording fails

                return True

            except Exception as e:
                logger.error(f"Failed to publish event {event.event_id} on attempt {attempt + 1}: {str(e)}")

                if attempt < max_retries:
                    # Exponential backoff: wait 2^attempt seconds before retry
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    # All retries exhausted, handle as permanent failure
                    await EventPublisher._handle_failed_event(event, str(e))
                    return False

        return False

    @staticmethod
    def publish_event_with_circuit_breaker(
        event: EventEnvelope,
        topic: Optional[str] = None,
        session: Optional[Session] = None,
        max_retries: int = 3
    ) -> Awaitable[bool]:
        """
        Publish an event with circuit breaker pattern for resilience

        Args:
            event: Event to publish
            topic: Optional topic name (defaults based on event type)
            session: Optional database session for audit logging
            max_retries: Maximum number of retry attempts

        Returns:
            bool: True if event published successfully
        """
        import asyncio
        from functools import wraps

        # Simple circuit breaker implementation
        failure_count = 0
        last_failure_time = None
        circuit_open = False
        circuit_timeout = 30  # 30 seconds before trying again

        async def circuit_breaker_wrapper():
            nonlocal failure_count, last_failure_time, circuit_open

            # Check if circuit is open (recent failures)
            if circuit_open:
                if last_failure_time and (datetime.utcnow() - last_failure_time).seconds > circuit_timeout:
                    # Reset circuit after timeout
                    circuit_open = False
                    failure_count = 0
                else:
                    logger.warning(f"Circuit breaker is open, skipping event {event.event_id}")
                    return False  # Circuit is open, don't try

            # Try to publish event
            success = await EventPublisher.publish_event(event, topic, session, max_retries)

            if success:
                # Reset failure count on success
                failure_count = 0
            else:
                # Increment failure count on failure
                failure_count += 1
                last_failure_time = datetime.utcnow()

                # Open circuit if too many failures
                if failure_count >= 5:  # After 5 consecutive failures
                    circuit_open = True
                    logger.warning("Circuit breaker opened due to repeated failures")

            return success

        return circuit_breaker_wrapper()

    @staticmethod
    def publish_batch_events(
        events: List[EventEnvelope],
        topic: Optional[str] = None,
        session: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Publish a batch of events with individual retry logic

        Args:
            events: List of events to publish
            topic: Optional topic name (defaults based on event type)
            session: Optional database session for audit logging

        Returns:
            Dict with success/failure counts and details
        """
        import asyncio

        results = {
            "total": len(events),
            "successful": 0,
            "failed": 0,
            "failed_events": []
        }

        async def process_batch():
            for event in events:
                success = await EventPublisher.publish_event(event, topic, session)
                if success:
                    results["successful"] += 1
                else:
                    results["failed"] += 1
                    results["failed_events"].append({
                        "event_id": event.event_id,
                        "event_type": event.event_type,
                        "error": f"Failed to publish event {event.event_id}"
                    })

        # Process batch in background
        asyncio.create_task(process_batch())

        return results

    @staticmethod
    async def _log_event_to_db(session: Session, event: EventEnvelope) -> bool:
        """
        Log event to database for audit purposes

        Args:
            session: Database session
            event: Event to log

        Returns:
            bool: True if event was logged successfully
        """
        try:
            from ..models import EventLog
            from ..services.task_service import TaskService

            # Create event log record
            event_log = EventLog(
                event_id=event.event_id,
                event_type=event.event_type,
                event_version=event.event_version,
                aggregate_type=event.aggregate_type,
                aggregate_id=event.aggregate_id,
                payload=event.data,
                metadata=event.metadata.dict() if event.metadata else {},
                timestamp=event.timestamp,
                user_id=event.metadata.user_id if event.metadata else None
            )

            # Add to database
            session.add(event_log)
            session.commit()

            return True
        except Exception as e:
            logger.error(f"Failed to log event to database: {str(e)}")
            return False

    @staticmethod
    async def _handle_failed_event(event: EventEnvelope, error_message: str) -> bool:
        """
        Handle failed event publishing by putting it in a dead letter queue

        Args:
            event: The event that failed to publish
            error_message: Error that occurred during publishing

        Returns:
            bool: True if event was handled successfully
        """
        # This method would be called when an event fails to publish
        # For now, we'll just log the failure
        logger.warning(f"Event {event.event_id} failed to publish: {error_message}")
        return True  # Return success to avoid infinite retries in this example

    @staticmethod
    def create_idempotency_key(operation: str, user_id: str, data: Dict[str, Any]) -> str:
        """
        Create an idempotency key to prevent duplicate event processing

        Args:
            operation: Operation type (create_task, update_task, etc.)
            user_id: User ID performing the operation
            data: Operation data for uniqueness

        Returns:
            str: Idempotency key
        """
        import hashlib
        # Create hash of operation + user_id + data for uniqueness
        data_str = json.dumps(data, sort_keys=True, default=str)
        key_str = f"{operation}:{user_id}:{data_str}"
        return hashlib.sha256(key_str.encode()).hexdigest()[:32]

    @staticmethod
    async def publish_with_retry(
        event: EventEnvelope,
        topic: str,
        max_retries: int = 3,
        session: Optional[Session] = None
    ) -> bool:
        """
        Publish an event with retry logic

        Args:
            event: Event to publish
            topic: Topic to publish to
            max_retries: Maximum number of retry attempts
            session: Optional database session

        Returns:
            bool: True if event published successfully after retries
        """
        for attempt in range(max_retries):
            try:
                success = await EventPublisher.publish_event(event, topic, session)
                if success:
                    logger.info(f"Event {event.event_id} published successfully after {attempt + 1} attempts")
                    return True
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} to publish event {event.event_id} failed: {str(e)}")
                if attempt < max_retries - 1:
                    # Wait before retrying with exponential backoff
                    await asyncio.sleep(2 ** attempt)  # 1s, 2s, 4s...

        logger.error(f"All {max_retries} attempts to publish event {event.event_id} failed")
        return False

    @staticmethod
    async def publish_task_event(
        session: Session,
        user_id: str,
        task: Task,
        event_type: EventType
    ) -> bool:
        """
        Publish a task-specific event with proper data structure

        Args:
            session: Database session
            user_id: User ID associated with the event
            task: Task object for the event
            event_type: Type of task event to publish

        Returns:
            bool: True if event published successfully
        """
        try:
            # Prepare event data based on task and event type
            task_data = {
                "task_id": task.id,
                "user_id": task.user_id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "recurrence_pattern": task.recurrence_pattern,
                "recurrence_config": task.recurrence_config,
                "parent_task_id": task.parent_task_id,
                "next_occurrence": task.next_occurrence.isoformat() if task.next_occurrence else None,
                "occurrences_remaining": task.occurrences_remaining,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }

            event = EventPublisher.create_task_event(
                event_type=event_type,
                user_id=user_id,
                data=task_data,
                task_id=task.id
            )

            return await EventPublisher.publish_with_retry(
                event=event,
                topic="task-events",
                session=session
            )
        except Exception as e:
            logger.error(f"Failed to publish task event: {str(e)}")
            return False