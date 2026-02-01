"""
PATH: physics/knowledge/equations/electromagnetism/__init__.py
PURPOSE: Electromagnetism equations
"""

from .maxwell import NODES as MAXWELL_NODES
from .coulomb import NODES as COULOMB_NODES
from .waves import NODES as WAVE_NODES
from .circuits import NODES as CIRCUIT_NODES
from .magnetic import NODES as MAGNETIC_NODES
from .radiation import NODES as RADIATION_NODES
from .electromagnetic_waves import NODES as EM_WAVE_NODES

NODES = MAXWELL_NODES + COULOMB_NODES + WAVE_NODES + CIRCUIT_NODES + MAGNETIC_NODES + RADIATION_NODES + EM_WAVE_NODES

__all__ = ['NODES']
