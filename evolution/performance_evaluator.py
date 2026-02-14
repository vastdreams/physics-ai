"""
Performance evaluation module.

Evaluates system performance to guide evolution.
"""

from __future__ import annotations

from typing import Any, Dict

from loggers.performance_logger import PerformanceLogger
from loggers.system_logger import SystemLogger

# ---------------------------------------------------------------------------
# Score thresholds for recommendations
# ---------------------------------------------------------------------------
_EXCELLENT_THRESHOLD = 0.8
_GOOD_THRESHOLD = 0.6
_NEEDS_IMPROVEMENT_THRESHOLD = 0.4


class PerformanceEvaluator:
    """Evaluates system performance and provides recommendations."""

    def __init__(self) -> None:
        """Initialize performance evaluator."""
        self._logger = SystemLogger()
        self.performance_logger = PerformanceLogger()

        self._logger.log("PerformanceEvaluator initialized", level="INFO")

    def evaluate(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Evaluate performance metrics.

        Args:
            metrics: Dictionary of metric names to values.

        Returns:
            Evaluation results containing score, metrics, and recommendation.
        """
        self._logger.log("Evaluating performance", level="DEBUG")

        for metric_name, value in metrics.items():
            self.performance_logger.log_metric(metric_name, value)

        score = sum(metrics.values()) / len(metrics) if metrics else 0.0

        result: Dict[str, Any] = {
            "score": score,
            "metrics": metrics,
            "recommendation": self._get_recommendation(score),
        }

        self._logger.log(f"Performance evaluation complete: score={score}", level="INFO")
        return result

    @staticmethod
    def _get_recommendation(score: float) -> str:
        """Get recommendation based on score."""
        if score > _EXCELLENT_THRESHOLD:
            return "excellent"
        if score > _GOOD_THRESHOLD:
            return "good"
        if score > _NEEDS_IMPROVEMENT_THRESHOLD:
            return "needs_improvement"
        return "poor"
