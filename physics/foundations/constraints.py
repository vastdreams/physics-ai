# physics/foundations/
"""
Physics constraints module.

First Principle Analysis:
- Physical constraints are fundamental bounds that all theories must respect
- Causality, unitarity, energy positivity, and speed limits are universal
- Mathematical foundation: Relativity, quantum mechanics, thermodynamics
- Architecture: Modular constraint checkers that prevent unphysical states

Planning:
1. Implement causality constraints (no faster-than-light)
2. Implement unitarity constraints (probability conservation)
3. Implement energy positivity constraints
4. Add thermodynamic constraints (entropy, temperature bounds)
5. Design for theory-specific constraint validation
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from validators.data_validator import DataValidator
from loggers.system_logger import SystemLogger


class PhysicsConstraints:
    """
    Checks fundamental physical constraints.
    
    Ensures that all physical theories respect universal constraints
    such as causality, unitarity, and energy bounds.
    """
    
    def __init__(self):
        """Initialize physics constraints checker."""
        self.validator = DataValidator()
        self.logger = SystemLogger()
        
        # Fundamental constants
        self.c = 299792458.0  # Speed of light (m/s)
        self.k_B = 1.380649e-23  # Boltzmann constant (J/K)
        self.hbar = 1.054571817e-34  # Reduced Planck constant (J·s)
        
        self.logger.log("PhysicsConstraints initialized", level="INFO")
    
    def check_causality(self,
                        velocity: np.ndarray,
                        tolerance: float = 1e-6) -> Tuple[bool, float]:
        """
        Check causality constraint (no faster-than-light).
        
        Mathematical principle: |v| ≤ c (speed of light)
        Violation would allow time travel and break causality
        
        Args:
            velocity: Velocity vector (3D) in m/s
            tolerance: Numerical tolerance
            
        Returns:
            Tuple of (is_causal, speed_ratio)
        """
        velocity = np.array(velocity)
        speed = np.linalg.norm(velocity)
        speed_ratio = speed / self.c
        
        is_causal = speed_ratio <= 1.0 + tolerance
        
        if not is_causal:
            self.logger.log(
                f"Causality violation: v/c = {speed_ratio} > 1",
                level="ERROR"
            )
        else:
            self.logger.log(f"Causality verified: v/c = {speed_ratio}", level="DEBUG")
        
        return is_causal, speed_ratio
    
    def check_energy_positivity(self,
                                 energy: float,
                                 tolerance: float = 1e-10) -> Tuple[bool, float]:
        """
        Check energy positivity constraint.
        
        Mathematical principle: E ≥ 0 (for physical states)
        Negative energy states are unphysical
        
        Args:
            energy: Energy value
            tolerance: Numerical tolerance
            
        Returns:
            Tuple of (is_positive, energy_value)
        """
        is_positive = energy >= -tolerance
        
        if not is_positive:
            self.logger.log(
                f"Energy positivity violation: E = {energy} < 0",
                level="ERROR"
            )
        else:
            self.logger.log(f"Energy positivity verified: E = {energy}", level="DEBUG")
        
        return is_positive, energy
    
    def check_unitarity(self,
                        probability_amplitudes: np.ndarray,
                        tolerance: float = 1e-10) -> Tuple[bool, float]:
        """
        Check unitarity constraint (probability conservation).
        
        Mathematical principle: Σ|ψ_i|² = 1 (normalization)
        Quantum mechanics requires probability conservation
        
        Args:
            probability_amplitudes: Array of probability amplitudes
            tolerance: Numerical tolerance
            
        Returns:
            Tuple of (is_unitary, total_probability)
        """
        probability_amplitudes = np.array(probability_amplitudes)
        total_probability = np.sum(np.abs(probability_amplitudes)**2)
        deviation = abs(total_probability - 1.0)
        is_unitary = deviation < tolerance
        
        if not is_unitary:
            self.logger.log(
                f"Unitarity violation: total probability = {total_probability} ≠ 1",
                level="WARNING"
            )
        else:
            self.logger.log(f"Unitarity verified: total probability = {total_probability}", level="DEBUG")
        
        return is_unitary, total_probability
    
    def check_thermodynamic_constraints(self,
                                         entropy: float,
                                         temperature: float) -> Tuple[bool, Dict[str, bool]]:
        """
        Check thermodynamic constraints.
        
        Mathematical principles:
        - Entropy: S ≥ 0 (third law of thermodynamics)
        - Temperature: T ≥ 0 (absolute zero is minimum)
        - Entropy increases in isolated systems
        
        Args:
            entropy: Entropy value
            temperature: Temperature value
            
        Returns:
            Tuple of (all_valid, constraint_results)
        """
        results = {}
        
        # Entropy non-negativity
        entropy_valid = entropy >= 0.0
        results['entropy_positive'] = entropy_valid
        if not entropy_valid:
            self.logger.log(f"Entropy constraint violation: S = {entropy} < 0", level="WARNING")
        
        # Temperature non-negativity
        temperature_valid = temperature >= 0.0
        results['temperature_positive'] = temperature_valid
        if not temperature_valid:
            self.logger.log(f"Temperature constraint violation: T = {temperature} < 0", level="WARNING")
        
        all_valid = entropy_valid and temperature_valid
        
        if all_valid:
            self.logger.log("Thermodynamic constraints verified", level="DEBUG")
        
        return all_valid, results
    
    def check_uncertainty_principle(self,
                                     position_uncertainty: float,
                                     momentum_uncertainty: float) -> Tuple[bool, float]:
        """
        Check Heisenberg uncertainty principle.
        
        Mathematical principle: Δx·Δp ≥ ℏ/2
        
        Args:
            position_uncertainty: Uncertainty in position
            momentum_uncertainty: Uncertainty in momentum
            
        Returns:
            Tuple of (satisfies_uncertainty, product_value)
        """
        product = position_uncertainty * momentum_uncertainty
        minimum = self.hbar / 2.0
        
        satisfies = product >= minimum
        
        if not satisfies:
            self.logger.log(
                f"Uncertainty principle violation: Δx·Δp = {product} < ℏ/2 = {minimum}",
                level="WARNING"
            )
        else:
            self.logger.log(f"Uncertainty principle verified: Δx·Δp = {product}", level="DEBUG")
        
        return satisfies, product
    
    def check_energy_time_uncertainty(self,
                                       energy_uncertainty: float,
                                       time_uncertainty: float) -> Tuple[bool, float]:
        """
        Check energy-time uncertainty principle.
        
        Mathematical principle: ΔE·Δt ≥ ℏ/2
        
        Args:
            energy_uncertainty: Uncertainty in energy
            time_uncertainty: Uncertainty in time
            
        Returns:
            Tuple of (satisfies_uncertainty, product_value)
        """
        product = energy_uncertainty * time_uncertainty
        minimum = self.hbar / 2.0
        
        satisfies = product >= minimum
        
        if not satisfies:
            self.logger.log(
                f"Energy-time uncertainty violation: ΔE·Δt = {product} < ℏ/2 = {minimum}",
                level="WARNING"
            )
        else:
            self.logger.log(f"Energy-time uncertainty verified: ΔE·Δt = {product}", level="DEBUG")
        
        return satisfies, product
    
    def check_relativistic_bounds(self,
                                   energy: float,
                                   momentum: np.ndarray,
                                   rest_mass: float) -> Tuple[bool, Dict[str, bool]]:
        """
        Check relativistic bounds.
        
        Mathematical principles:
        - E ≥ mc² (rest energy is minimum)
        - |p| ≤ E/c (momentum bound)
        - v ≤ c (velocity bound)
        
        Args:
            energy: Total energy
            momentum: Momentum vector
            rest_mass: Rest mass
            
        Returns:
            Tuple of (all_valid, constraint_results)
        """
        results = {}
        
        # Energy bound: E ≥ mc²
        rest_energy = rest_mass * self.c**2
        energy_bound = energy >= rest_energy
        results['energy_bound'] = energy_bound
        if not energy_bound:
            self.logger.log(
                f"Relativistic energy bound violation: E = {energy} < mc² = {rest_energy}",
                level="WARNING"
            )
        
        # Momentum bound: |p| ≤ E/c
        momentum_magnitude = np.linalg.norm(momentum)
        momentum_bound_value = energy / self.c
        momentum_bound = momentum_magnitude <= momentum_bound_value + 1e-6
        results['momentum_bound'] = momentum_bound
        if not momentum_bound:
            self.logger.log(
                f"Relativistic momentum bound violation: |p| = {momentum_magnitude} > E/c = {momentum_bound_value}",
                level="WARNING"
            )
        
        # Velocity bound: v ≤ c
        if energy > rest_energy:
            velocity_magnitude = momentum_magnitude * self.c**2 / energy
            velocity_bound, speed_ratio = self.check_causality(
                np.array([velocity_magnitude, 0, 0])
            )
            results['velocity_bound'] = velocity_bound
        else:
            results['velocity_bound'] = True
        
        all_valid = all(results.values())
        
        if all_valid:
            self.logger.log("Relativistic bounds verified", level="DEBUG")
        
        return all_valid, results
    
    def validate_system(self, system_state: Dict[str, Any]) -> Dict[str, Tuple[bool, Any]]:
        """
        Validate all constraints for a physical system.
        
        Args:
            system_state: Dictionary with system state variables
            
        Returns:
            Dictionary mapping constraint names to (is_valid, value) tuples
        """
        results = {}
        
        # Causality check
        if 'velocity' in system_state:
            velocity = system_state['velocity']
            results['causality'] = self.check_causality(velocity)
        
        # Energy positivity
        if 'energy' in system_state:
            energy = system_state['energy']
            results['energy_positivity'] = self.check_energy_positivity(energy)
        
        # Unitarity
        if 'wave_function' in system_state:
            wave_function = system_state['wave_function']
            results['unitarity'] = self.check_unitarity(wave_function)
        
        # Thermodynamic constraints
        if 'entropy' in system_state and 'temperature' in system_state:
            entropy = system_state['entropy']
            temperature = system_state['temperature']
            valid, constraint_results = self.check_thermodynamic_constraints(entropy, temperature)
            results['thermodynamics'] = (valid, constraint_results)
        
        # Uncertainty principles
        if 'position_uncertainty' in system_state and 'momentum_uncertainty' in system_state:
            delta_x = system_state['position_uncertainty']
            delta_p = system_state['momentum_uncertainty']
            results['uncertainty_principle'] = self.check_uncertainty_principle(delta_x, delta_p)
        
        # Relativistic bounds
        if all(key in system_state for key in ['energy', 'momentum', 'rest_mass']):
            energy = system_state['energy']
            momentum = system_state['momentum']
            rest_mass = system_state['rest_mass']
            valid, constraint_results = self.check_relativistic_bounds(energy, momentum, rest_mass)
            results['relativistic_bounds'] = (valid, constraint_results)
        
        self.logger.log(f"Constraint validation completed: {len(results)} constraints checked", level="INFO")
        return results

