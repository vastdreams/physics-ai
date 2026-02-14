"""
VECTOR Framework: Variance-Enhanced Computational Tuning for Optimized Responses.

Inspired by DREAM medical architecture Section 4.3.3.6.

First Principle Analysis:
- Variance throttling: V_obs = Sum(sigma^2_di), throttle if V_obs > V_max
- Bayesian updates: mu_post = (sigma^2_post / sigma^2_prior)*mu_prior
                             + (sigma^2_post / sigma^2_data)*x
- Multi-Head Attention: alpha_ij = exp(score - lambda*sigma^2_j) / Sum(exp(score - lambda*sigma^2_m))
- Overlay validation: Compare simple (A+B) vs complex (C+D+E) models
- Architecture: Hierarchical system with C2 center, base model, expansions
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from loggers.system_logger import SystemLogger

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_DEFAULT_V_MAX = 100.0
_DEFAULT_LAMBDA_PENALTY = 1.0
_DEFAULT_EPSILON_LIMIT = 0.1


@dataclass
class DeltaFactor:
    """Represents a delta-factor with variance."""

    name: str
    value: float
    variance: float = 0.0
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class VECTORFramework:
    """VECTOR Framework implementation.

    Features:
    - Variance throttling
    - Bayesian parameter updates
    - Multi-Head Attention for data weighting
    - Overlay validation (simple vs complex models)
    """

    def __init__(
        self,
        v_max: float = _DEFAULT_V_MAX,
        lambda_penalty: float = _DEFAULT_LAMBDA_PENALTY,
    ) -> None:
        """Initialize VECTOR framework.

        Args:
            v_max: Maximum allowed variance.
            lambda_penalty: Penalty factor for MHA uncertainty.
        """
        self._logger = SystemLogger()
        self.v_max = v_max
        self.lambda_penalty = lambda_penalty
        self.delta_factors: Dict[str, DeltaFactor] = {}
        self.synergy_weights: Dict[Tuple[str, str], float] = {}

        self._logger.log(f"VECTORFramework initialized (v_max={v_max})", level="INFO")

    def add_delta_factor(self, delta: DeltaFactor) -> None:
        """Add a delta-factor."""
        self.delta_factors[delta.name] = delta
        self._logger.log(
            f"Delta factor added: {delta.name} = {delta.value} +/- {delta.variance}",
            level="DEBUG",
        )

    # ------------------------------------------------------------------
    # Variance control
    # ------------------------------------------------------------------

    def compute_observed_variance(self) -> float:
        """Compute total observed variance.

        Mathematical: V_obs = Sum(sigma^2_di)

        Returns:
            Total variance.
        """
        return sum(delta.variance ** 2 for delta in self.delta_factors.values())

    def throttle_variance(self) -> Dict[str, float]:
        """Throttle variance if V_obs > V_max.

        Mathematical: sigma_throttle = sigma * (V_max / V_obs)

        Returns:
            Dictionary of throttled variances.
        """
        v_obs = self.compute_observed_variance()

        if v_obs <= self.v_max:
            return {name: delta.variance for name, delta in self.delta_factors.items()}

        throttle_factor = self.v_max / v_obs
        throttled: Dict[str, float] = {}

        for name, delta in self.delta_factors.items():
            throttled_variance = delta.variance * throttle_factor
            throttled[name] = throttled_variance
            self._logger.log(
                f"Variance throttled: {name} {delta.variance} -> {throttled_variance}",
                level="WARNING",
            )

        return throttled

    # ------------------------------------------------------------------
    # Bayesian inference
    # ------------------------------------------------------------------

    def bayesian_update(
        self,
        prior_mean: float,
        prior_variance: float,
        data_value: float,
        data_variance: float,
    ) -> Tuple[float, float]:
        """Bayesian parameter update.

        Mathematical:
        - sigma^2_post = 1 / (1/sigma^2_prior + 1/sigma^2_data)
        - mu_post = sigma^2_post * (mu_prior/sigma^2_prior + x/sigma^2_data)

        Args:
            prior_mean: Prior mean.
            prior_variance: Prior variance.
            data_value: Observed data value.
            data_variance: Data variance.

        Returns:
            Tuple of (posterior_mean, posterior_variance).
        """
        if prior_variance <= 0 or data_variance <= 0:
            return prior_mean, prior_variance

        posterior_variance = 1.0 / (1.0 / prior_variance + 1.0 / data_variance)
        posterior_mean = posterior_variance * (
            prior_mean / prior_variance + data_value / data_variance
        )

        self._logger.log(
            f"Bayesian update: mu = {posterior_mean:.4f}, sigma^2 = {posterior_variance:.4f}",
            level="DEBUG",
        )

        return posterior_mean, posterior_variance

    # ------------------------------------------------------------------
    # Multi-Head Attention
    # ------------------------------------------------------------------

    def multi_head_attention(
        self,
        queries: List[np.ndarray],
        keys: List[np.ndarray],
        values: List[np.ndarray],
        variances: List[float],
        num_heads: int = 4,
    ) -> Tuple[np.ndarray, List[float]]:
        """Multi-Head Attention with variance penalty.

        Mathematical:
        - score_ij = Q_i . K_j - lambda * sigma^2_j
        - alpha_ij = exp(score_ij) / Sum_m(exp(score_im))

        Args:
            queries: List of query vectors.
            keys: List of key vectors.
            values: List of value vectors.
            variances: List of variances for penalty.
            num_heads: Number of attention heads.

        Returns:
            Tuple of (attention_output, attention_weights).

        Raises:
            ValueError: If input lists have mismatched lengths.
        """
        if len(queries) != len(keys) or len(keys) != len(values):
            raise ValueError("Queries, keys, and values must have same length")
        if len(variances) != len(queries):
            raise ValueError("Variances must match queries length")

        scores = []
        for i, (q, k, _v) in enumerate(zip(queries, keys, values)):
            base_score = float(np.dot(q, k))
            penalty = self.lambda_penalty * variances[i] ** 2
            scores.append(base_score - penalty)

        scores_array = np.array(scores)
        exp_scores = np.exp(scores_array - np.max(scores_array))  # numerical stability
        attention_weights = exp_scores / np.sum(exp_scores)

        attention_output = np.sum(
            [w * v for w, v in zip(attention_weights, values)], axis=0
        )

        self._logger.log(
            f"MHA computed: {len(queries)} inputs, max_weight={np.max(attention_weights):.4f}",
            level="DEBUG",
        )

        return attention_output, attention_weights.tolist()

    # ------------------------------------------------------------------
    # Overlay validation
    # ------------------------------------------------------------------

    def overlay_validation(
        self,
        simple_output: Dict[str, Any],
        complex_output: Dict[str, Any],
        epsilon_limit: float = _DEFAULT_EPSILON_LIMIT,
    ) -> Tuple[bool, float]:
        """Validate complex model against simple baseline.

        Mathematical: delta_var = |X - Y| where X = simple, Y = complex

        Args:
            simple_output: Output from simple model.
            complex_output: Output from complex model.
            epsilon_limit: Maximum allowed deviation.

        Returns:
            Tuple of (is_valid, deviation).
        """
        deviation = 0.0
        common_keys = set(simple_output.keys()) & set(complex_output.keys())
        for key in common_keys:
            s_val, c_val = simple_output[key], complex_output[key]
            if isinstance(s_val, (int, float)) and isinstance(c_val, (int, float)):
                deviation += abs(c_val - s_val)

        is_valid = deviation <= epsilon_limit

        if not is_valid:
            self._logger.log(
                f"Overlay validation failed: delta = {deviation} > {epsilon_limit}",
                level="WARNING",
            )
        else:
            self._logger.log(
                f"Overlay validation passed: delta = {deviation} <= {epsilon_limit}",
                level="DEBUG",
            )

        return is_valid, deviation

    # ------------------------------------------------------------------
    # Delta-factor helpers
    # ------------------------------------------------------------------

    def update_delta_with_bayesian(
        self,
        delta_name: str,
        new_data_value: float,
        new_data_variance: float,
    ) -> None:
        """Update delta-factor using Bayesian inference.

        Args:
            delta_name: Name of delta-factor.
            new_data_value: New data value.
            new_data_variance: New data variance.
        """
        if delta_name not in self.delta_factors:
            self._logger.log(f"Delta factor not found: {delta_name}", level="WARNING")
            return

        delta = self.delta_factors[delta_name]

        posterior_mean, posterior_variance = self.bayesian_update(
            prior_mean=delta.value,
            prior_variance=delta.variance ** 2 if delta.variance > 0 else 1.0,
            data_value=new_data_value,
            data_variance=new_data_variance,
        )

        delta.value = posterior_mean
        delta.variance = float(np.sqrt(posterior_variance))

        self._logger.log(
            f"Delta factor updated: {delta_name} = {delta.value:.4f} +/- {delta.variance:.4f}",
            level="INFO",
        )

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def get_statistics(self) -> Dict[str, Any]:
        """Get VECTOR framework statistics."""
        v_obs = self.compute_observed_variance()
        is_throttled = v_obs > self.v_max

        return {
            "observed_variance": v_obs,
            "max_variance": self.v_max,
            "is_throttled": is_throttled,
            "throttle_factor": self.v_max / v_obs if is_throttled else 1.0,
            "num_delta_factors": len(self.delta_factors),
            "lambda_penalty": self.lambda_penalty,
        }
