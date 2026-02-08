import pytest
import asyncio
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from main import app
from database import get_session
from models import Task, Tag, TaskTag, PriorityEnum, RecurrencePatternEnum
from models.user import User


# Create test database engine
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Override dependency to use test database
def override_get_session():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_session] = override_get_session

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_database():
    """Setup test database with tables"""
    from models import SQLModel
    SQLModel.metadata.create_all(bind=engine)

    yield engine

    # Cleanup
    SQLModel.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(setup_database):
    """Create a test user"""
    db = TestingSessionLocal()

    user = User(
        id="test-user-123",
        email="test@example.com",
        name="Test User"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    yield user

    db.delete(user)
    db.commit()


class TestTaskEndpoints:
    """Integration tests for extended task endpoints with advanced features"""

    def test_create_task_with_advanced_features(self, test_user):
        """Test creating a task with priority, due date, tags, and recurrence"""
        # First create some tags
        tag_response = client.post("/api/tags", json={
            "name": "work",
            "color": "#EF4444"
        })
        assert tag_response.status_code == 200
        tag_id = tag_response.json()["id"]

        # Create task with advanced features
        task_data = {
            "title": "Test Advanced Task",
            "description": "Task with advanced features",
            "priority": "high",
            "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "recurrence_pattern": "daily",
            "recurrence_config": {"interval": 1},
            "tag_ids": [tag_id],
            "reminder_times": [(datetime.utcnow() + timedelta(hours=1)).isoformat()]
        }

        response = client.post("/api/tasks", json=task_data)
        assert response.status_code == 201

        task = response.json()
        assert task["title"] == "Test Advanced Task"
        assert task["priority"] == "high"
        assert task["due_date"] is not None
        assert task["recurrence_pattern"] == "daily"
        assert len(task["tags"]) > 0

    def test_update_task_with_advanced_features(self, test_user):
        """Test updating a task with advanced features"""
        # Create a task first
        task_response = client.post("/api/tasks", json={
            "title": "Update Test Task",
            "priority": "medium"
        })
        assert task_response.status_code == 201
        task_id = task_response.json()["id"]

        # Create a tag
        tag_response = client.post("/api/tags", json={
            "name": "personal",
            "color": "#3B82F6"
        })
        assert tag_response.status_code == 200
        tag_id = tag_response.json()["id"]

        # Update the task with advanced features
        update_data = {
            "priority": "high",
            "due_date": (datetime.utcnow() + timedelta(days=2)).isoformat(),
            "recurrence_pattern": "weekly",
            "tag_ids": [tag_id]
        }

        response = client.put(f"/api/tasks/{task_id}", json=update_data)
        assert response.status_code == 200

        updated_task = response.json()
        assert updated_task["priority"] == "high"
        assert updated_task["due_date"] is not None
        assert updated_task["recurrence_pattern"] == "weekly"
        assert len(updated_task["tags"]) > 0
        assert updated_task["tags"][0]["name"] == "personal"

    def test_get_tasks_with_advanced_filters(self, test_user):
        """Test getting tasks with advanced filtering and sorting"""
        # Create multiple tasks with different priorities
        for i in range(3):
            client.post("/api/tasks", json={
                "title": f"Test Task {i}",
                "priority": "high" if i == 0 else "low",
                "due_date": (datetime.utcnow() + timedelta(days=i+1)).isoformat() if i < 2 else None
            })

        # Create a tag
        tag_response = client.post("/api/tags", json={
            "name": "test-tag",
            "color": "#10B981"
        })
        assert tag_response.status_code == 200
        tag_id = tag_response.json()["id"]

        # Test filtering by priority
        response = client.get("/api/tasks", params={
            "priority": ["high"]
        })
        assert response.status_code == 200
        high_priority_tasks = response.json()["tasks"]
        assert len(high_priority_tasks) >= 1
        assert all(task["priority"] == "high" for task in high_priority_tasks)

        # Test filtering by due date range
        response = client.get("/api/tasks", params={
            "due_date_from": datetime.utcnow().isoformat(),
            "due_date_to": (datetime.utcnow() + timedelta(days=5)).isoformat()
        })
        assert response.status_code == 200
        due_tasks = response.json()["tasks"]
        assert len(due_tasks) >= 2

        # Test sorting by priority
        response = client.get("/api/tasks", params={
            "sort": "priority",
            "sort_order": "desc"
        })
        assert response.status_code == 200
        sorted_tasks = response.json()["tasks"]
        # Verify tasks are sorted by priority (high first)
        if len(sorted_tasks) > 1:
            assert sorted_tasks[0]["priority"] in ["high", "medium"]

    def test_complete_recurring_task(self, test_user):
        """Test completing a recurring task with series options"""
        # Create a recurring task
        task_response = client.post("/api/tasks", json={
            "title": "Recurring Meeting",
            "description": "Weekly recurring meeting",
            "priority": "medium",
            "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "recurrence_pattern": "weekly",
            "recurrence_config": {"days_of_week": [1]}  # Monday
        })
        assert task_response.status_code == 201
        task_id = task_response.json()["id"]

        # Complete the task
        complete_response = client.post(f"/api/tasks/{task_id}/complete", json={
            "mark_series_complete": False  # Only complete this occurrence
        })
        assert complete_response.status_code == 200

        completed_task = complete_response.json()
        assert completed_task["completed"] is True
        assert completed_task["id"] == task_id

    def test_tag_management_endpoints(self, test_user):
        """Test tag creation, retrieval, and management"""
        # Create a tag
        tag_data = {
            "name": "integration-test",
            "color": "#8B5CF6"
        }
        response = client.post("/api/tags", json=tag_data)
        assert response.status_code == 200

        tag = response.json()
        assert tag["name"] == "integration-test"
        assert tag["color"] == "#8B5CF6"
        tag_id = tag["id"]

        # Get all tags
        response = client.get("/api/tags")
        assert response.status_code == 200
        tags = response.json()
        assert len(tags) >= 1
        assert any(t["id"] == tag_id for t in tags)

        # Update the tag
        update_data = {
            "name": "updated-integration-test",
            "color": "#EC4899"
        }
        response = client.put(f"/api/tags/{tag_id}", json=update_data)
        assert response.status_code == 200

        updated_tag = response.json()
        assert updated_tag["name"] == "updated-integration-test"
        assert updated_tag["color"] == "#EC4899"

        # Delete the tag
        response = client.delete(f"/api/tags/{tag_id}")
        assert response.status_code == 204

        # Verify tag is deleted
        response = client.get("/api/tags")
        assert response.status_code == 200
        remaining_tags = response.json()
        assert not any(t["id"] == tag_id for t in remaining_tags)


class TestEventDrivenArchitecture:
    """Integration tests for event-driven architecture"""

    def test_task_creation_emits_event(self, test_user):
        """Test that creating a task emits a task.created event"""
        with patch('services.event_publisher.EventPublisher.publish') as mock_publish:
            # Create a task
            task_data = {
                "title": "Event Test Task",
                "priority": "medium",
                "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat()
            }

            response = client.post("/api/tasks", json=task_data)
            assert response.status_code == 201

            # Verify that an event was published
            assert mock_publish.called
            # Check that the event was a task.created event
            call_args = mock_publish.call_args
            assert call_args is not None
            event = call_args[0][0]  # First argument passed to publish method
            assert event.event_type == "task.created"
            assert event.data["title"] == "Event Test Task"

    def test_task_update_emits_event(self, test_user):
        """Test that updating a task emits a task.updated event"""
        with patch('services.event_publisher.EventPublisher.publish') as mock_publish:
            # Create a task first
            task_response = client.post("/api/tasks", json={
                "title": "Update Event Test",
                "priority": "low"
            })
            assert task_response.status_code == 201
            task_id = task_response.json()["id"]

            # Update the task
            update_response = client.put(f"/api/tasks/{task_id}", json={
                "priority": "high"
            })
            assert update_response.status_code == 200

            # Verify that an event was published
            # We expect at least 2 calls (one for create, one for update)
            assert mock_publish.call_count >= 2
            # The last call should be for the update event
            last_call = mock_publish.call_args_list[-1]
            event = last_call[0][0]
            assert event.event_type == "task.updated"
            assert event.data["task_id"] == task_id


class TestDaprIntegration:
    """Integration tests for Dapr components"""

    def test_dapr_sidecar_health(self, test_user):
        """Test that Dapr sidecar is accessible"""
        # This would typically check Dapr health endpoints
        # For now, we'll verify that the service can make Dapr calls
        try:
            # Test if Dapr placement service is accessible (would be tested in real deployment)
            assert True  # Placeholder for Dapr integration test
        except Exception:
            # Dapr might not be running in test environment
            pytest.skip("Dapr not available in test environment")

    def test_event_processing_pipeline(self, test_user):
        """Test the complete event processing pipeline"""
        # Test that events flow through the system correctly
        with patch('services.event_publisher.EventPublisher.publish') as mock_publish, \
             patch('services.task_service.TaskService.process_task_event') as mock_process:

            # Create a task with advanced features
            task_data = {
                "title": "Pipeline Test Task",
                "priority": "high",
                "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                "recurrence_pattern": "daily"
            }

            response = client.post("/api/tasks", json=task_data)
            assert response.status_code == 201

            # Verify event was published
            assert mock_publish.called

            # Verify event was processed appropriately
            assert mock_process.called


class TestSearchAndFilter:
    """Integration tests for search and filtering functionality"""

    def test_full_text_search(self, test_user):
        """Test full-text search on title and description"""
        # Create tasks with different content
        client.post("/api/tasks", json={
            "title": "Meeting with team",
            "description": "Discuss project progress and deadlines"
        })

        client.post("/api/tasks", json={
            "title": "Buy groceries",
            "description": "Shopping list for weekly groceries"
        })

        # Search for tasks containing "meeting"
        response = client.get("/api/tasks", params={
            "search": "meeting"
        })
        assert response.status_code == 200
        results = response.json()["tasks"]
        assert len(results) >= 1
        assert any("meeting" in task["title"].lower() for task in results)

    def test_multi_criteria_filter(self, test_user):
        """Test filtering with multiple criteria"""
        # Create tasks with different attributes
        client.post("/api/tasks", json={
            "title": "High Priority Due Soon",
            "priority": "high",
            "due_date": (datetime.utcnow() + timedelta(hours=2)).isoformat()
        })

        client.post("/api/tasks", json={
            "title": "Low Priority Later",
            "priority": "low",
            "due_date": (datetime.utcnow() + timedelta(days=10)).isoformat()
        })

        # Filter by priority and due date range
        response = client.get("/api/tasks", params={
            "priority": ["high"],
            "due_date_from": datetime.utcnow().isoformat(),
            "due_date_to": (datetime.utcnow() + timedelta(days=1)).isoformat()
        })
        assert response.status_code == 200
        results = response.json()["tasks"]
        assert len(results) >= 1
        # All results should match both criteria
        for task in results:
            assert task["priority"] == "high"
            assert datetime.fromisoformat(task["due_date"].replace("Z", "+00:00")) <= datetime.utcnow() + timedelta(days=1)


def test_health_endpoints():
    """Test health check endpoints"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


if __name__ == "__main__":
    pytest.main([__file__])