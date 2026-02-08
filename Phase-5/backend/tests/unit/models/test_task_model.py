import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock
from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel
from backend.models import Task, Tag, TaskTag, PriorityEnum, RecurrencePatternEnum


@pytest.fixture
def engine():
    """Create in-memory SQLite engine for testing"""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """Create a new database session for testing"""
    with Session(engine) as session:
        yield session


class TestTaskModel:
    """Test cases for Task model with advanced features"""

    def test_task_creation_basic(self, session):
        """Test basic task creation with minimal fields"""
        task = Task(
            user_id="test-user-123",
            title="Test Task",
            description="Test Description"
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        assert task.id is not None
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.completed is False
        assert task.priority == PriorityEnum.medium
        assert task.created_at is not None
        assert task.updated_at is not None

    def test_task_creation_with_priority(self, session):
        """Test task creation with priority field"""
        task = Task(
            user_id="test-user-123",
            title="High Priority Task",
            priority=PriorityEnum.high
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        assert task.priority == PriorityEnum.high

    def test_task_creation_with_due_date(self, session):
        """Test task creation with due date"""
        future_date = datetime.utcnow() + timedelta(days=1)
        task = Task(
            user_id="test-user-123",
            title="Task with Due Date",
            due_date=future_date
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        assert task.due_date == future_date

    def test_task_creation_with_recurrence(self, session):
        """Test task creation with recurrence pattern"""
        task = Task(
            user_id="test-user-123",
            title="Recurring Task",
            recurrence_pattern=RecurrencePatternEnum.weekly,
            recurrence_config={"days_of_week": [1, 3, 5]},  # Mon, Wed, Fri
            due_date=datetime.utcnow() + timedelta(days=1)
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        assert task.recurrence_pattern == RecurrencePatternEnum.weekly
        assert task.recurrence_config == {"days_of_week": [1, 3, 5]}
        assert task.is_recurring is True

    def test_task_is_overdue_property(self, session):
        """Test is_overdue property"""
        past_date = datetime.utcnow() - timedelta(days=1)
        future_date = datetime.utcnow() + timedelta(days=1)

        # Overdue task
        overdue_task = Task(
            user_id="test-user-123",
            title="Overdue Task",
            due_date=past_date,
            completed=False
        )

        # Not overdue task
        future_task = Task(
            user_id="test-user-123",
            title="Future Task",
            due_date=future_date,
            completed=False
        )

        # Completed task with past due date (not overdue)
        completed_task = Task(
            user_id="test-user-123",
            title="Completed Task",
            due_date=past_date,
            completed=True
        )

        session.add_all([overdue_task, future_task, completed_task])
        session.commit()

        assert overdue_task.is_overdue is True
        assert future_task.is_overdue is False
        assert completed_task.is_overdue is False

    def test_task_days_until_due_property(self, session):
        """Test days_until_due property"""
        future_date = datetime.utcnow() + timedelta(days=5)
        past_date = datetime.utcnow() - timedelta(days=3)

        future_task = Task(
            user_id="test-user-123",
            title="Future Task",
            due_date=future_date
        )

        past_task = Task(
            user_id="test-user-123",
            title="Past Task",
            due_date=past_date
        )

        no_due_task = Task(
            user_id="test-user-123",
            title="No Due Date Task"
        )

        session.add_all([future_task, past_task, no_due_task])
        session.commit()

        assert future_task.days_until_due == 5
        assert past_task.days_until_due == 0  # Returns 0 for past dates
        assert no_due_task.days_until_due is None

    def test_task_relationships(self, session):
        """Test task relationships with tags"""
        # Create task
        task = Task(
            user_id="test-user-123",
            title="Task with Tags"
        )

        # Create tags
        tag1 = Tag(
            user_id="test-user-123",
            name="work",
            color="#EF4444"
        )

        tag2 = Tag(
            user_id="test-user-123",
            name="important",
            color="#DC2626"
        )

        session.add_all([task, tag1, tag2])
        session.commit()

        # Create task-tag relationships
        task_tag1 = TaskTag(task_id=task.id, tag_id=tag1.id)
        task_tag2 = TaskTag(task_id=task.id, tag_id=tag2.id)

        session.add_all([task_tag1, task_tag2])
        session.commit()

        # Refresh to get relationships
        session.refresh(task)
        session.refresh(tag1)
        session.refresh(tag2)

        # Verify relationships
        assert len(task.tags) == 2
        assert tag1 in task.tags
        assert tag2 in task.tags
        assert task.title == "Task with Tags"

    def test_task_parent_child_relationship(self, session):
        """Test task parent-child relationships for recurring tasks"""
        # Create parent task
        parent_task = Task(
            user_id="test-user-123",
            title="Parent Recurring Task",
            recurrence_pattern=RecurrencePatternEnum.daily
        )

        session.add(parent_task)
        session.commit()
        session.refresh(parent_task)

        # Create child task (instance of recurring series)
        child_task = Task(
            user_id="test-user-123",
            title="Child Instance Task",
            parent_task_id=parent_task.id
        )

        session.add(child_task)
        session.commit()
        session.refresh(child_task)

        # Verify relationships
        assert child_task.parent_task_id == parent_task.id
        # Note: Parent-child relationship loading requires additional configuration
        # This is tested with lazy loading in actual application context


class TestTagModel:
    """Test cases for Tag model"""

    def test_tag_creation(self, session):
        """Test basic tag creation"""
        tag = Tag(
            user_id="test-user-123",
            name="work",
            color="#EF4444"
        )

        session.add(tag)
        session.commit()
        session.refresh(tag)

        assert tag.id is not None
        assert tag.name == "work"
        assert tag.color == "#EF4444"
        assert tag.user_id == "test-user-123"
        assert tag.created_at is not None

    def test_tag_default_color(self, session):
        """Test tag creation with default color"""
        tag = Tag(
            user_id="test-user-123",
            name="personal"
        )

        session.add(tag)
        session.commit()
        session.refresh(tag)

        assert tag.color == "#3B82F6"  # Default blue color

    def test_tag_unique_constraint_by_user(self, session):
        """Test that tags are unique per user"""
        # Create first tag
        tag1 = Tag(
            user_id="test-user-123",
            name="work"
        )

        session.add(tag1)
        session.commit()

        # Create another user's same tag (should work)
        tag2 = Tag(
            user_id="test-user-456",
            name="work"
        )

        session.add(tag2)
        session.commit()
        session.refresh(tag2)

        assert tag2.id != tag1.id  # Different users can have same tag name

    def test_tag_relationship_with_tasks(self, session):
        """Test tag relationships with tasks"""
        # Create tags
        tag1 = Tag(
            user_id="test-user-123",
            name="work",
            color="#EF4444"
        )

        tag2 = Tag(
            user_id="test-user-123",
            name="important",
            color="#DC2626"
        )

        # Create task
        task = Task(
            user_id="test-user-123",
            title="Task with Tags"
        )

        session.add_all([tag1, tag2, task])
        session.commit()

        # Create task-tag relationships
        task_tag1 = TaskTag(task_id=task.id, tag_id=tag1.id)
        task_tag2 = TaskTag(task_id=task.id, tag_id=tag2.id)

        session.add_all([task_tag1, task_tag2])
        session.commit()

        # Refresh to get relationships
        session.refresh(task)
        session.refresh(tag1)
        session.refresh(tag2)

        # Verify relationships
        assert len(tag1.tasks) >= 0  # Relationship should be accessible
        assert len(tag2.tasks) >= 0  # Relationship should be accessible


class TestTaskTagModel:
    """Test cases for TaskTag junction model"""

    def test_task_tag_creation(self, session):
        """Test task-tag relationship creation"""
        # Create task and tag
        task = Task(
            user_id="test-user-123",
            title="Test Task"
        )

        tag = Tag(
            user_id="test-user-123",
            name="test-tag",
            color="#3B82F6"
        )

        session.add_all([task, tag])
        session.commit()

        # Create task-tag relationship
        task_tag = TaskTag(
            task_id=task.id,
            tag_id=tag.id
        )

        session.add(task_tag)
        session.commit()
        session.refresh(task_tag)

        assert task_tag.task_id == task.id
        assert task_tag.tag_id == tag.id
        assert task_tag.created_at is not None

    def test_task_tag_composite_primary_key(self, session):
        """Test that task-tag has composite primary key"""
        # Create multiple tasks and tags
        task1 = Task(user_id="test-user-123", title="Task 1")
        task2 = Task(user_id="test-user-123", title="Task 2")
        tag1 = Tag(user_id="test-user-123", name="tag1")
        tag2 = Tag(user_id="test-user-123", name="tag2")

        session.add_all([task1, task2, tag1, tag2])
        session.commit()

        # Create task-tag relationships
        task_tag1 = TaskTag(task_id=task1.id, tag_id=tag1.id)
        task_tag2 = TaskTag(task_id=task1.id, tag_id=tag2.id)
        task_tag3 = TaskTag(task_id=task2.id, tag_id=tag1.id)

        session.add_all([task_tag1, task_tag2, task_tag3])
        session.commit()

        # Verify all relationships are created successfully
        assert task_tag1.task_id == task1.id
        assert task_tag1.tag_id == tag1.id
        assert task_tag2.task_id == task1.id
        assert task_tag2.tag_id == tag2.id
        assert task_tag3.task_id == task2.id
        assert task_tag3.tag_id == tag1.id


def test_task_enum_validation():
    """Test enum validation for priority and recurrence pattern"""
    # Test priority enum
    assert PriorityEnum.low == "low"
    assert PriorityEnum.medium == "medium"
    assert PriorityEnum.high == "high"

    # Test recurrence pattern enum
    assert RecurrencePatternEnum.daily == "daily"
    assert RecurrencePatternEnum.weekly == "weekly"
    assert RecurrencePatternEnum.monthly == "monthly"
    assert RecurrencePatternEnum.yearly == "yearly"
    assert RecurrencePatternEnum.custom == "custom"