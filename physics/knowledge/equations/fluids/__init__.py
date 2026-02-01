"""
PATH: physics/knowledge/equations/fluids/__init__.py
PURPOSE: Fluid dynamics equations
"""

from .fundamental import NODES as FUNDAMENTAL_NODES
from .compressible import NODES as COMPRESSIBLE_NODES
from .turbulence import NODES as TURBULENCE_NODES

NODES = FUNDAMENTAL_NODES + COMPRESSIBLE_NODES + TURBULENCE_NODES

__all__ = ['NODES']
