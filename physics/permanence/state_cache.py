# physics/permanence/
"""
State Cache - Storage for pre-computed states.

Inspired by DREAM architecture - permanence on equational states.

First Principle Analysis:
- Cache: C = {input_hash: {state, metadata, timestamp}}
- Hash function: H(input) → hash for fast lookup
- Mathematical foundation: Hash tables, caching algorithms
- Architecture: In-memory cache with optional persistence
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel


@dataclass
class CachedState:
    """Represents a cached state."""
    input_hash: str
    state: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    cached_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    ttl_seconds: Optional[int] = None  # Time to live


class StateCache:
    """
    State cache for pre-computed equational states.
    
    Features:
    - Hash-based storage
    - Fast lookup
    - TTL support
    - Access tracking
    """
    
    def __init__(self, max_size: int = 10000, default_ttl: Optional[int] = None):
        """
        Initialize state cache.
        
        Args:
            max_size: Maximum cache size
            default_ttl: Default time-to-live in seconds
        """
        self.logger = SystemLogger()
        self.cache: Dict[str, CachedState] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        
        self.logger.log(f"StateCache initialized (max_size={max_size})", level="INFO")
    
    def _compute_hash(self, input_data: Dict[str, Any]) -> str:
        """
        Compute hash for input data.
        
        Mathematical: H(input) = SHA256(JSON(input))
        
        Args:
            input_data: Input dictionary
            
        Returns:
            Hash string
        """
        # Sort keys for consistent hashing
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
            input_data: Input data dictionary
            state: Computed state dictionary
            metadata: Optional metadata
            ttl: Optional time-to-live in seconds
            
        Returns:
            Cache key (hash)
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="CACHE_STORE",
            level=LogLevel.INFO
        )
        
        try:
            # Compute hash
            cache_key = self._compute_hash(input_data)
            
            # Check if cache is full
            if len(self.cache) >= self.max_size and cache_key not in self.cache:
                # Evict least recently used
                self._evict_lru()
            
            # Store state
            cached = CachedState(
                input_hash=cache_key,
                state=state,
                metadata=metadata or {},
                ttl_seconds=ttl or self.default_ttl
            )
            
            self.cache[cache_key] = cached
            
            cot.end_step(step_id, output_data={'cache_key': cache_key}, validation_passed=True)
            
            self.logger.log(f"State cached: {cache_key[:16]}...", level="DEBUG")
            
            return cache_key
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error storing in cache: {str(e)}", level="ERROR")
            raise
    
    def retrieve(self, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Retrieve state from cache.
        
        Args:
            input_data: Input data dictionary
            
        Returns:
            Cached state or None
        """
        cache_key = self._compute_hash(input_data)
        
        if cache_key not in self.cache:
            return None
        
        cached = self.cache[cache_key]
        
        # Check TTL
        if cached.ttl_seconds:
            age = (datetime.now() - cached.cached_at).total_seconds()
            if age > cached.ttl_seconds:
                # Expired
                del self.cache[cache_key]
                return None
        
        # Update access statistics
        cached.access_count += 1
        cached.last_accessed = datetime.now()
        
        return cached.state
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self.cache:
            return
        
        # Find LRU entry
        lru_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k].last_accessed or self.cache[k].cached_at
        )
        
        del self.cache[lru_key]
        self.logger.log(f"Evicted LRU entry: {lru_key[:16]}...", level="DEBUG")
    
    def clear_expired(self) -> int:
        """
        Clear expired entries.
        
        Returns:
            Number of entries cleared
        """
        now = datetime.now()
        expired_keys = []
        
        for key, cached in self.cache.items():
            if cached.ttl_seconds:
                age = (now - cached.cached_at).total_seconds()
                if age > cached.ttl_seconds:
                    expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self.logger.log(f"Cleared {len(expired_keys)} expired entries", level="INFO")
        
        return len(expired_keys)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_access = sum(c.access_count for c in self.cache.values())
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'total_access': total_access,
            'avg_access_per_entry': total_access / len(self.cache) if self.cache else 0.0,
            'hit_rate': 0.0  # Would track hits/misses in production
        }

