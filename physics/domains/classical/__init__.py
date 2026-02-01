# physics/domains/classical/
"""
Classical mechanics module.

Implements Newtonian, Lagrangian, and Hamiltonian formulations
of classical mechanics with synergy factors for relativistic
and quantum corrections.
"""

from .newtonian import NewtonianMechanics
from .lagrangian import LagrangianMechanics
from .hamiltonian import HamiltonianMechanics

__all__ = [
    'NewtonianMechanics',
    'LagrangianMechanics',
    'HamiltonianMechanics'
]

