"""
PATH: physics/domains/classical/lagrangian.py
PURPOSE: Lagrangian mechanics — action principle and Euler-Lagrange equations

Core equations:
    Lagrangian:     L(q, q̇, t) = T(q̇) - V(q, t)
    Euler-Lagrange: d/dt(∂L/∂q̇) - ∂L/∂q = 0
    Action:         S = ∫ L dt
    Least action:   δS = 0

DEPENDENCIES:
- numpy: Numerical computation
- validators.data_validator: Input validation
- loggers.system_logger: Structured logging
- physics.foundations: Conservation laws and symmetry checking
"""

from typing import Any, Callable, Dict

import numpy as np

from loggers.system_logger import SystemLogger
from physics.foundations.conservation_laws import ConservationLaws
from physics.foundations.symmetries import SymmetryChecker
from validators.data_validator import DataValidator

# Standard gravitational acceleration (m/s²)
DEFAULT_GRAVITY: float = 9.81


class LagrangianMechanics:
    """
    Lagrangian mechanics implementation.

    Provides Lagrangian evaluation, Euler-Lagrange residuals, action
    integrals, and common Lagrangian systems (harmonic oscillator,
    pendulum).
    """

    def __init__(self) -> None:
        """Initialize Lagrangian mechanics system."""
        self.validator = DataValidator()
        self._logger = SystemLogger()
        self.conservation = ConservationLaws()
        self.symmetry = SymmetryChecker()

        self.delta_relativistic: float = 0.0
        self.delta_quantum: float = 0.0

        self._logger.log("LagrangianMechanics initialized", level="INFO")

    def compute_lagrangian(self,
                           kinetic_energy: Callable,
                           potential_energy: Callable,
                           coordinates: np.ndarray,
                           velocities: np.ndarray,
                           time: float) -> float:
        """
        Compute Lagrangian L = T - V.

        Equation: L(q, q̇, t) = T(q̇) - V(q, t)

        Args:
            kinetic_energy: Function T(q̇) returning kinetic energy
            potential_energy: Function V(q, t) returning potential energy
            coordinates: Generalized coordinates q
            velocities: Generalized velocities q̇
            time: Time t

        Returns:
            Lagrangian value
        """
        T = kinetic_energy(velocities)
        V = potential_energy(coordinates, time)
        L = T - V

        self._logger.log(f"Lagrangian computed: L = {L}", level="DEBUG")
        return L

    def euler_lagrange_equation(self,
                                 lagrangian: Callable,
                                 coordinates: np.ndarray,
                                 velocities: np.ndarray,
                                 time: float,
                                 coordinate_index: int,
                                 epsilon: float = 1e-6) -> float:
        """
        Compute Euler-Lagrange residual for one coordinate (should ≈ 0).

        Equation: d/dt(∂L/∂q̇_i) - ∂L/∂q_i = 0

        Uses central finite differences for partial derivatives.

        Args:
            lagrangian: Function L(q, q̇, t)
            coordinates: Generalized coordinates q
            velocities: Generalized velocities q̇
            time: Time t
            coordinate_index: Index i of coordinate
            epsilon: Numerical differentiation step

        Returns:
            Value of Euler-Lagrange residual
        """
        q = np.array(coordinates)
        q_dot = np.array(velocities)

        # ∂L/∂q_i via central difference
        q_perturbed = q.copy()
        q_perturbed[coordinate_index] += epsilon
        L_plus = lagrangian(q_perturbed, q_dot, time)
        L_minus = lagrangian(q - epsilon * (q == q[coordinate_index]), q_dot, time)
        dL_dq = (L_plus - L_minus) / (2 * epsilon)

        # ∂L/∂q̇_i via central difference
        q_dot_perturbed = q_dot.copy()
        q_dot_perturbed[coordinate_index] += epsilon
        L_plus_dot = lagrangian(q, q_dot_perturbed, time)
        L_minus_dot = lagrangian(q, q_dot - epsilon * (q_dot == q_dot[coordinate_index]), time)
        dL_dq_dot = (L_plus_dot - L_minus_dot) / (2 * epsilon)

        # d/dt(∂L/∂q̇_i) requires acceleration — placeholder (constant-accel approx)
        d_dt_dL_dq_dot = 0.0

        euler_lagrange = d_dt_dL_dq_dot - dL_dq

        self._logger.log(
            f"Euler-Lagrange equation [{coordinate_index}]: {euler_lagrange}",
            level="DEBUG"
        )
        return euler_lagrange

    def harmonic_oscillator_lagrangian(self,
                                       position: float,
                                       velocity: float,
                                       mass: float,
                                       spring_constant: float) -> float:
        """
        Lagrangian for a 1-D harmonic oscillator.

        Equation: L = (1/2)mẋ² - (1/2)kx²

        Args:
            position: Position x
            velocity: Velocity ẋ
            mass: Mass m
            spring_constant: Spring constant k

        Returns:
            Lagrangian value
        """
        T = 0.5 * mass * velocity ** 2
        V = 0.5 * spring_constant * position ** 2
        L = T - V

        self._logger.log(f"Harmonic oscillator Lagrangian: L = {L}", level="DEBUG")
        return L

    def pendulum_lagrangian(self,
                            angle: float,
                            angular_velocity: float,
                            mass: float,
                            length: float,
                            gravity: float = DEFAULT_GRAVITY) -> float:
        """
        Lagrangian for a simple pendulum.

        Equation: L = (1/2)ml²θ̇² - mgl(1 - cos θ)

        Args:
            angle: Angle θ (radians)
            angular_velocity: Angular velocity θ̇
            mass: Mass m
            length: Length l
            gravity: Gravitational acceleration g

        Returns:
            Lagrangian value
        """
        T = 0.5 * mass * length ** 2 * angular_velocity ** 2
        V = mass * gravity * length * (1 - np.cos(angle))
        L = T - V

        self._logger.log(f"Pendulum Lagrangian: L = {L}", level="DEBUG")
        return L

    def compute_action(self,
                       lagrangian: Callable,
                       trajectory: np.ndarray,
                       velocities: np.ndarray,
                       times: np.ndarray) -> float:
        """
        Compute action S = ∫ L dt via trapezoidal summation.

        Equation: S = ∫ L(q, q̇, t) dt

        Args:
            lagrangian: Function L(q, q̇, t)
            trajectory: Array of coordinates q(t)
            velocities: Array of velocities q̇(t)
            times: Array of time values

        Returns:
            Action value
        """
        action = 0.0

        for i in range(len(times) - 1):
            dt = times[i + 1] - times[i]
            L = lagrangian(trajectory[i], velocities[i], times[i])
            action += L * dt

        self._logger.log(f"Action computed: S = {action}", level="INFO")
        return action

    def principle_of_least_action(self,
                                   lagrangian: Callable,
                                   initial_coordinates: np.ndarray,
                                   final_coordinates: np.ndarray,
                                   initial_time: float,
                                   final_time: float) -> Dict[str, Any]:
        """
        Find trajectory minimizing action (simplified linear interpolation).

        Equation: δS = 0 (stationary action principle)

        Args:
            lagrangian: Function L(q, q̇, t)
            initial_coordinates: Initial q(t_i)
            final_coordinates: Final q(t_f)
            initial_time: Initial time t_i
            final_time: Final time t_f

        Returns:
            Dictionary with trajectory, velocities, times, and action
        """
        num_points = 100
        times = np.linspace(initial_time, final_time, num_points)
        trajectory = np.zeros((num_points, len(initial_coordinates)))
        velocities = np.zeros((num_points, len(initial_coordinates)))

        for i in range(num_points):
            alpha = i / (num_points - 1)
            trajectory[i] = (1 - alpha) * initial_coordinates + alpha * final_coordinates
            if i < num_points - 1:
                velocities[i] = (trajectory[i + 1] - trajectory[i]) / (times[i + 1] - times[i])

        action = self.compute_action(lagrangian, trajectory, velocities, times)

        self._logger.log(f"Principle of least action: S = {action}", level="INFO")

        return {
            'trajectory': trajectory,
            'velocities': velocities,
            'times': times,
            'action': action
        }

    def set_relativistic_correction(self, delta: float) -> None:
        """Set relativistic correction factor (clamped to [0, 1])."""
        self.delta_relativistic = max(0.0, min(1.0, delta))
        self._logger.log(f"Relativistic correction set: δ = {self.delta_relativistic}", level="INFO")

    def set_quantum_correction(self, delta: float) -> None:
        """Set quantum correction factor (clamped to [0, 1])."""
        self.delta_quantum = max(0.0, min(1.0, delta))
        self._logger.log(f"Quantum correction set: δ = {self.delta_quantum}", level="INFO")
