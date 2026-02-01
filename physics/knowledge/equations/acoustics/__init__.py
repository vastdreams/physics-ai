"""
PATH: physics/knowledge/equations/acoustics/__init__.py
PURPOSE: Acoustics and wave physics equations
"""

from .waves import NODES as WAVE_NODES
from .sound import NODES as SOUND_NODES

NODES = WAVE_NODES + SOUND_NODES

__all__ = ['NODES']
