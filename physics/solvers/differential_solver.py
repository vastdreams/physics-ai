# physics/solvers/
"""
Differential equation solver module.

First Principle Analysis:
- Many physics equations are differential equations
- ODE: d²x/dt² = f(x, dx/dt, t)
- PDE: ∂²u/∂t² = c²∇²u
- Mathematical foundation: Numerical methods, finite differences
- Architecture: Modular solvers respecting first-principles constraints

Planning:
1. Implement ODE solvers (Euler, Runge-Kutta)
2. Add PDE solvers (finite difference, finite element)
3. Implement adaptive step size methods
4. Add constraint checking during integration
"""

from typing import Any, Dict, List, Optional, Callable
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from validators.data_validator import DataValidator
from loggers.system_logger import SystemLogger
from physics.foundations.constraints import PhysicsConstraints


class DifferentialSolver:
    """
    Differential equation solver implementation.
    
    Solves ODEs and PDEs with constraint checking to ensure
    physical consistency.
    """
    
    def __init__(self):
        """Initialize differential solver."""
        self.validator = DataValidator()
        self.logger = SystemLogger()
        self.constraints = PhysicsConstraints()
        
        self.logger.log("DifferentialSolver initialized", level="INFO")
    
    def euler_method(self,
                     derivative_function: Callable,
                     initial_condition: np.ndarray,
                     time_step: float,
                     num_steps: int) -> Dict[str, np.ndarray]:
        """
        Solve ODE using Euler method.
        
        Mathematical principle: y(t+dt) = y(t) + f(t, y(t)) * dt
        
        Args:
            derivative_function: Function f(t, y) returning dy/dt
            initial_condition: Initial condition y(0)
            time_step: Time step dt
            num_steps: Number of steps
            
        Returns:
            Dictionary with solution array and times
        """
        solution = np.zeros((num_steps + 1, len(initial_condition)))
        times = np.zeros(num_steps + 1)
        
        solution[0] = np.array(initial_condition)
        times[0] = 0.0
        
        for i in range(num_steps):
            t = times[i]
            y = solution[i]
            
            # Compute derivative
            dydt = derivative_function(t, y)
            
            # Euler step
            solution[i + 1] = y + dydt * time_step
            times[i + 1] = t + time_step
        
        self.logger.log(f"Euler method: {num_steps} steps completed", level="INFO")
        return {'solution': solution, 'times': times}
    
    def runge_kutta_4(self,
                       derivative_function: Callable,
                       initial_condition: np.ndarray,
                       time_step: float,
                       num_steps: int) -> Dict[str, np.ndarray]:
        """
        Solve ODE using 4th order Runge-Kutta method.
        
        Mathematical principle: More accurate than Euler method
        
        Args:
            derivative_function: Function f(t, y) returning dy/dt
            initial_condition: Initial condition y(0)
            time_step: Time step dt
            num_steps: Number of steps
            
        Returns:
            Dictionary with solution array and times
        """
        solution = np.zeros((num_steps + 1, len(initial_condition)))
        times = np.zeros(num_steps + 1)
        
        solution[0] = np.array(initial_condition)
        times[0] = 0.0
        
        for i in range(num_steps):
            t = times[i]
            y = solution[i]
            
            # RK4 stages
            k1 = derivative_function(t, y)
            k2 = derivative_function(t + time_step/2, y + time_step*k1/2)
            k3 = derivative_function(t + time_step/2, y + time_step*k2/2)
            k4 = derivative_function(t + time_step, y + time_step*k3)
            
            # RK4 step
            solution[i + 1] = y + (time_step/6) * (k1 + 2*k2 + 2*k3 + k4)
            times[i + 1] = t + time_step
        
        self.logger.log(f"Runge-Kutta 4: {num_steps} steps completed", level="INFO")
        return {'solution': solution, 'times': times}
    
    def solve_with_constraints(self,
                                derivative_function: Callable,
                                initial_condition: np.ndarray,
                                time_step: float,
                                num_steps: int,
                                constraint_checker: Optional[Callable] = None) -> Dict[str, np.ndarray]:
        """
        Solve ODE with constraint checking.
        
        Args:
            derivative_function: Function f(t, y)
            initial_condition: Initial condition
            time_step: Time step
            num_steps: Number of steps
            constraint_checker: Function to check constraints
            
        Returns:
            Dictionary with solution and constraint violations
        """
        result = self.runge_kutta_4(derivative_function, initial_condition, time_step, num_steps)
        
        violations = []
        if constraint_checker:
            for i, state in enumerate(result['solution']):
                is_valid = constraint_checker(state)
                if not is_valid:
                    violations.append(i)
                    self.logger.log(f"Constraint violation at step {i}", level="WARNING")
        
        result['constraint_violations'] = violations
        return result

