"""
VECTOR Framework Integration with Self-Evolution Engine.

Integrates VECTOR for safe code evolution with variance control.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from evolution.self_evolution import SelfEvolutionEngine
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from utilities.vector_framework import DeltaFactor, VECTORFramework

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_DEFAULT_V_MAX = 50.0
_DEFAULT_LAMBDA_PENALTY = 1.0
_COMPLEXITY_VARIANCE = 0.2
_PERFORMANCE_VARIANCE = 0.1
_OVERLAY_EPSILON = 0.2


class VectorIntegratedEvolutionEngine(SelfEvolutionEngine):
    """Self-evolution engine with VECTOR framework integration.

    Features:
    - Variance throttling for code generation parameters
    - Overlay validation of evolved code
    - Bayesian updates for evolution parameters
    """

    def __init__(self, graph_builder: Any = None) -> None:
        """Initialize vector-integrated evolution engine."""
        super().__init__(graph_builder)
        self.vector = VECTORFramework(v_max=_DEFAULT_V_MAX, lambda_penalty=_DEFAULT_LAMBDA_PENALTY)
        self.logger.log("VectorIntegratedEvolutionEngine initialized", level="INFO")

    def evolve_function(
        self,
        file_path: str,
        function_name: str,
        improvement_spec: Dict[str, Any],
        use_vector: bool = True,
    ) -> Tuple[bool, Optional[str]]:
        """Evolve function with VECTOR framework.

        Args:
            file_path: File path.
            function_name: Function name.
            improvement_spec: Improvement specification.
            use_vector: Use VECTOR framework.

        Returns:
            Tuple of (success, new_code).
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="VECTOR_EVOLVE_FUNCTION",
            input_data={
                "file_path": file_path,
                "function_name": function_name,
                "use_vector": use_vector,
            },
            level=LogLevel.DECISION,
        )

        try:
            if use_vector:
                self._extract_evolution_parameters(improvement_spec)
                throttled = self.vector.throttle_variance()
                if throttled:
                    self.logger.log("Evolution variance throttled", level="WARNING")

            success, new_code = super().evolve_function(
                file_path=file_path,
                function_name=function_name,
                improvement_spec=improvement_spec,
            )

            if use_vector and success and new_code:
                validation_passed = self._validate_evolved_code(file_path, new_code)
                if not validation_passed:
                    self.logger.log("Evolved code failed overlay validation", level="WARNING")
                    cot.end_step(
                        step_id,
                        output_data={"validation_passed": False},
                        validation_passed=False,
                    )
                    return False, None

            cot.end_step(
                step_id,
                output_data={"success": success, "validation_passed": True},
                validation_passed=success,
            )
            return success, new_code

        except Exception as e:
            cot.end_step(step_id, output_data={"error": str(e)}, validation_passed=False)
            self.logger.log(f"Error in vector evolution: {e}", level="ERROR")
            return False, None

    def _extract_evolution_parameters(self, improvement_spec: Dict[str, Any]) -> None:
        """Extract evolution parameters as delta factors."""
        if "complexity_target" in improvement_spec:
            self.vector.add_delta_factor(
                DeltaFactor(
                    name="complexity_change",
                    value=improvement_spec["complexity_target"],
                    variance=_COMPLEXITY_VARIANCE,
                )
            )

        if "performance_target" in improvement_spec:
            self.vector.add_delta_factor(
                DeltaFactor(
                    name="performance_target",
                    value=improvement_spec["performance_target"],
                    variance=_PERFORMANCE_VARIANCE,
                )
            )

    def _validate_evolved_code(self, file_path: str, new_code: str) -> bool:
        """Validate evolved code using overlay validation.

        Args:
            file_path: Original file path.
            new_code: New code to validate.

        Returns:
            True if validation passed.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                original_code = f.read()

            original_lines = len(original_code.splitlines())
            new_lines = len(new_code.splitlines())

            simple_output = {"lines": original_lines, "complexity": 1.0}
            complex_output = {"lines": new_lines, "complexity": 1.1}

            is_valid, _ = self.vector.overlay_validation(
                simple_output, complex_output, epsilon_limit=_OVERLAY_EPSILON
            )
            return is_valid

        except Exception as e:
            self.logger.log(f"Error validating evolved code: {e}", level="ERROR")
            return False
