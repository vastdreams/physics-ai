"""
PATH: physics/knowledge/equations/plasma/__init__.py
PURPOSE: Plasma physics equations
"""

from .plasma_fundamentals import NODES as FUNDAMENTAL_NODES
from .mhd import NODES as MHD_NODES

NODES = FUNDAMENTAL_NODES + MHD_NODES

__all__ = ['NODES']
