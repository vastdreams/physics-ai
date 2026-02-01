# physics/domains/statistical/
"""
Ensemble theory module.

First Principle Analysis:
- Ensembles describe probability distributions over microstates
- Canonical: fixed T, V, N → partition function Z = Σ exp(-E_i/k_B T)
- Grand canonical: fixed T, V, μ → grand partition function
- Mathematical foundation: Probability theory, partition functions
- Architecture: Modular ensemble implementations with synergy for quantum corrections

Planning:
1. Implement canonical ensemble (fixed T, V, N)
2. Add grand canonical ensemble (fixed T, V, μ)
3. Implement microcanonical ensemble (fixed E, V, N)
4. Add partition function calculations
"""

from typing import Any, Dict, List, Optional, Callable
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from validators.data_validator import DataValidator
from loggers.system_logger import SystemLogger
from physics.foundations.conservation_laws import ConservationLaws
from physics.foundations.constraints import PhysicsConstraints


class EnsembleTheory:
    """
    Ensemble theory implementation.
    
    Implements statistical ensembles for computing thermodynamic
    properties from microscopic states.
    """
    
    def __init__(self):
        """Initialize ensemble theory system."""
        self.validator = DataValidator()
        self.logger = SystemLogger()
        self.conservation = ConservationLaws()
        self.constraints = PhysicsConstraints()
        
        # Fundamental constants
        self.k_B = 1.380649e-23  # Boltzmann constant (J/K)
        
        # Synergy factors
        self.delta_quantum = 0.0  # Quantum statistics corrections
        
        self.logger.log("EnsembleTheory initialized", level="INFO")
    
    def canonical_partition_function(self,
                                      energy_levels: np.ndarray,
                                      temperature: float) -> float:
        """
        Compute canonical partition function Z = Σ exp(-E_i/k_B T).
        
        Mathematical principle: Z = Σ_i exp(-βE_i) where β = 1/(k_B T)
        
        Args:
            energy_levels: Array of energy levels E_i
            temperature: Temperature T
            
        Returns:
            Partition function Z
        """
        if temperature <= 0:
            self.logger.log("Invalid temperature: must be positive", level="ERROR")
            raise ValueError("Temperature must be positive")
        
        beta = 1.0 / (self.k_B * temperature)
        partition_function = np.sum(np.exp(-beta * energy_levels))
        
        self.logger.log(f"Canonical partition function: Z = {partition_function}", level="INFO")
        return partition_function
    
    def canonical_probability(self,
                              energy: float,
                              temperature: float,
                              partition_function: float) -> float:
        """
        Compute probability of state in canonical ensemble.
        
        Mathematical principle: P_i = (1/Z) exp(-E_i/k_B T)
        
        Args:
            energy: Energy E_i
            temperature: Temperature T
            partition_function: Partition function Z
            
        Returns:
            Probability P_i
        """
        if partition_function <= 0:
            self.logger.log("Invalid partition function", level="ERROR")
            raise ValueError("Partition function must be positive")
        
        beta = 1.0 / (self.k_B * temperature)
        probability = (1.0 / partition_function) * np.exp(-beta * energy)
        
        self.logger.log(f"Canonical probability: P = {probability}", level="DEBUG")
        return probability
    
    def compute_thermodynamic_averages(self,
                                        energy_levels: np.ndarray,
                                        temperature: float) -> Dict[str, float]:
        """
        Compute thermodynamic averages from canonical ensemble.
        
        Mathematical principles:
        - <E> = (1/Z) Σ E_i exp(-βE_i)
        - F = -k_B T ln Z
        - S = k_B (ln Z + β<E>)
        
        Args:
            energy_levels: Array of energy levels
            temperature: Temperature T
            
        Returns:
            Dictionary with average energy, free energy, entropy
        """
        Z = self.canonical_partition_function(energy_levels, temperature)
        beta = 1.0 / (self.k_B * temperature)
        
        # Average energy: <E> = (1/Z) Σ E_i exp(-βE_i)
        weights = np.exp(-beta * energy_levels)
        average_energy = np.sum(energy_levels * weights) / Z
        
        # Helmholtz free energy: F = -k_B T ln Z
        free_energy = -self.k_B * temperature * np.log(Z)
        
        # Entropy: S = k_B (ln Z + β<E>)
        entropy = self.k_B * (np.log(Z) + beta * average_energy)
        
        self.logger.log(
            f"Thermodynamic averages: <E> = {average_energy}, F = {free_energy}, S = {entropy}",
            level="INFO"
        )
        
        return {
            'average_energy': average_energy,
            'free_energy': free_energy,
            'entropy': entropy,
            'partition_function': Z
        }
    
    def grand_canonical_partition_function(self,
                                            energy_levels: np.ndarray,
                                            particle_numbers: np.ndarray,
                                            temperature: float,
                                            chemical_potential: float) -> float:
        """
        Compute grand canonical partition function Ξ = Σ exp(-β(E_i - μN_i)).
        
        Mathematical principle: Ξ = Σ_i exp(-β(E_i - μN_i))
        
        Args:
            energy_levels: Array of energy levels E_i
            particle_numbers: Array of particle numbers N_i
            temperature: Temperature T
            chemical_potential: Chemical potential μ
            
        Returns:
            Grand partition function Ξ
        """
        if temperature <= 0:
            self.logger.log("Invalid temperature", level="ERROR")
            raise ValueError("Temperature must be positive")
        
        beta = 1.0 / (self.k_B * temperature)
        grand_partition = np.sum(np.exp(-beta * (energy_levels - chemical_potential * particle_numbers)))
        
        self.logger.log(f"Grand canonical partition function: Ξ = {grand_partition}", level="INFO")
        return grand_partition
    
    def microcanonical_entropy(self,
                                energy: float,
                                number_of_states: int) -> float:
        """
        Compute entropy in microcanonical ensemble.
        
        Mathematical principle: S = k_B ln Ω(E)
        
        Args:
            energy: Energy E
            number_of_states: Number of states at energy E
            
        Returns:
            Entropy S
        """
        entropy = self.k_B * np.log(number_of_states)
        
        self.logger.log(f"Microcanonical entropy: S = {entropy}", level="DEBUG")
        return entropy
    
    def set_quantum_correction(self, delta: float) -> None:
        """Set quantum statistics correction factor (Bose-Einstein, Fermi-Dirac)."""
        self.delta_quantum = max(0.0, min(1.0, delta))
        self.logger.log(f"Quantum correction set: δ = {self.delta_quantum}", level="INFO")

