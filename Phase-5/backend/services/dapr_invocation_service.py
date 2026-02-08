"""
Dapr Service Invocation Service for Phase V: Advanced Cloud Deployment
Provides methods to invoke other services through Dapr service invocation
"""
import json
import logging
from typing import Any, Dict, Optional
from dapr.clients import DaprClient

logger = logging.getLogger(__name__)


class DaprInvocationService:
    """
    Service for invoking other services through Dapr service invocation
    Provides methods to call other microservices using Dapr's service discovery
    """

    def __init__(self):
        """Initialize the Dapr Invocation Service"""
        pass

    async def invoke_service(
        self,
        app_id: str,
        method: str,
        data: Optional[Dict[str, Any]] = None,
        http_verb: str = "POST",
        http_querystring: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Invoke a method on another service through Dapr service invocation

        Args:
            app_id: The ID of the target service application
            method: The method/path to invoke on the target service
            data: Optional data to send with the invocation
            http_verb: HTTP verb to use (GET, POST, PUT, DELETE, etc.)
            http_querystring: Optional query parameters

        Returns:
            Response from the target service or None if invocation failed
        """
        try:
            # Serialize the data to JSON if provided
            serialized_data = json.dumps(data) if data else ""

            with DaprClient() as client:
                # Invoke the target service method
                response = client.invoke_method(
                    app_id=app_id,
                    method_name=method,
                    data=serialized_data,
                    http_verb=http_verb,
                    http_querystring=http_querystring
                )

                # Deserialize the response
                response_data = json.loads(response.text()) if response.text() else None
                return response_data

        except Exception as e:
            logger.error(f"Dapr service invocation failed: app_id={app_id}, method={method}, error={str(e)}")
            return None

    async def invoke_auth_service(self, method: str, data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Invoke methods on the auth service

        Args:
            method: Method to invoke on auth service
            data: Optional data to send

        Returns:
            Response from auth service
        """
        return await self.invoke_service(app_id="auth-service", method=method, data=data)

    async def invoke_task_service(self, method: str, data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Invoke methods on the task service

        Args:
            method: Method to invoke on task service
            data: Optional data to send

        Returns:
            Response from task service
        """
        return await self.invoke_service(app_id="task-service", method=method, data=data)

    async def invoke_notification_service(self, method: str, data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Invoke methods on the notification service

        Args:
            method: Method to invoke on notification service
            data: Optional data to send

        Returns:
            Response from notification service
        """
        return await self.invoke_service(app_id="notification-service", method=method, data=data)

    async def invoke_audit_service(self, method: str, data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Invoke methods on the audit service

        Args:
            method: Method to invoke on audit service
            data: Optional data to send

        Returns:
            Response from audit service
        """
        return await self.invoke_service(app_id="audit-service", method=method, data=data)

    async def invoke_search_service(self, method: str, data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Invoke methods on the search service

        Args:
            method: Method to invoke on search service
            data: Optional data to send

        Returns:
            Response from search service
        """
        return await self.invoke_service(app_id="search-service", method=method, data=data)

    async def invoke_user_service(self, method: str, data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Invoke methods on the user service

        Args:
            method: Method to invoke on user service
            data: Optional data to send

        Returns:
            Response from user service
        """
        return await self.invoke_service(app_id="user-service", method=method, data=data)

    async def health_check_service(self, app_id: str) -> bool:
        """
        Perform a health check on a target service

        Args:
            app_id: The ID of the service to check

        Returns:
            True if service is healthy, False otherwise
        """
        try:
            # Try to invoke a simple health check endpoint
            response = await self.invoke_service(
                app_id=app_id,
                method="health",
                http_verb="GET"
            )

            # If we got a response, consider it healthy
            return response is not None
        except Exception:
            return False

    async def batch_invoke_services(
        self,
        invocations: list
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Invoke multiple services in a batch operation

        Args:
            invocations: List of invocation dictionaries with app_id, method, data, etc.

        Returns:
            Dictionary mapping service identifiers to their responses
        """
        results = {}

        for i, invocation in enumerate(invocations):
            app_id = invocation.get('app_id')
            method = invocation.get('method')
            data = invocation.get('data')
            http_verb = invocation.get('http_verb', 'POST')

            response = await self.invoke_service(
                app_id=app_id,
                method=method,
                data=data,
                http_verb=http_verb
            )

            # Use a key based on index or app_id/method combination
            key = f"{app_id}_{method}_{i}" if app_id and method else f"invocation_{i}"
            results[key] = response

        return results

    async def invoke_with_retry(
        self,
        app_id: str,
        method: str,
        data: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        http_verb: str = "POST"
    ) -> Optional[Dict[str, Any]]:
        """
        Invoke a service method with retry logic

        Args:
            app_id: The ID of the target service application
            method: The method/path to invoke on the target service
            data: Optional data to send with the invocation
            max_retries: Maximum number of retry attempts
            http_verb: HTTP verb to use

        Returns:
            Response from the target service or None if all retries failed
        """
        import asyncio

        for attempt in range(max_retries):
            try:
                response = await self.invoke_service(
                    app_id=app_id,
                    method=method,
                    data=data,
                    http_verb=http_verb
                )

                if response is not None:
                    return response

            except Exception as e:
                logger.warning(f"Service invocation attempt {attempt + 1} failed: {str(e)}")

                if attempt < max_retries - 1:
                    # Exponential backoff: wait 2^attempt seconds
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)

        logger.error(f"All {max_retries} attempts to invoke {app_id}.{method} failed")
        return None

    async def invoke_with_circuit_breaker(
        self,
        app_id: str,
        method: str,
        data: Optional[Dict[str, Any]] = None,
        max_failures: int = 5,
        reset_timeout: int = 30,
        http_verb: str = "POST"
    ) -> Optional[Dict[str, Any]]:
        """
        Invoke a service method with circuit breaker pattern

        Args:
            app_id: The ID of the target service application
            method: The method/path to invoke on the target service
            data: Optional data to send with the invocation
            max_failures: Maximum number of failures before opening circuit
            reset_timeout: Timeout in seconds before attempting reset
            http_verb: HTTP verb to use

        Returns:
            Response from the target service or None if invocation failed/circuit open
        """
        import asyncio
        from datetime import datetime

        # Circuit breaker state tracking
        if not hasattr(self, '_circuit_states'):
            self._circuit_states = {}

        circuit_key = f"{app_id}:{method}"

        # Get or initialize circuit state
        if circuit_key not in self._circuit_states:
            self._circuit_states[circuit_key] = {
                'state': 'CLOSED',  # CLOSED, OPEN, HALF_OPEN
                'failure_count': 0,
                'last_failure_time': None,
                'last_attempt_time': None
            }

        circuit_state = self._circuit_states[circuit_key]

        # Check if circuit is OPEN
        if circuit_state['state'] == 'OPEN':
            # Check if enough time has passed to try again (HALF_OPEN)
            if circuit_state['last_failure_time'] and \
               (datetime.now() - circuit_state['last_failure_time']).seconds >= reset_timeout:
                circuit_state['state'] = 'HALF_OPEN'
            else:
                # Circuit is still open, return failure
                logger.warning(f"Circuit breaker OPEN for {circuit_key}, skipping invocation")
                return None

        # If circuit is HALF_OPEN, allow one request to test recovery
        if circuit_state['state'] == 'HALF_OPEN':
            logger.info(f"Circuit breaker HALF_OPEN for {circuit_key}, testing recovery")
            # Attempt the call
            response = await self.invoke_service(
                app_id=app_id,
                method=method,
                data=data,
                http_verb=http_verb
            )

            if response is not None:
                # Success, close the circuit
                circuit_state['state'] = 'CLOSED'
                circuit_state['failure_count'] = 0
                logger.info(f"Circuit breaker CLOSED for {circuit_key} after successful call")
                return response
            else:
                # Still failing, open the circuit again
                circuit_state['state'] = 'OPEN'
                circuit_state['last_failure_time'] = datetime.now()
                logger.warning(f"Circuit breaker remains OPEN for {circuit_key} after failed test")
                return None

        # Circuit is CLOSED, proceed with the call
        response = await self.invoke_service(
            app_id=app_id,
            method=method,
            data=data,
            http_verb=http_verb
        )

        if response is not None:
            # Success, reset failure count
            circuit_state['failure_count'] = 0
            circuit_state['last_attempt_time'] = datetime.now()
        else:
            # Failure, increment failure count
            circuit_state['failure_count'] += 1
            circuit_state['last_failure_time'] = datetime.now()
            circuit_state['last_attempt_time'] = datetime.now()

            # Check if we need to open the circuit
            if circuit_state['failure_count'] >= max_failures:
                circuit_state['state'] = 'OPEN'
                logger.warning(f"Circuit breaker OPENED for {circuit_key} after {max_failures} failures")

        return response

    async def invoke_with_resilience_patterns(
        self,
        app_id: str,
        method: str,
        data: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        max_failures: int = 5,
        reset_timeout: int = 30,
        timeout: int = 30,
        http_verb: str = "POST"
    ) -> Optional[Dict[str, Any]]:
        """
        Invoke a service method with combined resilience patterns (retry + circuit breaker + timeout)

        Args:
            app_id: The ID of the target service application
            method: The method/path to invoke on the target service
            data: Optional data to send with the invocation
            max_retries: Maximum number of retry attempts
            max_failures: Maximum number of failures before opening circuit
            reset_timeout: Timeout in seconds before attempting reset
            timeout: Timeout in seconds for the service call
            http_verb: HTTP verb to use

        Returns:
            Response from the target service or None if all resilience patterns failed
        """
        import asyncio

        # First check circuit breaker
        circuit_response = await self.invoke_with_circuit_breaker(
            app_id=app_id,
            method=method,
            data=data,
            max_failures=max_failures,
            reset_timeout=reset_timeout,
            http_verb=http_verb
        )

        if circuit_response is not None:
            return circuit_response

        # If circuit breaker allows the call or is closed, apply retry logic
        for attempt in range(max_retries):
            try:
                # Use asyncio.timeout for timeout handling (Python 3.11+)
                # For compatibility, we'll use a simpler approach
                response = await self.invoke_with_circuit_breaker(
                    app_id=app_id,
                    method=method,
                    data=data,
                    max_failures=max_failures,
                    reset_timeout=reset_timeout,
                    http_verb=http_verb
                )

                if response is not None:
                    return response

            except Exception as e:
                logger.warning(f"Service invocation attempt {attempt + 1} failed: {str(e)}")

                if attempt < max_retries - 1:
                    # Exponential backoff: wait 2^attempt seconds
                    wait_time = min(2 ** attempt, 10)  # Cap at 10 seconds
                    await asyncio.sleep(wait_time)

        logger.error(f"All resilience patterns failed for {app_id}.{method}")
        return None

    async def bulk_invoke_with_resilience(
        self,
        invocations: list,
        max_retries: int = 2,
        max_failures: int = 3,
        reset_timeout: int = 30
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Invoke multiple services with resilience patterns applied to each

        Args:
            invocations: List of invocation dictionaries with app_id, method, data, etc.
            max_retries: Maximum number of retry attempts for each invocation
            max_failures: Maximum number of failures before opening circuit for each service
            reset_timeout: Timeout in seconds before attempting reset

        Returns:
            Dictionary mapping service identifiers to their responses
        """
        results = {}

        for i, invocation in enumerate(invocations):
            app_id = invocation.get('app_id')
            method = invocation.get('method')
            data = invocation.get('data')
            http_verb = invocation.get('http_verb', 'POST')

            response = await self.invoke_with_resilience_patterns(
                app_id=app_id,
                method=method,
                data=data,
                max_retries=max_retries,
                max_failures=max_failures,
                reset_timeout=reset_timeout,
                http_verb=http_verb
            )

            # Use a key based on index or app_id/method combination
            key = f"{app_id}_{method}_{i}" if app_id and method else f"invocation_{i}"
            results[key] = response

        return results


# Global instance for easy access
dapr_invocation_service = DaprInvocationService()


def get_dapr_invocation_service() -> DaprInvocationService:
    """
    Get the global Dapr Invocation Service instance

    Returns:
        DaprInvocationService instance
    """
    return dapr_invocation_service