# loggers/
"""
Performance logging module.

Tracks system performance metrics.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from .system_logger import SystemLogger


class PerformanceLogger:
    """
    Logger for tracking performance metrics.
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize performance logger.
        
        Args:
            log_dir: Directory for log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.system_logger = SystemLogger(log_dir=log_dir)
        self.metrics: List[Dict[str, Any]] = []
        
        self.system_logger.log("PerformanceLogger initialized", level="INFO")
    
    def log_metric(self, metric_name: str, value: float, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a performance metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            context: Additional context
        """
        metric = {
            "timestamp": datetime.now().isoformat(),
            "metric": metric_name,
            "value": value,
            "context": context or {}
        }
        
        self.metrics.append(metric)
        self.system_logger.log(f"Performance metric: {metric_name} = {value}", level="DEBUG", **(context or {}))
        
        # Save to file
        perf_file = self.log_dir / f"performance_{datetime.now().strftime('%Y%m%d')}.json"
        with open(perf_file, 'a') as f:
            f.write(json.dumps(metric) + '\n')

