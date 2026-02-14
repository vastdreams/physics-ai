"""
PATH: physics/validation/physics_validator.py
PURPOSE: Unified validation against first-principles physics constraints

Checks conservation laws (energy, momentum, angular momentum),
symmetries, causality (v < c), and unitarity (|ψ|² = 1).

DEPENDENCIES:
- numpy: Numerical computation
- validators.data_validator: Input validation
- loggers.system_logger: Structured logging
- physics.foundations: Conservation, symmetry, and constraint modules
"""

from typing import Any, Dict, List, Tuple

import numpy as np

from loggers.system_logger import SystemLogger
from physics.foundations.conservation_laws import ConservationLaws
from physics.foundations.constraints import PhysicsConstraints
from physics.foundations.symmetries import SymmetryChecker
from validators.data_validator import DataValidator


class PhysicsValidator:
    """
    Unified physics constraint validator.

    Validates theories and simulation outputs against conservation
    laws, symmetries, causality, and unitarity.
    """

    def __init__(self) -> None:
        """Initialize physics validator."""
        self.validator = DataValidator()
        self._logger = SystemLogger()
        self.conservation = ConservationLaws()
        self.symmetry = SymmetryChecker()
        self.constraints = PhysicsConstraints()

        self._logger.log("PhysicsValidator initialized", level="INFO")

    def validate_system(self,
                        initial_state: Dict[str, Any],
                        final_state: Dict[str, Any],
                        external_forces: Dict[str, Any] | None = None) -> Dict[str, Tuple[bool, Any]]:
        """
        Validate complete physical system against conservation and constraints.

        Args:
            initial_state: Initial system state
            final_state: Final system state
            external_forces: External forces/torques (if any)

        Returns:
            Dictionary mapping check name to (is_valid, details)
        """
        results: Dict[str, Tuple[bool, Any]] = {}

        conservation_results = self.conservation.validate_system(
            initial_state, final_state, external_forces
        )
        results.update(conservation_results)

        constraint_results = self.constraints.validate_system(final_state)
        results.update(constraint_results)

        all_valid = all(is_valid for is_valid, _ in results.values())

        if all_valid:
            self._logger.log("System validation passed", level="INFO")
        else:
            self._logger.log("System validation failed", level="WARNING")

        return results

    def validate_theory(self,
                         theory_output: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate theory output for physical consistency.

        Checks energy positivity, causality (v < c), and
        unitarity (wave function normalization).

        Args:
            theory_output: Theory output dictionary

        Returns:
            Tuple of (is_valid, list of violations)
        """
        violations: List[str] = []

        if 'energy' in theory_output:
            is_positive, _ = self.constraints.check_energy_positivity(theory_output['energy'])
            if not is_positive:
                violations.append("Energy positivity violation")

        if 'velocity' in theory_output:
            is_causal, _ = self.constraints.check_causality(theory_output['velocity'])
            if not is_causal:
                violations.append("Causality violation")

        if 'wave_function' in theory_output:
            is_unitary, _ = self.constraints.check_unitarity(theory_output['wave_function'])
            if not is_unitary:
                violations.append("Unitarity violation")

        is_valid = len(violations) == 0

        if is_valid:
            self._logger.log("Theory validation passed", level="INFO")
        else:
            self._logger.log(f"Theory validation failed: {violations}", level="WARNING")

        return is_valid, violations
