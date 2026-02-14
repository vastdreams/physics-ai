"""
PATH: ai/context_memory/context_tree.py
PURPOSE: Hierarchical organisation of context bubbles.

Inspired by DREAM architecture — hierarchical context structure.

Mathematical model:
- Tree: T = (B, E) where B = bubbles, E = edges (pathways)
- Hierarchy: Parent-child relationships for organisation

DEPENDENCIES:
- loggers.system_logger: structured logging
- utilities.cot_logging: chain-of-thought audit trail
- context_bubble: atomic context units
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel

from .context_bubble import ContextBubble


@dataclass
class TreeNode:
    """Represents a node in the context tree."""

    bubble: ContextBubble
    parent: Optional[str] = None
    children: List[str] = field(default_factory=list)
    depth: int = 0


class ContextTree:
    """Hierarchical context tree for organising context bubbles.

    Features:
    - Hierarchical organisation
    - Parent-child relationships
    - Depth tracking
    - Tree traversal
    """

    def __init__(self, root_bubble: Optional[ContextBubble] = None) -> None:
        """Initialise context tree.

        Args:
            root_bubble: Optional root bubble.
        """
        self._logger = SystemLogger()
        self.nodes: Dict[str, TreeNode] = {}
        self.bubbles: Dict[str, ContextBubble] = {}
        self.root_id: Optional[str] = None

        if root_bubble:
            self.add_bubble(root_bubble, parent_id=None)
            self.root_id = root_bubble.bubble_id

        self._logger.log("ContextTree initialized", level="INFO")

    def add_bubble(
        self,
        bubble: ContextBubble,
        parent_id: Optional[str] = None,
    ) -> bool:
        """Add a bubble to the tree.

        Args:
            bubble: ContextBubble instance.
            parent_id: Optional parent bubble ID.

        Returns:
            True if added successfully.
        """
        if bubble.bubble_id in self.bubbles:
            self._logger.log(f"Bubble already exists: {bubble.bubble_id}", level="WARNING")
            return False

        depth = 0
        if parent_id and parent_id in self.nodes:
            depth = self.nodes[parent_id].depth + 1

        node = TreeNode(bubble=bubble, parent=parent_id, depth=depth)

        self.nodes[bubble.bubble_id] = node
        self.bubbles[bubble.bubble_id] = bubble

        if parent_id and parent_id in self.nodes:
            if bubble.bubble_id not in self.nodes[parent_id].children:
                self.nodes[parent_id].children.append(bubble.bubble_id)

        if parent_id is None and self.root_id is None:
            self.root_id = bubble.bubble_id

        self._logger.log(
            f"Bubble added to tree: {bubble.bubble_id} (depth={depth})", level="DEBUG"
        )
        return True

    def get_bubble(self, bubble_id: str) -> Optional[ContextBubble]:
        """Get bubble by ID."""
        return self.bubbles.get(bubble_id)

    def get_all_bubbles(self) -> Dict[str, ContextBubble]:
        """Return a shallow copy of all bubbles."""
        return self.bubbles.copy()

    def get_children(self, bubble_id: str) -> List[ContextBubble]:
        """Get child bubbles."""
        if bubble_id not in self.nodes:
            return []
        children_ids = self.nodes[bubble_id].children
        return [self.bubbles[cid] for cid in children_ids if cid in self.bubbles]

    def get_parent(self, bubble_id: str) -> Optional[ContextBubble]:
        """Get parent bubble."""
        if bubble_id not in self.nodes:
            return None
        parent_id = self.nodes[bubble_id].parent
        if parent_id:
            return self.bubbles.get(parent_id)
        return None

    def traverse_depth_first(
        self,
        bubble_id: Optional[str] = None,
        callback: Optional[Callable[[str, ContextBubble], None]] = None,
    ) -> List[str]:
        """Traverse tree depth-first.

        Args:
            bubble_id: Starting bubble ID (default: root).
            callback: Optional callback(bubble_id, bubble).

        Returns:
            List of bubble IDs in traversal order.
        """
        if bubble_id is None:
            bubble_id = self.root_id

        if bubble_id is None or bubble_id not in self.nodes:
            return []

        result: List[str] = []

        def _dfs(current_id: str) -> None:
            if current_id in self.bubbles:
                result.append(current_id)
                if callback:
                    callback(current_id, self.bubbles[current_id])
                for child_id in self.nodes[current_id].children:
                    _dfs(child_id)

        _dfs(bubble_id)
        return result

    def get_subtree(self, bubble_id: str) -> List[ContextBubble]:
        """Get subtree starting from *bubble_id*.

        Args:
            bubble_id: Root of subtree.

        Returns:
            List of bubbles in subtree.
        """
        bubble_ids = self.traverse_depth_first(bubble_id)
        return [self.bubbles[bid] for bid in bubble_ids if bid in self.bubbles]

    def get_statistics(self) -> Dict[str, Any]:
        """Return tree statistics."""
        depths = [node.depth for node in self.nodes.values()]

        return {
            "num_bubbles": len(self.bubbles),
            "num_nodes": len(self.nodes),
            "max_depth": max(depths) if depths else 0,
            "avg_depth": sum(depths) / len(depths) if depths else 0.0,
            "root_id": self.root_id,
        }
