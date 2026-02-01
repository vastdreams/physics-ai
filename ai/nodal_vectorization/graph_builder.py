# ai/nodal_vectorization/
"""
Graph builder for nodal graph structure.

First Principle Analysis:
- Build graph G = (V, E) from code nodes
- V = set of CodeNodes
- E = dependencies, imports, function calls
- Mathematical foundation: Graph theory, topological sorting
- Architecture: Builder pattern with incremental updates
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from loggers.system_logger import SystemLogger
from ai.nodal_vectorization.code_node import CodeNode
from ai.nodal_vectorization.vector_store import VectorStore


class GraphBuilder:
    """
    Builds and maintains the nodal graph structure.
    
    Mathematical representation:
    - Graph: G = (V, E) where V = nodes, E = edges (dependencies)
    - Adjacency: A[i][j] = 1 if node i depends on node j
    - Topological order: ordering where dependencies come before dependents
    """
    
    def __init__(self, vector_store: Optional[VectorStore] = None):
        """
        Initialize graph builder.
        
        Args:
            vector_store: Optional VectorStore for embeddings
        """
        self.logger = SystemLogger()
        self.nodes: Dict[str, CodeNode] = {}
        self.edges: Dict[str, Set[str]] = {}  # node_id -> set of dependency node_ids
        self.reverse_edges: Dict[str, Set[str]] = {}  # node_id -> set of dependent node_ids
        self.vector_store = vector_store
        
        self.logger.log("GraphBuilder initialized", level="INFO")
    
    def add_node(self, node: CodeNode) -> None:
        """
        Add a node to the graph.
        
        Args:
            node: CodeNode to add
        """
        self.nodes[node.node_id] = node
        
        # Initialize edge sets
        if node.node_id not in self.edges:
            self.edges[node.node_id] = set()
        if node.node_id not in self.reverse_edges:
            self.reverse_edges[node.node_id] = set()
        
        # Add edges from dependencies
        for dep_id in node.dependencies:
            if dep_id in self.nodes:
                self.add_edge(node.node_id, dep_id)
        
        # Add to vector store if available
        if self.vector_store:
            self.vector_store.add_node(node, node.embedding)
        
        self.logger.log(f"Node added to graph: {node.node_id}", level="DEBUG")
    
    def add_edge(self, from_id: str, to_id: str) -> None:
        """
        Add an edge from one node to another (dependency).
        
        Args:
            from_id: Dependent node ID
            to_id: Dependency node ID
        """
        if from_id not in self.edges:
            self.edges[from_id] = set()
        if to_id not in self.reverse_edges:
            self.reverse_edges[to_id] = set()
        
        self.edges[from_id].add(to_id)
        self.reverse_edges[to_id].add(from_id)
        
        self.logger.log(f"Edge added: {from_id} -> {to_id}", level="DEBUG")
    
    def get_node(self, node_id: str) -> Optional[CodeNode]:
        """Get node by ID."""
        return self.nodes.get(node_id)
    
    def get_dependencies(self, node_id: str) -> Set[str]:
        """Get direct dependencies of a node."""
        return self.edges.get(node_id, set()).copy()
    
    def get_dependents(self, node_id: str) -> Set[str]:
        """Get nodes that depend on this node."""
        return self.reverse_edges.get(node_id, set()).copy()
    
    def get_all_dependencies(self, node_id: str, visited: Optional[Set[str]] = None) -> Set[str]:
        """
        Get all transitive dependencies (recursive).
        
        Mathematical: D*(v) = D(v) ∪ ∪_{u ∈ D(v)} D*(u)
        
        Args:
            node_id: Node ID
            visited: Set of visited nodes (for cycle detection)
            
        Returns:
            Set of all transitive dependency node IDs
        """
        if visited is None:
            visited = set()
        
        if node_id in visited:
            # Cycle detected
            return set()
        
        visited.add(node_id)
        all_deps = set()
        
        direct_deps = self.get_dependencies(node_id)
        all_deps.update(direct_deps)
        
        for dep_id in direct_deps:
            transitive_deps = self.get_all_dependencies(dep_id, visited.copy())
            all_deps.update(transitive_deps)
        
        return all_deps
    
    def topological_sort(self) -> List[str]:
        """
        Compute topological ordering of nodes.
        
        Mathematical: Ordering σ such that if (i, j) ∈ E, then σ(i) < σ(j)
        
        Returns:
            List of node IDs in topological order
        """
        # Kahn's algorithm
        in_degree: Dict[str, int] = {node_id: 0 for node_id in self.nodes.keys()}
        
        # Compute in-degrees
        for node_id, deps in self.edges.items():
            for dep_id in deps:
                if dep_id in in_degree:
                    in_degree[dep_id] += 1
        
        # Find nodes with no incoming edges
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node_id = queue.pop(0)
            result.append(node_id)
            
            # Remove edges from this node
            for dep_id in self.get_dependents(node_id):
                in_degree[dep_id] -= 1
                if in_degree[dep_id] == 0:
                    queue.append(dep_id)
        
        # Check for cycles
        if len(result) != len(self.nodes):
            self.logger.log("Cycle detected in dependency graph", level="WARNING")
            # Add remaining nodes (part of cycle)
            remaining = set(self.nodes.keys()) - set(result)
            result.extend(remaining)
        
        return result
    
    def detect_cycles(self) -> List[List[str]]:
        """
        Detect cycles in the dependency graph.
        
        Returns:
            List of cycles (each cycle is a list of node IDs)
        """
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node_id: str, path: List[str]) -> None:
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)
            
            for dep_id in self.get_dependencies(node_id):
                if dep_id not in visited:
                    dfs(dep_id, path.copy())
                elif dep_id in rec_stack:
                    # Cycle found
                    cycle_start = path.index(dep_id)
                    cycle = path[cycle_start:] + [dep_id]
                    cycles.append(cycle)
            
            rec_stack.remove(node_id)
        
        for node_id in self.nodes.keys():
            if node_id not in visited:
                dfs(node_id, [])
        
        return cycles
    
    def get_connected_components(self) -> List[Set[str]]:
        """
        Find connected components in the graph.
        
        Returns:
            List of sets, each containing node IDs in a component
        """
        visited = set()
        components = []
        
        def dfs(node_id: str, component: Set[str]) -> None:
            visited.add(node_id)
            component.add(node_id)
            
            # Visit dependencies
            for dep_id in self.get_dependencies(node_id):
                if dep_id not in visited:
                    dfs(dep_id, component)
            
            # Visit dependents
            for dep_id in self.get_dependents(node_id):
                if dep_id not in visited:
                    dfs(dep_id, component)
        
        for node_id in self.nodes.keys():
            if node_id not in visited:
                component = set()
                dfs(node_id, component)
                components.append(component)
        
        return components
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics."""
        num_nodes = len(self.nodes)
        num_edges = sum(len(deps) for deps in self.edges.values())
        
        # Compute average degree
        if num_nodes > 0:
            avg_degree = num_edges / num_nodes
        else:
            avg_degree = 0.0
        
        # Find nodes with most dependencies
        max_deps = 0
        max_deps_node = None
        for node_id, deps in self.edges.items():
            if len(deps) > max_deps:
                max_deps = len(deps)
                max_deps_node = node_id
        
        # Find nodes with most dependents
        max_dependents = 0
        max_dependents_node = None
        for node_id, deps in self.reverse_edges.items():
            if len(deps) > max_dependents:
                max_dependents = len(deps)
                max_dependents_node = node_id
        
        cycles = self.detect_cycles()
        components = self.get_connected_components()
        
        return {
            'num_nodes': num_nodes,
            'num_edges': num_edges,
            'avg_degree': avg_degree,
            'max_dependencies': max_deps,
            'max_dependencies_node': max_deps_node,
            'max_dependents': max_dependents,
            'max_dependents_node': max_dependents_node,
            'num_cycles': len(cycles),
            'num_components': len(components),
            'cycles': cycles
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary representation."""
        return {
            'nodes': {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            'edges': {node_id: list(deps) for node_id, deps in self.edges.items()},
            'statistics': self.get_statistics()
        }

