"""
Dapr State Service for Phase V: Advanced Cloud Deployment
Provides access to Dapr state store for managing application state
"""
import json
import logging
from typing import Any, Dict, Optional, List
from datetime import datetime
from dapr.clients import DaprClient

logger = logging.getLogger(__name__)


class DaprStateService:
    """
    Service for managing state through Dapr state store
    Provides methods to interact with the configured Dapr state store
    """

    def __init__(self, state_store_name: str = "postgresql-statestore"):
        """
        Initialize the Dapr State Service

        Args:
            state_store_name: Name of the Dapr state store component to use
        """
        self.state_store_name = state_store_name

    async def save_state(self, key: str, value: Any, etag: Optional[str] = None) -> bool:
        """
        Save state to the Dapr state store

        Args:
            key: Key to store the value under
            value: Value to store (will be JSON serialized)
            etag: Optional etag for concurrency control

        Returns:
            bool: True if state was saved successfully
        """
        try:
            # Serialize the value to JSON
            serialized_value = json.dumps(value, default=str)

            with DaprClient() as client:
                # Prepare the state item
                state_item = {
                    'key': key,
                    'value': serialized_value
                }

                # Add etag if provided
                if etag:
                    state_item['etag'] = {'value': etag}

                # Save to state store
                client.save_state(
                    store_name=self.state_store_name,
                    states=[state_item]
                )

            logger.info(f"State saved successfully for key: {key}")
            return True

        except Exception as e:
            logger.error(f"Failed to save state for key {key}: {str(e)}")
            return False

    async def get_state(self, key: str, state_metadata: Optional[Dict[str, str]] = None) -> Optional[Any]:
        """
        Get state from the Dapr state store

        Args:
            key: Key to retrieve the value for
            state_metadata: Optional metadata for the state operation

        Returns:
            Retrieved value or None if not found
        """
        try:
            with DaprClient() as client:
                response = client.get_state(
                    store_name=self.state_store_name,
                    key=key,
                    state_metadata=state_metadata
                )

            # Deserialize the value from JSON
            if response.data:
                deserialized_value = json.loads(response.data.decode('utf-8'))
                return deserialized_value

            return None

        except Exception as e:
            logger.error(f"Failed to get state for key {key}: {str(e)}")
            return None

    async def get_states(self, keys: List[str], state_metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Get multiple states from the Dapr state store

        Args:
            keys: List of keys to retrieve
            state_metadata: Optional metadata for the state operation

        Returns:
            Dictionary mapping keys to their values
        """
        try:
            with DaprClient() as client:
                response = client.get_bulk_state(
                    store_name=self.state_store_name,
                    keys=keys,
                    state_metadata=state_metadata
                )

            results = {}
            for item in response.items:
                if item.data:
                    try:
                        deserialized_value = json.loads(item.data.decode('utf-8'))
                        results[item.key] = deserialized_value
                    except json.JSONDecodeError:
                        # If JSON parsing fails, return raw data
                        results[item.key] = item.data.decode('utf-8')

            return results

        except Exception as e:
            logger.error(f"Failed to get states for keys {keys}: {str(e)}")
            return {}

    async def delete_state(self, key: str, etag: Optional[str] = None) -> bool:
        """
        Delete state from the Dapr state store

        Args:
            key: Key to delete
            etag: Optional etag for concurrency control

        Returns:
            bool: True if state was deleted successfully
        """
        try:
            with DaprClient() as client:
                # Prepare options for the delete operation
                options = {}
                if etag:
                    options['etag'] = {'value': etag}

                # Delete from state store
                client.delete_state(
                    store_name=self.state_store_name,
                    key=key,
                    options=options
                )

            logger.info(f"State deleted successfully for key: {key}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete state for key {key}: {str(e)}")
            return False

    async def save_tasks_cache(self, user_id: str, tasks: List[Dict[str, Any]]) -> bool:
        """
        Save user's tasks to the state store as a cache

        Args:
            user_id: ID of the user whose tasks to cache
            tasks: List of task dictionaries to cache

        Returns:
            bool: True if cache was saved successfully
        """
        cache_key = f"tasks_cache:{user_id}"
        cache_data = {
            "tasks": tasks,
            "timestamp": datetime.utcnow().isoformat(),
            "ttl": 300  # 5 minutes TTL
        }

        return await self.save_state(cache_key, cache_data)

    async def get_tasks_cache(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get user's tasks from the state store cache

        Args:
            user_id: ID of the user whose tasks cache to retrieve

        Returns:
            Cached tasks or None if not found/expired
        """
        cache_key = f"tasks_cache:{user_id}"
        cache_data = await self.get_state(cache_key)

        if not cache_data:
            return None

        # Check if cache is expired (simple TTL check)
        if 'timestamp' in cache_data and 'ttl' in cache_data:
            try:
                import datetime
                cached_time = datetime.datetime.fromisoformat(cache_data['timestamp'])
                current_time = datetime.datetime.utcnow()
                if (current_time - cached_time).seconds > cache_data['ttl']:
                    # Cache expired, delete it and return None
                    await self.delete_state(cache_key)
                    return None
            except Exception:
                # If timestamp parsing fails, return the cache data anyway
                pass

        return cache_data.get("tasks", [])

    async def save_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Save user preferences to the state store

        Args:
            user_id: ID of the user whose preferences to save
            preferences: Dictionary of user preferences

        Returns:
            bool: True if preferences were saved successfully
        """
        preferences_key = f"user_preferences:{user_id}"
        preferences_data = {
            "preferences": preferences,
            "updated_at": datetime.utcnow().isoformat()
        }

        return await self.save_state(preferences_key, preferences_data)

    async def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user preferences from the state store

        Args:
            user_id: ID of the user whose preferences to retrieve

        Returns:
            User preferences or None if not found
        """
        preferences_key = f"user_preferences:{user_id}"
        preferences_data = await self.get_state(preferences_key)

        if not preferences_data:
            return None

        return preferences_data.get("preferences", {})

    async def save_conversation_state(self, session_id: str, conversation_state: Dict[str, Any]) -> bool:
        """
        Save conversation state to the state store

        Args:
            session_id: ID of the conversation session
            conversation_state: Dictionary representing the conversation state

        Returns:
            bool: True if conversation state was saved successfully
        """
        state_key = f"conversation:{session_id}"
        state_data = {
            "state": conversation_state,
            "updated_at": datetime.utcnow().isoformat()
        }

        return await self.save_state(state_key, state_data)

    async def get_conversation_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation state from the state store

        Args:
            session_id: ID of the conversation session

        Returns:
            Conversation state or None if not found
        """
        state_key = f"conversation:{session_id}"
        state_data = await self.get_state(state_key)

        if not state_data:
            return None

        return state_data.get("state", {})

    async def save_reminder_schedule(self, user_id: str, reminders: List[Dict[str, Any]]) -> bool:
        """
        Save user's reminder schedule to the state store

        Args:
            user_id: ID of the user whose reminders to save
            reminders: List of reminder dictionaries

        Returns:
            bool: True if reminders were saved successfully
        """
        reminders_key = f"reminders:{user_id}"
        reminders_data = {
            "reminders": reminders,
            "updated_at": datetime.utcnow().isoformat()
        }

        return await self.save_state(reminders_key, reminders_data)

    async def get_reminder_schedule(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get user's reminder schedule from the state store

        Args:
            user_id: ID of the user whose reminders to retrieve

        Returns:
            List of reminder dictionaries or None if not found
        """
        reminders_key = f"reminders:{user_id}"
        reminders_data = await self.get_state(reminders_key)

        if not reminders_data:
            return None

        return reminders_data.get("reminders", [])


# Global instance for easy access
dapr_state_service = DaprStateService()


def get_dapr_state_service() -> DaprStateService:
    """
    Get the global Dapr State Service instance

    Returns:
        DaprStateService instance
    """
    return dapr_state_service