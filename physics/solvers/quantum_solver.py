"""
PATH: physics/solvers/quantum_solver.py
PURPOSE: Quantum mechanics solver integrating QMsolve and QuTiP concepts

WHY: Provides numerical solutions to Schrödinger equation and open quantum systems
     using proven algorithms from QMsolve and QuTiP libraries.

REFERENCES:
- QMsolve: https://github.com/quantum-visualizations/qmsolve (BSD-3)
- QuTiP: https://github.com/qutip/qutip (BSD-3)

FLOW:
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│ Define      │────>│ Discretize   │────>│ Solve           │
│ Hamiltonian │     │ Grid/Basis   │     │ Eigenvalue/Time │
└─────────────┘     └──────────────┘     └─────────────────┘
                                                  │
                                                  v
                                         ┌─────────────────┐
                                         │ Visualize/      │
                                         │ Export Results  │
                                         └─────────────────┘

DEPENDENCIES:
- numpy: Numerical computations
- scipy: Sparse matrix solvers, FFT
- Optional: qmsolve, qutip for advanced features
"""

from typing import Callable, Optional, Tuple, List, Dict, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh, expm_multiply
from scipy.fft import fft, ifft, fft2, ifft2, fftn, ifftn
import logging

logger = logging.getLogger(__name__)


# Physical Constants (Hartree atomic units)
class AtomicUnits:
    """Hartree atomic units for quantum calculations."""
    hbar = 1.0  # Reduced Planck constant
    m_e = 1.0   # Electron mass
    e = 1.0     # Elementary charge
    a_0 = 1.0   # Bohr radius
    E_h = 1.0   # Hartree energy (27.2 eV)
    
    # Conversion factors
    eV = 1.0 / 27.211386  # eV to Hartree
    nm = 1.0 / 0.0529177  # nm to Bohr
    angstrom = 1.0 / 0.529177  # Angstrom to Bohr
    fs = 1.0 / 0.02419    # femtosecond to atomic time


class SolverMethod(Enum):
    """Numerical methods for time evolution."""
    SPLIT_STEP = "split-step"
    CRANK_NICOLSON = "crank-nicolson"
    RUNGE_KUTTA = "runge-kutta"


@dataclass
class QuantumGrid:
    """
    Spatial grid for discretizing quantum systems.
    
    Inspired by QMsolve's grid handling.
    """
    ndim: int
    N: int  # Grid points per dimension
    extent: float  # Physical extent in each dimension
    
    # Computed properties
    x: np.ndarray = field(init=False)
    dx: float = field(init=False)
    k: np.ndarray = field(init=False)
    dk: float = field(init=False)
    
    def __post_init__(self):
        """Initialize coordinate and momentum grids."""
        self.dx = self.extent / self.N
        self.x = np.linspace(-self.extent/2, self.extent/2, self.N, endpoint=False)
        
        # Momentum grid (FFT convention)
        self.dk = 2 * np.pi / self.extent
        self.k = np.fft.fftfreq(self.N, self.dx) * 2 * np.pi
        
    def meshgrid(self) -> Tuple[np.ndarray, ...]:
        """Create meshgrid for multi-dimensional potentials."""
        if self.ndim == 1:
            return (self.x,)
        elif self.ndim == 2:
            return np.meshgrid(self.x, self.x, indexing='ij')
        elif self.ndim == 3:
            return np.meshgrid(self.x, self.x, self.x, indexing='ij')
        else:
            raise ValueError(f"Unsupported dimension: {self.ndim}")
    
    def momentum_meshgrid(self) -> Tuple[np.ndarray, ...]:
        """Create momentum space meshgrid."""
        if self.ndim == 1:
            return (self.k,)
        elif self.ndim == 2:
            return np.meshgrid(self.k, self.k, indexing='ij')
        elif self.ndim == 3:
            return np.meshgrid(self.k, self.k, self.k, indexing='ij')
        else:
            raise ValueError(f"Unsupported dimension: {self.ndim}")


@dataclass
class Hamiltonian:
    """
    Quantum Hamiltonian with potential energy function.
    
    Inspired by QMsolve's Hamiltonian class.
    """
    grid: QuantumGrid
    potential: Callable[..., np.ndarray]
    mass: float = 1.0  # Particle mass in atomic units
    hbar: float = 1.0  # hbar in atomic units
    
    # Computed matrices
    V: np.ndarray = field(init=False, default=None)
    T_k: np.ndarray = field(init=False, default=None)
    
    def __post_init__(self):
        """Compute potential and kinetic energy arrays."""
        self._compute_potential()
        self._compute_kinetic()
    
    def _compute_potential(self):
        """Evaluate potential on grid."""
        coords = self.grid.meshgrid()
        if self.grid.ndim == 1:
            self.V = self.potential(coords[0])
        else:
            self.V = self.potential(*coords)
    
    def _compute_kinetic(self):
        """Compute kinetic energy in momentum space."""
        k_grids = self.grid.momentum_meshgrid()
        if self.grid.ndim == 1:
            k_squared = k_grids[0]**2
        elif self.grid.ndim == 2:
            k_squared = k_grids[0]**2 + k_grids[1]**2
        else:
            k_squared = sum(kg**2 for kg in k_grids)
        
        self.T_k = self.hbar**2 * k_squared / (2 * self.mass)
    
    def as_sparse_matrix(self) -> sparse.csr_matrix:
        """
        Construct sparse Hamiltonian matrix.
        
        Uses finite difference for kinetic energy (like QMsolve eigenstate solver).
        """
        N = self.grid.N
        dx = self.grid.dx
        
        if self.grid.ndim == 1:
            # 1D: Tridiagonal for kinetic energy
            diag = self.hbar**2 / (self.mass * dx**2) * np.ones(N)
            off_diag = -self.hbar**2 / (2 * self.mass * dx**2) * np.ones(N - 1)
            
            H = sparse.diags([off_diag, diag + self.V, off_diag], [-1, 0, 1], format='csr')
            return H
        else:
            # Multi-dimensional: Kronecker product structure
            # For simplicity, flatten to 1D representation
            total_points = N ** self.grid.ndim
            
            # Build Laplacian using Kronecker products
            I = sparse.eye(N)
            D2 = sparse.diags([1, -2, 1], [-1, 0, 1], shape=(N, N)) / dx**2
            
            if self.grid.ndim == 2:
                Laplacian = sparse.kron(D2, I) + sparse.kron(I, D2)
            else:  # 3D
                Laplacian = (sparse.kron(sparse.kron(D2, I), I) +
                            sparse.kron(sparse.kron(I, D2), I) +
                            sparse.kron(sparse.kron(I, I), D2))
            
            T = -self.hbar**2 / (2 * self.mass) * Laplacian
            V_diag = sparse.diags(self.V.flatten(), 0)
            
            return T + V_diag
    
    def solve_eigenstates(self, n_states: int = 10, method: str = 'eigsh') -> Tuple[np.ndarray, np.ndarray]:
        """
        Solve for eigenstates using sparse eigenvalue solver.
        
        Uses ARPACK (eigsh) like QMsolve for efficiency.
        
        Returns:
            energies: Array of eigenvalues
            states: Array of eigenvectors (n_states x grid_size)
        """
        H_matrix = self.as_sparse_matrix()
        
        # Use shift-invert mode for lowest eigenvalues (like QMsolve)
        try:
            energies, states = eigsh(H_matrix, k=n_states, which='SM', 
                                     sigma=0, mode='normal')
        except Exception:
            # Fallback without shift-invert
            energies, states = eigsh(H_matrix, k=n_states, which='SA')
        
        # Sort by energy
        idx = np.argsort(energies)
        energies = energies[idx]
        states = states[:, idx]
        
        # Normalize
        for i in range(n_states):
            norm = np.sqrt(np.sum(np.abs(states[:, i])**2) * self.grid.dx**self.grid.ndim)
            states[:, i] /= norm
        
        return energies, states.T


class TimeEvolution:
    """
    Time-dependent Schrödinger equation solver.
    
    Implements Split-Step Fourier method (fast, O(dt³) error)
    and Crank-Nicolson method (for momentum-dependent potentials).
    
    Inspired by QMsolve's TimeSimulation class.
    """
    
    def __init__(self, hamiltonian: Hamiltonian, method: SolverMethod = SolverMethod.SPLIT_STEP):
        self.H = hamiltonian
        self.method = method
        self.grid = hamiltonian.grid
        
    def evolve(self, psi0: np.ndarray, dt: float, total_time: float, 
               store_steps: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        Evolve initial wavefunction in time.
        
        Args:
            psi0: Initial wavefunction
            dt: Time step
            total_time: Total evolution time
            store_steps: Number of snapshots to store
            
        Returns:
            times: Array of times
            psi_t: Array of wavefunctions at each stored time
        """
        n_steps = int(total_time / dt)
        store_interval = max(1, n_steps // store_steps)
        
        times = []
        psi_history = []
        
        psi = psi0.copy().astype(complex)
        
        if self.method == SolverMethod.SPLIT_STEP:
            psi_t = self._split_step_evolution(psi, dt, n_steps, store_interval, times, psi_history)
        elif self.method == SolverMethod.CRANK_NICOLSON:
            psi_t = self._crank_nicolson_evolution(psi, dt, n_steps, store_interval, times, psi_history)
        else:
            raise ValueError(f"Unknown method: {self.method}")
        
        return np.array(times), np.array(psi_history)
    
    def _split_step_evolution(self, psi: np.ndarray, dt: float, n_steps: int,
                               store_interval: int, times: List, psi_history: List) -> np.ndarray:
        """
        Split-step Fourier method.
        
        ψ(t+dt) ≈ exp(-iV*dt/2ℏ) * F⁻¹[ exp(-iT*dt/ℏ) * F[ exp(-iV*dt/2ℏ) * ψ(t) ]]
        
        This is second-order accurate and very efficient.
        """
        # Pre-compute propagators
        exp_V_half = np.exp(-1j * self.H.V * dt / (2 * self.H.hbar))
        exp_T = np.exp(-1j * self.H.T_k * dt / self.H.hbar)
        
        # Choose FFT based on dimension
        if self.grid.ndim == 1:
            fft_func, ifft_func = fft, ifft
        elif self.grid.ndim == 2:
            fft_func, ifft_func = fft2, ifft2
        else:
            fft_func, ifft_func = fftn, ifftn
        
        for step in range(n_steps):
            # Half-step in position space
            psi = exp_V_half * psi
            
            # Full step in momentum space
            psi_k = fft_func(psi)
            psi_k = exp_T * psi_k
            psi = ifft_func(psi_k)
            
            # Half-step in position space
            psi = exp_V_half * psi
            
            # Store if needed
            if step % store_interval == 0:
                times.append(step * dt)
                psi_history.append(psi.copy())
        
        return psi
    
    def _crank_nicolson_evolution(self, psi: np.ndarray, dt: float, n_steps: int,
                                   store_interval: int, times: List, psi_history: List) -> np.ndarray:
        """
        Crank-Nicolson method (implicit, unconditionally stable).
        
        (1 + iH*dt/2ℏ) * ψ(t+dt) = (1 - iH*dt/2ℏ) * ψ(t)
        
        Required for momentum-dependent potentials (e.g., magnetic fields).
        """
        H_matrix = self.H.as_sparse_matrix()
        I = sparse.eye(H_matrix.shape[0])
        
        # Pre-compute matrices
        factor = 1j * dt / (2 * self.H.hbar)
        A = I + factor * H_matrix
        B = I - factor * H_matrix
        
        # LU decomposition for efficiency
        from scipy.sparse.linalg import splu
        A_lu = splu(A.tocsc())
        
        psi_flat = psi.flatten()
        
        for step in range(n_steps):
            # Solve A * psi_new = B * psi_old
            rhs = B @ psi_flat
            psi_flat = A_lu.solve(rhs)
            
            if step % store_interval == 0:
                times.append(step * dt)
                psi_history.append(psi_flat.reshape(psi.shape).copy())
        
        return psi_flat.reshape(psi.shape)


class OpenQuantumSystem:
    """
    Open quantum system dynamics using Lindblad master equation.
    
    Inspired by QuTiP's mesolve functionality.
    
    The Lindblad equation:
    dρ/dt = -i[H, ρ] + Σ_k γ_k (L_k ρ L_k† - 1/2 {L_k† L_k, ρ})
    """
    
    def __init__(self, hamiltonian: np.ndarray, collapse_operators: List[Tuple[np.ndarray, float]]):
        """
        Args:
            hamiltonian: System Hamiltonian matrix
            collapse_operators: List of (operator, rate) tuples for Lindblad terms
        """
        self.H = hamiltonian
        self.collapse_ops = collapse_operators
        self.dim = hamiltonian.shape[0]
    
    def lindblad_superoperator(self) -> np.ndarray:
        """
        Construct the Lindbladian superoperator.
        
        Returns matrix L such that dρ_vec/dt = L @ ρ_vec
        where ρ_vec is the vectorized density matrix.
        """
        dim = self.dim
        I = np.eye(dim)
        
        # Hamiltonian contribution: -i[H, ρ] = -i(H⊗I - I⊗H^T) @ ρ_vec
        L = -1j * (np.kron(self.H, I) - np.kron(I, self.H.T))
        
        # Collapse operator contributions
        for C, gamma in self.collapse_ops:
            C_dag = C.conj().T
            C_dag_C = C_dag @ C
            
            # γ(C⊗C* - 1/2 C†C⊗I - 1/2 I⊗C^T C*)
            L += gamma * (
                np.kron(C, C.conj()) - 
                0.5 * np.kron(C_dag_C, I) - 
                0.5 * np.kron(I, C_dag_C.T)
            )
        
        return L
    
    def evolve(self, rho0: np.ndarray, times: np.ndarray) -> np.ndarray:
        """
        Evolve density matrix using the Lindblad equation.
        
        Args:
            rho0: Initial density matrix
            times: Array of times to compute ρ(t)
            
        Returns:
            Array of density matrices at each time
        """
        L = self.lindblad_superoperator()
        rho_vec = rho0.flatten()
        
        results = []
        for t in times:
            if t == 0:
                results.append(rho0.copy())
            else:
                # Use matrix exponential
                rho_vec_t = expm_multiply(L * t, rho_vec)
                results.append(rho_vec_t.reshape(self.dim, self.dim))
        
        return np.array(results)
    
    def steady_state(self) -> np.ndarray:
        """Find the steady-state density matrix."""
        L = self.lindblad_superoperator()
        
        # Steady state satisfies L @ ρ_ss = 0
        # Add normalization constraint: Tr(ρ) = 1
        from scipy.linalg import null_space
        
        null = null_space(L)
        if null.shape[1] == 0:
            raise ValueError("No steady state found")
        
        rho_ss = null[:, 0].reshape(self.dim, self.dim)
        rho_ss /= np.trace(rho_ss)  # Normalize
        
        return rho_ss


# Convenience functions for common potentials
def harmonic_oscillator_potential(omega: float = 1.0, mass: float = 1.0) -> Callable:
    """Create harmonic oscillator potential V = 1/2 m ω² x²."""
    def potential(x):
        return 0.5 * mass * omega**2 * x**2
    return potential


def double_well_potential(barrier_height: float = 5.0, well_separation: float = 2.0) -> Callable:
    """Create symmetric double-well potential."""
    def potential(x):
        return barrier_height * (x**2 - well_separation**2)**2 / well_separation**4
    return potential


def hydrogen_potential(Z: int = 1) -> Callable:
    """Coulomb potential for hydrogen-like atom (3D)."""
    def potential(x, y, z):
        r = np.sqrt(x**2 + y**2 + z**2 + 1e-10)  # Regularization
        return -Z / r
    return potential


def gaussian_wavepacket(x0: float = 0.0, p0: float = 0.0, sigma: float = 1.0) -> Callable:
    """Create Gaussian wavepacket initial condition."""
    def psi(x):
        norm = (2 * np.pi * sigma**2)**(-0.25)
        return norm * np.exp(-(x - x0)**2 / (4 * sigma**2)) * np.exp(1j * p0 * x)
    return psi


# Integration with Beyond Frontier knowledge base
def get_schrodinger_solutions(equation_id: str = "schrodinger_time_independent") -> Dict[str, Any]:
    """
    Get analytical solutions that can be compared with numerical results.
    
    Returns dictionary with:
    - exact_energies: Analytical energy levels (if available)
    - exact_states: Analytical wave functions (if available)
    """
    solutions = {
        "harmonic_oscillator": {
            "energies": lambda n, omega=1: (n + 0.5) * omega,  # E_n = ℏω(n + 1/2)
            "states": "Hermite polynomials × Gaussian",
        },
        "hydrogen": {
            "energies": lambda n, Z=1: -13.6 * Z**2 / n**2,  # eV
            "states": "Laguerre polynomials × Spherical harmonics",
        },
        "infinite_well": {
            "energies": lambda n, L=1, m=1: n**2 * np.pi**2 / (2 * m * L**2),
            "states": "sin(nπx/L)",
        },
    }
    return solutions
