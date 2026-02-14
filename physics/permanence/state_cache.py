"""
PATH: physics/permanence/state_cache.py
PURPOSE: In-memory cache for pre-computed equational states

Implements hash-based (SHA-256) storage with TTL expiration and
LRU eviction, inspired by DREAM architecture permanence layer.

Algorithm:
    store:    H(input) = SHA256(JSON(input)) → cache[H] = state
    retrieve: H(input) → cache.get(H)
    evict:    min(last_accessed) when cache full

DEPENDENCIES:
- loggers.system_logger: Structured logging
- utilities.cot_logging: Chain-of-thought logging
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel


@dataclass
class CachedState:
    """Represents a cached state with access tracking metadata."""

    input_hash: str
    state: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    cached_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    ttl_seconds: Optional[int] = None


class StateCache:
    """
    Hash-based state cache with TTL and LRU eviction.

    Features:
    - SHA-256 keyed storage for deterministic lookups
    - Configurable time-to-live (TTL) per entry
    - LRU eviction when capacity is reached
    - Access count tracking
    """

    def __init__(self, max_size: int = 10000, default_ttl: Optional[int] = None) -> None:
        """
        Initialize state cache.

        Args:
            max_size: Maximum cache size
            default_ttl: Default time-to-live in seconds (None = no expiry)
        """
        self._logger = SystemLogger()
        self.cache: Dict[str, CachedState] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl

        self._logger.log(f"StateCache initialized (max_size={max_size})", level="INFO")

    def _compute_hash(self, input_data: Dict[str, Any]) -> str:
        """
        Compute deterministic hash for input data.

        Algorithm: H(input) = SHA256(JSON(input, sort_keys=True))

        Args:
            input_data: Input dictionary

        Returns:
            Hex digest string
        """
        sorted_data = json.dumps(input_data, sort_keys=True)
        return hashlib.sha256(sorted_data.encode()).hexdigest()

    def store(self,
             input_data: Dict[str, Any],
             state: Dict[str, Any],
             metadata: Optional[Dict[str, Any]] = None,
             ttl: Optional[int] = None) -> str:
        """
        Store state in cache.

        Args:
            input_data: Input data dictionary (used for hash key)
            state: Computed state dictionary
            metadata: Optional metadata
            ttl: Optional time-to-live in seconds

        Returns:
            Cache key (hex digest)
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(action="CACHE_STORE", level=LogLevel.INFO)

        try:
            cache_key = self._compute_hash(input_data)

            if len(self.cache) >= self.max_size and cache_key not in self.cache:
                self._evict_lru()

            cached = CachedState(
                input_hash=cache_key,
                state=state,
                metadata=metadata or {},
                ttl_seconds=ttl or self.default_ttl
            )

            self.cache[cache_key] = cached

            cot.end_step(step_id, output_data={'cache_key': cache_key}, validation_passed=True)
            self._logger.log(f"State cached: {cache_key[:16]}...", level="DEBUG")

            return cache_key

        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self._logger.log(f"Error storing in cache: {e}", level="ERROR")
            raise

    def retrieve(self, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Retrieve state from cache by input data hash.

        Args:
            input_data: Input data dictionary

        Returns:
            Cached state dictionary, or None on miss / expiry
        """
        cache_key = self._compute_hash(input_data)

        if cache_key not in self.cache:
            return None

        cached = self.cache[cache_key]

        if cached.ttl_seconds:
            age = (datetime.now() - cached.cached_at).total_seconds()
            if age > cached.ttl_seconds:
                del self.cache[cache_key]
                return None

        cached.access_count += 1
        cached.last_accessed = datetime.now()

        return cached.state

    def _evict_lru(self) -> None:
        """Evict the least recently used entry."""
        if not self.cache:
            return

        lru_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k].last_accessed or self.cache[k].cached_at
        )

        del self.cache[lru_key]
        self._logger.log(f"Evicted LRU entry: {lru_key[:16]}...", level="DEBUG")

    def clear_expired(self) -> int:
        """
        Remove all expired entries from cache.

        Returns:
            Number of entries cleared
        """
        now = datetime.now()
        expired_keys = [
            key for key, cached in self.cache.items()
            if cached.ttl_seconds and (now - cached.cached_at).total_seconds() > cached.ttl_seconds
        ]

        for key in expired_keys:
            del self.cache[key]

        if expired_keys:
            self._logger.log(f"Cleared {len(expired_keys)} expired entries", level="INFO")

        return len(expired_keys)

    def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_access = sum(c.access_count for c in self.cache.values())

        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'total_access': total_access,
            'avg_access_per_entry': total_access / len(self.cache) if self.cache else 0.0,
            'hit_rate': 0.0
        }
