# utilities/
"""
Confidence Weighting System.

Inspired by DREAM architecture - w_confidence(t) for down-weighting uncertain expansions.

First Principle Analysis:
- Confidence weights: w_i(t) ∈ [0, 1] for each expansion i
- Variance-based: w_i = f(σ²_i) where f is decreasing function
- Time-dependent: w_i(t) can change as data arrives
- Mathematical foundation: Weighted averaging, uncertainty propagation
- Architecture: Modular weighting with multiple strategies
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel


@dataclass
class ConfidenceWeight:
    """Represents a confidence weight."""
    name: str
    weight: float  # w ∈ [0, 1]
    variance: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConfidenceWeighting:
    """
    Confidence weighting system for uncertain expansions.
    
    Features:
    - Variance-based weighting
    - Time-dependent weights
    - Multiple weighting strategies
    - Automatic down-weighting of uncertain data
    """
    
    def __init__(self):
        """Initialize confidence weighting system."""
        self.logger = SystemLogger()
        self.weights: Dict[str, ConfidenceWeight] = {}
        self.default_variance_threshold = 1.0
        
        self.logger.log("ConfidenceWeighting initialized", level="INFO")
    
    def compute_weight(self,
                      variance: float,
                      variance_threshold: Optional[float] = None,
                      strategy: str = "exponential") -> float:
        """
        Compute confidence weight from variance.
        
        Mathematical:
        - Exponential: w = exp(-λ × σ²)
        - Linear: w = max(0, 1 - σ²/σ²_threshold)
        - Inverse: w = 1 / (1 + σ²)
        
        Args:
            variance: Variance σ²
            variance_threshold: Threshold for linear strategy
            strategy: Weighting strategy
            
        Returns:
            Confidence weight w ∈ [0, 1]
        """
        if variance_threshold is None:
            variance_threshold = self.default_variance_threshold
        
        if strategy == "exponential":
            # w = exp(-λ × σ²) where λ controls decay rate
            lambda_decay = 1.0 / variance_threshold
            weight = np.exp(-lambda_decay * variance)
        
        elif strategy == "linear":
            # w = max(0, 1 - σ²/σ²_threshold)
            weight = max(0.0, 1.0 - variance / variance_threshold)
        
        elif strategy == "inverse":
            # w = 1 / (1 + σ²)
            weight = 1.0 / (1.0 + variance)
        
        else:
            weight = 1.0
        
        return float(np.clip(weight, 0.0, 1.0))
    
    def set_weight(self,
                   name: str,
                   variance: float,
                   strategy: str = "exponential") -> None:
        """
        Set confidence weight for an expansion.
        
        Args:
            name: Expansion name
            variance: Variance
            strategy: Weighting strategy
        """
        weight = self.compute_weight(variance, strategy=strategy)
        
        confidence_weight = ConfidenceWeight(
            name=name,
            weight=weight,
            variance=variance
        )
        
        self.weights[name] = confidence_weight
        
        self.logger.log(
            f"Confidence weight set: {name} = {weight:.4f} (variance={variance:.4f})",
            level="DEBUG"
        )
    
    def get_weight(self, name: str, default: float = 1.0) -> float:
        """Get confidence weight."""
        if name in self.weights:
            return self.weights[name].weight
        return default
    
    def apply_weights(self, values: Dict[str, float]) -> Dict[str, float]:
        """
        Apply confidence weights to values.
        
        Mathematical: weighted_value = w_i × value_i
        
        Args:
            values: Dictionary of values
            
        Returns:
            Weighted values
        """
        weighted = {}
        
        for name, value in values.items():
            weight = self.get_weight(name, default=1.0)
            weighted[name] = weight * value
        
        return weighted
    
    def update_weight(self,
                     name: str,
                     new_variance: float,
                     strategy: str = "exponential") -> None:
        """
        Update confidence weight based on new variance.
        
        Args:
            name: Expansion name
            new_variance: New variance
            strategy: Weighting strategy
        """
        if name in self.weights:
            # Time-weighted update
            old_weight = self.weights[name].weight
            old_variance = self.weights[name].variance
            
            # Combine old and new (could use Bayesian update)
            combined_variance = (old_variance + new_variance) / 2.0
            
            self.set_weight(name, combined_variance, strategy)
        else:
            self.set_weight(name, new_variance, strategy)
    
    def get_all_weights(self) -> Dict[str, float]:
        """Get all confidence weights."""
        return {name: weight.weight for name, weight in self.weights.items()}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get weighting statistics."""
        if not self.weights:
            return {}
        
        weights_list = [w.weight for w in self.weights.values()]
        variances_list = [w.variance for w in self.weights.values()]
        
        return {
            'num_weights': len(self.weights),
            'avg_weight': float(np.mean(weights_list)),
            'min_weight': float(np.min(weights_list)),
            'max_weight': float(np.max(weights_list)),
            'avg_variance': float(np.mean(variances_list)),
            'low_confidence_count': sum(1 for w in weights_list if w < 0.5)
        }

