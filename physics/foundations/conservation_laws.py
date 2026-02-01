# physics/foundations/
"""
Conservation laws module.

First Principle Analysis:
- Conservation laws are fundamental constraints that all physical theories must respect
- Energy, momentum, charge, and other conserved quantities provide constraints on system evolution
- Mathematical foundation: Noether's theorem links symmetries to conservation laws
- Architecture: Modular conservation checkers that can be applied to any theory

Planning:
1. Implement energy conservation checker
2. Implement momentum conservation checker
3. Implement charge conservation checker
4. Add angular momentum conservation
5. Design for extensibility to other conserved quantities
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from validators.data_validator import DataValidator
from loggers.system_logger import SystemLogger


class ConservationLaws:
    """
    Checks conservation laws for physical systems.
    
    Ensures that energy, momentum, charge, and other conserved quantities
    remain constant throughout system evolution, providing fundamental
    constraints on all physics theories.
    """
    
    def __init__(self, tolerance: float = 1e-10):
        """
        Initialize conservation laws checker.
        
        Args:
            tolerance: Numerical tolerance for conservation checks
        """
        self.tolerance = tolerance
        self.validator = DataValidator()
        self.logger = SystemLogger()
        
        # Fundamental constants
        self.c = 299792458.0  # Speed of light (m/s)
        self.hbar = 1.054571817e-34  # Reduced Planck constant (J·s)
        
        self.logger.log("ConservationLaws initialized", level="INFO")
    
    def check_energy_conservation(self, 
                                  initial_energy: float, 
                                  final_energy: float,
                                  external_work: float = 0.0) -> Tuple[bool, float]:
        """
        Check energy conservation.
        
        Mathematical principle: dE/dt = 0 for closed systems
        For open systems: dE/dt = P_ext (power from external sources)
        
        Args:
            initial_energy: Initial total energy
            final_energy: Final total energy
            external_work: Work done by external forces (default: 0 for closed system)
            
        Returns:
            Tuple of (is_conserved, energy_difference)
        """
        if not self.validator.validate_type(initial_energy, (int, float)):
            self.logger.log("Invalid initial_energy type", level="ERROR")
            raise ValueError("Initial energy must be numeric")
        
        if not self.validator.validate_type(final_energy, (int, float)):
            self.logger.log("Invalid final_energy type", level="ERROR")
            raise ValueError("Final energy must be numeric")
        
        energy_difference = abs(final_energy - initial_energy - external_work)
        is_conserved = energy_difference < self.tolerance
        
        if not is_conserved:
            self.logger.log(
                f"Energy conservation violation: ΔE = {energy_difference}",
                level="WARNING"
            )
        else:
            self.logger.log("Energy conservation verified", level="DEBUG")
        
        return is_conserved, energy_difference
    
    def check_momentum_conservation(self,
                                    initial_momentum: np.ndarray,
                                    final_momentum: np.ndarray,
                                    external_force: np.ndarray = np.array([0.0, 0.0, 0.0]),
                                    time_step: float = 1.0) -> Tuple[bool, float]:
        """
        Check momentum conservation.
        
        Mathematical principle: dp/dt = 0 for closed systems
        For open systems: dp/dt = F_ext (external force)
        
        Args:
            initial_momentum: Initial momentum vector (3D)
            final_momentum: Final momentum vector (3D)
            external_force: External force vector (default: zero)
            time_step: Time interval for force integration
            
        Returns:
            Tuple of (is_conserved, momentum_difference_magnitude)
        """
        initial_momentum = np.array(initial_momentum)
        final_momentum = np.array(final_momentum)
        external_force = np.array(external_force)
        
        # Momentum change from external force
        momentum_change = external_force * time_step
        
        # Check conservation
        momentum_difference = final_momentum - initial_momentum - momentum_change
        difference_magnitude = np.linalg.norm(momentum_difference)
        is_conserved = difference_magnitude < self.tolerance
        
        if not is_conserved:
            self.logger.log(
                f"Momentum conservation violation: |Δp| = {difference_magnitude}",
                level="WARNING"
            )
        else:
            self.logger.log("Momentum conservation verified", level="DEBUG")
        
        return is_conserved, difference_magnitude
    
    def check_charge_conservation(self,
                                   initial_charge: float,
                                   final_charge: float) -> Tuple[bool, float]:
        """
        Check charge conservation.
        
        Mathematical principle: ∂_μ j^μ = 0 (continuity equation)
        Total charge in closed system remains constant
        
        Args:
            initial_charge: Initial total charge
            final_charge: Final total charge
            
        Returns:
            Tuple of (is_conserved, charge_difference)
        """
        charge_difference = abs(final_charge - initial_charge)
        is_conserved = charge_difference < self.tolerance
        
        if not is_conserved:
            self.logger.log(
                f"Charge conservation violation: ΔQ = {charge_difference}",
                level="WARNING"
            )
        else:
            self.logger.log("Charge conservation verified", level="DEBUG")
        
        return is_conserved, charge_difference
    
    def check_angular_momentum_conservation(self,
                                             initial_angular_momentum: np.ndarray,
                                             final_angular_momentum: np.ndarray,
                                             external_torque: np.ndarray = np.array([0.0, 0.0, 0.0]),
                                             time_step: float = 1.0) -> Tuple[bool, float]:
        """
        Check angular momentum conservation.
        
        Mathematical principle: dL/dt = 0 for closed systems
        For open systems: dL/dt = τ_ext (external torque)
        
        Args:
            initial_angular_momentum: Initial angular momentum vector (3D)
            final_angular_momentum: Final angular momentum vector (3D)
            external_torque: External torque vector (default: zero)
            time_step: Time interval for torque integration
            
        Returns:
            Tuple of (is_conserved, angular_momentum_difference_magnitude)
        """
        initial_angular_momentum = np.array(initial_angular_momentum)
        final_angular_momentum = np.array(final_angular_momentum)
        external_torque = np.array(external_torque)
        
        # Angular momentum change from external torque
        angular_momentum_change = external_torque * time_step
        
        # Check conservation
        difference = final_angular_momentum - initial_angular_momentum - angular_momentum_change
        difference_magnitude = np.linalg.norm(difference)
        is_conserved = difference_magnitude < self.tolerance
        
        if not is_conserved:
            self.logger.log(
                f"Angular momentum conservation violation: |ΔL| = {difference_magnitude}",
                level="WARNING"
            )
        else:
            self.logger.log("Angular momentum conservation verified", level="DEBUG")
        
        return is_conserved, difference_magnitude
    
    def check_relativistic_energy_momentum(self,
                                           energy: float,
                                           momentum: np.ndarray,
                                           rest_mass: float) -> Tuple[bool, float]:
        """
        Check relativistic energy-momentum relation.
        
        Mathematical principle: E² = (pc)² + (mc²)²
        
        Args:
            energy: Total energy
            momentum: Momentum vector (3D)
            rest_mass: Rest mass
            
        Returns:
            Tuple of (is_valid, deviation_from_relation)
        """
        momentum_magnitude = np.linalg.norm(momentum)
        pc = momentum_magnitude * self.c
        mc2 = rest_mass * self.c**2
        
        # E² = (pc)² + (mc²)²
        expected_energy_squared = (pc)**2 + (mc2)**2
        actual_energy_squared = energy**2
        
        deviation = abs(actual_energy_squared - expected_energy_squared)
        is_valid = deviation < self.tolerance * (expected_energy_squared + 1.0)
        
        if not is_valid:
            self.logger.log(
                f"Relativistic energy-momentum violation: deviation = {deviation}",
                level="WARNING"
            )
        else:
            self.logger.log("Relativistic energy-momentum relation verified", level="DEBUG")
        
        return is_valid, deviation
    
    def validate_system(self, 
                       initial_state: Dict[str, Any],
                       final_state: Dict[str, Any],
                       external_forces: Optional[Dict[str, Any]] = None) -> Dict[str, Tuple[bool, float]]:
        """
        Validate all conservation laws for a system.
        
        Args:
            initial_state: Dictionary with initial conserved quantities
            final_state: Dictionary with final conserved quantities
            external_forces: Dictionary with external forces/torques
            
        Returns:
            Dictionary mapping conservation law names to (is_conserved, difference) tuples
        """
        if external_forces is None:
            external_forces = {}
        
        results = {}
        
        # Energy conservation
        if 'energy' in initial_state and 'energy' in final_state:
            ext_work = external_forces.get('work', 0.0)
            results['energy'] = self.check_energy_conservation(
                initial_state['energy'],
                final_state['energy'],
                ext_work
            )
        
        # Momentum conservation
        if 'momentum' in initial_state and 'momentum' in final_state:
            ext_force = external_forces.get('force', np.array([0.0, 0.0, 0.0]))
            time_step = external_forces.get('time_step', 1.0)
            results['momentum'] = self.check_momentum_conservation(
                initial_state['momentum'],
                final_state['momentum'],
                ext_force,
                time_step
            )
        
        # Charge conservation
        if 'charge' in initial_state and 'charge' in final_state:
            results['charge'] = self.check_charge_conservation(
                initial_state['charge'],
                final_state['charge']
            )
        
        # Angular momentum conservation
        if 'angular_momentum' in initial_state and 'angular_momentum' in final_state:
            ext_torque = external_forces.get('torque', np.array([0.0, 0.0, 0.0]))
            time_step = external_forces.get('time_step', 1.0)
            results['angular_momentum'] = self.check_angular_momentum_conservation(
                initial_state['angular_momentum'],
                final_state['angular_momentum'],
                ext_torque,
                time_step
            )
        
        self.logger.log(f"Conservation validation completed: {len(results)} laws checked", level="INFO")
        return results

