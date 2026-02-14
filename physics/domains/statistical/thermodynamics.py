"""
PATH: physics/domains/statistical/thermodynamics.py
PURPOSE: Macroscopic thermodynamics — laws, potentials, and equations of state

Core equations:
    Boltzmann entropy:  S = k_B ln Ω
    Internal energy:    U = C_V (T - T₀)  (constant C_V)
    Helmholtz:          F = U - TS
    Gibbs:              G = U - TS + PV = H - TS
    Ideal gas law:      PV = nRT
    First law:          ΔU = Q - W
    Second law:         ΔS ≥ Q/T

DEPENDENCIES:
- numpy: Numerical computation
- validators.data_validator: Input validation
- loggers.system_logger: Structured logging
- physics.foundations: Conservation laws and constraints
"""

from typing import Any, Dict, Tuple

import numpy as np

from loggers.system_logger import SystemLogger
from physics.foundations.conservation_laws import ConservationLaws
from physics.foundations.constraints import PhysicsConstraints
from validators.data_validator import DataValidator

# ── Physical constants ──────────────────────────────────────────────
BOLTZMANN_CONSTANT: float = 1.380649e-23   # J/K (exact, SI 2019)
GAS_CONSTANT: float = 8.314462618          # J/(mol·K) (exact, SI)


class Thermodynamics:
    """
    Macroscopic thermodynamics implementation.

    Provides entropy, internal energy, free energies, ideal gas law,
    heat capacity, and first/second law checks.
    """

    def __init__(self) -> None:
        """Initialize thermodynamics system."""
        self.validator = DataValidator()
        self._logger = SystemLogger()
        self.conservation = ConservationLaws()
        self.constraints = PhysicsConstraints()

        self.delta_quantum: float = 0.0

        self._logger.log("Thermodynamics initialized", level="INFO")

    def compute_entropy(self,
                         number_of_states: int) -> float:
        """
        Compute entropy using Boltzmann's formula.

        Equation: S = k_B ln Ω

        Args:
            number_of_states: Number of microstates Ω (must be positive)

        Returns:
            Entropy S

        Raises:
            ValueError: If number_of_states is non-positive
        """
        if number_of_states <= 0:
            self._logger.log("Invalid number of states", level="ERROR")
            raise ValueError("Number of states must be positive")

        entropy = float(BOLTZMANN_CONSTANT * np.log(number_of_states))

        is_positive, _ = self.constraints.check_thermodynamic_constraints(entropy, 0.0)
        if not is_positive:
            self._logger.log("Entropy constraint violation", level="WARNING")

        self._logger.log(f"Entropy computed: S = {entropy}", level="DEBUG")
        return entropy

    def compute_internal_energy(self,
                                 temperature: float,
                                 heat_capacity: float,
                                 reference_temperature: float = 0.0) -> float:
        """
        Compute internal energy (constant heat capacity approximation).

        Equation: U = C_V (T - T₀)

        Args:
            temperature: Temperature T
            heat_capacity: Heat capacity C_V
            reference_temperature: Reference temperature T₀

        Returns:
            Internal energy U
        """
        internal_energy = heat_capacity * (temperature - reference_temperature)

        self._logger.log(f"Internal energy computed: U = {internal_energy}", level="DEBUG")
        return internal_energy

    def compute_helmholtz_free_energy(self,
                                      internal_energy: float,
                                      temperature: float,
                                      entropy: float) -> float:
        """
        Compute Helmholtz free energy.

        Equation: F = U - TS

        Args:
            internal_energy: Internal energy U
            temperature: Temperature T
            entropy: Entropy S

        Returns:
            Helmholtz free energy F
        """
        free_energy = internal_energy - temperature * entropy

        self._logger.log(f"Helmholtz free energy: F = {free_energy}", level="DEBUG")
        return free_energy

    def compute_gibbs_free_energy(self,
                                   internal_energy: float,
                                   temperature: float,
                                   entropy: float,
                                   pressure: float,
                                   volume: float) -> float:
        """
        Compute Gibbs free energy.

        Equation: G = U - TS + PV = H - TS

        Args:
            internal_energy: Internal energy U
            temperature: Temperature T
            entropy: Entropy S
            pressure: Pressure P
            volume: Volume V

        Returns:
            Gibbs free energy G
        """
        enthalpy = internal_energy + pressure * volume
        gibbs_free_energy = enthalpy - temperature * entropy

        self._logger.log(f"Gibbs free energy: G = {gibbs_free_energy}", level="DEBUG")
        return gibbs_free_energy

    def ideal_gas_law(self,
                      pressure: float,
                      volume: float,
                      temperature: float,
                      number_of_moles: float) -> float:
        """
        Check ideal gas law PV = nRT.

        Args:
            pressure: Pressure P
            volume: Volume V
            temperature: Temperature T
            number_of_moles: Number of moles n

        Returns:
            Residual |P - nRT/V| (should be ≈ 0)
        """
        expected_pressure = number_of_moles * GAS_CONSTANT * temperature / volume
        residual = abs(pressure - expected_pressure)

        if residual > 1e-6:
            self._logger.log(f"Ideal gas law violation: residual = {residual}", level="WARNING")
        else:
            self._logger.log("Ideal gas law verified", level="DEBUG")

        return residual

    def compute_heat_capacity(self,
                               energy_change: float,
                               temperature_change: float) -> float:
        """
        Compute heat capacity.

        Equation: C = dU/dT (constant volume)

        Args:
            energy_change: Change in energy dU
            temperature_change: Change in temperature dT

        Returns:
            Heat capacity C
        """
        if abs(temperature_change) < 1e-10:
            self._logger.log("Temperature change too small", level="WARNING")
            return 0.0

        heat_capacity = energy_change / temperature_change

        self._logger.log(f"Heat capacity computed: C = {heat_capacity}", level="DEBUG")
        return heat_capacity

    def first_law_thermodynamics(self,
                                 internal_energy_change: float,
                                 heat_added: float,
                                 work_done: float) -> Tuple[bool, float]:
        """
        Check the first law of thermodynamics: ΔU = Q - W.

        Args:
            internal_energy_change: Change in internal energy ΔU
            heat_added: Heat added to system Q
            work_done: Work done by system W

        Returns:
            Tuple of (is_valid, residual)
        """
        expected_change = heat_added - work_done
        residual = abs(internal_energy_change - expected_change)
        is_valid = residual < 1e-6

        if not is_valid:
            self._logger.log(f"First law violation: residual = {residual}", level="WARNING")
        else:
            self._logger.log("First law of thermodynamics verified", level="DEBUG")

        return is_valid, residual

    def second_law_thermodynamics(self,
                                   initial_entropy: float,
                                   final_entropy: float,
                                   heat_exchange: float,
                                   temperature: float) -> Tuple[bool, float]:
        """
        Check the second law of thermodynamics: ΔS ≥ Q/T.

        Args:
            initial_entropy: Initial entropy S_i
            final_entropy: Final entropy S_f
            heat_exchange: Heat exchange Q
            temperature: Temperature T

        Returns:
            Tuple of (is_valid, entropy_change)
        """
        entropy_change = final_entropy - initial_entropy
        minimum_change = heat_exchange / temperature if temperature > 0 else 0.0

        is_valid = entropy_change >= minimum_change - 1e-6

        if not is_valid:
            self._logger.log(
                f"Second law violation: ΔS = {entropy_change} < Q/T = {minimum_change}",
                level="WARNING"
            )
        else:
            self._logger.log("Second law of thermodynamics verified", level="DEBUG")

        return is_valid, entropy_change

    def set_quantum_correction(self, delta: float) -> None:
        """Set quantum statistics correction factor (clamped to [0, 1])."""
        self.delta_quantum = max(0.0, min(1.0, delta))
        self._logger.log(f"Quantum correction set: δ = {self.delta_quantum}", level="INFO")
