"""
PATH: api/middleware/rate_limit.py
PURPOSE: In-memory rate limiting middleware for API endpoints.

FLOW:
 ┌─────────┐    ┌──────────┐    ┌────────────┐    ┌─────────┐
 │ Request │───▶│  Lookup  │───▶│  Check     │───▶│ Allow / │
 │         │    │  Bucket  │    │  Limit     │    │ Reject  │
 └─────────┘    └──────────┘    └────────────┘    └─────────┘

Algorithm: Token bucket with sliding window.
- Each client (IP or user) gets a bucket with N tokens.
- Tokens are replenished at a fixed rate.
- Each request consumes one token.
- If no tokens remain, the request is rejected with 429.

In production, replace the in-memory store with Redis
using REDIS_URL from the environment.
"""

import time
import threading
from collections import defaultdict
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple

from flask import Flask, request, jsonify, g


class _TokenBucket:
    """Token-bucket rate limiter per key."""

    __slots__ = ("capacity", "refill_rate", "tokens", "last_refill")

    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.tokens = float(capacity)
        self.last_refill = time.monotonic()

    def consume(self) -> Tuple[bool, float]:
        """Try to consume one token. Returns (allowed, retry_after_seconds)."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True, 0.0
        else:
            retry_after = (1 - self.tokens) / self.refill_rate
            return False, retry_after


class RateLimiter:
    """
    In-memory rate limiter using token bucket algorithm.

    Thread-safe.  Expired buckets are garbage-collected periodically.
    """

    def __init__(
        self,
        default_limit: int = 60,
        default_window: int = 60,
        auth_limit: int = 10,
        auth_window: int = 60,
        cleanup_interval: int = 300,
    ):
        """
        Args:
            default_limit:  Max requests per window for general endpoints.
            default_window:  Window size in seconds.
            auth_limit:  Stricter limit for auth endpoints (login/register).
            auth_window:  Window for auth endpoints.
            cleanup_interval:  Seconds between stale-bucket cleanup.
        """
        self.default_limit = default_limit
        self.default_window = default_window
        self.auth_limit = auth_limit
        self.auth_window = auth_window

        self._buckets: Dict[str, _TokenBucket] = {}
        self._lock = threading.Lock()
        self._cleanup_interval = cleanup_interval
        self._last_cleanup = time.monotonic()

    # ── public API ──────────────────────────────────────────────

    def _get_bucket(self, key: str, capacity: int, window: int) -> _TokenBucket:
        with self._lock:
            self._maybe_cleanup()
            if key not in self._buckets:
                refill_rate = capacity / window
                self._buckets[key] = _TokenBucket(capacity, refill_rate)
            return self._buckets[key]

    def check(
        self,
        key: str,
        limit: Optional[int] = None,
        window: Optional[int] = None,
    ) -> Tuple[bool, float, int]:
        """
        Check whether the request is allowed.

        Returns:
            (allowed, retry_after_seconds, remaining_tokens)
        """
        limit = limit or self.default_limit
        window = window or self.default_window
        bucket = self._get_bucket(key, limit, window)
        allowed, retry_after = bucket.consume()
        remaining = max(0, int(bucket.tokens))
        return allowed, retry_after, remaining

    # ── cleanup ─────────────────────────────────────────────────

    def _maybe_cleanup(self) -> None:
        now = time.monotonic()
        if now - self._last_cleanup < self._cleanup_interval:
            return
        self._last_cleanup = now
        stale_keys = [
            k
            for k, b in self._buckets.items()
            if (now - b.last_refill) > self._cleanup_interval
        ]
        for k in stale_keys:
            del self._buckets[k]


# ── Singleton ───────────────────────────────────────────────────
_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    """Return the global rate limiter instance."""
    return _limiter


# ── Flask helpers ───────────────────────────────────────────────

def _client_key() -> str:
    """Derive a rate-limit key from the request."""
    # Prefer authenticated user ID, fall back to IP
    user = getattr(g, "current_user", None)
    if user and isinstance(user, dict):
        return f"user:{user.get('id', 'anon')}"
    return f"ip:{request.remote_addr}"


def rate_limit(
    limit: Optional[int] = None,
    window: Optional[int] = None,
    key_func: Optional[Callable[[], str]] = None,
):
    """
    Decorator to rate-limit a Flask route.

    Usage:
        @app.route('/api/search')
        @rate_limit(limit=30, window=60)
        def search():
            ...
    """

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            key = (key_func or _client_key)()
            allowed, retry_after, remaining = _limiter.check(key, limit, window)

            if not allowed:
                resp = jsonify(
                    {
                        "success": False,
                        "error": "Rate limit exceeded",
                        "retry_after": round(retry_after, 1),
                    }
                )
                resp.status_code = 429
                resp.headers["Retry-After"] = str(int(retry_after) + 1)
                resp.headers["X-RateLimit-Remaining"] = "0"
                return resp

            response = f(*args, **kwargs)

            # Attach informational headers if possible
            if hasattr(response, "headers"):
                response.headers["X-RateLimit-Remaining"] = str(remaining)

            return response

        return decorated

    return decorator


def rate_limit_auth(f):
    """Stricter rate limit for auth endpoints (login, register)."""

    @wraps(f)
    def decorated(*args, **kwargs):
        key = f"auth:{request.remote_addr}"
        allowed, retry_after, remaining = _limiter.check(
            key,
            _limiter.auth_limit,
            _limiter.auth_window,
        )

        if not allowed:
            resp = jsonify(
                {
                    "success": False,
                    "error": "Too many authentication attempts. Try again later.",
                    "retry_after": round(retry_after, 1),
                }
            )
            resp.status_code = 429
            resp.headers["Retry-After"] = str(int(retry_after) + 1)
            return resp

        return f(*args, **kwargs)

    return decorated


class RateLimitMiddleware:
    """
    Flask middleware that applies a global rate limit to every request.

    Usage in create_app():
        RateLimitMiddleware.setup(app)
    """

    @staticmethod
    def setup(
        app: Flask,
        global_limit: int = 120,
        global_window: int = 60,
    ) -> None:
        """Attach a global before_request rate-limit check."""

        @app.before_request
        def _global_rate_limit():
            # Skip health checks and static files
            if request.path in ("/health", "/favicon.ico"):
                return None
            if request.path.startswith("/static"):
                return None

            key = _client_key()
            allowed, retry_after, _ = _limiter.check(key, global_limit, global_window)

            if not allowed:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Rate limit exceeded",
                            "retry_after": round(retry_after, 1),
                        }
                    ),
                    429,
                    {"Retry-After": str(int(retry_after) + 1)},
                )
