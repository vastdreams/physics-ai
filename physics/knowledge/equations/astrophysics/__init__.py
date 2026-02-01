"""
PATH: physics/knowledge/equations/astrophysics/__init__.py
PURPOSE: Astrophysics and cosmology equations
"""

from .stellar import NODES as STELLAR_NODES
from .cosmology import NODES as COSMOLOGY_NODES

NODES = STELLAR_NODES + COSMOLOGY_NODES

__all__ = ['NODES']
