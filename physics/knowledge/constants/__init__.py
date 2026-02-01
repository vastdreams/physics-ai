"""
PATH: physics/knowledge/constants/__init__.py
PURPOSE: Physical constants organized by category

MICRO-MODULAR STRUCTURE:
- universal.py      : c, h, hbar, G
- electromagnetic.py : e, mu0, epsilon0, alpha
- particle.py       : electron mass, proton mass, etc.
- thermodynamic.py  : kb, R, Stefan-Boltzmann
- atomic.py         : Bohr radius, Rydberg, etc.
"""

from .universal import NODES as UNIVERSAL_CONSTANTS
from .electromagnetic import NODES as EM_CONSTANTS
from .particle import NODES as PARTICLE_CONSTANTS
from .thermodynamic import NODES as THERMO_CONSTANTS
from .atomic import NODES as ATOMIC_CONSTANTS

# Aggregate all constants
NODES = (
    UNIVERSAL_CONSTANTS +
    EM_CONSTANTS +
    PARTICLE_CONSTANTS +
    THERMO_CONSTANTS +
    ATOMIC_CONSTANTS
)

__all__ = ['NODES']
