"""
PATH: physics/domains/statistical/phase_transitions.py
PURPOSE: Phase transition models and critical phenomena

Core equations:
    Landau free energy:    F = a(T - T_c)φ² + bφ⁴
    Order parameter:       φ² = -a(T - T_c)/(2b)  for T < T_c
    Critical exponent β:   φ ~ |t|^β  where t = (T - T_c)/T_c
    Critical exponent α:   C ~ |t|^{-α}

DEPENDENCIES:
- numpy: Numerical computation
- validators.data_validator: Input validation
- loggers.system_logger: Structured logging
- physics.foundations: Conservation laws and constraints
"""

import numpy as np

from loggers.system_logger import SystemLogger
from physics.foundations.conservation_laws import ConservationLaws
from physics.foundations.constraints import PhysicsConstraints
from validators.data_validator import DataValidator

# ── Physical constants ──────────────────────────────────────────────
BOLTZMANN_CONSTANT: float = 1.380649e-23  # J/K (exact, SI 2019)

# Mean-field critical exponent β (Landau theory)
_MEAN_FIELD_BETA: float = 0.5


class PhaseTransitions:
    """
    Phase transition and critical phenomena implementation.

    Provides Landau free energy evaluation, equilibrium order parameter
    calculation, and critical exponent extraction.
    """

    def __init__(self) -> None:
        """Initialize phase transitions system."""
        self.validator = DataValidator()
        self._logger = SystemLogger()
        self.conservation = ConservationLaws()
        self.constraints = PhysicsConstraints()

        self.delta_quantum: float = 0.0

        self._logger.log("PhaseTransitions initialized", level="INFO")

    def landau_free_energy(self,
                            order_parameter: float,
                            temperature: float,
                            critical_temperature: float,
                            coefficient_a: float,
                            coefficient_b: float) -> float:
        """
        Compute Landau free energy.

        Equation: F = a(T - T_c)φ² + bφ⁴

        Args:
            order_parameter: Order parameter φ
            temperature: Temperature T
            critical_temperature: Critical temperature T_c
            coefficient_a: Coefficient a
            coefficient_b: Coefficient b

        Returns:
            Free energy F
        """
        free_energy = (
            coefficient_a * (temperature - critical_temperature) * order_parameter ** 2
            + coefficient_b * order_parameter ** 4
        )

        self._logger.log(f"Landau free energy: F = {free_energy}", level="DEBUG")
        return free_energy

    def compute_order_parameter(self,
                                 temperature: float,
                                 critical_temperature: float,
                                 coefficient_a: float,
                                 coefficient_b: float) -> float:
        """
        Compute equilibrium order parameter from Landau theory.

        Equation: ∂F/∂φ = 0 → φ = 0 (T ≥ T_c) or φ² = -a(T-T_c)/(2b) (T < T_c)

        Args:
            temperature: Temperature T
            critical_temperature: Critical temperature T_c
            coefficient_a: Coefficient a
            coefficient_b: Coefficient b

        Returns:
            Equilibrium order parameter φ
        """
        if temperature >= critical_temperature:
            order_parameter = 0.0
        else:
            phi_squared = -coefficient_a * (temperature - critical_temperature) / (2 * coefficient_b)
            order_parameter = np.sqrt(phi_squared) if phi_squared > 0 else 0.0

        self._logger.log(f"Order parameter: φ = {order_parameter}", level="DEBUG")
        return order_parameter

    def critical_exponent_beta(self,
                                order_parameter: float,
                                reduced_temperature: float) -> float:
        """
        Extract critical exponent β from φ ~ |t|^β near T_c.

        Equation: β = ln(|φ|) / ln(|t|)  where t = (T - T_c)/T_c

        Args:
            order_parameter: Order parameter φ
            reduced_temperature: Reduced temperature t

        Returns:
            Critical exponent β (returns mean-field 0.5 when indeterminate)
        """
        if abs(reduced_temperature) < 1e-10 or abs(order_parameter) < 1e-10:
            return _MEAN_FIELD_BETA

        beta = np.log(abs(order_parameter)) / np.log(abs(reduced_temperature))

        self._logger.log(f"Critical exponent β = {beta}", level="DEBUG")
        return beta

    def critical_exponent_alpha(self,
                                 heat_capacity: float,
                                 reduced_temperature: float,
                                 critical_heat_capacity: float) -> float:
        """
        Extract critical exponent α from C ~ |t|^{-α} near T_c.

        Equation: α = -ln(|(C - C_c)/C_c|) / ln(|t|)

        Args:
            heat_capacity: Heat capacity C
            reduced_temperature: Reduced temperature t
            critical_heat_capacity: Critical heat capacity C_c

        Returns:
            Critical exponent α
        """
        if abs(reduced_temperature) < 1e-10:
            return 0.0

        if abs(critical_heat_capacity) > 1e-10:
            alpha = (
                -np.log(abs((heat_capacity - critical_heat_capacity) / critical_heat_capacity))
                / np.log(abs(reduced_temperature))
            )
        else:
            alpha = 0.0

        self._logger.log(f"Critical exponent α = {alpha}", level="DEBUG")
        return alpha

    def set_quantum_correction(self, delta: float) -> None:
        """Set quantum corrections for phase transitions (clamped to [0, 1])."""
        self.delta_quantum = max(0.0, min(1.0, delta))
        self._logger.log(f"Quantum correction set: δ = {self.delta_quantum}", level="INFO")
