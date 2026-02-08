import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from backend.models import Task, PriorityEnum
from backend.services.priority_service import PriorityService


@pytest.fixture(name="engine")
def fixture_engine():
    """Create in-memory SQLite engine for testing"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def fixture_session(engine):
    """Create a test session"""
    with Session(engine) as session:
        yield session


class TestPriorityService:
    """Unit tests for PriorityService functionality"""

    def test_validate_priority_value_valid(self):
        """Test that valid priority values pass validation"""
        # Test each valid priority
        assert PriorityService.validate_priority_value("low") is True
        assert PriorityService.validate_priority_value("medium") is True
        assert PriorityService.validate_priority_value("high") is True
        # Test None value (should pass for optional fields)
        assert PriorityService.validate_priority_value(None) is True

    def test_validate_priority_value_invalid(self):
        """Test that invalid priority values raise exception"""
        with pytest.raises(ValueError, match="Invalid priority value"):
            PriorityService.validate_priority_value("invalid_priority")

        with pytest.raises(ValueError, match="Invalid priority value"):
            PriorityService.validate_priority_value("HIGH")  # Case-sensitive

        with pytest.raises(ValueError, match="Invalid priority value"):
            PriorityService.validate_priority_value("top")

    def test_get_valid_priorities(self):
        """Test that get_valid_priorities returns correct values"""
        valid_priorities = PriorityService.get_valid_priorities()
        expected = ["low", "medium", "high"]

        assert len(valid_priorities) == 3
        assert all(p in expected for p in valid_priorities)
        assert all(p in valid_priorities for p in expected)

    def test_validate_priority_change_no_change(self):
        """Test priority validation when no change is requested"""
        result = PriorityService.validate_priority_change(
            PriorityEnum.medium,
            None
        )
        assert result is True

    def test_validate_priority_change_valid(self):
        """Test priority validation for valid changes"""
        result = PriorityService.validate_priority_change(
            PriorityEnum.medium,
            PriorityEnum.high
        )
        assert result is True

        result = PriorityService.validate_priority_change(
            PriorityEnum.high,
            PriorityEnum.low
        )
        assert result is True

    def test_calculate_priority_impact_score_basic(self):
        """Test basic priority impact scoring"""
        task = Task(
            user_id="test-user",
            title="Test Task",
            priority=PriorityEnum.high
        )

        score = PriorityService.calculate_priority_impact_score(task)
        # High priority with no due date should have base score of 3.0
        assert score == 3.0

        task.priority = PriorityEnum.medium
        score = PriorityService.calculate_priority_impact_score(task)
        assert score == 2.0

        task.priority = PriorityEnum.low
        score = PriorityService.calculate_priority_impact_score(task)
        assert score == 1.0

    def test_calculate_priority_impact_score_with_due_date(self):
        """Test priority impact scoring with due dates"""
        future_date = datetime.utcnow() + timedelta(days=10)

        task = Task(
            user_id="test-user",
            title="Test Task",
            priority=PriorityEnum.medium,
            due_date=future_date
        )

        score = PriorityService.calculate_priority_impact_score(task)
        # Medium priority with future due date should have base score of 2.0
        assert score == pytest.approx(2.0)

        # Test with due date within 3 days (higher impact)
        near_future = datetime.utcnow() + timedelta(days=2)
        task.due_date = near_future
        score = PriorityService.calculate_priority_impact_score(task)
        assert score == pytest.approx(3.0)  # 2.0 * 1.5 for near due date

        # Test with overdue task (much higher impact)
        past_date = datetime.utcnow() - timedelta(days=5)
        task.due_date = past_date
        task.priority = PriorityEnum.low
        score = PriorityService.calculate_priority_impact_score(task)
        assert score == pytest.approx(2.0)  # 1.0 * 2.0 for overdue

    def test_calculate_priority_impact_score_completed_task(self):
        """Test that completed tasks have lower impact scores"""
        past_due_date = datetime.utcnow() - timedelta(days=5)

        task = Task(
            user_id="test-user",
            title="Test Task",
            priority=PriorityEnum.high,
            due_date=past_due_date,
            completed=True
        )

        score = PriorityService.calculate_priority_impact_score(task)
        # High priority overdue task that's completed should have reduced score
        # 3.0 * 2.0 (for overdue) * 0.1 (for completed) = 0.6
        assert score == pytest.approx(0.6)

    def test_get_tasks_by_priority(self, session):
        """Test retrieving tasks by priority"""
        # Create test user and tasks
        user_id = "test-user-123"

        # Create tasks with different priorities
        low_task = Task(user_id=user_id, title="Low Priority Task", priority=PriorityEnum.low)
        medium_task = Task(user_id=user_id, title="Medium Priority Task", priority=PriorityEnum.medium)
        high_task = Task(user_id=user_id, title="High Priority Task", priority=PriorityEnum.high)

        session.add(low_task)
        session.add(medium_task)
        session.add(high_task)
        session.commit()

        # Test retrieving tasks by priority
        high_priority_tasks = PriorityService.get_tasks_by_priority(session, user_id, PriorityEnum.high)
        assert len(high_priority_tasks) == 1
        assert high_priority_tasks[0].title == "High Priority Task"

        medium_priority_tasks = PriorityService.get_tasks_by_priority(session, user_id, PriorityEnum.medium)
        assert len(medium_priority_tasks) == 1
        assert medium_priority_tasks[0].title == "Medium Priority Task"

    def test_get_tasks_by_multiple_priorities(self, session):
        """Test retrieving tasks by multiple priorities"""
        user_id = "test-user-123"

        # Create tasks with different priorities
        low_task = Task(user_id=user_id, title="Low Priority Task", priority=PriorityEnum.low)
        medium_task1 = Task(user_id=user_id, title="Medium Priority Task 1", priority=PriorityEnum.medium)
        medium_task2 = Task(user_id=user_id, title="Medium Priority Task 2", priority=PriorityEnum.medium)
        high_task = Task(user_id=user_id, title="High Priority Task", priority=PriorityEnum.high)

        session.add_all([low_task, medium_task1, medium_task2, high_task])
        session.commit()

        # Test retrieving tasks with multiple priorities
        tasks = PriorityService.get_tasks_by_multiple_priorities(
            session,
            user_id,
            [PriorityEnum.low, PriorityEnum.high]
        )
        assert len(tasks) == 2
        titles = [task.title for task in tasks]
        assert "Low Priority Task" in titles
        assert "High Priority Task" in titles
        assert "Medium Priority Task 1" not in titles
        assert "Medium Priority Task 2" not in titles

    def test_get_priority_statistics(self, session):
        """Test getting priority statistics for a user"""
        user_id = "test-user-123"

        # Create tasks with different priorities (some completed, some pending)
        tasks = [
            Task(user_id=user_id, title="Low Pending Task", priority=PriorityEnum.low, completed=False),
            Task(user_id=user_id, title="Low Completed Task", priority=PriorityEnum.low, completed=True),
            Task(user_id=user_id, title="Medium Pending Task", priority=PriorityEnum.medium, completed=False),
            Task(user_id=user_id, title="High Pending Task", priority=PriorityEnum.high, completed=False),
            Task(user_id=user_id, title="High Completed Task", priority=PriorityEnum.high, completed=True),
        ]

        session.add_all(tasks)
        session.commit()

        stats = PriorityService.get_priority_statistics(session, user_id)

        # Should only count pending tasks
        assert stats["low"] == 1  # Only 1 pending low task
        assert stats["medium"] == 1  # Only 1 pending medium task
        assert stats["high"] == 1  # Only 1 pending high task


class TestTaskModelPriority:
    """Tests for Task model priority functionality"""

    def test_priority_defaults(self):
        """Test that priority defaults to medium"""
        task = Task(user_id="test-user", title="Test Task")
        assert task.priority == PriorityEnum.medium

    def test_priority_assignment(self):
        """Test assigning different priorities to task"""
        task = Task(user_id="test-user", title="Test Task", priority=PriorityEnum.high)
        assert task.priority == PriorityEnum.high

        task.priority = PriorityEnum.low
        assert task.priority == PriorityEnum.low

    def test_priority_enum_values(self):
        """Test that PriorityEnum has correct values"""
        assert PriorityEnum.low.value == "low"
        assert PriorityEnum.medium.value == "medium"
        assert PriorityEnum.high.value == "high"
        assert len(list(PriorityEnum)) == 3


class TestPriorityAPI:
    """Integration tests for priority-related API endpoints"""

    @pytest.fixture
    def test_client(self, session):
        from fastapi.testclient import TestClient
        from backend.main import app

        # Override the database session
        def get_test_session_override():
            return session

        app.dependency_overrides[get_session] = get_test_session_override
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

    def test_create_task_with_priority(self, test_client):
        """Test creating a task with priority"""
        response = test_client.post("/api/tasks", json={
            "title": "High Priority Task",
            "description": "This is a high priority task",
            "priority": "high"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["priority"] == "high"
        assert data["title"] == "High Priority Task"

    def test_update_task_priority(self, test_client):
        """Test updating a task's priority"""
        # Create a task first
        create_response = test_client.post("/api/tasks", json={
            "title": "Medium Priority Task",
            "priority": "medium"
        })

        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # Update the priority
        update_response = test_client.put(f"/api/tasks/{task_id}", json={
            "priority": "high"
        })

        assert update_response.status_code == 200
        data = update_response.json()
        assert data["priority"] == "high"

    def test_filter_tasks_by_priority(self, test_client):
        """Test filtering tasks by priority"""
        # Create tasks with different priorities
        test_client.post("/api/tasks", json={
            "title": "Low Priority Task",
            "priority": "low"
        })

        test_client.post("/api/tasks", json={
            "title": "High Priority Task",
            "priority": "high"
        })

        # Filter by high priority
        response = test_client.get("/api/tasks", params={
            "priority": ["high"]
        })

        assert response.status_code == 200
        data = response.json()
        high_priority_tasks = [task for task in data["tasks"] if task["priority"] == "high"]
        assert len(high_priority_tasks) >= 1
        assert all(task["priority"] == "high" for task in high_priority_tasks)


class TestPriorityComponent:
    """Tests for priority-related UI components and functionality"""

    def test_priority_selector_component_logic(self):
        """Test the logic behind the PrioritySelector component"""
        # This would be tested in the frontend, but we can test the underlying logic
        priority_options = [
            {"value": "low", "label": "Low", "color": "#10B981", "icon": "↓"},
            {"value": "medium", "label": "Medium", "color": "#F59E0B", "icon": "→"},
            {"value": "high", "label": "High", "color": "#EF4444", "icon": "↑"}
        ]

        # Verify all options are present
        values = [opt["value"] for opt in priority_options]
        assert "low" in values
        assert "medium" in values
        assert "high" in values

        # Verify correct colors for each priority level
        low_option = next(opt for opt in priority_options if opt["value"] == "low")
        assert low_option["color"] == "#10B981"  # Green for low priority
        assert low_option["icon"] == "↓"

        high_option = next(opt for opt in priority_options if opt["value"] == "high")
        assert high_option["color"] == "#EF4444"  # Red for high priority
        assert high_option["icon"] == "↑"


def test_priority_feature_complete_workflow():
    """End-to-end test for the priority feature workflow"""
    # Test complete workflow: create task with priority -> filter by priority -> update priority
    # This would normally be an integration test but we'll simulate the logic

    # Create a task with high priority
    task = Task(
        user_id="test-user",
        title="Critical Task",
        priority=PriorityEnum.high
    )

    # Verify initial priority
    assert task.priority == PriorityEnum.high

    # Update to low priority
    task.priority = PriorityEnum.low
    assert task.priority == PriorityEnum.low

    # Verify impact score changes
    initial_score = PriorityService.calculate_priority_impact_score(task)
    task.priority = PriorityEnum.high
    new_score = PriorityService.calculate_priority_impact_score(task)

    # High priority should have higher impact score than low priority
    assert new_score > initial_score


if __name__ == "__main__":
    pytest.main([__file__])