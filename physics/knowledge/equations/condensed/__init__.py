"""
PATH: physics/knowledge/equations/condensed/__init__.py
PURPOSE: Condensed matter physics equations
"""

from .solid_state import NODES as SOLID_STATE_NODES
from .superconductivity import NODES as SC_NODES

NODES = SOLID_STATE_NODES + SC_NODES

__all__ = ['NODES']
