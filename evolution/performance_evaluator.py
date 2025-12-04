# evolution/
"""
Performance evaluation module.

Evaluates system performance to guide evolution.
"""

from typing import Any, Dict, List, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loggers.system_logger import SystemLogger
from loggers.performance_logger import PerformanceLogger


class PerformanceEvaluator:
    """
    Evaluates system performance.
    """
    
    def __init__(self):
        """Initialize performance evaluator."""
        self.logger = SystemLogger()
        self.performance_logger = PerformanceLogger()
        
        self.logger.log("PerformanceEvaluator initialized", level="INFO")
    
    def evaluate(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Evaluate performance metrics.
        
        Args:
            metrics: Dictionary of metric names to values
            
        Returns:
            Evaluation results
        """
        self.logger.log("Evaluating performance", level="DEBUG")
        
        # Log metrics
        for metric_name, value in metrics.items():
            self.performance_logger.log_metric(metric_name, value)
        
        # Calculate overall score
        score = sum(metrics.values()) / len(metrics) if metrics else 0.0
        
        result = {
            "score": score,
            "metrics": metrics,
            "recommendation": self._get_recommendation(score)
        }
        
        self.logger.log(f"Performance evaluation complete: score={score}", level="INFO")
        return result
    
    def _get_recommendation(self, score: float) -> str:
        """Get recommendation based on score."""
        if score > 0.8:
            return "excellent"
        elif score > 0.6:
            return "good"
        elif score > 0.4:
            return "needs_improvement"
        else:
            return "poor"

