"""
PATH: physics/knowledge/equations/relativity/__init__.py
PURPOSE: Relativity equations (special and general)
"""

from .special import NODES as SPECIAL_NODES
from .general import NODES as GENERAL_NODES

NODES = SPECIAL_NODES + GENERAL_NODES

__all__ = ['NODES']
