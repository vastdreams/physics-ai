# physics/knowledge/
"""
Physics knowledge graph module.

This module provides a knowledge graph for storing physics laws,
equations, experimental results, and theoretical relationships.

Includes:
- PhysicsKnowledgeGraph: Graph-based knowledge representation
- PhysicsKnowledgeBase: Complete database of proven physics
- PhysicsConstantsDatabase: All physical constants
- PhysicsEquationsDatabase: All proven equations with derivations
"""

from .physics_graph import PhysicsKnowledgeGraph
from .equations_database import (
    PhysicsKnowledgeBase,
    PhysicsConstantsDatabase,
    PhysicsEquationsDatabase,
    PhysicalConstant,
    PhysicsEquation,
    PhysicsDomain,
    EquationStatus,
    get_knowledge_base
)

__all__ = [
    'PhysicsKnowledgeGraph',
    'PhysicsKnowledgeBase',
    'PhysicsConstantsDatabase',
    'PhysicsEquationsDatabase',
    'PhysicalConstant',
    'PhysicsEquation',
    'PhysicsDomain',
    'EquationStatus',
    'get_knowledge_base'
]

