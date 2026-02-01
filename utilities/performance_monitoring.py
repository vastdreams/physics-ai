# utilities/
"""
Advanced Performance Monitoring with Variance Tracking.

Inspired by DREAM architecture - comprehensive performance tracking.

First Principle Analysis:
- Performance metrics: M = {m_1, m_2, ..., m_n}
- Variance tracking: σ²(m_i) for each metric
- Trend analysis: Detect performance degradation
- Mathematical foundation: Statistics, time series analysis
- Architecture: Modular monitoring with alerting
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel


@dataclass
class PerformanceMetric:
    """Represents a performance metric."""
    name: str
    value: float
    variance: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricHistory:
    """History of a metric."""
    name: str
    values: List[float] = field(default_factory=list)
    timestamps: List[datetime] = field(default_factory=list)
    variances: List[float] = field(default_factory=list)
    max_history: int = 1000
    
    def add(self, value: float, variance: float = 0.0, timestamp: Optional[datetime] = None) -> None:
        """Add a metric value."""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.values.append(value)
        self.variances.append(variance)
        self.timestamps.append(timestamp)
        
        # Trim if exceeds max
        if len(self.values) > self.max_history:
            self.values.pop(0)
            self.variances.pop(0)
            self.timestamps.pop(0)
    
    def get_statistics(self) -> Dict[str, float]:
        """Get statistics for this metric."""
        if not self.values:
            return {}
        
        values_array = np.array(self.values)
        
        return {
            'mean': float(np.mean(values_array)),
            'std': float(np.std(values_array)),
            'min': float(np.min(values_array)),
            'max': float(np.max(values_array)),
            'variance_mean': float(np.mean(self.variances)) if self.variances else 0.0,
            'count': len(self.values)
        }


class PerformanceMonitor:
    """
    Advanced performance monitoring with variance tracking.
    
    Features:
    - Metric collection
    - Variance tracking
    - Trend analysis
    - Alerting
    """
    
    def __init__(self):
        """Initialize performance monitor."""
        self.logger = SystemLogger()
        self.metrics: Dict[str, MetricHistory] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.alert_thresholds: Dict[str, Dict[str, float]] = {}
        
        self.logger.log("PerformanceMonitor initialized", level="INFO")
    
    def record_metric(self,
                     name: str,
                     value: float,
                     variance: float = 0.0,
                     metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Record a performance metric.
        
        Args:
            name: Metric name
            value: Metric value
            variance: Metric variance
            metadata: Optional metadata
        """
        if name not in self.metrics:
            self.metrics[name] = MetricHistory(name=name)
        
        self.metrics[name].add(value, variance)
        
        # Check alerts
        self._check_alerts(name, value, variance)
        
        self.logger.log(
            f"Metric recorded: {name} = {value:.4f} ± {variance:.4f}",
            level="DEBUG"
        )
    
    def set_alert_threshold(self,
                           metric_name: str,
                           threshold_type: str,
                           threshold_value: float) -> None:
        """
        Set alert threshold for a metric.
        
        Args:
            metric_name: Metric name
            threshold_type: 'min', 'max', 'variance', 'trend'
            threshold_value: Threshold value
        """
        if metric_name not in self.alert_thresholds:
            self.alert_thresholds[metric_name] = {}
        
        self.alert_thresholds[metric_name][threshold_type] = threshold_value
        self.logger.log(
            f"Alert threshold set: {metric_name} {threshold_type} = {threshold_value}",
            level="INFO"
        )
    
    def _check_alerts(self, metric_name: str, value: float, variance: float) -> None:
        """Check if metric triggers alerts."""
        if metric_name not in self.alert_thresholds:
            return
        
        thresholds = self.alert_thresholds[metric_name]
        
        # Check min threshold
        if 'min' in thresholds and value < thresholds['min']:
            self._trigger_alert(metric_name, 'below_min', value, thresholds['min'])
        
        # Check max threshold
        if 'max' in thresholds and value > thresholds['max']:
            self._trigger_alert(metric_name, 'above_max', value, thresholds['max'])
        
        # Check variance threshold
        if 'variance' in thresholds and variance > thresholds['variance']:
            self._trigger_alert(metric_name, 'high_variance', variance, thresholds['variance'])
        
        # Check trend
        if 'trend' in thresholds and metric_name in self.metrics:
            trend = self._compute_trend(metric_name)
            if abs(trend) > thresholds['trend']:
                self._trigger_alert(metric_name, 'trend', trend, thresholds['trend'])
    
    def _trigger_alert(self,
                      metric_name: str,
                      alert_type: str,
                      current_value: float,
                      threshold: float) -> None:
        """Trigger an alert."""
        alert = {
            'metric_name': metric_name,
            'alert_type': alert_type,
            'current_value': current_value,
            'threshold': threshold,
            'timestamp': datetime.now().isoformat()
        }
        
        self.alerts.append(alert)
        self.logger.log(
            f"ALERT: {metric_name} {alert_type} - {current_value} vs {threshold}",
            level="WARNING"
        )
    
    def _compute_trend(self, metric_name: str, window: int = 10) -> float:
        """
        Compute trend (slope) of metric.
        
        Args:
            metric_name: Metric name
            window: Window size for trend computation
            
        Returns:
            Trend (slope)
        """
        if metric_name not in self.metrics:
            return 0.0
        
        history = self.metrics[metric_name]
        if len(history.values) < window:
            return 0.0
        
        # Use linear regression on recent values
        recent_values = history.values[-window:]
        recent_times = [(t - history.timestamps[-window]).total_seconds() for t in history.timestamps[-window:]]
        
        if len(recent_values) < 2:
            return 0.0
        
        # Simple linear regression
        x = np.array(recent_times)
        y = np.array(recent_values)
        
        if np.std(x) == 0:
            return 0.0
        
        slope = np.cov(x, y)[0, 1] / np.var(x)
        return float(slope)
    
    def get_metric_statistics(self, metric_name: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a metric."""
        if metric_name not in self.metrics:
            return None
        
        stats = self.metrics[metric_name].get_statistics()
        trend = self._compute_trend(metric_name)
        
        return {
            **stats,
            'trend': trend,
            'recent_values': self.metrics[metric_name].values[-10:] if len(self.metrics[metric_name].values) > 0 else []
        }
    
    def get_all_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all metrics."""
        return {
            name: self.get_metric_statistics(name)
            for name in self.metrics.keys()
        }
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent alerts."""
        return self.alerts[-limit:]
    
    def clear_alerts(self) -> None:
        """Clear all alerts."""
        self.alerts.clear()
        self.logger.log("Alerts cleared", level="INFO")

