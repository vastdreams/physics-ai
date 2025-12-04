# physics/
"""
Physics integration module.

This module integrates domain-specific physics knowledge
into the AI system.
"""

from .models import PhysicsModel
from .equations import EquationSolver
from .theory_integration import TheoryIntegrator

__all__ = [
    'PhysicsModel',
    'EquationSolver',
    'TheoryIntegrator'
]

