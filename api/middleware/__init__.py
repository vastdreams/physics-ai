# api/middleware/
"""
API Middleware for Cross-Cutting Concerns.

Inspired by DREAM architecture - clean separation of concerns.

First Principle Analysis:
- Middleware: M = {auth, validation, logging, error_handling}
- Cross-cutting: Applied to all requests
- Mathematical foundation: Function composition, decorators
- Architecture: Middleware pipeline for request processing
"""

from .auth import (
    require_auth,
    require_role,
    optional_auth,
    get_current_user,
    register_user,
    login_user,
    AUTH_CONFIG,
)
from .validation import ValidationMiddleware
from .logging import LoggingMiddleware
from .rate_limit import (
    RateLimitMiddleware,
    rate_limit,
    rate_limit_auth,
    get_rate_limiter,
)

__all__ = [
    'require_auth',
    'require_role',
    'optional_auth',
    'get_current_user',
    'register_user',
    'login_user',
    'AUTH_CONFIG',
    'ValidationMiddleware',
    'LoggingMiddleware',
    'RateLimitMiddleware',
    'rate_limit',
    'rate_limit_auth',
    'get_rate_limiter',
]

