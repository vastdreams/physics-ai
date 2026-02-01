"""
PATH: physics/knowledge/equations/optics/__init__.py
PURPOSE: Optics equations
"""

from .geometric import NODES as GEOMETRIC_NODES
from .wave_optics import NODES as WAVE_NODES
from .quantum_optics import NODES as QUANTUM_NODES

NODES = GEOMETRIC_NODES + WAVE_NODES + QUANTUM_NODES

__all__ = ['NODES']
