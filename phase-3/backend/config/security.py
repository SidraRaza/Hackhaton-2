"""
Security configuration for the Hackathon Todo App
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
from typing import List

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)

def setup_security(app: FastAPI):
    """
    Apply security configurations to the FastAPI application
    """

    # CORS Middleware - restrict to known origins
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        # Don't expose sensitive headers
        # expose_headers=["Access-Control-Allow-Origin"]
    )

    # Trusted Host Middleware - only allow requests from known hosts
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    )

    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    return app

def validate_user_access(user_id: int, requested_user_id: int) -> bool:
    """
    Validate that the authenticated user can access the requested resource
    """
    return user_id == requested_user_id

def get_current_user_id(credentials: HTTPAuthorizationCredentials = None) -> int:
    """
    Extract user ID from JWT token
    This is a simplified version - in practice, you'd decode the JWT and extract user info
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication credentials provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # In a real implementation, you would:
    # 1. Decode the JWT token
    # 2. Validate the signature
    # 3. Check expiration
    # 4. Extract user ID

    # Placeholder implementation
    token = credentials.credentials
    # This would be replaced with actual JWT decoding logic
    user_id = 1  # Placeholder - would come from decoded token

    return user_id

# Security headers configuration
def add_security_headers(response):
    """
    Add security headers to responses
    """
    # Prevent MIME-type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"

    # Enable XSS protection
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Strict transport security
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    # Content security policy (basic)
    response.headers["Content-Security-Policy"] = "default-src 'self'"

    return response