# api/services/
"""
Service Layer for Business Logic.

Inspired by DREAM architecture - clean separation of concerns.

First Principle Analysis:
- Services: Encapsulate business logic separate from API endpoints
- Dependency injection: Services can be injected into endpoints
- Mathematical foundation: Service-oriented architecture, dependency injection
- Architecture: Service layer between API and core logic
"""

from .simulation_service import SimulationService
from .node_service import NodeService
from .rule_service import RuleService
from .evolution_service import EvolutionService

__all__ = [
    'SimulationService',
    'NodeService',
    'RuleService',
    'EvolutionService'
]

