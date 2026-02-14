"""
PATH: physics/solvers/perturbation_solver.py
PURPOSE: Perturbation theory solver for equations with small parameters

Implements regular perturbation expansion:
    x(ε) = x₀ + ε·x₁ + ε²·x₂ + ...

DEPENDENCIES:
- numpy: Numerical computation
- validators.data_validator: Input validation
- loggers.system_logger: Structured logging
"""

from typing import Callable

import numpy as np

from loggers.system_logger import SystemLogger
from validators.data_validator import DataValidator


class PerturbationSolver:
    """
    Perturbation theory solver.

    Solves equations using perturbation expansions where a small
    parameter ε allows series approximation around a known solution.
    """

    def __init__(self) -> None:
        """Initialize perturbation solver."""
        self.validator = DataValidator()
        self._logger = SystemLogger()

        self._logger.log("PerturbationSolver initialized", level="INFO")

    def regular_perturbation(self,
                             unperturbed_solution: Callable,
                             perturbation: Callable,
                             epsilon: float,
                             order: int = 2) -> Callable:
        """
        Compute regular perturbation expansion.

        Algorithm: x(ε) = x₀ + ε·x₁ + ε²·x₂ + ...
        Currently implements first-order correction only.

        Args:
            unperturbed_solution: Zeroth order solution x₀(t)
            perturbation: First order correction x₁(t)
            epsilon: Small parameter ε
            order: Expansion order (reserved for higher-order expansion)

        Returns:
            Perturbed solution function
        """
        def perturbed_solution(t: float) -> float:
            x0 = unperturbed_solution(t)
            x1 = perturbation(t)
            return x0 + epsilon * x1

        self._logger.log(f"Regular perturbation: order {order}", level="DEBUG")
        return perturbed_solution
