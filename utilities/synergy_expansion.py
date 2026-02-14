"""
Synergy Expansion Engine with Interaction Terms.

Inspired by DREAM architecture - advanced synergy calculations with interaction terms.

First Principle Analysis:
- Synergy: S_net = Sum(S_i) + Sum(w_ij * S_i * S_j) (interaction terms)
- Log-space: log(S) = Sum(log(1+delta_i)) + Sum(w_ij * delta_i * delta_j)
- Regularization: Group-lasso for sparse synergy
- Mathematical foundation: Synergy matrices, interaction terms, regularization
- Architecture: Modular expansion engine with validation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from utilities.vector_framework import VECTORFramework, DeltaFactor

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_BASE_VALUE_MIN = -1.0
_BASE_VALUE_MAX = 10.0
_MAX_INTERACTION_WEIGHT = 10.0
_DEFAULT_REGULARIZATION_LAMBDA = 0.1


@dataclass
class SynergyExpansion:
    """Represents a synergy expansion."""

    name: str
    base_value: float
    delta_factors: List[str] = field(default_factory=list)
    interaction_terms: Dict[Tuple[str, str], float] = field(default_factory=dict)
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class SynergyExpansionEngine:
    """Synergy expansion engine with interaction terms.

    Features:
    - Base expansions: S_i
    - Interaction terms: w_ij * S_i * S_j
    - Log-space calculations
    - Regularization (group-lasso)
    - Validation against first-principles
    """

    def __init__(self) -> None:
        """Initialize synergy expansion engine."""
        self._logger = SystemLogger()
        self.vector = VECTORFramework()
        self.expansions: Dict[str, SynergyExpansion] = {}
        self.interaction_matrix: Dict[Tuple[str, str], float] = {}

        self._logger.log("SynergyExpansionEngine initialized", level="INFO")

    def add_expansion(self, expansion: SynergyExpansion) -> None:
        """Add a synergy expansion and register its interaction terms."""
        self.expansions[expansion.name] = expansion

        for (factor1, factor2), weight in expansion.interaction_terms.items():
            self.interaction_matrix[(factor1, factor2)] = weight

        self._logger.log(f"Synergy expansion added: {expansion.name}", level="INFO")

    def compute_net_synergy(
        self,
        expansion_names: List[str],
        delta_values: Dict[str, float],
        use_log_space: bool = True,
    ) -> float:
        """Compute net synergy from multiple expansions.

        Mathematical:
        - Linear:    S_net = Sum(S_i) + Sum(w_ij * S_i * S_j)
        - Log-space: log(S_net) = Sum(log(1+delta_i)) + Sum(w_ij * delta_i * delta_j)

        Args:
            expansion_names: List of expansion names to include.
            delta_values: Dictionary of delta-factor values.
            use_log_space: Whether to use log-space calculations.

        Returns:
            Net synergy value.
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="COMPUTE_NET_SYNERGY",
            input_data={"expansions": expansion_names, "use_log_space": use_log_space},
            level=LogLevel.INFO,
        )

        try:
            if use_log_space:
                net_synergy = self._compute_log_space(expansion_names, delta_values)
            else:
                net_synergy = self._compute_linear(expansion_names, delta_values)

            cot.end_step(
                step_id,
                output_data={"net_synergy": net_synergy},
                validation_passed=True,
            )
            self._logger.log(f"Net synergy computed: {net_synergy:.4f}", level="DEBUG")
            return float(net_synergy)

        except Exception as e:
            cot.end_step(step_id, output_data={"error": str(e)}, validation_passed=False)
            self._logger.log(f"Error computing net synergy: {e}", level="ERROR")
            raise

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _compute_log_space(
        self,
        expansion_names: List[str],
        delta_values: Dict[str, float],
    ) -> float:
        """Compute synergy in log-space."""
        log_synergy = 0.0

        for expansion_name in expansion_names:
            if expansion_name in self.expansions:
                expansion = self.expansions[expansion_name]
                for delta_name in expansion.delta_factors:
                    if delta_name in delta_values:
                        log_synergy += np.log(1.0 + delta_values[delta_name])

        log_synergy += self._interaction_sum(delta_values)
        return float(np.exp(log_synergy))

    def _compute_linear(
        self,
        expansion_names: List[str],
        delta_values: Dict[str, float],
    ) -> float:
        """Compute synergy in linear space."""
        net_synergy = 0.0

        for expansion_name in expansion_names:
            if expansion_name in self.expansions:
                net_synergy += self.expansions[expansion_name].base_value

        for (name1, name2), weight in self.interaction_matrix.items():
            if name1 in delta_values and name2 in delta_values:
                net_synergy += weight * delta_values[name1] * delta_values[name2]

        return net_synergy

    def _interaction_sum(self, delta_values: Dict[str, float]) -> float:
        """Compute pairwise interaction sum: Sum(w_ij * delta_i * delta_j)."""
        interaction = 0.0
        delta_list = list(delta_values.items())
        for i, (name1, value1) in enumerate(delta_list):
            for j, (name2, value2) in enumerate(delta_list):
                if i < j:
                    weight = self.interaction_matrix.get((name1, name2), 0.0)
                    interaction += weight * value1 * value2
        return interaction

    # ------------------------------------------------------------------
    # Regularization
    # ------------------------------------------------------------------

    def apply_group_lasso_regularization(
        self,
        lambda_reg: float = _DEFAULT_REGULARIZATION_LAMBDA,
    ) -> Dict[Tuple[str, str], float]:
        """Apply group-lasso regularization to interaction terms.

        Zeroes out interaction terms whose absolute weight falls below *lambda_reg*.

        Args:
            lambda_reg: Regularization parameter.

        Returns:
            Regularized interaction matrix.
        """
        regularized: Dict[Tuple[str, str], float] = {}

        for (name1, name2), weight in self.interaction_matrix.items():
            if abs(weight) >= lambda_reg:
                regularized[(name1, name2)] = weight
            else:
                self._logger.log(
                    f"Regularized out interaction: {name1}-{name2} "
                    f"(weight={weight:.4f} < {lambda_reg})",
                    level="DEBUG",
                )

        self.interaction_matrix = regularized
        return regularized

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_expansion(
        self, expansion_name: str, context: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Validate expansion against first-principles.

        Args:
            expansion_name: Expansion name.
            context: Validation context.

        Returns:
            Tuple of (is_valid, violations).
        """
        if expansion_name not in self.expansions:
            return False, ["Expansion not found"]

        expansion = self.expansions[expansion_name]
        violations: List[str] = []

        if expansion.base_value < _BASE_VALUE_MIN or expansion.base_value > _BASE_VALUE_MAX:
            violations.append(f"Base value out of range: {expansion.base_value}")

        for (name1, name2), weight in expansion.interaction_terms.items():
            if abs(weight) > _MAX_INTERACTION_WEIGHT:
                violations.append(f"Large interaction term: {name1}-{name2} = {weight}")

        is_valid = len(violations) == 0

        if is_valid:
            self._logger.log(f"Expansion validated: {expansion_name}", level="DEBUG")
        else:
            self._logger.log(
                f"Expansion validation failed: {expansion_name} - {violations}",
                level="WARNING",
            )

        return is_valid, violations

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def get_statistics(self) -> Dict[str, Any]:
        """Get expansion statistics."""
        num_interactions = len(self.interaction_matrix)
        avg_interaction = (
            float(np.mean([abs(w) for w in self.interaction_matrix.values()]))
            if num_interactions > 0
            else 0.0
        )

        return {
            "num_expansions": len(self.expansions),
            "num_interactions": num_interactions,
            "avg_interaction_strength": avg_interaction,
        }
