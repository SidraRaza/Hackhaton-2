"""
Integration tests for event consumers
Tests for audit, notification, and recurrence consumers
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from sqlmodel import Session, create_engine
from datetime import datetime
from typing import Dict, Any

from backend.models import Task, AuditLog
from backend.events.consumers.audit_consumer import AuditEventConsumer
from backend.events.consumers.notification_consumer import NotificationEventConsumer
from backend.events.consumers.recurrence_consumer import RecurrenceEventConsumer
from backend.services.audit_service import AuditAction
from backend.database import create_db_and_tables


@pytest.fixture
def db_session():
    """Create a test database session"""
    engine = create_engine("sqlite:///./test.db", echo=True)
    create_db_and_tables(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture
def sample_task_data():
    """Sample task data for testing"""
    return {
        "id": 1,
        "user_id": "test-user-123",
        "title": "Test Task",
        "description": "Test Description",
        "completed": False,
        "priority": "medium",
        "due_date": datetime(2024, 12, 31),
        "recurrence_pattern": None,
        "recurrence_config": None,
        "parent_task_id": None,
        "next_occurrence": None,
        "occurrences_remaining": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


class TestAuditEventConsumer:
    """Tests for the AuditEventConsumer class"""

    def test_process_task_created_event(self, db_session, sample_task_data):
        """Test processing of task.created events"""
        consumer = AuditEventConsumer(db_session)

        event_data = {
            "event_type": "task.created",
            "task_id": 1,
            "user_id": "test-user-123",
            "title": "Test Task",
            "priority": "high",
            "due_date": "2024-12-31T00:00:00Z",
            "recurrence_pattern": None,
            "recurrence_config": None,
            "tag_ids": [],
            "created_at": "2024-01-01T00:00:00Z"
        }

        result = consumer.process_task_created_event(event_data)

        # Check that an audit log was created
        assert result is not None
        assert result.action == AuditAction.TASK_CREATED.value
        assert result.user_id == "test-user-123"
        assert result.resource_type == "task"
        assert result.resource_id == "1"

    def test_process_task_updated_event(self, db_session, sample_task_data):
        """Test processing of task.updated events"""
        consumer = AuditEventConsumer(db_session)

        event_data = {
            "event_type": "task.updated",
            "task_id": 1,
            "user_id": "test-user-123",
            "changes": {"title": "Updated Title"},
            "updated_fields": ["title"],
            "updated_at": "2024-01-02T00:00:00Z"
        }

        result = consumer.process_task_updated_event(event_data)

        # Check that an audit log was created
        assert result is not None
        assert result.action == AuditAction.TASK_UPDATED.value
        assert result.user_id == "test-user-123"

    def test_process_task_completed_event(self, db_session, sample_task_data):
        """Test processing of task.completed events"""
        consumer = AuditEventConsumer(db_session)

        event_data = {
            "event_type": "task.completed",
            "task_id": 1,
            "user_id": "test-user-123",
            "completed_at": "2024-01-03T00:00:00Z",
            "was_recurring": False,
            "mark_series_complete": False
        }

        result = consumer.process_task_completed_event(event_data)

        # Check that an audit log was created
        assert result is not None
        assert result.action == AuditAction.TASK_COMPLETED.value
        assert result.user_id == "test-user-123"

    def test_process_task_deleted_event(self, db_session, sample_task_data):
        """Test processing of task.deleted events"""
        consumer = AuditEventConsumer(db_session)

        event_data = {
            "event_type": "task.deleted",
            "task_id": 1,
            "user_id": "test-user-123",
            "deleted_at": "2024-01-04T00:00:00Z",
            "was_recurring": False
        }

        result = consumer.process_task_deleted_event(event_data)

        # Check that an audit log was created
        assert result is not None
        assert result.action == AuditAction.TASK_DELETED.value
        assert result.user_id == "test-user-123"

    def test_consume_unknown_event(self, db_session):
        """Test consuming an unknown event type"""
        consumer = AuditEventConsumer(db_session)

        event_data = {
            "event_type": "unknown.event.type",
            "user_id": "test-user-123"
        }

        result = consumer.consume_event(event_data)

        # Unknown event types should return False
        assert result is False


class TestNotificationEventConsumer:
    """Tests for the NotificationEventConsumer class"""

    @patch('backend.services.notification_service.NotificationService.send_task_reminder_notification')
    def test_process_reminder_triggered_event(self, mock_send_notification, db_session, sample_task_data):
        """Test processing of reminder.triggered events"""
        consumer = NotificationEventConsumer(db_session)

        # Create a mock task in the session
        task = Task(**sample_task_data)
        db_session.add(task)
        db_session.commit()

        event_data = {
            "event_type": "reminder.triggered",
            "user_id": "test-user-123",
            "task_id": 1,
            "reminder_type": "due_soon"
        }

        # Mock the notification service to return True
        mock_send_notification.return_value = True

        result = consumer.process_reminder_triggered_event(event_data)

        # Check that the notification service was called and result is True
        assert result is True
        mock_send_notification.assert_called_once()

    @patch('backend.services.notification_service.NotificationService.send_task_completion_notification')
    def test_process_task_completed_event_for_notification(self, mock_send_notification, db_session, sample_task_data):
        """Test processing of task.completed events for notifications"""
        consumer = NotificationEventConsumer(db_session)

        # Create a mock task in the session
        task = Task(**sample_task_data)
        db_session.add(task)
        db_session.commit()

        event_data = {
            "event_type": "task.completed",
            "user_id": "test-user-123",
            "task_id": 1
        }

        # Mock the notification service to return True
        mock_send_notification.return_value = True

        result = consumer.process_task_completed_event(event_data)

        # Check that the notification service was called and result is True
        assert result is True
        mock_send_notification.assert_called_once()

    def test_process_notification_sent_event(self, db_session):
        """Test processing of notification.sent events"""
        consumer = NotificationEventConsumer(db_session)

        event_data = {
            "event_type": "notification.sent",
            "notification_id": "notif-123",
            "user_id": "test-user-123",
            "task_id": 1,
            "channel": "browser",
            "sent_at": "2024-01-05T00:00:00Z"
        }

        result = consumer.process_notification_sent_event(event_data)

        # Processing should succeed
        assert result is True


class TestRecurrenceEventConsumer:
    """Tests for the RecurrenceEventConsumer class"""

    def test_process_task_completed_event_non_recurring(self, db_session, sample_task_data):
        """Test processing of task.completed events for non-recurring tasks"""
        consumer = RecurrenceEventConsumer(db_session)

        # Create a mock task in the session
        task = Task(**sample_task_data)
        db_session.add(task)
        db_session.commit()

        event_data = {
            "event_type": "task.completed",
            "task_id": 1,
            "user_id": "test-user-123",
            "completed_at": "2024-01-06T00:00:00Z",
            "was_recurring": False,
            "mark_series_complete": False
        }

        result = consumer.process_task_completed_event(event_data)

        # Processing should succeed (even if no recurrence is created)
        assert result is True

    def test_process_task_deleted_event(self, db_session, sample_task_data):
        """Test processing of task.deleted events"""
        consumer = RecurrenceEventConsumer(db_session)

        # Create a mock task in the session
        task = Task(**sample_task_data)
        db_session.add(task)
        db_session.commit()

        event_data = {
            "event_type": "task.deleted",
            "task_id": 1,
            "user_id": "test-user-123"
        }

        result = consumer.process_task_deleted_event(event_data)

        # Processing should succeed
        assert result is True


def test_end_to_end_event_flow(db_session):
    """Test a complete event flow from task creation to completion"""
    # This is a simplified test to verify the flow conceptually

    # 1. Simulate task creation event
    audit_consumer = AuditEventConsumer(db_session)

    task_created_event = {
        "event_type": "task.created",
        "task_id": 1,
        "user_id": "test-user-123",
        "title": "Test Recurring Task",
        "priority": "high",
        "due_date": "2024-12-31T00:00:00Z",
        "recurrence_pattern": "daily",
        "recurrence_config": {"interval": 1},
        "tag_ids": [],
        "created_at": "2024-01-01T00:00:00Z"
    }

    # Process the creation event
    audit_result = audit_consumer.consume_event(task_created_event)
    assert audit_result is True

    # 2. Simulate task completion event (which should trigger recurrence)
    recurrence_consumer = RecurrenceEventConsumer(db_session)

    task_completed_event = {
        "event_type": "task.completed",
        "task_id": 1,
        "user_id": "test-user-123",
        "completed_at": "2024-01-02T10:00:00Z",
        "was_recurring": True,
        "mark_series_complete": False
    }

    # Process the completion event
    recurrence_result = recurrence_consumer.consume_event(task_completed_event)
    assert recurrence_result is True

    # 3. Verify that the flow completed successfully
    assert audit_result and recurrence_result