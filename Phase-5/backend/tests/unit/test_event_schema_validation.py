import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from uuid import uuid4

from models import Task
from services.task_service import TaskService
from services.search_service import SearchService
from services.priority_service import PriorityService
from events.schemas.event_envelope import EventEnvelope, EventMetadata, TaskEventEnvelope, UserEventEnvelope, SystemEventEnvelope, EventValidator, EventFactory
from events.schemas.task_events import TaskCreatedEvent, TaskCreatedEventData, EventType


@pytest.fixture(name="engine")
def fixture_engine():
    """Create in-memory SQLite engine for testing"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(name="session")
def fixture_session(engine):
    """Create a test session"""
    with Session(engine) as session:
        yield session


class TestEventSchemaValidation:
    """Unit tests for event schema validation"""

    def test_event_envelope_required_fields(self):
        """Test that event envelope has all required fields"""
        # Create event with minimal required data
        event = EventEnvelope(
            event_type="test.event",
            source="test-service",
            data={"test": "data"}
        )

        # Verify required fields exist
        assert event.event_id is not None
        assert event.event_type == "test.event"
        assert event.source == "test-service"
        assert event.data == {"test": "data"}
        assert event.timestamp is not None
        assert event.metadata is not None

    def test_event_metadata_defaults(self):
        """Test that event metadata has correct defaults"""
        metadata = EventMetadata()

        # Verify defaults are set
        assert metadata.correlation_id is not None
        assert metadata.source_service == "todo-service"
        assert metadata.timestamp is not None

    def test_task_event_envelope_creation(self):
        """Test creating task-specific event envelope"""
        task_event = TaskEventEnvelope(
            event_type="task.created",
            source="todo-service",
            data={"task_id": 1, "title": "Test Task"},
            task_id=1,
            user_id="test-user-123"
        )

        assert task_event.event_type == "task.created"
        assert task_event.task_id == 1
        assert task_event.user_id == "test-user-123"
        assert task_event.aggregate_type == "task"
        assert task_event.aggregate_id is not None

    def test_user_event_envelope_creation(self):
        """Test creating user-specific event envelope"""
        user_event = UserEventEnvelope(
            event_type="user.registered",
            source="auth-service",
            data={"user_id": "test-user-123", "email": "test@example.com"},
            user_id="test-user-123"
        )

        assert user_event.event_type == "user.registered"
        assert user_event.user_id == "test-user-123"
        assert user_event.aggregate_type == "user"
        assert user_event.aggregate_id is not None

    def test_system_event_envelope_creation(self):
        """Test creating system-specific event envelope"""
        sys_event = SystemEventEnvelope(
            event_type="system.started",
            source="system-service",
            data={"status": "started", "component": "scheduler"},
            service_name="scheduler-service",
            component_name="task-processor"
        )

        assert sys_event.event_type == "system.started"
        assert sys_event.service_name == "scheduler-service"
        assert sys_event.component_name == "task-processor"
        assert sys_event.aggregate_type == "system"

    def test_event_validator_base_structure(self):
        """Test event validator for base event structure"""
        event = EventEnvelope(
            event_type="test.event",
            source="test-service",
            data={"test": "data"}
        )

        result = EventValidator.validate_event_structure(event)
        assert result is True

        # Test with missing required fields
        event_missing_type = EventEnvelope(
            source="test-service",
            data={"test": "data"}
        )
        # Set event_type to None to test validation
        event_missing_type.event_type = None
        result = EventValidator.validate_event_structure(event_missing_type)
        assert result is False

    def test_task_event_validator_structure(self):
        """Test task event validator for structure"""
        task_event = TaskEventEnvelope(
            event_type="task.created",
            source="todo-service",
            data={"task_id": 1, "title": "Test Task"},
            task_id=1,
            user_id="test-user-123"
        )

        result = EventValidator.validate_task_event_structure(task_event)
        assert result is True

        # Test with missing task_id
        task_event_missing_task = TaskEventEnvelope(
            event_type="task.created",
            source="todo-service",
            data={"title": "Test Task"},
            user_id="test-user-123"
        )
        result = EventValidator.validate_task_event_structure(task_event_missing_task)
        assert result is False

        # Test with missing user_id
        task_event_missing_user = TaskEventEnvelope(
            event_type="task.created",
            source="todo-service",
            data={"task_id": 1, "title": "Test Task"},
            task_id=1
        )
        result = EventValidator.validate_task_event_structure(task_event_missing_user)
        assert result is False

    def test_user_event_validator_structure(self):
        """Test user event validator for structure"""
        user_event = UserEventEnvelope(
            event_type="user.registered",
            source="auth-service",
            data={"email": "test@example.com"},
            user_id="test-user-123"
        )

        result = EventValidator.validate_user_event_structure(user_event)
        assert result is True

        # Test with missing user_id
        user_event_missing_user = UserEventEnvelope(
            event_type="user.registered",
            source="auth-service",
            data={"email": "test@example.com"}
        )
        result = EventValidator.validate_user_event_structure(user_event_missing_user)
        assert result is False

    def test_system_event_validator_structure(self):
        """Test system event validator for structure"""
        sys_event = SystemEventEnvelope(
            event_type="system.started",
            source="system-service",
            data={"status": "started"}
        )

        result = EventValidator.validate_system_event_structure(sys_event)
        assert result is True

    def test_event_serialization(self):
        """Test event serialization to/from dict"""
        event = EventEnvelope(
            event_type="task.created",
            source="todo-service",
            data={"task_id": 1, "title": "Test Task"}
        )

        # Convert to dict
        event_dict = event.dict()
        assert "event_type" in event_dict
        assert "source" in event_dict
        assert "data" in event_dict
        assert event_dict["data"]["task_id"] == 1

    def test_task_event_serialization(self):
        """Test task event serialization"""
        task_event = TaskEventEnvelope(
            event_type="task.created",
            source="todo-service",
            data={
                "task_id": 1,
                "user_id": "test-user-123",
                "title": "Test Task",
                "priority": "high"
            },
            task_id=1,
            user_id="test-user-123"
        )

        event_dict = task_event.dict()
        assert event_dict["task_id"] == 1
        assert event_dict["user_id"] == "test-user-123"
        assert event_dict["aggregate_type"] == "task"
        assert event_dict["data"]["priority"] == "high"

    def test_event_factory_creation(self):
        """Test event factory for creating properly formatted events"""
        # Test task event creation
        task_event = EventFactory.create_task_event(
            event_type="task.created",
            task_id=1,
            user_id="test-user-123",
            data={"title": "New Task", "priority": "high"}
        )

        assert task_event.event_type == "task.created"
        assert task_event.task_id == 1
        assert task_event.user_id == "test-user-123"
        assert task_event.aggregate_type == "task"
        assert task_event.aggregate_id == "1"

        # Test user event creation
        user_event = EventFactory.create_user_event(
            event_type="user.registered",
            user_id="test-user-123",
            data={"email": "test@example.com", "name": "Test User"}
        )

        assert user_event.event_type == "user.registered"
        assert user_event.user_id == "test-user-123"
        assert user_event.aggregate_type == "user"
        assert user_event.aggregate_id == "test-user-123"

        # Test system event creation
        sys_event = EventFactory.create_system_event(
            event_type="system.started",
            data={"status": "running", "component": "scheduler"},
            service_name="scheduler-service",
            component_name="task-processor"
        )

        assert sys_event.event_type == "system.started"
        assert sys_event.service_name == "scheduler-service"
        assert sys_event.component_name == "task-processor"
        assert sys_event.aggregate_type == "system"

    def test_event_envelope_json_encoding(self):
        """Test JSON encoding of event envelope"""
        event = EventEnvelope(
            event_type="test.event",
            source="test-service",
            data={"timestamp": datetime.utcnow()}
        )

        # Test JSON serialization
        import json
        json_str = event.json()
        assert "event_type" in json_str
        assert "test.event" in json_str
        assert "data" in json_str

        # Test deserialization
        parsed_event = EventEnvelope.parse_raw(json_str)
        assert parsed_event.event_type == "test.event"
        assert parsed_event.source == "test-service"

    def test_event_versioning(self):
        """Test event versioning for backward compatibility"""
        # Test default version
        event_default = EventEnvelope(
            event_type="test.event",
            source="test-service",
            data={"test": "data"}
        )
        assert event_default.event_version == "1.0"

        # Test explicit version
        event_v1 = EventEnvelope(
            event_type="test.event",
            event_version="1.5",
            source="test-service",
            data={"test": "data"}
        )
        assert event_v1.event_version == "1.5"

    def test_event_metadata_enrichment(self):
        """Test that event metadata is properly enriched"""
        metadata = EventMetadata(
            user_id="test-user-123",
            trace_id="test-trace-123",
            client_ip="192.168.1.1"
        )

        assert metadata.user_id == "test-user-123"
        assert metadata.trace_id == "test-trace-123"
        assert metadata.client_ip == "192.168.1.1"
        assert metadata.timestamp is not None
        assert metadata.correlation_id is not None

    def test_task_event_priority_validation(self):
        """Test validation of priority in task events"""
        # Valid priority
        task_data = TaskCreatedEventData(
            task_id=1,
            user_id="test-user-123",
            title="Test Task",
            priority="high",
            created_at=datetime.utcnow()
        )
        assert task_data.priority == "high"

        # Test validation through service
        result = PriorityService.validate_priority_value("high")
        assert result is True

        # Test invalid priority
        with pytest.raises(ValueError):
            PriorityService.validate_priority_value("invalid_priority")

    def test_event_factory_with_complex_data(self):
        """Test event factory with complex data structures"""
        complex_data = {
            "task_id": 1,
            "user_id": "test-user-123",
            "title": "Complex Task",
            "description": "Task with complex data",
            "priority": "high",
            "due_date": datetime.utcnow().isoformat(),
            "tags": ["work", "urgent"],
            "metadata": {
                "source_app": "todo-web",
                "device": "desktop",
                "location": "US-East"
            }
        }

        task_event = EventFactory.create_task_event(
            event_type="task.created",
            task_id=1,
            user_id="test-user-123",
            data=complex_data
        )

        assert task_event.event_type == "task.created"
        assert task_event.data["task_id"] == 1
        assert task_event.data["tags"] == ["work", "urgent"]
        assert task_event.data["metadata"]["source_app"] == "todo-web"

    def test_event_validator_handles_none_values_gracefully(self):
        """Test that validators handle None values gracefully"""
        # Test with None event
        result = EventValidator.validate_event_structure(None)
        assert result is False

        # Test with minimal valid event
        event = EventEnvelope(
            event_type="test.event",
            source="test-service",
            data={}
        )
        result = EventValidator.validate_event_structure(event)
        assert result is True

    def test_event_envelope_extra_fields_allowed(self):
        """Test that event envelope allows extra fields for flexibility"""
        event = EventEnvelope(
            event_type="test.event",
            source="test-service",
            data={"test": "data"},
            # Extra fields should be allowed
            custom_field="custom_value",
            another_field=123
        )

        # Should not raise an error for extra fields
        assert event.event_type == "test.event"
        # The extra fields would be accessible depending on the model configuration


class TestTaskEventValidation:
    """Tests specifically for task-related event validation"""

    def test_task_created_event_validation(self):
        """Test validation of task.created event"""
        event_data = {
            "task_id": 1,
            "user_id": "test-user-123",
            "title": "Test Task",
            "description": "Test Description",
            "priority": "medium",
            "due_date": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }

        task_created_event = TaskCreatedEventData(**event_data)
        assert task_created_event.task_id == 1
        assert task_created_event.user_id == "test-user-123"
        assert task_created_event.priority == "medium"

    def test_task_created_event_with_all_fields(self, session):
        """Test task.created event with all possible fields"""
        future_date = datetime.utcnow() + timedelta(days=1)

        event_data = {
            "task_id": 1,
            "user_id": "test-user-123",
            "title": "Full Featured Task",
            "description": "Task with all features",
            "priority": "high",
            "due_date": future_date,
            "recurrence_pattern": "daily",
            "recurrence_config": {"interval": 1},
            "tag_ids": [1, 2, 3],
            "created_at": datetime.utcnow()
        }

        task_created_event = TaskCreatedEventData(**event_data)
        assert task_created_event.task_id == 1
        assert task_created_event.priority == "high"
        assert task_created_event.due_date == future_date
        assert task_created_event.recurrence_pattern == "daily"

    def test_task_event_factory_methods(self):
        """Test specialized task event creation methods"""
        # Test creating various task events
        task_created = EventFactory.create_task_event(
            event_type=EventType.TASK_CREATED.value,
            task_id=1,
            user_id="test-user-123",
            data={"title": "New Task", "priority": "low"}
        )
        assert task_created.event_type == EventType.TASK_CREATED.value

        task_updated = EventFactory.create_task_event(
            event_type=EventType.TASK_UPDATED.value,
            task_id=1,
            user_id="test-user-123",
            data={"title": "Updated Task", "changes": {"priority": "low -> high"}}
        )
        assert task_updated.event_type == EventType.TASK_UPDATED.value

        task_completed = EventFactory.create_task_event(
            event_type=EventType.TASK_COMPLETED.value,
            task_id=1,
            user_id="test-user-123",
            data={"completed_at": datetime.utcnow()}
        )
        assert task_completed.event_type == EventType.TASK_COMPLETED.value

    def test_event_type_enum_validation(self):
        """Test that event type enum has correct values"""
        assert EventType.TASK_CREATED.value == "task.created"
        assert EventType.TASK_UPDATED.value == "task.updated"
        assert EventType.TASK_COMPLETED.value == "task.completed"
        assert EventType.TASK_DELETED.value == "task.deleted"
        assert EventType.TASK_RECURRENCE_CREATED.value == "task.recurrence_created"
        assert EventType.USER_REGISTERED.value == "user.registered"
        assert EventType.USER_LOGGED_IN.value == "user.logged_in"
        assert EventType.USER_PREFERENCES_UPDATED.value == "user.preferences_updated"
        assert EventType.REMINDER_TRIGGERED.value == "reminder.triggered"
        assert EventType.NOTIFICATION_SENT.value == "notification.sent"
        assert EventType.AUDIT_LOG_CREATED.value == "audit.log_created"


class TestIntegrationEventValidation:
    """Integration tests for event validation with other services"""

    def test_task_service_event_integration(self, session):
        """Test that task service properly validates events"""
        # Create a task through the service
        task = Task(
            user_id="test-user-123",
            title="Integration Test Task",
            priority="medium",
            due_date=datetime.utcnow() + timedelta(days=1)
        )

        # Create the task in the database
        created_task = TaskService.create_task(session, task)
        assert created_task.id is not None
        assert created_task.priority == "medium"

        # Verify that the task can be used to create an event
        event_data = {
            "task_id": created_task.id,
            "user_id": created_task.user_id,
            "title": created_task.title,
            "priority": created_task.priority,
            "due_date": created_task.due_date,
            "created_at": created_task.created_at
        }

        task_event = TaskCreatedEventData(**event_data)
        assert task_event.task_id == created_task.id
        assert task_event.title == "Integration Test Task"

    def test_search_service_with_events(self, session):
        """Test that search service works with event data"""
        # Create tasks with different priorities
        tasks = [
            Task(user_id="test-user-123", title="High Priority Task", priority="high"),
            Task(user_id="test-user-123", title="Low Priority Task", priority="low"),
            Task(user_id="test-user-123", title="Medium Priority Task", priority="medium")
        ]

        for task in tasks:
            session.add(task)
        session.commit()

        # Test searching with priority filter
        results = SearchService.search_tasks_with_filters(
            session=session,
            user_id="test-user-123",
            query="",
            filters={"priority": ["high"]}
        )

        assert len(results) == 1
        assert results[0]["task"].priority == "high"

    def test_priority_service_with_events(self):
        """Test that priority service validates event data properly"""
        # Test priority validation
        assert PriorityService.validate_priority_value("high") is True
        assert PriorityService.validate_priority_value("medium") is True
        assert PriorityService.validate_priority_value("low") is True

        # Test invalid priority
        with pytest.raises(ValueError):
            PriorityService.validate_priority_value("invalid")

        # Test None value (should be allowed)
        assert PriorityService.validate_priority_value(None) is True


def test_event_schema_completeness():
    """Test that all required event schemas are complete"""
    # Verify all event types exist
    event_types = [e.value for e in EventType]
    required_events = [
        "task.created", "task.updated", "task.completed", "task.deleted",
        "task.recurrence_created", "user.registered", "user.logged_in",
        "user.preferences_updated", "reminder.triggered", "notification.sent",
        "audit.log_created"
    ]

    for event_type in required_events:
        assert event_type in event_types, f"Missing required event type: {event_type}"


def test_event_schema_backward_compatibility():
    """Test that event schemas maintain backward compatibility"""
    # Create event with minimal data (older format)
    minimal_event = EventEnvelope(
        event_type="task.created",
        source="todo-service",
        data={"task_id": 1, "title": "Test"},
        timestamp=datetime.utcnow()
    )

    # Should still be valid with newer schema
    validation_result = EventValidator.validate_event_structure(minimal_event)
    assert validation_result is True


if __name__ == "__main__":
    pytest.main([__file__])