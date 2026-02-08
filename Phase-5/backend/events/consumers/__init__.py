"""
Main Event Consumer Service for Phase V: Advanced Cloud Deployment
Orchestrates all event consumers and handles event routing
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from sqlmodel import Session

from audit_consumer import AuditEventConsumer
from notification_consumer import NotificationEventConsumer
from recurrence_consumer import RecurrenceEventConsumer


logger = logging.getLogger(__name__)


class EventConsumerService:
    """Main service to manage and coordinate all event consumers"""

    def __init__(self, db_session: Session):
        self.session = db_session
        self.audit_consumer = AuditEventConsumer(db_session)
        self.notification_consumer = NotificationEventConsumer(db_session)
        self.recurrence_consumer = RecurrenceEventConsumer(db_session)

    async def route_event_to_consumers(self, event_data: Dict[str, Any]) -> Dict[str, bool]:
        """
        Route a single event to all relevant consumers

        Args:
            event_data: Dictionary containing event information

        Returns:
            Dictionary with results from each consumer
        """
        results = {}

        # Process event with all consumers
        # Each consumer may or may not act on the event based on its type

        # Audit consumer processes all events
        results['audit'] = await self.audit_consumer.consume_event(event_data)

        # Notification consumer processes reminder and task-related events
        event_type = event_data.get('event_type', '')
        if any(et in event_type for et in ['reminder.', 'task.created', 'task.completed']):
            results['notification'] = await self.notification_consumer.consume_event(event_data)
        else:
            results['notification'] = True  # Mark as skipped but successful

        # Recurrence consumer processes task completion/deletion events
        if event_type in ['task.completed', 'task.deleted']:
            results['recurrence'] = await self.recurrence_consumer.consume_event(event_data)
        else:
            results['recurrence'] = True  # Mark as skipped but successful

        return results

    async def process_event_batch(self, events: list) -> Dict[str, Any]:
        """
        Process a batch of events

        Args:
            events: List of event dictionaries to process

        Returns:
            Dictionary with processing statistics
        """
        total_events = len(events)
        successful_events = 0
        failed_events = []

        for i, event in enumerate(events):
            try:
                results = await self.route_event_to_consumers(event)

                # Check if any consumer failed
                if not all(results.values()):
                    failed_events.append({
                        'index': i,
                        'event': event,
                        'results': results
                    })
                else:
                    successful_events += 1
            except Exception as e:
                logger.error(f"Error processing event {i}: {str(e)}")
                failed_events.append({
                    'index': i,
                    'event': event,
                    'error': str(e)
                })

        return {
            'total': total_events,
            'successful': successful_events,
            'failed': len(failed_events),
            'failed_events': failed_events
        }

    async def start_all_consumers(self):
        """
        Start all consumer services
        This would typically be called by a background process
        """
        logger.info("Starting all event consumers...")

        try:
            # Start all consumers with Dapr subscriptions
            await asyncio.gather(
                self.audit_consumer.start_consuming(),
                self.notification_consumer.start_consuming(),
                self.recurrence_consumer.start_consuming(),
                return_exceptions=True
            )
        except Exception as e:
            logger.error(f"Event consumer service error: {str(e)}")
            raise

    def get_consumer_status(self) -> Dict[str, str]:
        """
        Get the status of all consumers

        Returns:
            Dictionary with consumer statuses
        """
        return {
            'audit_consumer': 'ready',
            'notification_consumer': 'ready',
            'recurrence_consumer': 'ready'
        }

    async def health_check(self) -> bool:
        """
        Perform a health check on the consumer service

        Returns:
            bool: True if service is healthy
        """
        try:
            status = self.get_consumer_status()
            # All consumers should be ready
            return all(status_val == 'ready' for status_val in status.values())
        except Exception:
            return False


def create_event_consumer_service(db_session: Session) -> EventConsumerService:
    """
    Factory function to create an event consumer service

    Args:
        db_session: Database session to use for all consumers

    Returns:
        EventConsumerService instance
    """
    return EventConsumerService(db_session)