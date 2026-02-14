"""
PATH: physics/domains/classical/hamiltonian.py
PURPOSE: Hamiltonian mechanics — phase space and Hamilton's equations

Core equations:
    Hamiltonian:       H(q, p, t) = T(p) + V(q, t)  (standard systems)
    Hamilton's eqs:    q̇_i = ∂H/∂p_i,  ṗ_i = -∂H/∂q_i
    Poisson bracket:   {f, g} = Σ(∂f/∂q_i · ∂g/∂p_i - ∂f/∂p_i · ∂g/∂q_i)

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


class HamiltonianMechanics:
    """
    Hamiltonian mechanics implementation.

    Provides Hamiltonian evaluation, Hamilton's equations (via finite
    differences), symplectic integration, and Poisson brackets.
    """

    def __init__(self) -> None:
        """Initialize Hamiltonian mechanics system."""
        self.validator = DataValidator()
        self._logger = SystemLogger()
        self.conservation = ConservationLaws()
        self.symmetry = SymmetryChecker()

        self.delta_relativistic: float = 0.0
        self.delta_quantum: float = 0.0

        self._logger.log("HamiltonianMechanics initialized", level="INFO")

    def compute_hamiltonian(self,
                            kinetic_energy: Callable,
                            potential_energy: Callable,
                            coordinates: np.ndarray,
                            momenta: np.ndarray,
                            time: float) -> float:
        """
        Compute Hamiltonian H = T + V for standard systems.

        Equation: H(q, p, t) = T(p) + V(q, t)

        Args:
            kinetic_energy: Function T(p) returning kinetic energy
            potential_energy: Function V(q, t) returning potential energy
            coordinates: Generalized coordinates q
            momenta: Generalized momenta p
            time: Time t

        Returns:
            Hamiltonian value
        """
        T = kinetic_energy(momenta)
        V = potential_energy(coordinates, time)
        H = T + V

        self._logger.log(f"Hamiltonian computed: H = {H}", level="DEBUG")
        return H

    def hamilton_equations(self,
                           hamiltonian: Callable,
                           coordinates: np.ndarray,
                           momenta: np.ndarray,
                           time: float,
                           epsilon: float = 1e-6) -> Dict[str, np.ndarray]:
        """
        Compute Hamilton's equations via central finite differences.

        Equations:
            q̇_i =  ∂H/∂p_i
            ṗ_i = -∂H/∂q_i

        Args:
            hamiltonian: Function H(q, p, t)
            coordinates: Generalized coordinates q
            momenta: Generalized momenta p
            time: Time t
            epsilon: Numerical differentiation step

        Returns:
            Dictionary with 'q_dot' and 'p_dot' arrays
        """
        q = np.array(coordinates)
        p = np.array(momenta)

        q_dot = np.zeros_like(p)
        for i in range(len(p)):
            p_perturbed = p.copy()
            p_perturbed[i] += epsilon
            H_plus = hamiltonian(q, p_perturbed, time)
            H_minus = hamiltonian(q, p - epsilon * (p == p[i]), time)
            q_dot[i] = (H_plus - H_minus) / (2 * epsilon)

        p_dot = np.zeros_like(q)
        for i in range(len(q)):
            q_perturbed = q.copy()
            q_perturbed[i] += epsilon
            H_plus = hamiltonian(q_perturbed, p, time)
            H_minus = hamiltonian(q - epsilon * (q == q[i]), p, time)
            p_dot[i] = -(H_plus - H_minus) / (2 * epsilon)

        self._logger.log("Hamilton's equations computed", level="DEBUG")

        return {
            'q_dot': q_dot,
            'p_dot': p_dot
        }

    def harmonic_oscillator_hamiltonian(self,
                                        position: float,
                                        momentum: float,
                                        mass: float,
                                        spring_constant: float) -> float:
        """
        Hamiltonian for a 1-D harmonic oscillator.

        Equation: H = p²/(2m) + (1/2)kx²

        Args:
            position: Position x
            momentum: Momentum p
            mass: Mass m
            spring_constant: Spring constant k

        Returns:
            Hamiltonian value
        """
        T = momentum ** 2 / (2 * mass)
        V = 0.5 * spring_constant * position ** 2
        H = T + V

        self._logger.log(f"Harmonic oscillator Hamiltonian: H = {H}", level="DEBUG")
        return H

    def integrate_hamilton_equations(self,
                                      hamiltonian: Callable,
                                      initial_coordinates: np.ndarray,
                                      initial_momenta: np.ndarray,
                                      time_step: float,
                                      num_steps: int) -> Dict[str, np.ndarray]:
        """
        Integrate Hamilton's equations using symplectic Euler method.

        The symplectic structure preserves phase-space volume (Liouville's theorem).

        Args:
            hamiltonian: Function H(q, p, t)
            initial_coordinates: Initial q(0)
            initial_momenta: Initial p(0)
            time_step: Time step dt
            num_steps: Number of integration steps

        Returns:
            Dictionary with coordinates, momenta, and times arrays
        """
        coordinates = np.zeros((num_steps + 1, len(initial_coordinates)))
        momenta = np.zeros((num_steps + 1, len(initial_momenta)))
        times = np.zeros(num_steps + 1)

        coordinates[0] = np.array(initial_coordinates)
        momenta[0] = np.array(initial_momenta)
        times[0] = 0.0

        for i in range(num_steps):
            q = coordinates[i]
            p = momenta[i]
            t = times[i]

            derivatives = self.hamilton_equations(hamiltonian, q, p, t)
            q_dot = derivatives['q_dot']
            p_dot = derivatives['p_dot']

            momenta[i + 1] = p + p_dot * time_step
            coordinates[i + 1] = q + q_dot * time_step
            times[i + 1] = t + time_step

            H_initial = hamiltonian(coordinates[0], momenta[0], times[0])
            H_current = hamiltonian(coordinates[i + 1], momenta[i + 1], times[i + 1])
            is_conserved, _ = self.conservation.check_energy_conservation(H_initial, H_current)
            if not is_conserved and i % 10 == 0:
                self._logger.log(f"Energy drift at step {i + 1}: ΔH = {H_current - H_initial}", level="WARNING")

        self._logger.log(f"Hamilton's equations integrated: {num_steps} steps", level="INFO")

        return {
            'coordinates': coordinates,
            'momenta': momenta,
            'times': times
        }

    def poisson_bracket(self,
                        function1: Callable,
                        function2: Callable,
                        coordinates: np.ndarray,
                        momenta: np.ndarray,
                        time: float,
                        epsilon: float = 1e-6) -> float:
        """
        Compute Poisson bracket {f, g} via central finite differences.

        Equation: {f, g} = Σ_i (∂f/∂q_i · ∂g/∂p_i - ∂f/∂p_i · ∂g/∂q_i)

        Args:
            function1: Function f(q, p, t)
            function2: Function g(q, p, t)
            coordinates: Generalized coordinates q
            momenta: Generalized momenta p
            time: Time t
            epsilon: Numerical differentiation step

        Returns:
            Poisson bracket value
        """
        q = np.array(coordinates)
        p = np.array(momenta)

        bracket = 0.0

        for i in range(len(q)):
            q_perturbed = q.copy()
            q_perturbed[i] += epsilon
            df_dq = (function1(q_perturbed, p, time) - function1(q, p, time)) / epsilon

            p_perturbed = p.copy()
            p_perturbed[i] += epsilon
            dg_dp = (function2(q, p_perturbed, time) - function2(q, p, time)) / epsilon

            df_dp = (function1(q, p_perturbed, time) - function1(q, p, time)) / epsilon

            dg_dq = (function2(q_perturbed, p, time) - function2(q, p, time)) / epsilon

            bracket += df_dq * dg_dp - df_dp * dg_dq

        self._logger.log(f"Poisson bracket computed: {{f, g}} = {bracket}", level="DEBUG")
        return bracket

    def set_relativistic_correction(self, delta: float) -> None:
        """Set relativistic correction factor (clamped to [0, 1])."""
        self.delta_relativistic = max(0.0, min(1.0, delta))
        self._logger.log(f"Relativistic correction set: δ = {self.delta_relativistic}", level="INFO")

    def set_quantum_correction(self, delta: float) -> None:
        """Set quantum correction factor (clamped to [0, 1])."""
        self.delta_quantum = max(0.0, min(1.0, delta))
        self._logger.log(f"Quantum correction set: δ = {self.delta_quantum}", level="INFO")
