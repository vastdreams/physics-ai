"""
VECTOR Framework Integration with Enhanced Rule Engine.

Integrates VECTOR for uncertainty-aware rule execution.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from loggers.system_logger import SystemLogger
from rules.enhanced_rule_engine import EnhancedRule, EnhancedRuleEngine
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from utilities.vector_framework import DeltaFactor, VECTORFramework

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_DEFAULT_V_MAX = 50.0
_DEFAULT_LAMBDA_PENALTY = 1.0
_DEFAULT_NUMERIC_UNCERTAINTY = 0.1


class VectorIntegratedRuleEngine(EnhancedRuleEngine):
    """Enhanced rule engine with VECTOR framework integration.

    Features:
    - Uncertainty-aware rule execution
    - Variance throttling for rule parameters
    - Bayesian updates of rule weights
    """

    def __init__(self) -> None:
        """Initialize vector-integrated rule engine."""
        super().__init__()
        self.vector = VECTORFramework(v_max=_DEFAULT_V_MAX, lambda_penalty=_DEFAULT_LAMBDA_PENALTY)
        self.logger.log("VectorIntegratedRuleEngine initialized", level="INFO")

    def execute_enhanced(
        self,
        context: Dict[str, Any],
        validate_physics: bool = True,
        use_cot: bool = True,
        use_vector: bool = True,
    ) -> List[Any]:
        """Execute rules with VECTOR framework.

        Args:
            context: Execution context.
            validate_physics: Validate physics constraints.
            use_cot: Use chain-of-thought logging.
            use_vector: Use VECTOR framework.

        Returns:
            Execution results.
        """
        cot = ChainOfThoughtLogger() if use_cot else None
        step_id: Optional[str] = None

        if cot:
            step_id = cot.start_step(
                action="VECTOR_EXECUTE_RULES",
                input_data={"context_keys": list(context.keys()), "use_vector": use_vector},
                level=LogLevel.INFO,
            )

        try:
            if use_vector:
                self._extract_uncertainty_from_context(context)
                throttled = self.vector.throttle_variance()
                if throttled:
                    self.logger.log("Rule execution variance throttled", level="WARNING")

            results = super().execute_enhanced(
                context=context,
                validate_physics=validate_physics,
                use_cot=use_cot,
            )

            if use_vector and results:
                self._update_rule_weights_from_results(results)

            if cot and step_id:
                cot.end_step(
                    step_id,
                    output_data={"results_count": len(results)},
                    validation_passed=True,
                )

            return results

        except Exception as e:
            if cot and step_id:
                cot.end_step(step_id, output_data={"error": str(e)}, validation_passed=False)
            self.logger.log(f"Error in vector rule execution: {e}", level="ERROR")
            raise

    def _extract_uncertainty_from_context(self, context: Dict[str, Any]) -> None:
        """Extract uncertainty information from context and register delta factors."""
        for key, value in context.items():
            if isinstance(value, dict) and "value" in value and "uncertainty" in value:
                self.vector.add_delta_factor(
                    DeltaFactor(name=key, value=value["value"], variance=value["uncertainty"])
                )
            elif isinstance(value, (int, float)):
                self.vector.add_delta_factor(
                    DeltaFactor(name=key, value=float(value), variance=_DEFAULT_NUMERIC_UNCERTAINTY)
                )

    def _update_rule_weights_from_results(self, results: List[Dict[str, Any]]) -> None:
        """Update rule weights based on execution results."""
        for result in results:
            rule_name = result.get("rule_name")
            success = result.get("success", False)

            if rule_name and rule_name in self.enhanced_rules:
                self._update_rule_performance(rule_name, success)
