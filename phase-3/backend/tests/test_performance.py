import pytest
import time
import statistics
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.config.database import get_db, Base
from backend.models.user import User
from backend.models.task import Task
import threading
import concurrent.futures
from typing import List, Tuple

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_performance.db"
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

def create_test_user(email: str = "performance_test@example.com"):
    """Helper function to create a test user and return their token."""
    # Register a test user
    registration_response = client.post("/api/auth/register", json={
        "email": email,
        "password": "SecurePassword123!"
    })

    # Get token from registration or login
    login_response = client.post("/api/auth/login", json={
        "email": email,
        "password": "SecurePassword123!"
    })

    return login_response.json()["access_token"]


def measure_response_time(url: str, headers: dict = None, method: str = "GET", json_data: dict = None) -> Tuple[float, int]:
    """
    Measure the response time for a single API call.

    Args:
        url: The API endpoint URL
        headers: Request headers
        method: HTTP method (GET, POST, PUT, DELETE, PATCH)
        json_data: JSON payload for POST/PUT requests

    Returns:
        Tuple of (response_time_in_seconds, status_code)
    """
    start_time = time.time()

    if method.upper() == "GET":
        response = client.get(url, headers=headers)
    elif method.upper() == "POST":
        response = client.post(url, headers=headers, json=json_data)
    elif method.upper() == "PUT":
        response = client.put(url, headers=headers, json=json_data)
    elif method.upper() == "DELETE":
        response = client.delete(url, headers=headers)
    elif method.upper() == "PATCH":
        response = client.patch(url, headers=headers)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")

    end_time = time.time()
    response_time = end_time - start_time

    return response_time, response.status_code


def test_basic_response_times():
    """
    Test basic response times for API endpoints.
    """
    user_token = create_test_user("basic_perf_test@example.com")
    headers = {"Authorization": f"Bearer {user_token}"}

    # Test various endpoints
    endpoints = [
        ("/api/tasks", "GET"),
        ("/api/auth/profile", "GET"),  # Assuming this endpoint exists
    ]

    for url, method in endpoints:
        response_time, status_code = measure_response_time(url, headers, method)

        # Basic performance requirement: responses should be under 1 second
        assert response_time < 1.0, f"{method} {url} took {response_time:.3f}s, exceeding 1s threshold"

        # Ensure request was successful
        assert status_code in [200, 201, 204, 404], f"{method} {url} returned unexpected status {status_code}"


def test_task_creation_performance():
    """
    Test performance of task creation endpoint.
    """
    user_token = create_test_user("task_creation_perf_test@example.com")
    headers = {"Authorization": f"Bearer {user_token}"}

    # Measure task creation time
    start_time = time.time()

    task_data = {
        "title": "Performance Test Task",
        "description": "Task created for performance testing"
    }

    response = client.post("/api/tasks", json=task_data, headers=headers)

    end_time = time.time()
    creation_time = end_time - start_time

    assert response.status_code in [200, 201], f"Task creation failed with status {response.status_code}"
    assert creation_time < 0.5, f"Task creation took {creation_time:.3f}s, exceeding 0.5s threshold"

    # Extract task ID for further testing
    task_response = response.json()
    task_id = task_response.get("id") or task_response.get("data", {}).get("id")
    assert task_id is not None, "Task creation did not return a valid task ID"


def test_concurrent_user_requests():
    """
    Test performance under concurrent requests from a single user.
    """
    user_token = create_test_user("concurrent_perf_test@example.com")
    headers = {"Authorization": f"Bearer {user_token}"}

    # Prepare multiple tasks to create
    num_requests = 10
    response_times = []

    for i in range(num_requests):
        start_time = time.time()

        task_data = {
            "title": f"Concurrent Test Task {i}",
            "description": f"Task {i} for concurrent performance testing"
        }

        response = client.post("/api/tasks", json=task_data, headers=headers)
        end_time = time.time()

        response_times.append(end_time - start_time)

        assert response.status_code in [200, 201], f"Request {i} failed with status {response.status_code}"

    # Calculate performance metrics
    avg_response_time = statistics.mean(response_times)
    median_response_time = statistics.median(response_times)
    max_response_time = max(response_times)

    print(f"Concurrent requests - Avg: {avg_response_time:.3f}s, Median: {median_response_time:.3f}s, Max: {max_response_time:.3f}s")

    # Performance requirements
    assert avg_response_time < 0.5, f"Average response time {avg_response_time:.3f}s exceeds 0.5s threshold"
    assert max_response_time < 1.0, f"Max response time {max_response_time:.3f}s exceeds 1.0s threshold"


def test_multiple_users_concurrent():
    """
    Test performance with multiple users making concurrent requests.
    """
    # Create multiple test users
    user_tokens = []
    for i in range(5):  # 5 concurrent users
        email = f"multi_user_perf_test_{i}@example.com"
        token = create_test_user(email)
        user_tokens.append(token)

    def make_requests_for_user(user_idx: int):
        """Function to run requests for a specific user."""
        headers = {"Authorization": f"Bearer {user_tokens[user_idx]}"}
        response_times = []

        for j in range(5):  # Each user makes 5 requests
            start_time = time.time()

            task_data = {
                "title": f"Multi-user Test Task {user_idx}-{j}",
                "description": f"Task for user {user_idx}, request {j}"
            }

            response = client.post("/api/tasks", json=task_data, headers=headers)
            end_time = time.time()

            response_times.append(end_time - start_time)

            if response.status_code not in [200, 201]:
                print(f"User {user_idx}, request {j} failed with status {response.status_code}")

        return response_times

    # Execute requests concurrently
    all_response_times = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_requests_for_user, i) for i in range(5)]

        for future in concurrent.futures.as_completed(futures):
            user_response_times = future.result()
            all_response_times.extend(user_response_times)

    # Calculate overall performance metrics
    if all_response_times:  # Check if we have any results
        avg_response_time = statistics.mean(all_response_times)
        median_response_time = statistics.median(all_response_times)
        max_response_time = max(all_response_times)

        print(f"Multi-user concurrent - Avg: {avg_response_time:.3f}s, Median: {median_response_time:.3f}s, Max: {max_response_time:.3f}s")

        # Performance requirements
        assert avg_response_time < 1.0, f"Average response time {avg_response_time:.3f}s exceeds 1.0s threshold"
        assert max_response_time < 2.0, f"Max response time {max_response_time:.3f}s exceeds 2.0s threshold"


def test_large_dataset_performance():
    """
    Test performance with a larger dataset.
    """
    user_token = create_test_user("large_dataset_perf_test@example.com")
    headers = {"Authorization": f"Bearer {user_token}"}

    # Create a larger number of tasks
    num_tasks = 50

    print(f"Creating {num_tasks} tasks for large dataset performance test...")

    # Create tasks
    created_task_ids = []
    for i in range(num_tasks):
        task_data = {
            "title": f"Large Dataset Test Task {i}",
            "description": f"This is task number {i} in the large dataset performance test"
        }

        response = client.post("/api/tasks", json=task_data, headers=headers)
        assert response.status_code in [200, 201], f"Task {i} creation failed with status {response.status_code}"

        task_response = response.json()
        task_id = task_response.get("id") or task_response.get("data", {}).get("id")
        assert task_id is not None, f"Task {i} creation did not return a valid task ID"
        created_task_ids.append(task_id)

    # Now test retrieving all tasks
    start_time = time.time()
    response = client.get("/api/tasks", headers=headers)
    end_time = time.time()

    retrieval_time = end_time - start_time
    assert response.status_code == 200, f"Task retrieval failed with status {response.status_code}"
    assert len(response.json()) >= num_tasks, f"Expected at least {num_tasks} tasks, got {len(response.json())}"

    print(f"Retrieved {len(response.json())} tasks in {retrieval_time:.3f}s")

    # Performance requirement for large dataset
    assert retrieval_time < 2.0, f"Retrieving {num_tasks} tasks took {retrieval_time:.3f}s, exceeding 2.0s threshold"


def test_task_update_performance():
    """
    Test performance of task update operations.
    """
    user_token = create_test_user("update_perf_test@example.com")
    headers = {"Authorization": f"Bearer {user_token}"}

    # Create a task to update
    task_data = {
        "title": "Update Performance Test Task",
        "description": "Original description"
    }

    create_response = client.post("/api/tasks", json=task_data, headers=headers)
    assert create_response.status_code in [200, 201], f"Task creation failed with status {create_response.status_code}"

    task_response = create_response.json()
    task_id = task_response.get("id") or task_response.get("data", {}).get("id")
    assert task_id is not None, "Task creation did not return a valid task ID"

    # Measure update performance
    update_times = []
    for i in range(10):
        start_time = time.time()

        update_data = {
            "title": f"Updated Title {i}",
            "description": f"Updated description {i}",
            "completed": i % 2 == 0  # Alternate completion status
        }

        response = client.put(f"/api/tasks/{task_id}", json=update_data, headers=headers)
        end_time = time.time()

        update_time = end_time - start_time
        update_times.append(update_time)

        assert response.status_code == 200, f"Task update {i} failed with status {response.status_code}"

    avg_update_time = statistics.mean(update_times)
    max_update_time = max(update_times)

    print(f"Task updates - Avg: {avg_update_time:.3f}s, Max: {max_update_time:.3f}s")

    assert avg_update_time < 0.5, f"Average update time {avg_update_time:.3f}s exceeds 0.5s threshold"
    assert max_update_time < 1.0, f"Max update time {max_update_time:.3f}s exceeds 1.0s threshold"


def test_task_completion_toggle_performance():
    """
    Test performance of task completion toggle operations.
    """
    user_token = create_test_user("completion_perf_test@example.com")
    headers = {"Authorization": f"Bearer {user_token}"}

    # Create a task to toggle
    task_data = {
        "title": "Completion Toggle Test Task",
        "description": "Task for completion toggle performance testing"
    }

    create_response = client.post("/api/tasks", json=task_data, headers=headers)
    assert create_response.status_code in [200, 201], f"Task creation failed with status {create_response.status_code}"

    task_response = create_response.json()
    task_id = task_response.get("id") or task_response.get("data", {}).get("id")
    assert task_id is not None, "Task creation did not return a valid task ID"

    # Measure completion toggle performance
    toggle_times = []
    for i in range(20):  # Toggle 20 times
        start_time = time.time()

        response = client.patch(f"/api/tasks/{task_id}/complete", headers=headers)
        end_time = time.time()

        toggle_time = end_time - start_time
        toggle_times.append(toggle_time)

        assert response.status_code == 200, f"Task toggle {i} failed with status {response.status_code}"

    avg_toggle_time = statistics.mean(toggle_times)
    max_toggle_time = max(toggle_times)

    print(f"Task toggles - Avg: {avg_toggle_time:.3f}s, Max: {max_toggle_time:.3f}s")

    assert avg_toggle_time < 0.3, f"Average toggle time {avg_toggle_time:.3f}s exceeds 0.3s threshold"
    assert max_toggle_time < 0.5, f"Max toggle time {max_toggle_time:.3f}s exceeds 0.5s threshold"


def test_api_throughput():
    """
    Test the API's ability to handle multiple requests per second.
    """
    user_token = create_test_user("throughput_test@example.com")
    headers = {"Authorization": f"Bearer {user_token}"}

    # Measure how many requests we can handle in 10 seconds
    start_time = time.time()
    request_count = 0
    successful_requests = 0

    # Make requests for 5 seconds
    while time.time() - start_time < 5:
        task_data = {
            "title": f"Throughput Test Task {request_count}",
            "description": "Task for throughput testing"
        }

        response = client.post("/api/tasks", json=task_data, headers=headers)
        request_count += 1

        if response.status_code in [200, 201]:
            successful_requests += 1

        # Brief pause to avoid overwhelming the system during testing
        time.sleep(0.01)

    total_time = time.time() - start_time
    requests_per_second = successful_requests / total_time

    print(f"Throughput test: {successful_requests} successful requests in {total_time:.2f}s ({requests_per_second:.2f} req/s)")

    # Basic throughput requirement
    assert requests_per_second > 5, f"Throughput {requests_per_second:.2f} req/s is too low (expected >5 req/s)"


if __name__ == "__main__":
    pytest.main([__file__])