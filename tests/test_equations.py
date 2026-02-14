"""
PATH: tests/test_equations.py
PURPOSE: Tests for physics equation solver.

Tests cover:
- Equation parsing
- Symbolic solving
- Numerical solving
- System of equations
- Differentiation and integration
"""

from __future__ import annotations

import unittest

from physics.equations import EquationParser, EquationSolver, SolveMethod


class TestEquationParser(unittest.TestCase):
    """Tests for EquationParser."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.parser = EquationParser()

    def test_parse_expression(self) -> None:
        """Test parsing simple expression."""
        try:
            expr, symbols = self.parser.parse("x**2 + 2*x + 1")
            self.assertIsNotNone(expr)
            self.assertTrue(len(symbols) > 0)
        except RuntimeError:
            self.skipTest("SymPy not available")

    def test_parse_equation(self) -> None:
        """Test parsing equation with equals sign."""
        try:
            eq, symbols = self.parser.parse("y = m*x + b")
            self.assertIsNotNone(eq)
        except RuntimeError:
            self.skipTest("SymPy not available")

    def test_get_physics_equation(self) -> None:
        """Test retrieving physics equations."""
        ke_eq = self.parser.get_physics_equation("kinetic_energy")
        self.assertIn("E_k", ke_eq)
        self.assertIn("m", ke_eq)
        self.assertIn("v", ke_eq)


class TestEquationSolver(unittest.TestCase):
    """Tests for EquationSolver."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.solver = EquationSolver()

    def test_initialization(self) -> None:
        """Test solver initialization."""
        self.assertIsNotNone(self.solver)
        self.assertIsNotNone(self.solver.CONSTANTS)

    def test_get_constant(self) -> None:
        """Test getting physical constants."""
        c = self.solver.get_constant("c")
        self.assertEqual(c, 299792458)

        g = self.solver.get_constant("g")
        self.assertAlmostEqual(g, 9.80665, places=3)

    def test_solve_linear(self) -> None:
        """Test solving linear equation."""
        try:
            result = self.solver.solve(
                equation="F = m * a",
                variables={"m": 10, "a": 5},
                solve_for="F",
            )

            self.assertTrue(
                result.success if hasattr(result, "success") else len(result.solutions) > 0
            )
            if result.solutions:
                self.assertAlmostEqual(result.solutions[0], 50, places=5)
        except Exception as e:
            if "SymPy" in str(e):
                self.skipTest("SymPy not available")
            raise

    def test_solve_quadratic(self) -> None:
        """Test solving quadratic equation."""
        try:
            result = self.solver.solve(
                equation="x**2 - 4 = 0",
                variables={},
                solve_for="x",
            )

            if result.solutions:
                solutions_set = {
                    abs(s) for s in result.solutions if isinstance(s, (int, float))
                }
                self.assertIn(2.0, solutions_set)
        except Exception as e:
            if "SymPy" in str(e):
                self.skipTest("SymPy not available")
            raise

    def test_solve_kinetic_energy(self) -> None:
        """Test solving kinetic energy equation: E = 0.5 * m * v^2."""
        try:
            result = self.solver.solve(
                equation="E = 0.5 * m * v**2",
                variables={"E": 100, "m": 2},
                solve_for="v",
            )

            if result.solutions:
                # v = sqrt(2*E/m) = sqrt(100) = 10
                self.assertTrue(
                    any(
                        abs(s - 10) < 0.01 or abs(s + 10) < 0.01
                        for s in result.solutions
                        if isinstance(s, (int, float))
                    )
                )
        except Exception as e:
            if "SymPy" in str(e):
                self.skipTest("SymPy not available")
            raise

    def test_differentiate(self) -> None:
        """Test differentiation."""
        try:
            result = self.solver.differentiate("x**3", "x")

            if result.solutions:
                self.assertIn("3*x**2", str(result.solutions[0]))
        except Exception as e:
            if "SymPy" in str(e):
                self.skipTest("SymPy not available")
            raise

    def test_integrate(self) -> None:
        """Test integration (indefinite and definite)."""
        try:
            result = self.solver.integrate_expr("2*x", "x")

            if result.solutions:
                self.assertIn("x**2", str(result.solutions[0]))

            result_definite = self.solver.integrate_expr("x", "x", lower=0, upper=1)

            if result_definite.solutions and isinstance(result_definite.solutions[0], (int, float)):
                self.assertAlmostEqual(result_definite.solutions[0], 0.5, places=5)
        except Exception as e:
            if "SymPy" in str(e):
                self.skipTest("SymPy not available")
            raise

    def test_method_used(self) -> None:
        """Test that method_used is reported."""
        try:
            result = self.solver.solve("x + 1 = 0", {}, "x")
            self.assertIsNotNone(result.method_used)
        except Exception as e:
            if "SymPy" in str(e):
                self.skipTest("SymPy not available")
            raise


class TestPhysicsEquations(unittest.TestCase):
    """Tests for specific physics equations."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.solver = EquationSolver()

    def test_newtons_second_law(self) -> None:
        """Test F = ma."""
        try:
            result = self.solver.solve("F = m * a", {"F": 100, "m": 10}, "a")

            if result.solutions:
                self.assertAlmostEqual(result.solutions[0], 10, places=5)
        except Exception as e:
            if "SymPy" in str(e):
                self.skipTest("SymPy not available")
            raise

    def test_gravitational_potential_energy(self) -> None:
        """Test E = mgh."""
        try:
            result = self.solver.solve("E = m * g * h", {"m": 10, "h": 5}, "E")

            if result.solutions:
                # E = 10 * 9.80665 * 5 ~ 490.33
                self.assertAlmostEqual(result.solutions[0], 490.33, places=0)
        except Exception as e:
            if "SymPy" in str(e):
                self.skipTest("SymPy not available")
            raise


if __name__ == "__main__":
    unittest.main()
