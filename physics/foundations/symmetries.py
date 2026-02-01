# physics/foundations/
"""
Symmetries module.

First Principle Analysis:
- Symmetries are fundamental to physics and lead to conservation laws via Noether's theorem
- Continuous symmetries (translation, rotation, gauge) generate conserved quantities
- Discrete symmetries (parity, time reversal, charge conjugation) constrain interactions
- Mathematical foundation: Group theory, Lie algebras, gauge theory
- Architecture: Modular symmetry checkers for different symmetry types

Planning:
1. Implement continuous symmetry checkers (translation, rotation, gauge)
2. Implement discrete symmetry checkers (P, T, C)
3. Add Noether's theorem integration
4. Design for theory-specific symmetry validation
"""

from typing import Any, Dict, List, Optional, Tuple, Callable
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from validators.data_validator import DataValidator
from loggers.system_logger import SystemLogger


class SymmetryChecker:
    """
    Checks symmetry properties of physical systems.
    
    Validates that physical laws respect fundamental symmetries,
    which are linked to conservation laws via Noether's theorem.
    """
    
    def __init__(self, tolerance: float = 1e-10):
        """
        Initialize symmetry checker.
        
        Args:
            tolerance: Numerical tolerance for symmetry checks
        """
        self.tolerance = tolerance
        self.validator = DataValidator()
        self.logger = SystemLogger()
        
        self.logger.log("SymmetryChecker initialized", level="INFO")
    
    def check_translation_symmetry(self,
                                    system_function: Callable,
                                    position: np.ndarray,
                                    translation: np.ndarray) -> Tuple[bool, float]:
        """
        Check translation symmetry.
        
        Mathematical principle: Physics should be invariant under spatial translations
        Leads to momentum conservation via Noether's theorem
        
        Args:
            system_function: Function f(x) representing the system
            position: Original position vector
            translation: Translation vector
            
        Returns:
            Tuple of (is_symmetric, deviation)
        """
        original_value = system_function(position)
        translated_position = position + np.array(translation)
        translated_value = system_function(translated_position)
        
        deviation = abs(original_value - translated_value)
        is_symmetric = deviation < self.tolerance
        
        if not is_symmetric:
            self.logger.log(
                f"Translation symmetry violation: deviation = {deviation}",
                level="WARNING"
            )
        else:
            self.logger.log("Translation symmetry verified", level="DEBUG")
        
        return is_symmetric, deviation


# Alias for compatibility
class Symmetries(SymmetryChecker):
    """Backward-compatible alias for symmetry checker."""
    
    def check_rotation_symmetry(self,
                                 system_function: Callable,
                                 position: np.ndarray,
                                 rotation_angle: float,
                                 axis: np.ndarray = np.array([0, 0, 1])) -> Tuple[bool, float]:
        """
        Check rotation symmetry.
        
        Mathematical principle: Physics should be invariant under rotations
        Leads to angular momentum conservation via Noether's theorem
        
        Args:
            system_function: Function f(x) representing the system
            position: Original position vector
            rotation_angle: Rotation angle in radians
            axis: Rotation axis (default: z-axis)
            
        Returns:
            Tuple of (is_symmetric, deviation)
        """
        # Rotation matrix around axis
        axis = axis / np.linalg.norm(axis)  # Normalize
        cos_a = np.cos(rotation_angle)
        sin_a = np.sin(rotation_angle)
        
        # Rodrigues' rotation formula
        K = np.array([
            [0, -axis[2], axis[1]],
            [axis[2], 0, -axis[0]],
            [-axis[1], axis[0], 0]
        ])
        R = np.eye(3) + sin_a * K + (1 - cos_a) * np.dot(K, K)
        
        original_value = system_function(position)
        rotated_position = np.dot(R, position)
        rotated_value = system_function(rotated_position)
        
        deviation = abs(original_value - rotated_value)
        is_symmetric = deviation < self.tolerance
        
        if not is_symmetric:
            self.logger.log(
                f"Rotation symmetry violation: deviation = {deviation}",
                level="WARNING"
            )
        else:
            self.logger.log("Rotation symmetry verified", level="DEBUG")
        
        return is_symmetric, deviation
    
    def check_time_translation_symmetry(self,
                                         system_function: Callable,
                                         time: float,
                                         time_shift: float) -> Tuple[bool, float]:
        """
        Check time translation symmetry.
        
        Mathematical principle: Physics should be invariant under time translations
        Leads to energy conservation via Noether's theorem
        
        Args:
            system_function: Function f(t) representing the system
            time: Original time
            time_shift: Time translation
            
        Returns:
            Tuple of (is_symmetric, deviation)
        """
        original_value = system_function(time)
        shifted_time = time + time_shift
        shifted_value = system_function(shifted_time)
        
        deviation = abs(original_value - shifted_value)
        is_symmetric = deviation < self.tolerance
        
        if not is_symmetric:
            self.logger.log(
                f"Time translation symmetry violation: deviation = {deviation}",
                level="WARNING"
            )
        else:
            self.logger.log("Time translation symmetry verified", level="DEBUG")
        
        return is_symmetric, deviation
    
    def check_gauge_symmetry(self,
                              field_configuration: Dict[str, np.ndarray],
                              gauge_transformation: Callable) -> Tuple[bool, float]:
        """
        Check gauge symmetry.
        
        Mathematical principle: Physics should be invariant under gauge transformations
        Essential for quantum field theory and electromagnetism
        
        Args:
            field_configuration: Dictionary of field values
            gauge_transformation: Function that applies gauge transformation
            
        Returns:
            Tuple of (is_symmetric, deviation)
        """
        # This is a simplified check - full gauge symmetry requires checking
        # that the action/Lagrangian is invariant
        # For now, we check if observable quantities are unchanged
        
        original_observable = self._compute_observable(field_configuration)
        transformed_fields = gauge_transformation(field_configuration)
        transformed_observable = self._compute_observable(transformed_fields)
        
        deviation = abs(original_observable - transformed_observable)
        is_symmetric = deviation < self.tolerance
        
        if not is_symmetric:
            self.logger.log(
                f"Gauge symmetry violation: deviation = {deviation}",
                level="WARNING"
            )
        else:
            self.logger.log("Gauge symmetry verified", level="DEBUG")
        
        return is_symmetric, deviation
    
    def check_parity_symmetry(self,
                               system_function: Callable,
                               position: np.ndarray) -> Tuple[bool, float]:
        """
        Check parity (P) symmetry.
        
        Mathematical principle: P: x → -x
        Some interactions violate parity (weak interaction)
        
        Args:
            system_function: Function f(x) representing the system
            position: Position vector
            
        Returns:
            Tuple of (is_symmetric, deviation)
        """
        original_value = system_function(position)
        parity_transformed = system_function(-position)
        
        deviation = abs(original_value - parity_transformed)
        is_symmetric = deviation < self.tolerance
        
        if not is_symmetric:
            self.logger.log(
                f"Parity symmetry violation: deviation = {deviation}",
                level="WARNING"
            )
        else:
            self.logger.log("Parity symmetry verified", level="DEBUG")
        
        return is_symmetric, deviation
    
    def check_time_reversal_symmetry(self,
                                      system_function: Callable,
                                      time: float) -> Tuple[bool, float]:
        """
        Check time reversal (T) symmetry.
        
        Mathematical principle: T: t → -t
        Some processes violate time reversal (weak interaction, dissipation)
        
        Args:
            system_function: Function f(t) representing the system
            time: Time value
            
        Returns:
            Tuple of (is_symmetric, deviation)
        """
        original_value = system_function(time)
        time_reversed = system_function(-time)
        
        deviation = abs(original_value - time_reversed)
        is_symmetric = deviation < self.tolerance
        
        if not is_symmetric:
            self.logger.log(
                f"Time reversal symmetry violation: deviation = {deviation}",
                level="WARNING"
            )
        else:
            self.logger.log("Time reversal symmetry verified", level="DEBUG")
        
        return is_symmetric, deviation
    
    def _compute_observable(self, field_configuration: Dict[str, np.ndarray]) -> float:
        """
        Compute an observable quantity from field configuration.
        
        For gauge symmetry, we need gauge-invariant observables.
        Example: |E|² + |B|² for electromagnetic fields
        
        Args:
            field_configuration: Dictionary of field values
            
        Returns:
            Observable value
        """
        # Simple implementation: sum of field magnitudes squared
        observable = 0.0
        for field_name, field_value in field_configuration.items():
            if isinstance(field_value, np.ndarray):
                observable += np.sum(field_value**2)
            else:
                observable += field_value**2
        
        return observable
    
    def apply_noether_theorem(self,
                               symmetry_type: str,
                               lagrangian: Callable) -> Optional[str]:
        """
        Apply Noether's theorem to identify conserved quantity.
        
        Mathematical principle: Continuous symmetry → Conserved quantity
        - Translation symmetry → Momentum conservation
        - Rotation symmetry → Angular momentum conservation
        - Time translation → Energy conservation
        
        Args:
            symmetry_type: Type of symmetry ('translation', 'rotation', 'time')
            lagrangian: Lagrangian function L(q, q_dot, t)
            
        Returns:
            Name of conserved quantity or None
        """
        noether_map = {
            'translation': 'momentum',
            'rotation': 'angular_momentum',
            'time': 'energy'
        }
        
        conserved_quantity = noether_map.get(symmetry_type)
        
        if conserved_quantity:
            self.logger.log(
                f"Noether's theorem: {symmetry_type} symmetry → {conserved_quantity} conservation",
                level="INFO"
            )
        
        return conserved_quantity

