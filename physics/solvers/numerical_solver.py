"""
PATH: physics/solvers/numerical_solver.py
PURPOSE: Numerical methods for solving physics equations

Provides root finding (Newton-Raphson) and numerical integration
(Simpson's rule) for physics computations.

DEPENDENCIES:
- numpy: Numerical computation
- validators.data_validator: Input validation
- loggers.system_logger: Structured logging
"""

from typing import Callable, Tuple

import numpy as np

from loggers.system_logger import SystemLogger
from validators.data_validator import DataValidator

# Numerical tolerance for derivative near-zero check
_DERIVATIVE_ZERO_TOL: float = 1e-10


class NumericalSolver:
    """
    Numerical solver for physics equations.

    Provides Newton-Raphson root finding and Simpson's rule integration.
    """

    def __init__(self) -> None:
        """Initialize numerical solver."""
        self.validator = DataValidator()
        self._logger = SystemLogger()

        self._logger.log("NumericalSolver initialized", level="INFO")

    def newton_raphson(self,
                       function: Callable[[float], float],
                       derivative: Callable[[float], float],
                       initial_guess: float,
                       tolerance: float = 1e-10,
                       max_iterations: int = 100) -> Tuple[float, bool]:
        """
        Solve f(x) = 0 using Newton-Raphson iteration.

        Algorithm: x_{n+1} = x_n - f(x_n) / f'(x_n)

        Args:
            function: Function f(x)
            derivative: Derivative f'(x)
            initial_guess: Initial guess x₀
            tolerance: Convergence tolerance
            max_iterations: Maximum iterations

        Returns:
            Tuple of (root, converged)
        """
        x = initial_guess

        for i in range(max_iterations):
            f_x = function(x)
            f_prime_x = derivative(x)

            if abs(f_prime_x) < _DERIVATIVE_ZERO_TOL:
                self._logger.log("Derivative too small", level="WARNING")
                return x, False

            x_new = x - f_x / f_prime_x

            if abs(x_new - x) < tolerance:
                self._logger.log(f"Newton-Raphson converged: {i + 1} iterations", level="INFO")
                return x_new, True

            x = x_new

        self._logger.log("Newton-Raphson did not converge", level="WARNING")
        return x, False

    def numerical_integration(self,
                               function: Callable[[float], float],
                               lower_bound: float,
                               upper_bound: float,
                               num_points: int = 100) -> float:
        """
        Compute numerical integral using Simpson's rule.

        Algorithm: ∫_a^b f(x)dx ≈ (h/3)[f(x₀) + 4f(x₁) + 2f(x₂) + ... + f(x_n)]

        Args:
            function: Function to integrate
            lower_bound: Lower bound a
            upper_bound: Upper bound b
            num_points: Number of integration points

        Returns:
            Integral value
        """
        if num_points % 2 == 0:
            num_points += 1  # Simpson's rule needs odd number

        x = np.linspace(lower_bound, upper_bound, num_points)
        y = np.array([function(xi) for xi in x])

        h = (upper_bound - lower_bound) / (num_points - 1)

        integral = (h / 3) * (y[0] + y[-1] + 4 * np.sum(y[1:-1:2]) + 2 * np.sum(y[2:-1:2]))

        self._logger.log(f"Numerical integration: I = {integral}", level="DEBUG")
        return integral
