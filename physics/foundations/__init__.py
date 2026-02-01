# physics/foundations/
"""
First-principles foundation module.

This module establishes fundamental physical laws as immutable constraints
that all physics theories must respect. These foundations ensure that
any theory expansion or unification remains physically consistent.
"""

from .conservation_laws import ConservationLaws
from .symmetries import SymmetryChecker
from .constraints import PhysicsConstraints

__all__ = [
    'ConservationLaws',
    'SymmetryChecker',
    'PhysicsConstraints'
]

