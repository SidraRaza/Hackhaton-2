"""
End-to-End Event Flow Tests for Phase V: Advanced Cloud Deployment
Tests complete event flows from task creation through completion with all consumers
"""
import pytest
from unittest.mock import Mock, patch
from sqlmodel import Session, create_engine
from datetime import datetime, timedelta
from typing import Dict, Any

from backend.models import Task, AuditLog
from backend.events.consumers import EventConsumerService
from backend.services.event_publisher import EventPublisher
from backend.events.schemas.event_envelope import EventType
from backend.database import create_db_and_tables


@pytest.fixture
def db_session():
    """Create a test database session"""
    engine = create_engine("sqlite:///:memory:", echo=True)
    create_db_and_tables(engine)

    with Session(engine) as session:
        yield session


class TestCompleteEventFlows:
    """Tests for complete end-to-end event flows"""

    def test_task_lifecycle_with_all_consumers(self, db_session):
        """Test complete task lifecycle: create -> update -> complete -> audit -> notification -> recurrence"""

        # 1. Create a recurring task
        task_data = {
            "id": 1,
            "user_id": "test-user-123",
            "title": "Daily Workout",
            "description": "Do 30 minutes of exercise",
            "completed": False,
            "priority": "high",
            "due_date": datetime.now() + timedelta(days=1),
            "recurrence_pattern": "daily",
            "recurrence_config": {"interval": 1},
            "parent_task_id": None,
            "next_occurrence": None,
            "occurrences_remaining": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Create the task in the database
        task = Task(**task_data)
        db_session.add(task)
        db_session.commit()

        # 2. Simulate task created event
        event_publisher = EventPublisher()
        task_created_event = event_publisher.create_task_event(
            event_type=EventType.TASK_CREATED,
            user_id="test-user-123",
            data={
                "task_id": 1,
                "user_id": "test-user-123",
                "title": "Daily Workout",
                "priority": "high",
                "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "recurrence_pattern": "daily",
                "recurrence_config": {"interval": 1},
                "tag_ids": [],
                "created_at": datetime.utcnow().isoformat()
            },
            task_id=1
        )

        # 3. Process the event through all consumers
        consumer_service = EventConsumerService(db_session)
        results = consumer_service.route_event_to_consumers(task_created_event.dict())

        # Verify audit consumer processed the event
        assert results['audit'] is True

        # 4. Simulate task completion event (which should trigger recurrence)
        task_completed_event = event_publisher.create_task_event(
            event_type=EventType.TASK_COMPLETED,
            user_id="test-user-123",
            data={
                "task_id": 1,
                "user_id": "test-user-123",
                "completed_at": datetime.utcnow().isoformat(),
                "was_recurring": True,
                "mark_series_complete": False
            },
            task_id=1
        )

        # Process the completion event through all consumers
        completion_results = consumer_service.route_event_to_consumers(task_completed_event.dict())

        # Verify recurrence consumer processed the event and created a new occurrence
        assert completion_results['recurrence'] is True
        assert completion_results['audit'] is True

        # 5. Verify that audit logs were created for both events
        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.user_id == "test-user-123"
        ).all()

        # Should have at least 2 audit logs (created and completed)
        assert len(audit_logs) >= 2

        # 6. Verify that the next occurrence was created
        # Look for a task with parent_task_id = 1 (the original task)
        next_occurrence = db_session.query(Task).filter(
            Task.parent_task_id == 1
        ).first()

        assert next_occurrence is not None
        assert next_occurrence.title == "Daily Workout"
        assert next_occurrence.completed is False

        print("✅ Complete task lifecycle test passed!")

    def test_reminder_notification_flow(self, db_session):
        """Test reminder notification flow: task created -> reminder triggered -> notification sent"""

        # 1. Create a task with due date
        task_data = {
            "id": 2,
            "user_id": "test-user-456",
            "title": "Meeting with team",
            "description": "Weekly team meeting",
            "completed": False,
            "priority": "medium",
            "due_date": datetime.now() + timedelta(minutes=30),
            "recurrence_pattern": None,
            "recurrence_config": None,
            "parent_task_id": None,
            "next_occurrence": None,
            "occurrences_remaining": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Create the task in the database
        task = Task(**task_data)
        db_session.add(task)
        db_session.commit()

        # 2. Simulate reminder triggered event
        event_publisher = EventPublisher()
        reminder_event = event_publisher.create_task_event(
            event_type=EventType.REMINDER_TRIGGERED,
            user_id="test-user-456",
            data={
                "user_id": "test-user-456",
                "task_id": 2,
                "reminder_type": "due_soon",
                "trigger_time": datetime.utcnow().isoformat()
            }
        )

        # 3. Process the reminder event through all consumers
        consumer_service = EventConsumerService(db_session)

        # Mock the notification service to avoid actual notification sending
        with patch('backend.services.notification_service.NotificationService.send_task_reminder_notification') as mock_notify:
            mock_notify.return_value = True

            reminder_results = consumer_service.route_event_to_consumers(reminder_event.dict())

        # Verify notification consumer processed the event
        assert reminder_results['notification'] is True

        # Verify the mock was called (meaning notification would have been sent)
        mock_notify.assert_called_once()

        print("✅ Reminder notification flow test passed!")

    def test_multiple_event_types_flow(self, db_session):
        """Test processing multiple different event types in sequence"""

        # 1. Create a task
        task_data = {
            "id": 3,
            "user_id": "test-user-789",
            "title": "Project deadline",
            "description": "Submit project proposal",
            "completed": False,
            "priority": "high",
            "due_date": datetime.now() + timedelta(days=7),
            "recurrence_pattern": "weekly",
            "recurrence_config": {"days_of_week": [0]},  # Every Monday
            "parent_task_id": None,
            "next_occurrence": None,
            "occurrences_remaining": 4,  # 4 occurrences total
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        task = Task(**task_data)
        db_session.add(task)
        db_session.commit()

        # 2. Create event publisher
        event_publisher = EventPublisher()

        # 3. Simulate multiple events in sequence
        events_sequence = [
            # Task created
            event_publisher.create_task_event(
                event_type=EventType.TASK_CREATED,
                user_id="test-user-789",
                data={
                    "task_id": 3,
                    "user_id": "test-user-789",
                    "title": "Project deadline",
                    "priority": "high",
                    "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                    "recurrence_pattern": "weekly",
                    "recurrence_config": {"days_of_week": [0]},
                    "occurrences_remaining": 4,
                    "created_at": datetime.utcnow().isoformat()
                },
                task_id=3
            ),

            # Task updated
            event_publisher.create_task_event(
                event_type=EventType.TASK_UPDATED,
                user_id="test-user-789",
                data={
                    "task_id": 3,
                    "user_id": "test-user-789",
                    "changes": {"priority": "high", "title": "URGENT: Project deadline"},
                    "updated_fields": ["priority", "title"],
                    "updated_at": datetime.utcnow().isoformat()
                },
                task_id=3
            ),

            # Task completed (should trigger next occurrence)
            event_publisher.create_task_event(
                event_type=EventType.TASK_COMPLETED,
                user_id="test-user-789",
                data={
                    "task_id": 3,
                    "user_id": "test-user-789",
                    "completed_at": datetime.utcnow().isoformat(),
                    "was_recurring": True,
                    "mark_series_complete": False,
                    "occurrences_remaining": 3
                },
                task_id=3
            )
        ]

        # 4. Process all events through the consumer service
        consumer_service = EventConsumerService(db_session)

        all_results = []
        for event in events_sequence:
            result = consumer_service.route_event_to_consumers(event.dict())
            all_results.append(result)

        # 5. Verify all events were processed successfully
        for result in all_results:
            assert all(value is True for value in result.values()), f"Event processing failed: {result}"

        # 6. Verify that audit logs were created for all events
        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.user_id == "test-user-789"
        ).all()

        assert len(audit_logs) >= 3  # At least one for each event type

        # 7. Verify that the next occurrence was created
        next_occurrence = db_session.query(Task).filter(
            Task.parent_task_id == 3
        ).first()

        assert next_occurrence is not None
        assert next_occurrence.title == "Project deadline"
        assert next_occurrence.completed is False

        print("✅ Multiple event types flow test passed!")

    def test_batch_processing_flow(self, db_session):
        """Test processing a batch of events"""

        # Create some tasks
        tasks_data = [
            {
                "id": 4,
                "user_id": "batch-user-1",
                "title": "Batch Task 1",
                "completed": False,
                "priority": "medium",
                "due_date": datetime.now() + timedelta(days=1),
                "recurrence_pattern": None,
                "recurrence_config": None,
                "parent_task_id": None,
                "next_occurrence": None,
                "occurrences_remaining": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": 5,
                "user_id": "batch-user-2",
                "title": "Batch Task 2",
                "completed": False,
                "priority": "high",
                "due_date": datetime.now() + timedelta(days=2),
                "recurrence_pattern": None,
                "recurrence_config": None,
                "parent_task_id": None,
                "next_occurrence": None,
                "occurrences_remaining": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]

        for task_data in tasks_data:
            task = Task(**task_data)
            db_session.add(task)
        db_session.commit()

        # Create event publisher and batch of events
        event_publisher = EventPublisher()
        batch_events = []

        for i, task_data in enumerate(tasks_data, start=4):
            event = event_publisher.create_task_event(
                event_type=EventType.TASK_CREATED,
                user_id=task_data["user_id"],
                data={
                    "task_id": task_data["id"],
                    "user_id": task_data["user_id"],
                    "title": task_data["title"],
                    "priority": task_data["priority"],
                    "due_date": task_data["due_date"].isoformat(),
                    "created_at": datetime.utcnow().isoformat()
                },
                task_id=task_data["id"]
            )
            batch_events.append(event.dict())

        # Process the batch
        consumer_service = EventConsumerService(db_session)
        batch_results = consumer_service.process_event_batch(batch_events)

        # Verify batch processing results
        assert batch_results['total'] == 2
        assert batch_results['successful'] == 2
        assert batch_results['failed'] == 0

        print("✅ Batch processing flow test passed!")


if __name__ == "__main__":
    # Run the tests manually if this file is executed directly
    import sys
    import os

    # Add the backend directory to the path so imports work
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

    # Create a simple test session
    engine = create_engine("sqlite:///:memory:", echo=False)
    create_db_and_tables(engine)

    with Session(engine) as session:
        test_instance = TestCompleteEventFlows()

        print("Running end-to-end event flow tests...")
        test_instance.test_task_lifecycle_with_all_consumers(session)
        session.rollback()  # Reset for next test

        test_instance.test_reminder_notification_flow(session)
        session.rollback()

        test_instance.test_multiple_event_types_flow(session)
        session.rollback()

        test_instance.test_batch_processing_flow(session)

        print("\n🎉 All end-to-end event flow tests passed!")