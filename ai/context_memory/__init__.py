# ai/context_memory/
"""
Intelligent Context Memory System with Micro-Agents.

Inspired by DREAM architecture - traffic-direction agents with micro-maps.

First Principle Analysis:
- Context bubbles: Atomic units of context with embedded micro-agents
- Traffic signals: Weighted pathways through knowledge graph
- Pathfinding: Optimal route discovery through context tree
- Mathematical foundation: Graph theory, pathfinding algorithms, attention mechanisms
- Architecture: Hierarchical context tree with micro-agentic blueprints
"""

from .context_bubble import ContextBubble
from .micro_agent import MicroAgent
from .traffic_agent import TrafficAgent
from .context_tree import ContextTree
from .path_optimizer import PathOptimizer
from .usage_tracker import UsageTracker

__all__ = [
    'ContextBubble',
    'MicroAgent',
    'TrafficAgent',
    'ContextTree',
    'PathOptimizer',
    'UsageTracker'
]

