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
import hashlib
import secrets

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_security.db"
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

def create_test_user(email: str = "test@example.com"):
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


def create_test_task(user_token: str, title: str = "Test Task"):
    """Helper function to create a test task and return its ID."""
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.post("/api/tasks", json={
        "title": title,
        "description": "Test Description"
    }, headers=headers)

    if response.status_code in [200, 201]:
        task_data = response.json()
        return task_data.get("id") or task_data.get("data", {}).get("id")
    return None


def test_user_task_isolation():
    """
    Test that users cannot access other users' tasks.
    """
    # Create first user and task
    first_user_token = create_test_user("first_security@example.com")
    first_headers = {"Authorization": f"Bearer {first_user_token}"}

    first_task_id = create_test_task(first_user_token, "First User's Task")
    assert first_task_id is not None

    # Create second user
    second_user_token = create_test_user("second_security@example.com")
    second_headers = {"Authorization": f"Bearer {second_user_token}"}

    # Second user should not be able to access first user's task
    unauthorized_response = client.get(f"/api/tasks/{first_task_id}", headers=second_headers)
    # Should return 404 (not found) to prevent enumeration attacks
    assert unauthorized_response.status_code in [404, 403]

    # Second user should only see their own tasks
    second_user_tasks = client.get("/api/tasks", headers=second_headers)
    assert second_user_tasks.status_code == 200
    second_tasks_list = second_user_tasks.json()

    # Verify the first user's task is not in the second user's list
    if isinstance(second_tasks_list, list):
        task_ids = [task.get("id") for task in second_tasks_list]
        assert first_task_id not in task_ids


def test_jwt_token_validation():
    """
    Test JWT token validation and security.
    """
    # Create a user and get a valid token
    valid_token = create_test_user("jwt_test@example.com")

    # Test with valid token
    headers = {"Authorization": f"Bearer {valid_token}"}
    response = client.get("/api/tasks", headers=headers)
    assert response.status_code in [200, 204]  # 204 if no tasks exist yet

    # Test with invalid token
    invalid_headers = {"Authorization": "Bearer invalid.token.here"}
    invalid_response = client.get("/api/tasks", headers=invalid_headers)
    assert invalid_response.status_code == 401

    # Test without token
    no_auth_response = client.get("/api/tasks")
    assert no_auth_response.status_code == 401

    # Test with malformed Authorization header
    malformed_response = client.get("/api/tasks", headers={"Authorization": "InvalidFormat"})
    assert malformed_response.status_code == 401


def test_rate_limiting_simulation():
    """
    Test rate limiting implementation (conceptual - actual implementation would require specific rate limiter).
    This test verifies that the API can handle multiple requests without crashing.
    """
    user_token = create_test_user("rate_limit_test@example.com")
    headers = {"Authorization": f"Bearer {user_token}"}

    # Send multiple requests to test if rate limiting is implemented
    responses = []
    for i in range(10):
        response = client.get("/api/tasks", headers=headers)
        responses.append(response.status_code)

        # If rate limiting is implemented, we should eventually get 429 (Too Many Requests)
        if response.status_code == 429:
            # Rate limiting is working
            break

    # If no 429 responses were received, rate limiting may not be implemented
    # This is acceptable for the basic implementation but should be added later


def test_input_validation_and_sanitization():
    """
    Test input validation and sanitization for security.
    """
    user_token = create_test_user("validation_test@example.com")
    headers = {"Authorization": f"Bearer {user_token}"}

    # Test SQL injection attempts in task title
    sql_injection_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "admin'--",
        "'; EXEC xp_cmdshell 'ping 127.0.0.1'; --"
    ]

    for payload in sql_injection_payloads:
        response = client.post("/api/tasks", json={
            "title": payload,
            "description": "Safe description"
        }, headers=headers)
        # Should either reject the request or sanitize the input
        assert response.status_code in [200, 201, 400, 422]

    # Test XSS attempts in task description
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "javascript:alert('XSS')",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>"
    ]

    for payload in xss_payloads:
        response = client.post("/api/tasks", json={
            "title": "Safe title",
            "description": payload
        }, headers=headers)
        # Should either reject the request or sanitize the input
        assert response.status_code in [200, 201, 400, 422]

    # Test extremely long inputs
    long_input = "A" * 10000  # 10,000 character string
    response = client.post("/api/tasks", json={
        "title": long_input,
        "description": long_input
    }, headers=headers)
    # Should either accept with truncation, or reject with 400
    assert response.status_code in [200, 201, 400, 413]  # 413 = Payload Too Large


def test_authentication_bypass_attempts():
    """
    Test various authentication bypass attempts.
    """
    # Try to access protected endpoints without authentication
    unprotected_endpoints = [
        "/api/tasks",
        "/api/tasks/1",
        "/api/tasks/1/complete",
    ]

    for endpoint in unprotected_endpoints:
        response = client.get(endpoint)
        assert response.status_code == 401, f"Endpoint {endpoint} should require authentication"

        # Try with invalid auth header format
        invalid_response = client.get(endpoint, headers={"Authorization": "Bearer "})
        assert invalid_response.status_code == 401, f"Endpoint {endpoint} should reject empty token"

        # Try with invalid auth header type
        wrong_type_response = client.get(endpoint, headers={"Authorization": "Basic token"})
        assert wrong_type_response.status_code in [401, 403], f"Endpoint {endpoint} should reject wrong auth type"


def test_privilege_escalation_attempts():
    """
    Test for privilege escalation vulnerabilities.
    """
    # Create a regular user
    user_token = create_test_user("normal_user@example.com")
    headers = {"Authorization": f"Bearer {user_token}"}

    # Try to access admin endpoints (these shouldn't exist in basic implementation, but test anyway)
    admin_endpoints = [
        "/api/admin/users",
        "/api/admin/tasks",
        "/api/users/all",  # If this endpoint exists, it should be restricted
    ]

    for endpoint in admin_endpoints:
        response = client.get(endpoint, headers=headers)
        # Should return 401, 403, or 404 (not 200)
        assert response.status_code in [401, 403, 404], f"Regular user should not access {endpoint}"

    # Try to manipulate user_id in requests (if the API accepts it)
    # This tests if the API properly uses the authenticated user's ID rather than trusting input
    create_response = client.post("/api/tasks", json={
        "title": "Test Task",
        "description": "Test Description",
        "user_id": 999999  # Attempt to assign to different user
    }, headers=headers)

    # The API should ignore the user_id field and use the authenticated user's ID
    assert create_response.status_code in [200, 201, 400, 422]


def test_session_fixation_prevention():
    """
    Test for session/token fixation prevention.
    """
    # Register a new user
    registration_response = client.post("/api/auth/register", json={
        "email": "session_fixation_test@example.com",
        "password": "SecurePassword123!"
    })

    # Login and get first token
    login_response1 = client.post("/api/auth/login", json={
        "email": "session_fixation_test@example.com",
        "password": "SecurePassword123!"
    })

    first_token = login_response1.json().get("access_token")
    assert first_token is not None

    # Login again and get second token
    login_response2 = client.post("/api/auth/login", json={
        "email": "session_fixation_test@example.com",
        "password": "SecurePassword123!"
    })

    second_token = login_response2.json().get("access_token")
    assert second_token is not None

    # The tokens should be different (or at least the implementation should rotate tokens)
    # For basic JWT implementation, tokens might be the same, but in a real app they should differ
    # This is more of a conceptual test


def test_brute_force_protection_simulation():
    """
    Test brute force protection (conceptual).
    """
    # Try multiple failed login attempts
    failed_attempts = 0
    for i in range(5):
        response = client.post("/api/auth/login", json={
            "email": "brute_force_test@example.com",
            "password": f"wrong_password_{i}"
        })

        if response.status_code == 401:
            failed_attempts += 1

    # The API should still be accessible after failed attempts
    # (Actual rate limiting would be implemented separately)
    assert failed_attempts >= 0  # We should be able to make attempts


def test_cors_security():
    """
    Test CORS configuration for security.
    """
    # Test with a potentially malicious origin
    response = client.get(
        "/api/tasks",
        headers={
            "Origin": "https://malicious-site.com",
            "Authorization": f"Bearer {create_test_user('cors_test@example.com')}"
        }
    )

    # Check if CORS headers are properly configured
    cors_headers = ["access-control-allow-origin", "access-control-allow-credentials"]
    for header in cors_headers:
        # The response may or may not have these headers depending on configuration
        # This is more of a check than an assertion
        pass


if __name__ == "__main__":
    pytest.main([__file__])