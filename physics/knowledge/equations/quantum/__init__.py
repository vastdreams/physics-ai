"""
PATH: physics/knowledge/equations/quantum/__init__.py
PURPOSE: Quantum mechanics equations
"""

from .schrodinger import NODES as SCHRODINGER_NODES
from .uncertainty import NODES as UNCERTAINTY_NODES
from .angular_momentum import NODES as ANGULAR_MOMENTUM_NODES
from .perturbation import NODES as PERTURBATION_NODES
from .scattering import NODES as SCATTERING_NODES
from .many_body import NODES as MANY_BODY_NODES
from .hydrogen import NODES as HYDROGEN_NODES
from .quantum_field import NODES as QFT_NODES

NODES = (
    SCHRODINGER_NODES + UNCERTAINTY_NODES + ANGULAR_MOMENTUM_NODES +
    PERTURBATION_NODES + SCATTERING_NODES + MANY_BODY_NODES + HYDROGEN_NODES +
    QFT_NODES
)

__all__ = ['NODES']
