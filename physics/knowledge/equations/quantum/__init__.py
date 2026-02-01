"""
PATH: physics/knowledge/equations/quantum/__init__.py
PURPOSE: Quantum mechanics equations
"""

from .schrodinger import NODES as SCHRODINGER_NODES
from .uncertainty import NODES as UNCERTAINTY_NODES

NODES = SCHRODINGER_NODES + UNCERTAINTY_NODES

__all__ = ['NODES']
