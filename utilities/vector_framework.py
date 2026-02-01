# utilities/
"""
VECTOR Framework: Variance-Enhanced Computational Tuning for Optimized Responses.

Inspired by DREAM medical architecture Section 4.3.3.6.

First Principle Analysis:
- Variance throttling: V_obs = Σ σ²_δi, throttle if V_obs > V_max
- Bayesian updates: μ_post = (σ²_post/σ²_prior)μ_prior + (σ²_post/σ²_data)x
- Multi-Head Attention: α_ij = exp(score - λσ²_j) / Σ exp(score - λσ²_m)
- Overlay validation: Compare simple (A+B) vs complex (C+D+E) models
- Mathematical foundation: Bayesian inference, attention mechanisms, variance control
- Architecture: Hierarchical system with C2 center, base model, expansions
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel


@dataclass
class DeltaFactor:
    """Represents a δ-factor with variance."""
    name: str
    value: float
    variance: float = 0.0
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class VECTORFramework:
    """
    VECTOR Framework implementation.
    
    Features:
    - Variance throttling
    - Bayesian parameter updates
    - Multi-Head Attention for data weighting
    - Overlay validation (simple vs complex models)
    """
    
    def __init__(self, v_max: float = 100.0, lambda_penalty: float = 1.0):
        """
        Initialize VECTOR framework.
        
        Args:
            v_max: Maximum allowed variance
            lambda_penalty: Penalty factor for MHA uncertainty
        """
        self.logger = SystemLogger()
        self.v_max = v_max
        self.lambda_penalty = lambda_penalty
        self.delta_factors: Dict[str, DeltaFactor] = {}
        self.synergy_weights: Dict[Tuple[str, str], float] = {}
        
        self.logger.log(f"VECTORFramework initialized (v_max={v_max})", level="INFO")
    
    def add_delta_factor(self, delta: DeltaFactor) -> None:
        """Add a δ-factor."""
        self.delta_factors[delta.name] = delta
        self.logger.log(f"Delta factor added: {delta.name} = {delta.value} ± {delta.variance}", level="DEBUG")
    
    def compute_observed_variance(self) -> float:
        """
        Compute total observed variance.
        
        Mathematical: V_obs = Σ σ²_δi
        
        Returns:
            Total variance
        """
        v_obs = sum(delta.variance**2 for delta in self.delta_factors.values())
        return v_obs
    
    def throttle_variance(self) -> Dict[str, float]:
        """
        Throttle variance if V_obs > V_max.
        
        Mathematical: σ_throttle = σ × (V_max / V_obs)
        
        Returns:
            Dictionary of throttled variances
        """
        v_obs = self.compute_observed_variance()
        
        if v_obs <= self.v_max:
            return {name: delta.variance for name, delta in self.delta_factors.items()}
        
        throttle_factor = self.v_max / v_obs
        throttled = {}
        
        for name, delta in self.delta_factors.items():
            throttled_variance = delta.variance * throttle_factor
            throttled[name] = throttled_variance
            
            self.logger.log(
                f"Variance throttled: {name} {delta.variance} -> {throttled_variance}",
                level="WARNING"
            )
        
        return throttled
    
    def bayesian_update(self,
                       prior_mean: float,
                       prior_variance: float,
                       data_value: float,
                       data_variance: float) -> Tuple[float, float]:
        """
        Bayesian parameter update.
        
        Mathematical:
        - σ²_post = 1 / (1/σ²_prior + 1/σ²_data)
        - μ_post = σ²_post × (μ_prior/σ²_prior + x/σ²_data)
        
        Args:
            prior_mean: Prior mean μ_prior
            prior_variance: Prior variance σ²_prior
            data_value: Data value x
            data_variance: Data variance σ²_data
            
        Returns:
            Tuple of (posterior_mean, posterior_variance)
        """
        if prior_variance <= 0 or data_variance <= 0:
            return prior_mean, prior_variance
        
        posterior_variance = 1.0 / (1.0 / prior_variance + 1.0 / data_variance)
        posterior_mean = posterior_variance * (prior_mean / prior_variance + data_value / data_variance)
        
        self.logger.log(
            f"Bayesian update: μ = {posterior_mean:.4f}, σ² = {posterior_variance:.4f}",
            level="DEBUG"
        )
        
        return posterior_mean, posterior_variance
    
    def multi_head_attention(self,
                            queries: List[np.ndarray],
                            keys: List[np.ndarray],
                            values: List[np.ndarray],
                            variances: List[float],
                            num_heads: int = 4) -> Tuple[np.ndarray, List[float]]:
        """
        Multi-Head Attention with variance penalty.
        
        Mathematical:
        - score_ij = Q_i · K_j - λ × σ²_j
        - α_ij = exp(score_ij) / Σ_m exp(score_im)
        
        Args:
            queries: List of query vectors
            keys: List of key vectors
            values: List of value vectors
            variances: List of variances for penalty
            num_heads: Number of attention heads
            
        Returns:
            Tuple of (attention_output, attention_weights)
        """
        if len(queries) != len(keys) or len(keys) != len(values):
            raise ValueError("Queries, keys, and values must have same length")
        
        if len(variances) != len(queries):
            raise ValueError("Variances must match queries length")
        
        # Compute attention scores with variance penalty
        scores = []
        for i, (q, k, v) in enumerate(zip(queries, keys, values)):
            base_score = np.dot(q, k)
            penalty = self.lambda_penalty * variances[i]**2
            score = base_score - penalty
            scores.append(score)
        
        # Softmax
        scores_array = np.array(scores)
        exp_scores = np.exp(scores_array - np.max(scores_array))  # Numerical stability
        attention_weights = exp_scores / np.sum(exp_scores)
        
        # Weighted sum of values
        attention_output = np.sum([w * v for w, v in zip(attention_weights, values)], axis=0)
        
        self.logger.log(
            f"MHA computed: {len(queries)} inputs, max_weight={np.max(attention_weights):.4f}",
            level="DEBUG"
        )
        
        return attention_output, attention_weights.tolist()
    
    def overlay_validation(self,
                          simple_output: Dict[str, Any],
                          complex_output: Dict[str, Any],
                          epsilon_limit: float = 0.1) -> Tuple[bool, float]:
        """
        Validate complex model against simple baseline.
        
        Mathematical: Δ_var = |X - Y| where X = simple, Y = complex
        
        Args:
            simple_output: Output from simple model (A+B)
            complex_output: Output from complex model (C+D+E)
            epsilon_limit: Maximum allowed deviation
            
        Returns:
            Tuple of (is_valid, deviation)
        """
        # Compute deviation (simplified - would compare actual outputs)
        deviation = 0.0
        
        # Compare common keys
        common_keys = set(simple_output.keys()) & set(complex_output.keys())
        for key in common_keys:
            if isinstance(simple_output[key], (int, float)) and isinstance(complex_output[key], (int, float)):
                deviation += abs(complex_output[key] - simple_output[key])
        
        is_valid = deviation <= epsilon_limit
        
        if not is_valid:
            self.logger.log(
                f"Overlay validation failed: Δ = {deviation} > {epsilon_limit}",
                level="WARNING"
            )
        else:
            self.logger.log(
                f"Overlay validation passed: Δ = {deviation} ≤ {epsilon_limit}",
                level="DEBUG"
            )
        
        return is_valid, deviation
    
    def update_delta_with_bayesian(self,
                                   delta_name: str,
                                   new_data_value: float,
                                   new_data_variance: float) -> None:
        """
        Update δ-factor using Bayesian inference.
        
        Args:
            delta_name: Name of δ-factor
            new_data_value: New data value
            new_data_variance: New data variance
        """
        if delta_name not in self.delta_factors:
            self.logger.log(f"Delta factor not found: {delta_name}", level="WARNING")
            return
        
        delta = self.delta_factors[delta_name]
        
        # Bayesian update
        posterior_mean, posterior_variance = self.bayesian_update(
            prior_mean=delta.value,
            prior_variance=delta.variance**2 if delta.variance > 0 else 1.0,
            data_value=new_data_value,
            data_variance=new_data_variance
        )
        
        # Update delta
        delta.value = posterior_mean
        delta.variance = np.sqrt(posterior_variance)
        
        self.logger.log(
            f"Delta factor updated: {delta_name} = {delta.value:.4f} ± {delta.variance:.4f}",
            level="INFO"
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get VECTOR framework statistics."""
        v_obs = self.compute_observed_variance()
        is_throttled = v_obs > self.v_max
        
        return {
            'observed_variance': v_obs,
            'max_variance': self.v_max,
            'is_throttled': is_throttled,
            'throttle_factor': self.v_max / v_obs if is_throttled else 1.0,
            'num_delta_factors': len(self.delta_factors),
            'lambda_penalty': self.lambda_penalty
        }

