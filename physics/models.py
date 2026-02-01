# physics/
"""
PATH: physics/models.py
PURPOSE: Physics model simulation with numerical integration and state management.

FLOW:
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│   Define    │───▶│   Initialize │───▶│   Time      │───▶│   Validate   │
│   Model     │    │    State     │    │   Stepping  │    │   Results    │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘

First Principle Analysis:
- Physics models represent physical systems mathematically
- State evolution governed by differential equations
- Conservation laws provide validation constraints
- Numerical integration approximates continuous dynamics

Mathematical Foundation:
- Ordinary Differential Equations (ODEs)
- Partial Differential Equations (PDEs)
- Numerical integration (RK4, adaptive step methods)
- Conservation law checking

DEPENDENCIES:
- numpy: Array operations and numerical math
- scipy: Numerical integration
- validators: Data validation
- loggers: System logging
"""

from typing import Any, Dict, List, Optional, Tuple, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from abc import ABC, abstractmethod
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from validators.data_validator import DataValidator
from loggers.system_logger import SystemLogger

# Try to import scipy
try:
    from scipy.integrate import odeint, solve_ivp, RK45
    from scipy.optimize import fsolve
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class IntegrationMethod(Enum):
    """Numerical integration methods."""
    EULER = "euler"
    RK4 = "rk4"
    RK45 = "rk45"
    ADAPTIVE = "adaptive"


@dataclass
class SimulationState:
    """State of a simulation at a point in time."""
    time: float
    variables: Dict[str, float]
    derivatives: Dict[str, float] = field(default_factory=dict)
    energy: Optional[float] = None
    momentum: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'time': self.time,
            'variables': self.variables,
            'derivatives': self.derivatives,
            'energy': self.energy,
            'momentum': self.momentum.tolist() if self.momentum is not None else None,
            'metadata': self.metadata
        }
    
    def to_array(self, var_order: List[str]) -> np.ndarray:
        """Convert to numpy array in specified variable order."""
        return np.array([self.variables[v] for v in var_order])
    
    @classmethod
    def from_array(cls, arr: np.ndarray, var_order: List[str], time: float) -> 'SimulationState':
        """Create from numpy array."""
        variables = {v: float(arr[i]) for i, v in enumerate(var_order)}
        return cls(time=time, variables=variables)


@dataclass
class SimulationResult:
    """Result of a simulation run."""
    states: List[SimulationState]
    times: np.ndarray
    success: bool
    method_used: str
    conservation_violations: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'states': [s.to_dict() for s in self.states],
            'times': self.times.tolist(),
            'success': self.success,
            'method_used': self.method_used,
            'conservation_violations': self.conservation_violations,
            'metadata': self.metadata
        }
    
    def get_variable_history(self, var_name: str) -> np.ndarray:
        """Get the time history of a variable."""
        return np.array([s.variables.get(var_name, 0) for s in self.states])
    
    def get_energy_history(self) -> np.ndarray:
        """Get the time history of energy."""
        return np.array([s.energy if s.energy is not None else np.nan for s in self.states])


class PhysicsModel(ABC):
    """
    Abstract base class for physics models.
    
    Subclasses must implement:
    - derivatives(): Compute time derivatives of state
    - energy(): Compute total energy (optional but recommended)
    """
    
    def __init__(self, model_type: str, parameters: Dict[str, Any]):
        """
        Initialize physics model.
        
        Args:
            model_type: Type of physics model
            parameters: Model parameters
        """
        self.model_type = model_type
        self.parameters = parameters
        self.validator = DataValidator()
        self.logger = SystemLogger()
        
        # State variables
        self.state_variables: List[str] = []
        
        # Conservation laws to check
        self.conservation_laws: List[Callable] = []
        
        if not self.validator.validate_dict(parameters):
            self.logger.log("Invalid parameters provided", level="WARNING")
        
        self.logger.log(f"PhysicsModel initialized: {model_type}", level="INFO")
    
    @abstractmethod
    def derivatives(self, state: SimulationState) -> Dict[str, float]:
        """
        Compute time derivatives of state variables.
        
        Args:
            state: Current simulation state
            
        Returns:
            Dictionary of variable derivatives
        """
        pass
    
    def energy(self, state: SimulationState) -> Optional[float]:
        """
        Compute total energy of the system.
        
        Override in subclasses for energy conservation checking.
        
        Args:
            state: Current simulation state
            
        Returns:
            Total energy or None if not applicable
        """
        return None
    
    def momentum(self, state: SimulationState) -> Optional[np.ndarray]:
        """
        Compute total momentum of the system.
        
        Override in subclasses for momentum conservation checking.
        
        Args:
            state: Current simulation state
            
        Returns:
            Momentum vector or None if not applicable
        """
        return None
    
    def validate(self) -> bool:
        """
        Validate the physics model configuration.
        
        Returns:
            True if valid, False otherwise
        """
        if not self.state_variables:
            self.logger.log("No state variables defined", level="WARNING")
            return False
        return True
    
    def simulate(self, initial_conditions: Dict[str, Any],
                t_start: float = 0.0,
                t_end: float = 10.0,
                dt: float = 0.01,
                method: IntegrationMethod = IntegrationMethod.RK4) -> SimulationResult:
        """
        Simulate the physics model.
        
        Args:
            initial_conditions: Initial values for state variables
            t_start: Start time
            t_end: End time
            dt: Time step
            method: Integration method
            
        Returns:
            SimulationResult with state history
        """
        self.logger.log(f"Starting simulation from t={t_start} to t={t_end}", level="INFO")
        
        # Validate initial conditions
        for var in self.state_variables:
            if var not in initial_conditions:
                self.logger.log(f"Missing initial condition for {var}", level="ERROR")
                return SimulationResult(
                    states=[],
                    times=np.array([]),
                    success=False,
                    method_used=method.value,
                    metadata={'error': f'Missing initial condition for {var}'}
                )
        
        # Create time array
        times = np.arange(t_start, t_end + dt, dt)
        
        # Initialize state
        initial_state = SimulationState(
            time=t_start,
            variables={v: initial_conditions.get(v, 0) for v in self.state_variables}
        )
        initial_state.energy = self.energy(initial_state)
        initial_state.momentum = self.momentum(initial_state)
        initial_state.derivatives = self.derivatives(initial_state)
        
        states = [initial_state]
        
        # Run simulation
        if method == IntegrationMethod.EULER:
            states = self._integrate_euler(initial_state, times, dt)
        elif method == IntegrationMethod.RK4:
            states = self._integrate_rk4(initial_state, times, dt)
        elif method == IntegrationMethod.RK45 or method == IntegrationMethod.ADAPTIVE:
            if SCIPY_AVAILABLE:
                states = self._integrate_scipy(initial_state, times)
            else:
                self.logger.log("scipy not available, falling back to RK4", level="WARNING")
                states = self._integrate_rk4(initial_state, times, dt)
        
        # Check conservation laws
        violations = self._check_conservation(states)
        
        return SimulationResult(
            states=states,
            times=times,
            success=True,
            method_used=method.value,
            conservation_violations=violations,
            metadata={
                'dt': dt,
                'num_steps': len(times),
                'model_type': self.model_type
            }
        )
    
    def _integrate_euler(self, initial_state: SimulationState,
                        times: np.ndarray, dt: float) -> List[SimulationState]:
        """Euler integration method."""
        states = [initial_state]
        current_state = initial_state
        
        for t in times[1:]:
            derivs = self.derivatives(current_state)
            
            # Update variables
            new_vars = {}
            for var in self.state_variables:
                new_vars[var] = current_state.variables[var] + derivs.get(var, 0) * dt
            
            new_state = SimulationState(
                time=t,
                variables=new_vars,
                derivatives=derivs
            )
            new_state.energy = self.energy(new_state)
            new_state.momentum = self.momentum(new_state)
            
            states.append(new_state)
            current_state = new_state
        
        return states
    
    def _integrate_rk4(self, initial_state: SimulationState,
                      times: np.ndarray, dt: float) -> List[SimulationState]:
        """4th order Runge-Kutta integration."""
        states = [initial_state]
        current_vars = initial_state.variables.copy()
        
        for i, t in enumerate(times[1:], 1):
            # k1
            k1 = self._compute_k(current_vars, t - dt)
            
            # k2
            mid_vars1 = {v: current_vars[v] + 0.5 * dt * k1[v] for v in self.state_variables}
            k2 = self._compute_k(mid_vars1, t - dt/2)
            
            # k3
            mid_vars2 = {v: current_vars[v] + 0.5 * dt * k2[v] for v in self.state_variables}
            k3 = self._compute_k(mid_vars2, t - dt/2)
            
            # k4
            end_vars = {v: current_vars[v] + dt * k3[v] for v in self.state_variables}
            k4 = self._compute_k(end_vars, t)
            
            # Update
            new_vars = {}
            for v in self.state_variables:
                new_vars[v] = current_vars[v] + (dt / 6) * (k1[v] + 2*k2[v] + 2*k3[v] + k4[v])
            
            new_state = SimulationState(
                time=t,
                variables=new_vars
            )
            new_state.derivatives = self.derivatives(new_state)
            new_state.energy = self.energy(new_state)
            new_state.momentum = self.momentum(new_state)
            
            states.append(new_state)
            current_vars = new_vars
        
        return states
    
    def _compute_k(self, variables: Dict[str, float], time: float) -> Dict[str, float]:
        """Compute k values for RK4."""
        temp_state = SimulationState(time=time, variables=variables)
        return self.derivatives(temp_state)
    
    def _integrate_scipy(self, initial_state: SimulationState,
                        times: np.ndarray) -> List[SimulationState]:
        """Integration using scipy's solve_ivp."""
        # Convert to ODE function
        def ode_func(t, y):
            state = SimulationState.from_array(y, self.state_variables, t)
            derivs = self.derivatives(state)
            return np.array([derivs.get(v, 0) for v in self.state_variables])
        
        y0 = initial_state.to_array(self.state_variables)
        
        # Solve
        solution = solve_ivp(
            ode_func,
            (times[0], times[-1]),
            y0,
            t_eval=times,
            method='RK45'
        )
        
        # Convert back to states
        states = []
        for i, t in enumerate(solution.t):
            state = SimulationState.from_array(solution.y[:, i], self.state_variables, t)
            state.derivatives = self.derivatives(state)
            state.energy = self.energy(state)
            state.momentum = self.momentum(state)
            states.append(state)
        
        return states
    
    def _check_conservation(self, states: List[SimulationState]) -> List[Dict[str, Any]]:
        """Check conservation laws."""
        violations = []
        
        if len(states) < 2:
            return violations
        
        # Check energy conservation
        energies = [s.energy for s in states if s.energy is not None]
        if energies:
            initial_energy = energies[0]
            for i, e in enumerate(energies):
                if initial_energy != 0:
                    relative_error = abs(e - initial_energy) / abs(initial_energy)
                    if relative_error > 0.01:  # 1% threshold
                        violations.append({
                            'type': 'energy_conservation',
                            'time': states[i].time,
                            'expected': initial_energy,
                            'actual': e,
                            'relative_error': relative_error
                        })
        
        # Check momentum conservation
        momenta = [s.momentum for s in states if s.momentum is not None]
        if momenta:
            initial_momentum = momenta[0]
            for i, p in enumerate(momenta):
                diff = np.linalg.norm(p - initial_momentum)
                if diff > 1e-6:
                    violations.append({
                        'type': 'momentum_conservation',
                        'time': states[i].time,
                        'difference': float(diff)
                    })
        
        return violations


class HarmonicOscillator(PhysicsModel):
    """
    Simple harmonic oscillator model.
    
    Equation: m * d²x/dt² = -k * x
    Or: d²x/dt² = -ω² * x, where ω = sqrt(k/m)
    """
    
    def __init__(self, mass: float = 1.0, spring_constant: float = 1.0, damping: float = 0.0):
        """
        Initialize harmonic oscillator.
        
        Args:
            mass: Mass of oscillator (kg)
            spring_constant: Spring constant k (N/m)
            damping: Damping coefficient (kg/s)
        """
        super().__init__(
            model_type="harmonic_oscillator",
            parameters={
                'mass': mass,
                'spring_constant': spring_constant,
                'damping': damping
            }
        )
        
        self.mass = mass
        self.spring_constant = spring_constant
        self.damping = damping
        self.omega = np.sqrt(spring_constant / mass)
        
        self.state_variables = ['x', 'v']  # position, velocity
    
    def derivatives(self, state: SimulationState) -> Dict[str, float]:
        """
        Compute derivatives for harmonic oscillator.
        
        dx/dt = v
        dv/dt = -(k/m)*x - (c/m)*v
        """
        x = state.variables['x']
        v = state.variables['v']
        
        dx_dt = v
        dv_dt = -(self.spring_constant / self.mass) * x - (self.damping / self.mass) * v
        
        return {'x': dx_dt, 'v': dv_dt}
    
    def energy(self, state: SimulationState) -> float:
        """
        Compute total energy.
        
        E = (1/2)mv² + (1/2)kx²
        """
        x = state.variables['x']
        v = state.variables['v']
        
        kinetic = 0.5 * self.mass * v**2
        potential = 0.5 * self.spring_constant * x**2
        
        return kinetic + potential
    
    def analytical_solution(self, x0: float, v0: float, t: float) -> Dict[str, float]:
        """
        Compute analytical solution (for undamped case).
        
        Args:
            x0: Initial position
            v0: Initial velocity
            t: Time
            
        Returns:
            Dictionary with x and v
        """
        if self.damping == 0:
            # Undamped case
            A = np.sqrt(x0**2 + (v0/self.omega)**2)
            phi = np.arctan2(-v0/self.omega, x0)
            
            x = A * np.cos(self.omega * t + phi)
            v = -A * self.omega * np.sin(self.omega * t + phi)
            
            return {'x': x, 'v': v}
        else:
            # Damped case - numerical only
            return {}


class Pendulum(PhysicsModel):
    """
    Simple pendulum model.
    
    Equation: d²θ/dt² = -(g/L)*sin(θ) - (c/m)*dθ/dt
    """
    
    def __init__(self, length: float = 1.0, mass: float = 1.0, 
                 gravity: float = 9.81, damping: float = 0.0):
        """
        Initialize pendulum.
        
        Args:
            length: Pendulum length (m)
            mass: Bob mass (kg)
            gravity: Gravitational acceleration (m/s²)
            damping: Damping coefficient
        """
        super().__init__(
            model_type="pendulum",
            parameters={
                'length': length,
                'mass': mass,
                'gravity': gravity,
                'damping': damping
            }
        )
        
        self.length = length
        self.mass = mass
        self.gravity = gravity
        self.damping = damping
        
        self.state_variables = ['theta', 'omega']  # angle, angular velocity
    
    def derivatives(self, state: SimulationState) -> Dict[str, float]:
        """
        Compute derivatives for pendulum.
        
        dθ/dt = ω
        dω/dt = -(g/L)*sin(θ) - (c/m)*ω
        """
        theta = state.variables['theta']
        omega = state.variables['omega']
        
        dtheta_dt = omega
        domega_dt = -(self.gravity / self.length) * np.sin(theta) - (self.damping / self.mass) * omega
        
        return {'theta': dtheta_dt, 'omega': domega_dt}
    
    def energy(self, state: SimulationState) -> float:
        """
        Compute total energy.
        
        E = (1/2)*m*L²*ω² + m*g*L*(1 - cos(θ))
        """
        theta = state.variables['theta']
        omega = state.variables['omega']
        
        kinetic = 0.5 * self.mass * self.length**2 * omega**2
        potential = self.mass * self.gravity * self.length * (1 - np.cos(theta))
        
        return kinetic + potential


class TwoBodyGravity(PhysicsModel):
    """
    Two-body gravitational model (e.g., planet orbiting a star).
    
    Uses reduced mass formulation in 2D.
    """
    
    def __init__(self, mass1: float, mass2: float, G: float = 6.67430e-11):
        """
        Initialize two-body system.
        
        Args:
            mass1: Mass of body 1 (kg)
            mass2: Mass of body 2 (kg)
            G: Gravitational constant
        """
        super().__init__(
            model_type="two_body_gravity",
            parameters={
                'mass1': mass1,
                'mass2': mass2,
                'G': G
            }
        )
        
        self.mass1 = mass1
        self.mass2 = mass2
        self.G = G
        self.mu = G * (mass1 + mass2)  # Standard gravitational parameter
        
        # State: relative position and velocity (x, y, vx, vy)
        self.state_variables = ['x', 'y', 'vx', 'vy']
    
    def derivatives(self, state: SimulationState) -> Dict[str, float]:
        """
        Compute derivatives for two-body problem.
        
        d²r/dt² = -μ * r / |r|³
        """
        x = state.variables['x']
        y = state.variables['y']
        vx = state.variables['vx']
        vy = state.variables['vy']
        
        r = np.sqrt(x**2 + y**2)
        
        if r < 1e-10:  # Avoid singularity
            return {'x': vx, 'y': vy, 'vx': 0, 'vy': 0}
        
        ax = -self.mu * x / r**3
        ay = -self.mu * y / r**3
        
        return {'x': vx, 'y': vy, 'vx': ax, 'vy': ay}
    
    def energy(self, state: SimulationState) -> float:
        """
        Compute total orbital energy.
        
        E = (1/2)*v² - μ/r
        """
        x = state.variables['x']
        y = state.variables['y']
        vx = state.variables['vx']
        vy = state.variables['vy']
        
        r = np.sqrt(x**2 + y**2)
        v2 = vx**2 + vy**2
        
        if r < 1e-10:
            return 0
        
        return 0.5 * v2 - self.mu / r
    
    def momentum(self, state: SimulationState) -> np.ndarray:
        """
        Compute angular momentum.
        
        L = r × v (in 2D, this is a scalar but we return as array)
        """
        x = state.variables['x']
        y = state.variables['y']
        vx = state.variables['vx']
        vy = state.variables['vy']
        
        # Angular momentum in z-direction
        Lz = x * vy - y * vx
        
        return np.array([0, 0, Lz])


class ProjectileMotion(PhysicsModel):
    """
    Projectile motion with optional air resistance.
    """
    
    def __init__(self, mass: float = 1.0, gravity: float = 9.81,
                 drag_coefficient: float = 0.0, cross_section: float = 0.01,
                 air_density: float = 1.225):
        """
        Initialize projectile model.
        
        Args:
            mass: Projectile mass (kg)
            gravity: Gravitational acceleration (m/s²)
            drag_coefficient: Drag coefficient Cd
            cross_section: Cross-sectional area (m²)
            air_density: Air density (kg/m³)
        """
        super().__init__(
            model_type="projectile_motion",
            parameters={
                'mass': mass,
                'gravity': gravity,
                'drag_coefficient': drag_coefficient,
                'cross_section': cross_section,
                'air_density': air_density
            }
        )
        
        self.mass = mass
        self.gravity = gravity
        self.drag_coefficient = drag_coefficient
        self.cross_section = cross_section
        self.air_density = air_density
        
        # Drag factor: (1/2) * Cd * A * ρ
        self.drag_factor = 0.5 * drag_coefficient * cross_section * air_density
        
        self.state_variables = ['x', 'y', 'vx', 'vy']
    
    def derivatives(self, state: SimulationState) -> Dict[str, float]:
        """
        Compute derivatives for projectile motion.
        """
        x = state.variables['x']
        y = state.variables['y']
        vx = state.variables['vx']
        vy = state.variables['vy']
        
        v = np.sqrt(vx**2 + vy**2)
        
        # Drag force: F_drag = (1/2) * Cd * A * ρ * v² (opposite to velocity)
        if v > 0 and self.drag_factor > 0:
            drag_x = -self.drag_factor * v * vx / self.mass
            drag_y = -self.drag_factor * v * vy / self.mass
        else:
            drag_x = 0
            drag_y = 0
        
        ax = drag_x
        ay = -self.gravity + drag_y
        
        return {'x': vx, 'y': vy, 'vx': ax, 'vy': ay}
    
    def energy(self, state: SimulationState) -> float:
        """
        Compute mechanical energy (not conserved with drag).
        """
        x = state.variables['x']
        y = state.variables['y']
        vx = state.variables['vx']
        vy = state.variables['vy']
        
        kinetic = 0.5 * self.mass * (vx**2 + vy**2)
        potential = self.mass * self.gravity * y
        
        return kinetic + potential


# Factory function for creating models
def create_model(model_type: str, **kwargs) -> PhysicsModel:
    """
    Factory function to create physics models.
    
    Args:
        model_type: Type of model to create
        **kwargs: Model-specific parameters
        
    Returns:
        PhysicsModel instance
    """
    models = {
        'harmonic_oscillator': HarmonicOscillator,
        'pendulum': Pendulum,
        'two_body_gravity': TwoBodyGravity,
        'projectile_motion': ProjectileMotion,
    }
    
    if model_type not in models:
        raise ValueError(f"Unknown model type: {model_type}. Available: {list(models.keys())}")
    
    return models[model_type](**kwargs)
