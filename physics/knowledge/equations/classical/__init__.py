"""
PATH: physics/knowledge/equations/classical/__init__.py
PURPOSE: Classical mechanics equations
"""

from .newton import NODES as NEWTON_NODES
from .energy import NODES as ENERGY_NODES
from .momentum import NODES as MOMENTUM_NODES
from .oscillations import NODES as OSCILLATION_NODES
from .rotational import NODES as ROTATIONAL_NODES
from .lagrangian import NODES as LAGRANGIAN_NODES
from .orbital import NODES as ORBITAL_NODES
from .elasticity import NODES as ELASTICITY_NODES

NODES = (
    NEWTON_NODES + ENERGY_NODES + MOMENTUM_NODES + OSCILLATION_NODES +
    ROTATIONAL_NODES + LAGRANGIAN_NODES + ORBITAL_NODES + ELASTICITY_NODES
)

__all__ = ['NODES']
