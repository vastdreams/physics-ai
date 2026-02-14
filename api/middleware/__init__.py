"""
PATH: api/middleware/__init__.py
PURPOSE: API middleware for cross-cutting concerns (auth, validation, logging, rate limiting).
"""

from .auth import (
    AUTH_CONFIG,
    get_current_user,
    login_user,
    optional_auth,
    register_user,
    require_auth,
    require_role,
)
from .logging import LoggingMiddleware
from .rate_limit import (
    RateLimitMiddleware,
    get_rate_limiter,
    rate_limit,
    rate_limit_auth,
)
from .validation import ValidationMiddleware

__all__ = [
    "require_auth",
    "require_role",
    "optional_auth",
    "get_current_user",
    "register_user",
    "login_user",
    "AUTH_CONFIG",
    "ValidationMiddleware",
    "LoggingMiddleware",
    "RateLimitMiddleware",
    "rate_limit",
    "rate_limit_auth",
    "get_rate_limiter",
]
