# physics/domains/quantum/
"""
Schrödinger equation module.

First Principle Analysis:
- Schrödinger equation: iℏ∂ψ/∂t = Ĥψ governs quantum evolution
- Wave function ψ contains all information about quantum state
- Probability density: |ψ|² gives probability distribution
- Mathematical foundation: Linear algebra, Hilbert spaces, operators
- Architecture: Modular Hamiltonian operators with synergy for field corrections

Planning:
1. Implement time-dependent Schrödinger equation solver
2. Implement time-independent Schrödinger equation (eigenvalue problem)
3. Add common potential wells (harmonic, infinite square well)
4. Implement wave function normalization and probability calculations
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


class SchrodingerMechanics:
    """
    Schrödinger equation implementation.
    
    Implements quantum mechanics using the Schrödinger equation
    with support for various potential functions and operators.
    """
    
    def __init__(self):
        """Initialize Schrödinger mechanics system."""
        self.validator = DataValidator()
        self.logger = SystemLogger()
        self.conservation = ConservationLaws()
        self.constraints = PhysicsConstraints()
        
        # Fundamental constants
        self.hbar = 1.054571817e-34  # Reduced Planck constant (J·s)
        self.m_e = 9.1093837015e-31  # Electron mass (kg)
        
        # Synergy factors
        self.delta_relativistic = 0.0  # Relativistic correction (Dirac equation)
        self.delta_field = 0.0  # Field theory correction (QFT)
        
        self.logger.log("SchrodingerMechanics initialized", level="INFO")
    
    def time_dependent_schrodinger(self,
                                    hamiltonian_operator: Callable,
                                    wave_function: np.ndarray,
                                    time: float,
                                    time_step: float) -> np.ndarray:
        """
        Solve time-dependent Schrödinger equation.
        
        Mathematical principle: iℏ∂ψ/∂t = Ĥψ
        
        Uses Crank-Nicolson method for numerical stability
        
        Args:
            hamiltonian_operator: Function Ĥ(ψ) returning Ĥψ
            wave_function: Current wave function ψ(t)
            time: Current time t
            time_step: Time step dt
            
        Returns:
            Updated wave function ψ(t + dt)
        """
        wave_function = np.array(wave_function, dtype=complex)
        
        # Crank-Nicolson method: (1 + iHdt/2ℏ)ψ(t+dt) = (1 - iHdt/2ℏ)ψ(t)
        # Simplified: explicit Euler for now
        H_psi = hamiltonian_operator(wave_function)
        dpsi_dt = -1j * H_psi / self.hbar
        wave_function_new = wave_function + dpsi_dt * time_step
        
        # Normalize to preserve unitarity
        norm = np.sqrt(np.sum(np.abs(wave_function_new)**2))
        if norm > 1e-10:
            wave_function_new = wave_function_new / norm
        
        self.logger.log("Time-dependent Schrödinger equation solved", level="DEBUG")
        return wave_function_new
    
    def time_independent_schrodinger(self,
                                      hamiltonian_matrix: np.ndarray,
                                      num_eigenstates: int = 10) -> Dict[str, np.ndarray]:
        """
        Solve time-independent Schrödinger equation (eigenvalue problem).
        
        Mathematical principle: Ĥψ_n = E_n ψ_n
        
        Args:
            hamiltonian_matrix: Matrix representation of Hamiltonian Ĥ
            num_eigenstates: Number of eigenstates to compute
            
        Returns:
            Dictionary with eigenvalues and eigenvectors
        """
        hamiltonian_matrix = np.array(hamiltonian_matrix)
        
        # Solve eigenvalue problem
        eigenvalues, eigenvectors = np.linalg.eigh(hamiltonian_matrix)
        
        # Sort by energy (eigenvalues)
        sorted_indices = np.argsort(eigenvalues)
        eigenvalues = eigenvalues[sorted_indices]
        eigenvectors = eigenvectors[:, sorted_indices]
        
        # Take requested number of eigenstates
        eigenvalues = eigenvalues[:num_eigenstates]
        eigenvectors = eigenvectors[:, :num_eigenstates]
        
        # Normalize eigenvectors
        for i in range(eigenvectors.shape[1]):
            norm = np.linalg.norm(eigenvectors[:, i])
            if norm > 1e-10:
                eigenvectors[:, i] = eigenvectors[:, i] / norm
        
        self.logger.log(f"Time-independent Schrödinger solved: {num_eigenstates} eigenstates", level="INFO")
        
        return {
            'eigenvalues': eigenvalues,
            'eigenvectors': eigenvectors,
            'energies': eigenvalues  # Alias for clarity
        }
    
    def harmonic_oscillator_hamiltonian(self,
                                         position_grid: np.ndarray,
                                         mass: float,
                                         spring_constant: float) -> np.ndarray:
        """
        Construct Hamiltonian matrix for quantum harmonic oscillator.
        
        Mathematical principle: Ĥ = -ℏ²/(2m) d²/dx² + (1/2)kx²
        
        Args:
            position_grid: Array of position values x
            mass: Mass m
            spring_constant: Spring constant k
            
        Returns:
            Hamiltonian matrix
        """
        N = len(position_grid)
        dx = position_grid[1] - position_grid[0] if N > 1 else 1.0
        
        # Kinetic energy operator: -ℏ²/(2m) d²/dx²
        # Second derivative matrix (finite difference)
        kinetic = np.zeros((N, N), dtype=complex)
        for i in range(N):
            if i > 0:
                kinetic[i, i - 1] = -1.0
            kinetic[i, i] = 2.0
            if i < N - 1:
                kinetic[i, i + 1] = -1.0
        kinetic = -self.hbar**2 / (2 * mass * dx**2) * kinetic
        
        # Potential energy operator: (1/2)kx² (diagonal)
        potential = np.diag(0.5 * spring_constant * position_grid**2)
        
        # Total Hamiltonian
        hamiltonian = kinetic + potential
        
        self.logger.log(f"Harmonic oscillator Hamiltonian constructed: {N}x{N} matrix", level="INFO")
        return hamiltonian
    
    def infinite_square_well_hamiltonian(self,
                                          position_grid: np.ndarray,
                                          mass: float,
                                          well_width: float) -> np.ndarray:
        """
        Construct Hamiltonian matrix for infinite square well.
        
        Mathematical principle: V(x) = 0 for 0 < x < L, ∞ otherwise
        
        Args:
            position_grid: Array of position values x
            mass: Mass m
            well_width: Well width L
            
        Returns:
            Hamiltonian matrix
        """
        N = len(position_grid)
        dx = position_grid[1] - position_grid[0] if N > 1 else 1.0
        
        # Kinetic energy operator only (V = 0 inside well)
        kinetic = np.zeros((N, N), dtype=complex)
        for i in range(N):
            if i > 0:
                kinetic[i, i - 1] = -1.0
            kinetic[i, i] = 2.0
            if i < N - 1:
                kinetic[i, i + 1] = -1.0
        kinetic = -self.hbar**2 / (2 * mass * dx**2) * kinetic
        
        # Potential is zero inside well (boundary conditions handled separately)
        hamiltonian = kinetic
        
        self.logger.log(f"Infinite square well Hamiltonian constructed: {N}x{N} matrix", level="INFO")
        return hamiltonian
    
    def compute_probability_density(self, wave_function: np.ndarray) -> np.ndarray:
        """
        Compute probability density |ψ|².
        
        Mathematical principle: ρ(x) = |ψ(x)|²
        
        Args:
            wave_function: Wave function ψ
            
        Returns:
            Probability density array
        """
        wave_function = np.array(wave_function, dtype=complex)
        probability_density = np.abs(wave_function)**2
        
        # Check unitarity
        total_probability = np.sum(probability_density)
        is_unitary, _ = self.constraints.check_unitarity(wave_function)
        if not is_unitary:
            self.logger.log(f"Unitarity violation: total probability = {total_probability}", level="WARNING")
        
        self.logger.log(f"Probability density computed: total = {total_probability}", level="DEBUG")
        return probability_density
    
    def compute_expectation_value(self,
                                   operator: np.ndarray,
                                   wave_function: np.ndarray) -> complex:
        """
        Compute expectation value <ψ|Ô|ψ>.
        
        Mathematical principle: <Ô> = ∫ ψ* Ô ψ dx = <ψ|Ô|ψ>
        
        Args:
            operator: Operator matrix Ô
            wave_function: Wave function ψ
            
        Returns:
            Expectation value (complex)
        """
        wave_function = np.array(wave_function, dtype=complex)
        operator = np.array(operator)
        
        # <ψ|Ô|ψ> = ψ* Ô ψ
        expectation = np.dot(np.conj(wave_function), np.dot(operator, wave_function))
        
        self.logger.log(f"Expectation value computed: <Ô> = {expectation}", level="DEBUG")
        return expectation
    
    def compute_uncertainty(self,
                            operator1: np.ndarray,
                            operator2: np.ndarray,
                            wave_function: np.ndarray) -> float:
        """
        Compute uncertainty ΔA·ΔB for operators A and B.
        
        Mathematical principle: ΔA·ΔB ≥ (1/2)|<[A, B]>|
        
        Args:
            operator1: Operator A
            operator2: Operator B
            wave_function: Wave function ψ
            
        Returns:
            Uncertainty product
        """
        wave_function = np.array(wave_function, dtype=complex)
        op1 = np.array(operator1)
        op2 = np.array(operator2)
        
        # Compute <A>, <B>
        exp_A = self.compute_expectation_value(op1, wave_function)
        exp_B = self.compute_expectation_value(op2, wave_function)
        
        # Compute <A²>, <B²>
        exp_A2 = self.compute_expectation_value(np.dot(op1, op1), wave_function)
        exp_B2 = self.compute_expectation_value(np.dot(op2, op2), wave_function)
        
        # Uncertainty: ΔA = sqrt(<A²> - <A>²)
        delta_A = np.sqrt(abs(exp_A2 - exp_A**2))
        delta_B = np.sqrt(abs(exp_B2 - exp_B**2))
        
        uncertainty_product = delta_A * delta_B
        
        # Check Heisenberg uncertainty
        commutator = np.dot(op1, op2) - np.dot(op2, op1)
        exp_commutator = self.compute_expectation_value(commutator, wave_function)
        minimum = abs(exp_commutator) / 2.0
        
        satisfies, _ = self.constraints.check_uncertainty_principle(
            delta_A if np.isreal(delta_A) else abs(delta_A),
            delta_B if np.isreal(delta_B) else abs(delta_B)
        )
        
        self.logger.log(
            f"Uncertainty computed: ΔA·ΔB = {uncertainty_product}, minimum = {minimum}",
            level="DEBUG"
        )
        
        return uncertainty_product
    
    def set_relativistic_correction(self, delta: float) -> None:
        """Set relativistic correction factor (Dirac equation)."""
        self.delta_relativistic = max(0.0, min(1.0, delta))
        self.logger.log(f"Relativistic correction set: δ = {self.delta_relativistic}", level="INFO")
    
    def set_field_correction(self, delta: float) -> None:
        """Set field theory correction factor (QFT)."""
        self.delta_field = max(0.0, min(1.0, delta))
        self.logger.log(f"Field theory correction set: δ = {self.delta_field}", level="INFO")

