import time
from collections import defaultdict, deque
from typing import Dict
from fastapi import Request, HTTPException
from app.config.settings import settings


class RateLimiter:
    """
    Application-level rate limiter using a sliding window algorithm.
    Tracks requests per user/IP and enforces rate limits.
    """

    def __init__(self):
        # Dictionary to store request timestamps for each identifier
        self.requests: Dict[str, deque] = defaultdict(deque)

    def is_allowed(self, identifier: str) -> bool:
        """
        Check if a request from the given identifier is allowed

        Args:
            identifier: Unique identifier for the requester (user_id, IP, etc.)

        Returns:
            bool: True if request is allowed, False otherwise
        """
        now = time.time()
        window_start = now - 60  # 60 seconds window

        # Clean old requests outside the window
        while self.requests[identifier] and self.requests[identifier][0] < window_start:
            self.requests[identifier].popleft()

        # Check if we're under the limit
        if len(self.requests[identifier]) < settings.RATE_LIMIT_PER_MINUTE:
            # Add current request timestamp
            self.requests[identifier].append(now)
            return True

        return False


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit_check(request: Request, user_id: str = None) -> bool:
    """
    Check if a request is within rate limits

    Args:
        request: FastAPI request object
        user_id: User ID if available (falls back to IP address)

    Returns:
        bool: True if request is allowed, raises HTTPException if not
    """
    # Use user_id if available, otherwise use IP address
    identifier = user_id if user_id else request.client.host

    if not rate_limiter.is_allowed(identifier):
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Limit is {settings.RATE_LIMIT_PER_MINUTE} per minute."
            }
        )

    return True