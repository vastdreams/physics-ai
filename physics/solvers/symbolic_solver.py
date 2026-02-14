"""
PATH: physics/solvers/symbolic_solver.py
PURPOSE: Symbolic manipulation of physics equations via SymPy

Provides exact equation solving, symbolic differentiation, and
symbolic integration when SymPy is available.

DEPENDENCIES:
- sympy (optional): Computer algebra system
- validators.data_validator: Input validation
- loggers.system_logger: Structured logging
"""

from typing import Any, List

from loggers.system_logger import SystemLogger
from validators.data_validator import DataValidator

try:
    import sympy as sp
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    sp = None  # type: ignore[assignment]


class SymbolicSolver:
    """
    Symbolic equation solver using SymPy.

    Solves equations exactly, computes symbolic derivatives and integrals.
    Gracefully degrades when SymPy is not installed.
    """

    def __init__(self) -> None:
        """Initialize symbolic solver."""
        self.validator = DataValidator()
        self._logger = SystemLogger()

        if not SYMPY_AVAILABLE:
            self._logger.log("SymPy not available, symbolic solving disabled", level="WARNING")

        self._logger.log("SymbolicSolver initialized", level="INFO")

    def solve_equation(self,
                       equation: str,
                       variable: str) -> List[Any]:
        """
        Solve a symbolic equation for the given variable.

        Args:
            equation: Equation string (e.g., "x**2 - 4")
            variable: Variable to solve for

        Returns:
            List of solutions (empty if SymPy unavailable)
        """
        if not SYMPY_AVAILABLE:
            self._logger.log("SymPy required for symbolic solving", level="ERROR")
            return []

        try:
            x = sp.Symbol(variable)
            eq = sp.sympify(equation)
            solutions = sp.solve(eq, x)

            self._logger.log(f"Equation solved: {len(solutions)} solutions", level="INFO")
            return solutions
        except Exception as e:
            self._logger.log(f"Symbolic solving failed: {e}", level="ERROR")
            return []

    def differentiate(self,
                      expression: str,
                      variable: str,
                      order: int = 1) -> str:
        """
        Compute symbolic derivative d^n/dx^n of an expression.

        Args:
            expression: Expression string
            variable: Variable to differentiate with respect to
            order: Derivative order

        Returns:
            Derivative expression string (empty if SymPy unavailable)
        """
        if not SYMPY_AVAILABLE:
            return ""

        try:
            x = sp.Symbol(variable)
            expr = sp.sympify(expression)
            derivative = sp.diff(expr, x, order)

            return str(derivative)
        except Exception as e:
            self._logger.log(f"Differentiation failed: {e}", level="ERROR")
            return ""

    def integrate(self,
                   expression: str,
                   variable: str) -> str:
        """
        Compute symbolic indefinite integral ∫ expr dx.

        Args:
            expression: Expression string
            variable: Variable to integrate with respect to

        Returns:
            Integral expression string (empty if SymPy unavailable)
        """
        if not SYMPY_AVAILABLE:
            return ""

        try:
            x = sp.Symbol(variable)
            expr = sp.sympify(expression)
            integral = sp.integrate(expr, x)

            return str(integral)
        except Exception as e:
            self._logger.log(f"Integration failed: {e}", level="ERROR")
            return ""
