"""
PATH: physics/knowledge/equations/thermodynamics/__init__.py
PURPOSE: Thermodynamics equations
"""

from .laws import NODES as LAW_NODES
from .statistical import NODES as STATISTICAL_NODES
from .kinetic import NODES as KINETIC_NODES
from .phase import NODES as PHASE_NODES
from .heat_transfer import NODES as HEAT_TRANSFER_NODES
from .entropy import NODES as ENTROPY_NODES

NODES = LAW_NODES + STATISTICAL_NODES + KINETIC_NODES + PHASE_NODES + HEAT_TRANSFER_NODES + ENTROPY_NODES

__all__ = ['NODES']
