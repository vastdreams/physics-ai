"""
PATH: physics/knowledge/equations/electromagnetism/__init__.py
PURPOSE: Electromagnetism equations
"""

from .maxwell import NODES as MAXWELL_NODES
from .coulomb import NODES as COULOMB_NODES
from .waves import NODES as WAVE_NODES

NODES = MAXWELL_NODES + COULOMB_NODES + WAVE_NODES

__all__ = ['NODES']
