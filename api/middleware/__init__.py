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

from .auth import AuthMiddleware
from .validation import ValidationMiddleware
from .logging import LoggingMiddleware

__all__ = [
    'AuthMiddleware',
    'ValidationMiddleware',
    'LoggingMiddleware'
]

