"""
PATH: physics/domains/statistical/ensemble_theory.py
PURPOSE: Statistical ensembles and partition functions

Core equations:
    Canonical Z:        Z = Σ exp(-βE_i)  where β = 1/(k_B T)
    Probability:        P_i = (1/Z) exp(-βE_i)
    Helmholtz free E:   F = -k_B T ln Z
    Entropy:            S = k_B (ln Z + β⟨E⟩)
    Grand canonical Ξ:  Ξ = Σ exp(-β(E_i - μN_i))
    Microcanonical S:   S = k_B ln Ω(E)

DEPENDENCIES:
- numpy: Numerical computation
- validators.data_validator: Input validation
- loggers.system_logger: Structured logging
- physics.foundations: Conservation laws and constraints
"""

from typing import Any, Dict

import numpy as np

from loggers.system_logger import SystemLogger
from physics.foundations.conservation_laws import ConservationLaws
from physics.foundations.constraints import PhysicsConstraints
from validators.data_validator import DataValidator

# ── Physical constants ──────────────────────────────────────────────
BOLTZMANN_CONSTANT: float = 1.380649e-23  # J/K (exact, SI 2019)


class EnsembleTheory:
    """
    Statistical ensemble implementation.

    Computes partition functions and thermodynamic averages for
    canonical, grand canonical, and microcanonical ensembles.
    """

    def __init__(self) -> None:
        """Initialize ensemble theory system."""
        self.validator = DataValidator()
        self._logger = SystemLogger()
        self.conservation = ConservationLaws()
        self.constraints = PhysicsConstraints()

        self.delta_quantum: float = 0.0

        self._logger.log("EnsembleTheory initialized", level="INFO")

    def canonical_partition_function(self,
                                      energy_levels: np.ndarray,
                                      temperature: float) -> float:
        """
        Compute canonical partition function.

        Equation: Z = Σ_i exp(-βE_i)  where β = 1/(k_B T)

        Args:
            energy_levels: Array of energy levels E_i
            temperature: Temperature T (must be positive)

        Returns:
            Partition function Z

        Raises:
            ValueError: If temperature is non-positive
        """
        if temperature <= 0:
            self._logger.log("Invalid temperature: must be positive", level="ERROR")
            raise ValueError("Temperature must be positive")

        beta = 1.0 / (BOLTZMANN_CONSTANT * temperature)
        partition_function = float(np.sum(np.exp(-beta * energy_levels)))

        self._logger.log(f"Canonical partition function: Z = {partition_function}", level="INFO")
        return partition_function

    def canonical_probability(self,
                              energy: float,
                              temperature: float,
                              partition_function: float) -> float:
        """
        Compute probability of a state in the canonical ensemble.

        Equation: P_i = (1/Z) exp(-βE_i)

        Args:
            energy: Energy E_i
            temperature: Temperature T
            partition_function: Partition function Z

        Returns:
            Probability P_i

        Raises:
            ValueError: If partition function is non-positive
        """
        if partition_function <= 0:
            self._logger.log("Invalid partition function", level="ERROR")
            raise ValueError("Partition function must be positive")

        beta = 1.0 / (BOLTZMANN_CONSTANT * temperature)
        probability = (1.0 / partition_function) * np.exp(-beta * energy)

        self._logger.log(f"Canonical probability: P = {probability}", level="DEBUG")
        return float(probability)

    def compute_thermodynamic_averages(self,
                                        energy_levels: np.ndarray,
                                        temperature: float) -> Dict[str, float]:
        """
        Compute thermodynamic averages from the canonical ensemble.

        Equations:
            ⟨E⟩ = (1/Z) Σ E_i exp(-βE_i)
            F   = -k_B T ln Z
            S   = k_B (ln Z + β⟨E⟩)

        Args:
            energy_levels: Array of energy levels
            temperature: Temperature T

        Returns:
            Dictionary with average_energy, free_energy, entropy, partition_function
        """
        Z = self.canonical_partition_function(energy_levels, temperature)
        beta = 1.0 / (BOLTZMANN_CONSTANT * temperature)

        weights = np.exp(-beta * energy_levels)
        average_energy = float(np.sum(energy_levels * weights) / Z)

        free_energy = -BOLTZMANN_CONSTANT * temperature * np.log(Z)
        entropy = BOLTZMANN_CONSTANT * (np.log(Z) + beta * average_energy)

        self._logger.log(
            f"Thermodynamic averages: ⟨E⟩ = {average_energy}, F = {free_energy}, S = {entropy}",
            level="INFO"
        )

        return {
            'average_energy': average_energy,
            'free_energy': float(free_energy),
            'entropy': float(entropy),
            'partition_function': Z
        }

    def grand_canonical_partition_function(self,
                                            energy_levels: np.ndarray,
                                            particle_numbers: np.ndarray,
                                            temperature: float,
                                            chemical_potential: float) -> float:
        """
        Compute grand canonical partition function.

        Equation: Ξ = Σ_i exp(-β(E_i - μN_i))

        Args:
            energy_levels: Array of energy levels E_i
            particle_numbers: Array of particle numbers N_i
            temperature: Temperature T
            chemical_potential: Chemical potential μ

        Returns:
            Grand partition function Ξ

        Raises:
            ValueError: If temperature is non-positive
        """
        if temperature <= 0:
            self._logger.log("Invalid temperature", level="ERROR")
            raise ValueError("Temperature must be positive")

        beta = 1.0 / (BOLTZMANN_CONSTANT * temperature)
        grand_partition = float(
            np.sum(np.exp(-beta * (energy_levels - chemical_potential * particle_numbers)))
        )

        self._logger.log(f"Grand canonical partition function: Ξ = {grand_partition}", level="INFO")
        return grand_partition

    def microcanonical_entropy(self,
                                energy: float,
                                number_of_states: int) -> float:
        """
        Compute entropy in the microcanonical ensemble.

        Equation: S = k_B ln Ω(E)

        Args:
            energy: Energy E (unused, for interface consistency)
            number_of_states: Number of accessible microstates Ω

        Returns:
            Entropy S
        """
        entropy = float(BOLTZMANN_CONSTANT * np.log(number_of_states))

        self._logger.log(f"Microcanonical entropy: S = {entropy}", level="DEBUG")
        return entropy

    def set_quantum_correction(self, delta: float) -> None:
        """Set quantum statistics correction (Bose-Einstein / Fermi-Dirac), clamped to [0, 1]."""
        self.delta_quantum = max(0.0, min(1.0, delta))
        self._logger.log(f"Quantum correction set: δ = {self.delta_quantum}", level="INFO")
