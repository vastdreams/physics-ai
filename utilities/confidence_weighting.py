"""
Confidence Weighting System.

Inspired by DREAM architecture - w_confidence(t) for down-weighting uncertain expansions.

First Principle Analysis:
- Confidence weights: w_i(t) in [0, 1] for each expansion i
- Variance-based: w_i = f(variance_i) where f is decreasing function
- Time-dependent: w_i(t) can change as data arrives
- Mathematical foundation: Weighted averaging, uncertainty propagation
- Architecture: Modular weighting with multiple strategies
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np

from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_LOW_CONFIDENCE_THRESHOLD = 0.5


@dataclass
class ConfidenceWeight:
    """Represents a confidence weight for a named expansion."""

    name: str
    weight: float  # w in [0, 1]
    variance: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConfidenceWeighting:
    """Confidence weighting system for uncertain expansions.

    Features:
    - Variance-based weighting
    - Time-dependent weights
    - Multiple weighting strategies
    - Automatic down-weighting of uncertain data
    """

    def __init__(self) -> None:
        """Initialize confidence weighting system."""
        self._logger = SystemLogger()
        self.weights: Dict[str, ConfidenceWeight] = {}
        self.default_variance_threshold = 1.0

        self._logger.log("ConfidenceWeighting initialized", level="INFO")

    # ------------------------------------------------------------------
    # Core computation
    # ------------------------------------------------------------------

    def compute_weight(
        self,
        variance: float,
        variance_threshold: Optional[float] = None,
        strategy: str = "exponential",
    ) -> float:
        """Compute confidence weight from variance.

        Mathematical:
        - Exponential: w = exp(-lambda * variance)
        - Linear: w = max(0, 1 - variance / threshold)
        - Inverse: w = 1 / (1 + variance)

        Args:
            variance: Variance value.
            variance_threshold: Threshold for linear strategy.
            strategy: Weighting strategy name.

        Returns:
            Confidence weight w in [0, 1].
        """
        if variance_threshold is None:
            variance_threshold = self.default_variance_threshold

        if strategy == "exponential":
            lambda_decay = 1.0 / variance_threshold
            weight = np.exp(-lambda_decay * variance)
        elif strategy == "linear":
            weight = max(0.0, 1.0 - variance / variance_threshold)
        elif strategy == "inverse":
            weight = 1.0 / (1.0 + variance)
        else:
            weight = 1.0

        return float(np.clip(weight, 0.0, 1.0))

    # ------------------------------------------------------------------
    # Weight management
    # ------------------------------------------------------------------

    def set_weight(
        self,
        name: str,
        variance: float,
        strategy: str = "exponential",
    ) -> None:
        """Set confidence weight for an expansion.

        Args:
            name: Expansion name.
            variance: Variance value.
            strategy: Weighting strategy.
        """
        weight = self.compute_weight(variance, strategy=strategy)

        self.weights[name] = ConfidenceWeight(
            name=name,
            weight=weight,
            variance=variance,
        )

        self._logger.log(
            f"Confidence weight set: {name} = {weight:.4f} (variance={variance:.4f})",
            level="DEBUG",
        )

    def get_weight(self, name: str, default: float = 1.0) -> float:
        """Get confidence weight by name."""
        if name in self.weights:
            return self.weights[name].weight
        return default

    def apply_weights(self, values: Dict[str, float]) -> Dict[str, float]:
        """Apply confidence weights to values.

        Mathematical: weighted_value = w_i * value_i

        Args:
            values: Dictionary of name -> value.

        Returns:
            Dictionary of name -> weighted value.
        """
        return {
            name: self.get_weight(name, default=1.0) * value
            for name, value in values.items()
        }

    def update_weight(
        self,
        name: str,
        new_variance: float,
        strategy: str = "exponential",
    ) -> None:
        """Update confidence weight based on new variance.

        Args:
            name: Expansion name.
            new_variance: New variance observation.
            strategy: Weighting strategy.
        """
        if name in self.weights:
            old_variance = self.weights[name].variance
            combined_variance = (old_variance + new_variance) / 2.0
            self.set_weight(name, combined_variance, strategy)
        else:
            self.set_weight(name, new_variance, strategy)

    def get_all_weights(self) -> Dict[str, float]:
        """Get all confidence weights as ``{name: weight}``."""
        return {name: cw.weight for name, cw in self.weights.items()}

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def get_statistics(self) -> Dict[str, Any]:
        """Get weighting statistics."""
        if not self.weights:
            return {}

        weights_list = [w.weight for w in self.weights.values()]
        variances_list = [w.variance for w in self.weights.values()]

        return {
            "num_weights": len(self.weights),
            "avg_weight": float(np.mean(weights_list)),
            "min_weight": float(np.min(weights_list)),
            "max_weight": float(np.max(weights_list)),
            "avg_variance": float(np.mean(variances_list)),
            "low_confidence_count": sum(
                1 for w in weights_list if w < _LOW_CONFIDENCE_THRESHOLD
            ),
        }
