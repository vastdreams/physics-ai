# physics/solvers/
"""
Perturbation theory solver module.

First Principle Analysis:
- Perturbation theory solves equations with small parameters
- Expansion: x = x_0 + ε x_1 + ε² x_2 + ...
- Mathematical foundation: Asymptotic analysis
- Architecture: Modular perturbation expansions

Planning:
1. Implement regular perturbation expansion
2. Add singular perturbation methods
3. Implement multi-scale analysis
4. Add asymptotic matching
"""

from typing import Any, Dict, List, Optional, Callable
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from validators.data_validator import DataValidator
from loggers.system_logger import SystemLogger


class PerturbationSolver:
    """
    Perturbation theory solver implementation.
    
    Solves equations using perturbation expansions.
    """
    
    def __init__(self):
        """Initialize perturbation solver."""
        self.validator = DataValidator()
        self.logger = SystemLogger()
        
        self.logger.log("PerturbationSolver initialized", level="INFO")
    
    def regular_perturbation(self,
                             unperturbed_solution: Callable,
                             perturbation: Callable,
                             epsilon: float,
                             order: int = 2) -> Callable:
        """
        Compute regular perturbation expansion.
        
        Mathematical principle: x(ε) = x_0 + ε x_1 + ε² x_2 + ...
        
        Args:
            unperturbed_solution: Zeroth order solution x_0
            perturbation: Perturbation function
            epsilon: Small parameter ε
            order: Expansion order
            
        Returns:
            Perturbed solution function
        """
        # Simplified: return unperturbed solution with first order correction
        def perturbed_solution(t):
            x0 = unperturbed_solution(t)
            x1 = perturbation(t)  # First order correction
            return x0 + epsilon * x1
        
        self.logger.log(f"Regular perturbation: order {order}", level="DEBUG")
        return perturbed_solution

