# physics/domains/statistical/
"""
Phase transitions module.

First Principle Analysis:
- Phase transitions occur when free energy has non-analytic behavior
- Critical exponents describe behavior near critical point
- Landau theory: F = F₀ + a(T-T_c)φ² + bφ⁴
- Mathematical foundation: Renormalization group, critical phenomena
- Architecture: Modular phase transition models with synergy for corrections

Planning:
1. Implement Landau theory for phase transitions
2. Add critical exponent calculations
3. Implement order parameter calculations
4. Add phase diagrams
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


class PhaseTransitions:
    """
    Phase transition implementation.
    
    Implements models for phase transitions and critical phenomena
    with support for various transition types.
    """
    
    def __init__(self):
        """Initialize phase transitions system."""
        self.validator = DataValidator()
        self.logger = SystemLogger()
        self.conservation = ConservationLaws()
        self.constraints = PhysicsConstraints()
        
        # Fundamental constants
        self.k_B = 1.380649e-23  # Boltzmann constant (J/K)
        
        # Synergy factors
        self.delta_quantum = 0.0  # Quantum corrections
        
        self.logger.log("PhaseTransitions initialized", level="INFO")
    
    def landau_free_energy(self,
                            order_parameter: float,
                            temperature: float,
                            critical_temperature: float,
                            coefficient_a: float,
                            coefficient_b: float) -> float:
        """
        Compute Landau free energy.
        
        Mathematical principle: F = F₀ + a(T-T_c)φ² + bφ⁴
        
        Args:
            order_parameter: Order parameter φ
            temperature: Temperature T
            critical_temperature: Critical temperature T_c
            coefficient_a: Coefficient a
            coefficient_b: Coefficient b
            
        Returns:
            Free energy F
        """
        free_energy = coefficient_a * (temperature - critical_temperature) * order_parameter**2 + \
                     coefficient_b * order_parameter**4
        
        self.logger.log(f"Landau free energy: F = {free_energy}", level="DEBUG")
        return free_energy
    
    def compute_order_parameter(self,
                                 temperature: float,
                                 critical_temperature: float,
                                 coefficient_a: float,
                                 coefficient_b: float) -> float:
        """
        Compute equilibrium order parameter from Landau theory.
        
        Mathematical principle: ∂F/∂φ = 0 → φ = 0 or φ² = -a(T-T_c)/(2b)
        
        Args:
            temperature: Temperature T
            critical_temperature: Critical temperature T_c
            coefficient_a: Coefficient a
            coefficient_b: Coefficient b
            
        Returns:
            Order parameter φ
        """
        if temperature >= critical_temperature:
            # Above T_c: φ = 0 (disordered phase)
            order_parameter = 0.0
        else:
            # Below T_c: φ² = -a(T-T_c)/(2b)
            order_parameter_squared = -coefficient_a * (temperature - critical_temperature) / (2 * coefficient_b)
            if order_parameter_squared > 0:
                order_parameter = np.sqrt(order_parameter_squared)
            else:
                order_parameter = 0.0
        
        self.logger.log(f"Order parameter: φ = {order_parameter}", level="DEBUG")
        return order_parameter
    
    def critical_exponent_beta(self,
                                order_parameter: float,
                                reduced_temperature: float) -> float:
        """
        Compute critical exponent β: φ ~ |t|^β near T_c.
        
        Mathematical principle: φ ~ |t|^β where t = (T-T_c)/T_c
        
        Args:
            order_parameter: Order parameter φ
            reduced_temperature: Reduced temperature t = (T-T_c)/T_c
            
        Returns:
            Critical exponent β
        """
        if abs(reduced_temperature) < 1e-10 or abs(order_parameter) < 1e-10:
            return 0.5  # Mean field value
        
        # β = ln(φ) / ln(|t|)
        beta = np.log(abs(order_parameter)) / np.log(abs(reduced_temperature))
        
        self.logger.log(f"Critical exponent β = {beta}", level="DEBUG")
        return beta
    
    def critical_exponent_alpha(self,
                                 heat_capacity: float,
                                 reduced_temperature: float,
                                 critical_heat_capacity: float) -> float:
        """
        Compute critical exponent α: C ~ |t|^(-α) near T_c.
        
        Mathematical principle: C ~ |t|^(-α)
        
        Args:
            heat_capacity: Heat capacity C
            reduced_temperature: Reduced temperature t
            critical_heat_capacity: Critical heat capacity C_c
            
        Returns:
            Critical exponent α
        """
        if abs(reduced_temperature) < 1e-10:
            return 0.0
        
        # C - C_c ~ |t|^(-α)
        # α = -ln((C-C_c)/C_c) / ln(|t|)
        if abs(critical_heat_capacity) > 1e-10:
            alpha = -np.log(abs((heat_capacity - critical_heat_capacity) / critical_heat_capacity)) / \
                    np.log(abs(reduced_temperature))
        else:
            alpha = 0.0
        
        self.logger.log(f"Critical exponent α = {alpha}", level="DEBUG")
        return alpha
    
    def set_quantum_correction(self, delta: float) -> None:
        """Set quantum corrections for phase transitions."""
        self.delta_quantum = max(0.0, min(1.0, delta))
        self.logger.log(f"Quantum correction set: δ = {self.delta_quantum}", level="INFO")

