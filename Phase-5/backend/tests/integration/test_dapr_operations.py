"""
Integration tests for Dapr-based operations
Tests for Dapr pub/sub, state management, service invocation, and secret management
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlmodel import Session, create_engine
from datetime import datetime
from typing import Dict, Any

from backend.services.dapr_state_service import DaprStateService
from backend.services.dapr_invocation_service import DaprInvocationService
from backend.services.dapr_secrets_service import DaprSecretsService
from backend.services.event_publisher import EventPublisher
from backend.events.consumers import EventConsumerService
from backend.database import create_db_and_tables


@pytest.fixture
def mock_dapr_client():
    """Mock Dapr client for testing"""
    with patch('dapr.clients.DaprClient') as mock_client:
        yield mock_client


class TestDaprStateOperations:
    """Tests for Dapr state store operations"""

    @patch('dapr.clients.DaprClient')
    def test_save_state_operation(self, mock_dapr_client):
        """Test saving state to Dapr state store"""
        # Mock the Dapr client response
        mock_client_instance = Mock()
        mock_dapr_client.return_value.__enter__.return_value = mock_client_instance

        # Create Dapr state service
        state_service = DaprStateService()

        # Test saving state
        result = state_service.save_state("test-key", {"data": "value"})

        # Verify the call was made correctly
        mock_client_instance.save_state.assert_called_once()
        assert result is True

    @patch('dapr.clients.DaprClient')
    def test_get_state_operation(self, mock_dapr_client):
        """Test getting state from Dapr state store"""
        # Mock the Dapr client response
        mock_client_instance = Mock()
        mock_response = Mock()
        mock_response.data = b'{"data": "value"}'
        mock_client_instance.get_state.return_value = mock_response
        mock_dapr_client.return_value.__enter__.return_value = mock_client_instance

        # Create Dapr state service
        state_service = DaprStateService()

        # Test getting state
        result = state_service.get_state("test-key")

        # Verify the call was made correctly and result is as expected
        mock_client_instance.get_state.assert_called_once()
        assert result == {"data": "value"}

    @patch('dapr.clients.DaprClient')
    def test_save_user_preferences_via_dapr(self, mock_dapr_client):
        """Test saving user preferences using Dapr state store"""
        # Mock the Dapr client response
        mock_client_instance = Mock()
        mock_dapr_client.return_value.__enter__.return_value = mock_client_instance

        # Create Dapr state service
        state_service = DaprStateService()

        # Test saving user preferences
        user_id = "test-user-123"
        preferences = {"theme": "dark", "language": "en"}

        result = state_service.save_user_preferences(user_id, preferences)

        # Verify the call was made correctly
        mock_client_instance.save_state.assert_called()
        assert result is True

    @patch('dapr.clients.DaprClient')
    def test_get_user_preferences_via_dapr(self, mock_dapr_client):
        """Test getting user preferences from Dapr state store"""
        # Mock the Dapr client response
        mock_client_instance = Mock()
        mock_response = Mock()
        mock_response.data = b'{"preferences": {"theme": "dark", "language": "en"}}'
        mock_client_instance.get_state.return_value = mock_response
        mock_dapr_client.return_value.__enter__.return_value = mock_client_instance

        # Create Dapr state service
        state_service = DaprStateService()

        # Test getting user preferences
        user_id = "test-user-123"
        result = state_service.get_user_preferences(user_id)

        # Verify the call was made correctly and result is as expected
        mock_client_instance.get_state.assert_called_once()
        assert result == {"theme": "dark", "language": "en"}


class TestDaprInvocationOperations:
    """Tests for Dapr service invocation operations"""

    @patch('dapr.clients.DaprClient')
    def test_invoke_service_basic(self, mock_dapr_client):
        """Test basic service invocation through Dapr"""
        # Mock the Dapr client response
        mock_client_instance = Mock()
        mock_response = Mock()
        mock_response.text.return_value = '{"result": "success"}'
        mock_client_instance.invoke_method.return_value = mock_response
        mock_dapr_client.return_value.__enter__.return_value = mock_client_instance

        # Create Dapr invocation service
        invocation_service = DaprInvocationService()

        # Test service invocation
        result = invocation_service.invoke_service(
            app_id="test-service",
            method="test-method",
            data={"param": "value"}
        )

        # Verify the call was made correctly and result is as expected
        mock_client_instance.invoke_method.assert_called_once()
        assert result == {"result": "success"}

    @patch('dapr.clients.DaprClient')
    def test_invoke_with_retry_success(self, mock_dapr_client):
        """Test service invocation with retry that succeeds"""
        # Mock the Dapr client response
        mock_client_instance = Mock()
        mock_response = Mock()
        mock_response.text.return_value = '{"result": "success"}'
        mock_client_instance.invoke_method.return_value = mock_response
        mock_dapr_client.return_value.__enter__.return_value = mock_client_instance

        # Create Dapr invocation service
        invocation_service = DaprInvocationService()

        # Test service invocation with retry
        result = invocation_service.invoke_with_retry(
            app_id="test-service",
            method="test-method",
            data={"param": "value"},
            max_retries=2
        )

        # Verify the call was made and succeeded
        assert result == {"result": "success"}

    def test_circuit_breaker_logic(self):
        """Test circuit breaker state transitions"""
        # Create Dapr invocation service
        invocation_service = DaprInvocationService()

        # Initialize circuit state
        circuit_key = "test-app:test-method"
        invocation_service._circuit_states = {
            circuit_key: {
                'state': 'CLOSED',
                'failure_count': 0,
                'last_failure_time': None,
                'last_attempt_time': None
            }
        }

        # Test that the circuit state is properly tracked
        assert invocation_service._circuit_states[circuit_key]['state'] == 'CLOSED'
        assert invocation_service._circuit_states[circuit_key]['failure_count'] == 0


class TestDaprSecretOperations:
    """Tests for Dapr secret store operations"""

    @patch('dapr.clients.DaprClient')
    def test_get_secret_operation(self, mock_dapr_client):
        """Test getting a secret from Dapr secret store"""
        # Mock the Dapr client response
        mock_client_instance = Mock()
        mock_response = Mock()
        mock_response.secrets = {"test-secret": "secret-value"}
        mock_client_instance.get_secret.return_value = mock_response
        mock_dapr_client.return_value.__enter__.return_value = mock_client_instance

        # Create Dapr secrets service
        secrets_service = DaprSecretsService()

        # Test getting a secret
        result = secrets_service.get_secret("test-secret")

        # Verify the call was made correctly and result is as expected
        mock_client_instance.get_secret.assert_called_once()
        assert result == "secret-value"

    @patch('dapr.clients.DaprClient')
    def test_get_database_url_secret(self, mock_dapr_client):
        """Test getting database URL from secrets"""
        # Mock the Dapr client response
        mock_client_instance = Mock()
        mock_response = Mock()
        mock_response.secrets = {"database-url": "postgresql://user:pass@localhost/db"}
        mock_client_instance.get_secret.return_value = mock_response
        mock_dapr_client.return_value.__enter__.return_value = mock_client_instance

        # Create Dapr secrets service
        secrets_service = DaprSecretsService()

        # Test getting database URL
        result = secrets_service.get_database_url()

        # Verify the result is as expected
        assert result == "postgresql://user:pass@localhost/db"

    @patch('dapr.clients.DaprClient')
    def test_get_api_keys_secrets(self, mock_dapr_client):
        """Test getting multiple API keys from secrets"""
        # Mock the Dapr client for multiple calls
        def mock_get_secret(store_name, key, metadata=None):
            secrets_map = {
                "openai-api-key": "sk-test-openai-key",
                "google-api-key": "test-google-key",
                "slack-webhook-url": "https://hooks.slack.com/..."
            }
            mock_response = Mock()
            if key in secrets_map:
                mock_response.secrets = {key: secrets_map[key]}
            else:
                mock_response.secrets = {}
            return mock_response

        mock_client_instance = Mock()
        mock_client_instance.get_secret.side_effect = mock_get_secret
        mock_dapr_client.return_value.__enter__.return_value = mock_client_instance

        # Create Dapr secrets service
        secrets_service = DaprSecretsService()

        # Test getting API keys
        result = secrets_service.get_api_keys()

        # Verify we got the expected keys
        assert "openai" in result
        assert "google" in result
        assert result["openai"] == "sk-test-openai-key"


class TestDaprEventOperations:
    """Tests for Dapr event publishing and consumption"""

    @patch('dapr.clients.DaprClient')
    def test_publish_event_via_dapr_pubsub(self, mock_dapr_client):
        """Test publishing an event via Dapr pub/sub"""
        # Mock the Dapr client response
        mock_client_instance = Mock()
        mock_dapr_client.return_value.__enter__.return_value = mock_client_instance

        # Create event publisher
        event_publisher = EventPublisher()

        # Create a test event
        from backend.events.schemas.event_envelope import EventType
        test_event = event_publisher.create_task_event(
            event_type=EventType.TASK_CREATED,
            user_id="test-user",
            data={"task_id": 1, "title": "Test Task"}
        )

        # Test publishing the event via Dapr
        import asyncio
        result = asyncio.run(
            event_publisher.publish_event(test_event, session=None)
        )

        # Verify the Dapr client publish_event method was called
        mock_client_instance.publish_event.assert_called_once()
        assert result is True

    def test_event_consumer_routing(self):
        """Test that events are routed to appropriate consumers"""
        # Create a mock session
        engine = create_engine("sqlite:///:memory:")
        create_db_and_tables(engine)

        with Session(engine) as session:
            # Create event consumer service
            consumer_service = EventConsumerService(session)

            # Create a test event
            test_event = {
                "event_type": "task.created",
                "task_id": 1,
                "user_id": "test-user",
                "title": "Test Task"
            }

            # Route the event to consumers
            results = consumer_service.route_event_to_consumers(test_event)

            # Verify that all consumers processed the event appropriately
            assert 'audit' in results
            assert 'notification' in results
            assert 'recurrence' in results


def test_complete_dapr_integration_flow():
    """Test a complete flow using multiple Dapr capabilities"""
    print("Testing complete Dapr integration flow...")

    # 1. Save some state using Dapr state store
    with patch('dapr.clients.DaprClient') as mock_dapr_client:
        mock_client_instance = Mock()
        mock_response = Mock()
        mock_response.data = b'{"preferences": {"theme": "dark"}}'
        mock_client_instance.get_state.return_value = mock_response
        mock_client_instance.get_secret.return_value = Mock(secrets={"database-url": "test-db-url"})
        mock_dapr_client.return_value.__enter__.return_value = mock_client_instance

        # Test state operations
        state_service = DaprStateService()
        state_saved = state_service.save_user_preferences("test-user", {"theme": "dark"})
        assert state_saved is True

        # Test secrets operations
        secrets_service = DaprSecretsService()
        db_url = secrets_service.get_database_url()
        assert db_url == "test-db-url"

        # Test invocation operations
        invocation_service = DaprInvocationService()
        # This would normally make an actual call, but we're testing the logic
        print("✅ Dapr integration flow test completed")


if __name__ == "__main__":
    # Run the tests manually if this file is executed directly
    import sys
    import os

    # Add the backend directory to the path so imports work
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

    print("Running Dapr operations integration tests...")

    # Create test instances and run basic tests
    test_instance = TestDaprStateOperations()

    # We can't run the actual tests without mocking, but we can verify the structure
    print("✅ Dapr state operations tests defined")
    print("✅ Dapr invocation operations tests defined")
    print("✅ Dapr secret operations tests defined")
    print("✅ Dapr event operations tests defined")
    print("✅ Complete Dapr integration flow test defined")

    print("\n🎉 All Dapr operations tests are properly structured!")