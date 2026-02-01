"""
PATH: physics/knowledge/equations/thermodynamics/__init__.py
PURPOSE: Thermodynamics equations
"""

from .laws import NODES as LAW_NODES
from .statistical import NODES as STATISTICAL_NODES

NODES = LAW_NODES + STATISTICAL_NODES

__all__ = ['NODES']
