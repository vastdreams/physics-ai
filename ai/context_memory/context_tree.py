# ai/context_memory/
"""
Context Tree - Hierarchical organization of context bubbles.

Inspired by DREAM architecture - hierarchical context structure.

First Principle Analysis:
- Tree: T = (B, E) where B = bubbles, E = edges (pathways)
- Hierarchy: Parent-child relationships for organization
- Mathematical foundation: Tree data structures, hierarchical graphs
- Architecture: Rooted tree with context bubbles as nodes
"""

from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
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
    """
    Hierarchical context tree for organizing context bubbles.
    
    Features:
    - Hierarchical organization
    - Parent-child relationships
    - Depth tracking
    - Tree traversal
    """
    
    def __init__(self, root_bubble: Optional[ContextBubble] = None):
        """
        Initialize context tree.
        
        Args:
            root_bubble: Optional root bubble
        """
        self.logger = SystemLogger()
        self.nodes: Dict[str, TreeNode] = {}
        self.bubbles: Dict[str, ContextBubble] = {}
        self.root_id: Optional[str] = None
        
        if root_bubble:
            self.add_bubble(root_bubble, parent_id=None)
            self.root_id = root_bubble.bubble_id
        
        self.logger.log("ContextTree initialized", level="INFO")
    
    def add_bubble(self,
                   bubble: ContextBubble,
                   parent_id: Optional[str] = None) -> bool:
        """
        Add bubble to tree.
        
        Args:
            bubble: ContextBubble instance
            parent_id: Optional parent bubble ID
            
        Returns:
            True if added successfully
        """
        if bubble.bubble_id in self.bubbles:
            self.logger.log(f"Bubble already exists: {bubble.bubble_id}", level="WARNING")
            return False
        
        # Calculate depth
        depth = 0
        if parent_id and parent_id in self.nodes:
            depth = self.nodes[parent_id].depth + 1
        
        # Create tree node
        node = TreeNode(
            bubble=bubble,
            parent=parent_id,
            depth=depth
        )
        
        self.nodes[bubble.bubble_id] = node
        self.bubbles[bubble.bubble_id] = bubble
        
        # Update parent's children
        if parent_id and parent_id in self.nodes:
            if bubble.bubble_id not in self.nodes[parent_id].children:
                self.nodes[parent_id].children.append(bubble.bubble_id)
        
        # Set as root if no parent
        if parent_id is None and self.root_id is None:
            self.root_id = bubble.bubble_id
        
        self.logger.log(f"Bubble added to tree: {bubble.bubble_id} (depth={depth})", level="DEBUG")
        return True
    
    def get_bubble(self, bubble_id: str) -> Optional[ContextBubble]:
        """Get bubble by ID."""
        return self.bubbles.get(bubble_id)
    
    def get_all_bubbles(self) -> Dict[str, ContextBubble]:
        """Get all bubbles."""
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
    
    def traverse_depth_first(self,
                            bubble_id: Optional[str] = None,
                            callback: Optional[callable] = None) -> List[str]:
        """
        Traverse tree depth-first.
        
        Args:
            bubble_id: Starting bubble ID (default: root)
            callback: Optional callback function(bubble_id, bubble)
            
        Returns:
            List of bubble IDs in traversal order
        """
        if bubble_id is None:
            bubble_id = self.root_id
        
        if bubble_id is None or bubble_id not in self.nodes:
            return []
        
        result = []
        
        def dfs(current_id: str):
            if current_id in self.bubbles:
                result.append(current_id)
                if callback:
                    callback(current_id, self.bubbles[current_id])
                
                # Traverse children
                for child_id in self.nodes[current_id].children:
                    dfs(child_id)
        
        dfs(bubble_id)
        return result
    
    def get_subtree(self, bubble_id: str) -> List[ContextBubble]:
        """
        Get subtree starting from bubble.
        
        Args:
            bubble_id: Root of subtree
            
        Returns:
            List of bubbles in subtree
        """
        bubble_ids = self.traverse_depth_first(bubble_id)
        return [self.bubbles[bid] for bid in bubble_ids if bid in self.bubbles]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get tree statistics."""
        depths = [node.depth for node in self.nodes.values()]
        
        return {
            'num_bubbles': len(self.bubbles),
            'num_nodes': len(self.nodes),
            'max_depth': max(depths) if depths else 0,
            'avg_depth': sum(depths) / len(depths) if depths else 0.0,
            'root_id': self.root_id
        }

