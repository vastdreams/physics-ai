"""
Simple cache layer: Redis if available, else in-memory TTL cache.
"""

from __future__ import annotations

import os
import time
from typing import Any, Callable, Optional

_redis_client: Optional[Any] = None
_DEFAULT_TTL = 3600  # 1 hour
_in_memory: dict = {}
_in_memory_expiry: dict = {}


def _get_redis():
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    try:
        import redis
        url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        _redis_client = redis.from_url(url)
        _redis_client.ping()
        return _redis_client
    except Exception:
        return None


def cache_get(key: str) -> Optional[Any]:
    """Get value from cache."""
    r = _get_redis()
    if r:
        try:
            import json
            raw = r.get(key)
            if raw:
                return json.loads(raw)
        except Exception:
            pass
    else:
        if key in _in_memory and _in_memory_expiry.get(key, 0) > time.time():
            return _in_memory[key]
    return None


def cache_set(key: str, value: Any, ttl: int = _DEFAULT_TTL) -> None:
    """Set value in cache."""
    r = _get_redis()
    if r:
        try:
            import json
            r.setex(key, ttl, json.dumps(value, default=str))
        except Exception:
            pass
    else:
        _in_memory[key] = value
        _in_memory_expiry[key] = time.time() + ttl


def cached(prefix: str = "cache", ttl: int = _DEFAULT_TTL):
    """Decorator to cache function results by args."""

    def decorator(fn: Callable):
        def wrapper(*args, **kwargs):
            import hashlib
            import json
            key_data = json.dumps((args, kwargs), default=str, sort_keys=True)
            key_hash = hashlib.sha256(key_data.encode()).hexdigest()[:16]
            cache_key = f"{prefix}:{fn.__name__}:{key_hash}"
            hit = cache_get(cache_key)
            if hit is not None:
                return hit
            result = fn(*args, **kwargs)
            cache_set(cache_key, result, ttl=ttl)
            return result
        return wrapper
    return decorator
