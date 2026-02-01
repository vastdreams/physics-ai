# ai/context_memory/
"""
Usage Tracker - Track pathway usage and statistics.

Inspired by DREAM architecture - usage-based pathway weighting.

First Principle Analysis:
- Usage tracking: U = {pathway: count} over time
- Statistics: Mean, variance, trends
- Mathematical foundation: Time series analysis, statistics
- Architecture: Tracker that monitors and analyzes usage patterns
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel


@dataclass
class UsageRecord:
    """Represents a usage record."""
    pathway: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class UsageTracker:
    """
    Usage tracker for pathway statistics.
    
    Features:
    - Usage recording
    - Statistics computation
    - Trend analysis
    - Hot/cold pathway identification
    """
    
    def __init__(self, retention_days: int = 30):
        """
        Initialize usage tracker.
        
        Args:
            retention_days: Number of days to retain records
        """
        self.logger = SystemLogger()
        self.retention_days = retention_days
        self.records: List[UsageRecord] = []
        self.pathway_counts: Dict[str, int] = defaultdict(int)
        
        self.logger.log(f"UsageTracker initialized (retention={retention_days} days)", level="INFO")
    
    def record_usage(self,
                    pathway: str,
                    metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Record pathway usage.
        
        Args:
            pathway: Pathway identifier
            metadata: Optional metadata
        """
        record = UsageRecord(
            pathway=pathway,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        self.records.append(record)
        self.pathway_counts[pathway] += 1
        
        # Clean old records
        self._clean_old_records()
    
    def _clean_old_records(self) -> None:
        """Remove records older than retention period."""
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        self.records = [r for r in self.records if r.timestamp > cutoff]
    
    def get_pathway_statistics(self, pathway: str) -> Dict[str, Any]:
        """
        Get statistics for a pathway.
        
        Args:
            pathway: Pathway identifier
            
        Returns:
            Statistics dictionary
        """
        pathway_records = [r for r in self.records if r.pathway == pathway]
        
        if not pathway_records:
            return {
                'pathway': pathway,
                'total_usage': 0,
                'recent_usage': 0,
                'avg_time_between_usage': 0.0
            }
        
        # Recent usage (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_records = [r for r in pathway_records if r.timestamp > recent_cutoff]
        
        # Average time between usage
        if len(pathway_records) > 1:
            time_diffs = [
                (pathway_records[i+1].timestamp - pathway_records[i].timestamp).total_seconds()
                for i in range(len(pathway_records) - 1)
            ]
            avg_time = sum(time_diffs) / len(time_diffs)
        else:
            avg_time = 0.0
        
        return {
            'pathway': pathway,
            'total_usage': len(pathway_records),
            'recent_usage': len(recent_records),
            'avg_time_between_usage': avg_time,
            'last_used': pathway_records[-1].timestamp.isoformat() if pathway_records else None
        }
    
    def get_hot_pathways(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most frequently used pathways.
        
        Args:
            limit: Number of pathways to return
            
        Returns:
            List of pathway statistics
        """
        sorted_pathways = sorted(
            self.pathway_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [
            self.get_pathway_statistics(pathway)
            for pathway, _ in sorted_pathways
        ]
    
    def get_cold_pathways(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get least frequently used pathways.
        
        Args:
            limit: Number of pathways to return
            
        Returns:
            List of pathway statistics
        """
        sorted_pathways = sorted(
            self.pathway_counts.items(),
            key=lambda x: x[1]
        )[:limit]
        
        return [
            self.get_pathway_statistics(pathway)
            for pathway, _ in sorted_pathways
        ]
    
    def get_all_statistics(self) -> Dict[str, Any]:
        """Get overall statistics."""
        total_pathways = len(self.pathway_counts)
        total_usage = sum(self.pathway_counts.values())
        
        return {
            'total_pathways': total_pathways,
            'total_usage': total_usage,
            'avg_usage_per_pathway': total_usage / total_pathways if total_pathways > 0 else 0.0,
            'num_records': len(self.records),
            'retention_days': self.retention_days
        }

