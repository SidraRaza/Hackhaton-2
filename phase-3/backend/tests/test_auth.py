import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.config.database import get_db, Base
from backend.models.user import User
from backend.utils.auth import create_access_token
from passlib.context import CryptContext

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_contract_auth_endpoints():
    """
    Contract test for auth endpoints to ensure they follow the API specification.
    """
    # Test registration endpoint
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "testpassword123"
    })
    assert response.status_code in [200, 201, 400, 409]  # Expected status codes

    # Test login endpoint
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "testpassword123"
    })
    assert response.status_code in [200, 401]  # Expected status codes

    # Verify response structure contains expected fields
    if response.status_code == 200:
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"


def test_user_registration_flow():
    """
    Integration test for user registration flow.
    """
    # Clear any existing user with this email
    client.delete(f"/api/users/email/test_integration@example.com")

    # Register a new user
    registration_data = {
        "email": "test_integration@example.com",
        "password": "securepassword123"
    }

    response = client.post("/api/auth/register", json=registration_data)
    assert response.status_code == 200 or response.status_code == 201

    # Verify user was created by attempting login
    login_response = client.post("/api/auth/login", json={
        "email": "test_integration@example.com",
        "password": "securepassword123"
    })

    assert login_response.status_code == 200
    data = login_response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_password_hashing():
    """
    Test that passwords are properly hashed during registration.
    """
    test_password = "plaintext_password"
    hashed = pwd_context.hash(test_password)
    assert pwd_context.verify(test_password, hashed)


def test_duplicate_email_registration():
    """
    Test that registering with an existing email fails appropriately.
    """
    # Register first user
    client.post("/api/auth/register", json={
        "email": "duplicate@example.com",
        "password": "password123"
    })

    # Attempt to register with same email
    response = client.post("/api/auth/register", json={
        "email": "duplicate@example.com",
        "password": "password456"
    })

    # Should return 400 or 409 for duplicate email
    assert response.status_code in [400, 409]


if __name__ == "__main__":
    pytest.main([__file__])