# physics/solvers/
"""
Equation solvers module.

This module provides various solvers for physics equations:
- Differential equation solvers (ODE/PDE)
- Symbolic solvers (SymPy integration)
- Numerical solvers
- Perturbation theory solvers
- Quantum mechanics (Schrodinger equation, open systems)
- Astrophysics (coordinates, cosmology, stellar physics)
- Physical optics (diffraction, wavefront propagation)

INTEGRATED CONCEPTS FROM:
- QMsolve: Schrodinger equation solver (BSD-3)
- QuTiP: Open quantum systems (BSD-3)
- AstroPy: Astronomical computations (BSD-3)
- SunPy: Solar physics (BSD-2)
- POPPY: Physical optics propagation (BSD-3)
"""

from .differential_solver import DifferentialSolver
from .symbolic_solver import SymbolicSolver
from .numerical_solver import NumericalSolver
from .perturbation_solver import PerturbationSolver

# Quantum mechanics solvers
from .quantum_solver import (
    QuantumGrid,
    Hamiltonian,
    TimeEvolution,
    OpenQuantumSystem,
    SolverMethod,
    AtomicUnits,
    harmonic_oscillator_potential,
    double_well_potential,
    hydrogen_potential,
    gaussian_wavepacket,
)

# Astrophysics and cosmology
from .astro_solver import (
    AstroConstants,
    SkyCoord,
    CoordinateFrame,
    Cosmology,
    StellarPhysics,
    SolarPhysics,
    OrbitalMechanics,
    Planck18,
    WMAP9,
)

# Physical optics
from .optics_solver import (
    OpticsConstants,
    Wavefront,
    OpticalElement,
    CircularAperture,
    AnnularAperture,
    ThinLens,
    ZernikeWFE,
    DoubleSlits,
    FresnelPropagator,
    FraunhoferPropagator,
    OpticalSystem,
    AnalyticalDiffraction,
    compute_psf_circular,
    compute_psf_with_aberrations,
)

__all__ = [
    # Original solvers
    'DifferentialSolver',
    'SymbolicSolver',
    'NumericalSolver',
    'PerturbationSolver',
    
    # Quantum mechanics
    'QuantumGrid',
    'Hamiltonian',
    'TimeEvolution',
    'OpenQuantumSystem',
    'SolverMethod',
    'AtomicUnits',
    'harmonic_oscillator_potential',
    'double_well_potential',
    'hydrogen_potential',
    'gaussian_wavepacket',
    
    # Astrophysics
    'AstroConstants',
    'SkyCoord',
    'CoordinateFrame',
    'Cosmology',
    'StellarPhysics',
    'SolarPhysics',
    'OrbitalMechanics',
    'Planck18',
    'WMAP9',
    
    # Optics
    'OpticsConstants',
    'Wavefront',
    'OpticalElement',
    'CircularAperture',
    'AnnularAperture',
    'ThinLens',
    'ZernikeWFE',
    'DoubleSlits',
    'FresnelPropagator',
    'FraunhoferPropagator',
    'OpticalSystem',
    'AnalyticalDiffraction',
    'compute_psf_circular',
    'compute_psf_with_aberrations',
]

