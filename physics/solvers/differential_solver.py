"""
PATH: physics/solvers/differential_solver.py
PURPOSE: ODE solvers with physics constraint checking

Implements Euler and 4th-order Runge-Kutta (RK4) methods for solving
ordinary differential equations of the form dy/dt = f(t, y).

Algorithms:
- Euler: y(t+dt) = y(t) + f(t, y(t))·dt
- RK4:   y(t+dt) = y(t) + (dt/6)(k₁ + 2k₂ + 2k₃ + k₄)

DEPENDENCIES:
- numpy: Numerical arrays
- validators.data_validator: Input validation
- loggers.system_logger: Structured logging
- physics.foundations.constraints: Physics constraint enforcement
"""

from typing import Any, Callable, Dict, Optional

import numpy as np

from loggers.system_logger import SystemLogger
from physics.foundations.constraints import PhysicsConstraints
from validators.data_validator import DataValidator


class DifferentialSolver:
    """
    ODE solver with optional physics constraint checking.

    Solves systems of the form dy/dt = f(t, y) using explicit
    integration methods and validates physical consistency.
    """

    def __init__(self) -> None:
        """Initialize differential solver."""
        self.validator = DataValidator()
        self._logger = SystemLogger()
        self.constraints = PhysicsConstraints()

        self._logger.log("DifferentialSolver initialized", level="INFO")

    def euler_method(self,
                     derivative_function: Callable,
                     initial_condition: np.ndarray,
                     time_step: float,
                     num_steps: int) -> Dict[str, np.ndarray]:
        """
        Solve ODE using the forward Euler method.

        Algorithm: y(t+dt) = y(t) + f(t, y(t))·dt

        Args:
            derivative_function: Function f(t, y) returning dy/dt
            initial_condition: Initial condition y(0)
            time_step: Time step dt
            num_steps: Number of steps

        Returns:
            Dictionary with 'solution' array and 'times' array
        """
        solution = np.zeros((num_steps + 1, len(initial_condition)))
        times = np.zeros(num_steps + 1)

        solution[0] = np.array(initial_condition)
        times[0] = 0.0

        for i in range(num_steps):
            t = times[i]
            y = solution[i]
            dydt = derivative_function(t, y)

            solution[i + 1] = y + dydt * time_step
            times[i + 1] = t + time_step

        self._logger.log(f"Euler method: {num_steps} steps completed", level="INFO")
        return {'solution': solution, 'times': times}

    def runge_kutta_4(self,
                       derivative_function: Callable,
                       initial_condition: np.ndarray,
                       time_step: float,
                       num_steps: int) -> Dict[str, np.ndarray]:
        """
        Solve ODE using the classical 4th-order Runge-Kutta method.

        Algorithm:
            k₁ = f(tₙ, yₙ)
            k₂ = f(tₙ + dt/2, yₙ + dt·k₁/2)
            k₃ = f(tₙ + dt/2, yₙ + dt·k₂/2)
            k₄ = f(tₙ + dt, yₙ + dt·k₃)
            yₙ₊₁ = yₙ + (dt/6)(k₁ + 2k₂ + 2k₃ + k₄)

        Args:
            derivative_function: Function f(t, y) returning dy/dt
            initial_condition: Initial condition y(0)
            time_step: Time step dt
            num_steps: Number of steps

        Returns:
            Dictionary with 'solution' array and 'times' array
        """
        solution = np.zeros((num_steps + 1, len(initial_condition)))
        times = np.zeros(num_steps + 1)

        solution[0] = np.array(initial_condition)
        times[0] = 0.0

        for i in range(num_steps):
            t = times[i]
            y = solution[i]

            k1 = derivative_function(t, y)
            k2 = derivative_function(t + time_step / 2, y + time_step * k1 / 2)
            k3 = derivative_function(t + time_step / 2, y + time_step * k2 / 2)
            k4 = derivative_function(t + time_step, y + time_step * k3)

            solution[i + 1] = y + (time_step / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
            times[i + 1] = t + time_step

        self._logger.log(f"Runge-Kutta 4: {num_steps} steps completed", level="INFO")
        return {'solution': solution, 'times': times}

    def solve_with_constraints(self,
                                derivative_function: Callable,
                                initial_condition: np.ndarray,
                                time_step: float,
                                num_steps: int,
                                constraint_checker: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Solve ODE with RK4 and check constraints at each step.

        Args:
            derivative_function: Function f(t, y)
            initial_condition: Initial condition
            time_step: Time step
            num_steps: Number of steps
            constraint_checker: Function(state) → bool to check constraints

        Returns:
            Dictionary with solution, times, and constraint_violations list
        """
        result = self.runge_kutta_4(derivative_function, initial_condition, time_step, num_steps)

        violations: list[int] = []
        if constraint_checker:
            for i, state in enumerate(result['solution']):
                if not constraint_checker(state):
                    violations.append(i)
                    self._logger.log(f"Constraint violation at step {i}", level="WARNING")

        result['constraint_violations'] = violations
        return result
