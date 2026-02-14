"""
PATH: ai/context_memory/path_optimizer.py
PURPOSE: Route optimisation for context pathways.

Inspired by DREAM architecture — adaptive path refinement.

Mathematical model:
- Optimisation: Minimise path cost C(path) = sum weight(edge)
- Adaptive: Update weights based on usage

DEPENDENCIES:
- loggers.system_logger: structured logging
- utilities.cot_logging: chain-of-thought audit trail
- traffic_agent: pathfinding
- context_tree: hierarchical structure
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel

from .context_tree import ContextTree
from .traffic_agent import TrafficAgent


class PathOptimizer:
    """Path optimiser for route optimisation.

    Features:
    - Route optimisation
    - Weight adjustment
    - Performance tracking
    - Adaptive refinement
    """

    def __init__(self, traffic_agent: Optional[TrafficAgent] = None) -> None:
        """Initialise path optimiser.

        Args:
            traffic_agent: Optional traffic agent instance.
        """
        self._logger = SystemLogger()
        self.traffic_agent = traffic_agent
        self.optimization_history: List[Dict[str, Any]] = []

        self._logger.log("PathOptimizer initialized", level="INFO")

    def optimize_path(
        self,
        start: str,
        target: str,
        context_tree: ContextTree,
    ) -> Optional[List[str]]:
        """Find and optimise a path between two bubbles.

        Args:
            start: Starting bubble ID.
            target: Target bubble ID.
            context_tree: Context tree instance.

        Returns:
            Optimised path, or None.
        """
        if not self.traffic_agent:
            temp_agent = TrafficAgent(context_tree)
            path = temp_agent.find_path(start, target)
        else:
            path = self.traffic_agent.find_path(start, target)

        if path:
            optimized = self._refine_path(path, context_tree)

            self.optimization_history.append({
                "timestamp": datetime.now().isoformat(),
                "start": start,
                "target": target,
                "original_length": len(path),
                "optimized_length": len(optimized) if optimized else 0,
                "improvement": len(path) - len(optimized) if optimized else 0,
            })

            return optimized

        return path

    def _refine_path(self, path: List[str], context_tree: ContextTree) -> List[str]:
        """Refine path by removing unnecessary hops.

        Args:
            path: Original path.
            context_tree: Context tree instance.

        Returns:
            Refined path.
        """
        if len(path) <= 2:
            return path

        refined = [path[0]]

        i = 0
        while i < len(path) - 1:
            for j in range(len(path) - 1, i + 1, -1):
                if self._has_direct_connection(path[i], path[j], context_tree):
                    refined.append(path[j])
                    i = j
                    break
            else:
                refined.append(path[i + 1])
                i += 1

        return refined

    @staticmethod
    def _has_direct_connection(
        bubble1_id: str,
        bubble2_id: str,
        context_tree: ContextTree,
    ) -> bool:
        """Check if a direct connection exists between two bubbles."""
        bubble1 = context_tree.get_bubble(bubble1_id)
        if not bubble1:
            return False
        return bubble2_id in bubble1.traffic_signals

    def update_weights_from_usage(self, usage_data: Dict[str, int]) -> None:
        """Update pathway weights based on usage.

        Mathematical: weight = 1 / (usage + 1)  (inverse relationship).

        Args:
            usage_data: Dictionary of pathway -> usage count.
        """
        if not self.traffic_agent:
            return

        for pathway_key, usage in usage_data.items():
            if isinstance(pathway_key, tuple) and len(pathway_key) == 2:
                from_bubble, to_bubble = pathway_key
                weight = 1.0 / (usage + 1)
                self.traffic_agent.add_pathway(from_bubble, to_bubble, weight)

    def get_optimization_statistics(self) -> Dict[str, Any]:
        """Return optimisation statistics."""
        if not self.optimization_history:
            return {}

        improvements = [
            h["improvement"]
            for h in self.optimization_history
            if h["improvement"] > 0
        ]

        return {
            "num_optimizations": len(self.optimization_history),
            "total_improvements": len(improvements),
            "avg_improvement": sum(improvements) / len(improvements) if improvements else 0.0,
            "max_improvement": max(improvements) if improvements else 0,
        }
