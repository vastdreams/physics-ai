# physics/domains/
"""
Physics domain modules.

This module contains domain-specific physics implementations:
- Classical mechanics (Newtonian, Lagrangian, Hamiltonian)
- Quantum mechanics (Schrödinger, path integral)
- Field theory (EM, gauge, GR)
- Statistical mechanics (thermodynamics, ensembles)
"""

from .classical.newtonian import NewtonianMechanics
from .classical.lagrangian import LagrangianMechanics
from .classical.hamiltonian import HamiltonianMechanics

__all__ = [
    'NewtonianMechanics',
    'LagrangianMechanics',
    'HamiltonianMechanics'
]

