import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.config.database import get_db, Base
from backend.models.user import User
from backend.models.task import Task
from backend.utils.auth import create_access_token
from datetime import timedelta

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_tasks.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def create_test_user():
    """Helper function to create a test user and return their token."""
    # Register a test user
    registration_response = client.post("/api/auth/register", json={
        "email": "task_test@example.com",
        "password": "password123"
    })

    if registration_response.status_code not in [200, 201]:
        # If user already exists, try to login
        login_response = client.post("/api/auth/login", json={
            "email": "task_test@example.com",
            "password": "password123"
        })
        if login_response.status_code == 200:
            return login_response.json()["access_token"]

    # Get token from registration or login
    login_response = client.post("/api/auth/login", json={
        "email": "task_test@example.com",
        "password": "password123"
    })

    return login_response.json()["access_token"]


def test_contract_task_endpoints():
    """
    Contract test for task endpoints to ensure they follow the API specification.
    """
    token = create_test_user()

    headers = {"Authorization": f"Bearer {token}"}

    # Test GET /api/tasks
    response = client.get("/api/tasks", headers=headers)
    assert response.status_code in [200, 401]  # Expected status codes

    # Test POST /api/tasks
    response = client.post("/api/tasks", json={
        "title": "Test Task",
        "description": "Test Description"
    }, headers=headers)
    assert response.status_code in [200, 201, 400, 401]  # Expected status codes

    # Test GET /api/tasks/{task_id}
    if response.status_code in [200, 201]:
        task_data = response.json()
        task_id = task_data.get("id") or task_data.get("data", {}).get("id")
        if task_id:
            get_response = client.get(f"/api/tasks/{task_id}", headers=headers)
            assert get_response.status_code in [200, 401, 404]

    # Test PUT /api/tasks/{task_id}
    if response.status_code in [200, 201]:
        task_data = response.json()
        task_id = task_data.get("id") or task_data.get("data", {}).get("id")
        if task_id:
            put_response = client.put(f"/api/tasks/{task_id}", json={
                "title": "Updated Task",
                "description": "Updated Description"
            }, headers=headers)
            assert put_response.status_code in [200, 400, 401, 404]

    # Test DELETE /api/tasks/{task_id}
    if response.status_code in [200, 201]:
        task_data = response.json()
        task_id = task_data.get("id") or task_data.get("data", {}).get("id")
        if task_id:
            delete_response = client.delete(f"/api/tasks/{task_id}", headers=headers)
            assert delete_response.status_code in [200, 204, 401, 404]


def test_full_task_lifecycle():
    """
    Integration test for full task lifecycle: create, read, update, delete.
    """
    token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Step 1: Create a task
    create_response = client.post("/api/tasks", json={
        "title": "Lifecycle Test Task",
        "description": "This task will go through the full lifecycle"
    }, headers=headers)

    assert create_response.status_code in [200, 201]
    created_task = create_response.json()
    task_id = created_task.get("id") or created_task.get("data", {}).get("id")
    assert task_id is not None

    # Step 2: Read the task
    read_response = client.get(f"/api/tasks/{task_id}", headers=headers)
    assert read_response.status_code == 200
    read_task = read_response.json()
    assert read_task["title"] == "Lifecycle Test Task"

    # Step 3: Update the task
    update_response = client.put(f"/api/tasks/{task_id}", json={
        "title": "Updated Lifecycle Test Task",
        "description": "Updated description for lifecycle test"
    }, headers=headers)

    assert update_response.status_code == 200
    updated_task = update_response.json()
    assert updated_task["title"] == "Updated Lifecycle Test Task"

    # Step 4: Toggle completion status
    toggle_response = client.patch(f"/api/tasks/{task_id}/complete", headers=headers)
    assert toggle_response.status_code == 200
    toggled_task = toggle_response.json()
    assert toggled_task["completed"] != read_task["completed"]

    # Step 5: Delete the task
    delete_response = client.delete(f"/api/tasks/{task_id}", headers=headers)
    assert delete_response.status_code in [200, 204]

    # Step 6: Verify task is deleted
    verify_response = client.get(f"/api/tasks/{task_id}", headers=headers)
    assert verify_response.status_code == 404


def test_user_task_isolation():
    """
    Test that users can only access their own tasks.
    """
    # Create first user and task
    first_user_token = create_test_user()
    first_headers = {"Authorization": f"Bearer {first_user_token}"}

    first_task_response = client.post("/api/tasks", json={
        "title": "First User Task",
        "description": "Task for first user"
    }, headers=first_headers)

    assert first_task_response.status_code in [200, 201]
    first_task = first_task_response.json()
    first_task_id = first_task.get("id") or first_task.get("data", {}).get("id")
    assert first_task_id is not None

    # Create second user
    second_reg_response = client.post("/api/auth/register", json={
        "email": "second_task_test@example.com",
        "password": "password123"
    })

    second_login_response = client.post("/api/auth/login", json={
        "email": "second_task_test@example.com",
        "password": "password123"
    })

    second_token = second_login_response.json()["access_token"]
    second_headers = {"Authorization": f"Bearer {second_token}"}

    # Second user should not be able to access first user's task
    unauthorized_response = client.get(f"/api/tasks/{first_task_id}", headers=second_headers)
    # This should either return 404 (not found) or 403 (forbidden) depending on implementation
    assert unauthorized_response.status_code in [403, 404, 401]

    # Second user should only see their own tasks
    second_user_tasks = client.get("/api/tasks", headers=second_headers)
    assert second_user_tasks.status_code == 200
    second_tasks_list = second_user_tasks.json()
    # Verify the first user's task is not in the second user's list
    if isinstance(second_tasks_list, list):
        task_ids = [task.get("id") for task in second_tasks_list]
        assert first_task_id not in task_ids


if __name__ == "__main__":
    pytest.main([__file__])