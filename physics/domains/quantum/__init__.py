# physics/domains/quantum/
"""
Quantum mechanics module.

Implements Schrödinger equation, path integral formulation,
and quantum mechanical principles with synergy factors for
field theory and relativistic corrections.
"""

from .schrodinger import SchrodingerMechanics
from .path_integral import PathIntegralMechanics

__all__ = [
    'SchrodingerMechanics',
    'PathIntegralMechanics'
]

