"""
PATH: ai/context_memory/traffic_agent.py
PURPOSE: Intelligent pathfinding through the context tree.

Inspired by DREAM architecture — traffic-direction agents with micro-maps.

Mathematical model:
- Pathfinding: Find optimal route P = {bubble_1 -> bubble_2 -> ... -> bubble_n}
- Traffic signals: Weight edges based on usage and relevance
- Algorithm: Dijkstra with traffic signal weights

DEPENDENCIES:
- loggers.system_logger: structured logging
- utilities.cot_logging: chain-of-thought audit trail
- context_bubble: atomic context units
- context_tree: hierarchical structure
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel

from .context_bubble import ContextBubble
from .context_tree import ContextTree

_DEFAULT_TRAFFIC_SIGNAL = 0.1
_WEIGHT_SMOOTHING = 0.1  # added to traffic signal to avoid division by zero


@dataclass
class Pathway:
    """Represents a pathway between bubbles."""

    from_bubble: str
    to_bubble: str
    weight: float = 1.0
    usage_count: int = 0
    last_used: Optional[datetime] = None
    metadata: Dict[str, Any] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class TrafficAgent:
    """Traffic agent for intelligent pathfinding through the context tree.

    Manages pathways, tracks usage, and optimises routing.
    """

    def __init__(self, context_tree: Optional[ContextTree] = None) -> None:
        """Initialise traffic agent.

        Args:
            context_tree: Optional context tree instance.
        """
        self._logger = SystemLogger()
        self.context_tree = context_tree
        self.pathways: Dict[Tuple[str, str], Pathway] = {}
        self.usage_stats: Dict[str, int] = {}

        self._logger.log("TrafficAgent initialized", level="INFO")

    def find_path(
        self,
        start_bubble_id: str,
        target_bubble_id: str,
        max_depth: int = 10,
    ) -> Optional[List[str]]:
        """Find optimal path between bubbles.

        Uses Dijkstra's algorithm with traffic signal weights.

        Args:
            start_bubble_id: Starting bubble ID.
            target_bubble_id: Target bubble ID.
            max_depth: Maximum path depth.

        Returns:
            List of bubble IDs forming the path, or None.
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="TRAFFIC_AGENT_FIND_PATH",
            input_data={"start": start_bubble_id, "target": target_bubble_id},
            level=LogLevel.INFO,
        )

        try:
            if not self.context_tree:
                cot.end_step(
                    step_id, output_data={"error": "No context tree"}, validation_passed=False
                )
                return None

            path = self._dijkstra_pathfinding(start_bubble_id, target_bubble_id, max_depth)

            if path:
                self._update_pathway_usage(path)

            cot.end_step(
                step_id,
                output_data={"path_length": len(path) if path else 0},
                validation_passed=path is not None,
            )

            return path

        except Exception as e:
            cot.end_step(step_id, output_data={"error": str(e)}, validation_passed=False)
            self._logger.log(f"Error finding path: {e}", level="ERROR")
            return None

    def _dijkstra_pathfinding(
        self,
        start: str,
        target: str,
        max_depth: int,
    ) -> Optional[List[str]]:
        """Dijkstra's algorithm with traffic signal weights.

        Args:
            start: Starting bubble ID.
            target: Target bubble ID.
            max_depth: Maximum depth.

        Returns:
            Path as list of bubble IDs.
        """
        if not self.context_tree:
            return None

        bubbles = self.context_tree.get_all_bubbles()
        if start not in bubbles or target not in bubbles:
            return None

        distances: Dict[str, float] = {bid: float("inf") for bid in bubbles}
        distances[start] = 0.0
        previous: Dict[str, Optional[str]] = {}
        unvisited = set(bubbles)

        while unvisited:
            current = min(unvisited, key=lambda x: distances[x])

            if current == target:
                path: List[str] = []
                node: Optional[str] = current
                while node is not None:
                    path.insert(0, node)
                    node = previous.get(node)
                return path

            unvisited.remove(current)

            neighbors = self._get_neighbors(current)
            for neighbor in neighbors:
                if neighbor in unvisited:
                    bubble = bubbles[current]
                    traffic_signal = bubble.get_traffic_signal(
                        neighbor, default=_DEFAULT_TRAFFIC_SIGNAL
                    )
                    weight = 1.0 / (traffic_signal + _WEIGHT_SMOOTHING)

                    alt_distance = distances[current] + weight
                    if alt_distance < distances[neighbor]:
                        distances[neighbor] = alt_distance
                        previous[neighbor] = current

        return None

    def _get_neighbors(self, bubble_id: str) -> List[str]:
        """Get neighbouring bubbles via traffic signals."""
        if not self.context_tree:
            return []

        bubble = self.context_tree.get_bubble(bubble_id)
        if not bubble:
            return []

        return list(bubble.traffic_signals.keys())

    def _update_pathway_usage(self, path: List[str]) -> None:
        """Update usage statistics for each edge in *path*."""
        for i in range(len(path) - 1):
            from_bubble = path[i]
            to_bubble = path[i + 1]

            pathway_key = (from_bubble, to_bubble)
            if pathway_key not in self.pathways:
                self.pathways[pathway_key] = Pathway(
                    from_bubble=from_bubble, to_bubble=to_bubble
                )

            pathway = self.pathways[pathway_key]
            pathway.usage_count += 1
            pathway.last_used = datetime.now()

            usage_key = f"{from_bubble}->{to_bubble}"
            self.usage_stats[usage_key] = self.usage_stats.get(usage_key, 0) + 1

    def add_pathway(
        self,
        from_bubble: str,
        to_bubble: str,
        weight: float = 1.0,
    ) -> None:
        """Add a pathway between bubbles.

        Args:
            from_bubble: Source bubble ID.
            to_bubble: Target bubble ID.
            weight: Pathway weight.
        """
        pathway_key = (from_bubble, to_bubble)
        self.pathways[pathway_key] = Pathway(
            from_bubble=from_bubble, to_bubble=to_bubble, weight=weight
        )

        self._logger.log(f"Pathway added: {from_bubble} -> {to_bubble}", level="DEBUG")

    def get_statistics(self) -> Dict[str, Any]:
        """Return traffic agent statistics."""
        total_usage = sum(self.usage_stats.values())

        return {
            "num_pathways": len(self.pathways),
            "total_usage": total_usage,
            "most_used_pathway": (
                max(self.usage_stats.items(), key=lambda x: x[1])[0]
                if self.usage_stats
                else None
            ),
            "avg_pathway_usage": total_usage / len(self.pathways) if self.pathways else 0.0,
        }
