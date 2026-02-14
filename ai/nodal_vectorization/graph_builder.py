"""
PATH: ai/nodal_vectorization/graph_builder.py
PURPOSE: Build and maintain the nodal graph structure.

Mathematical model:
- Graph: G = (V, E) where V = CodeNodes, E = dependencies
- Adjacency: A[i][j] = 1 if node i depends on node j
- Topological order: ordering where dependencies precede dependents

DEPENDENCIES:
- loggers.system_logger: structured logging
- code_node: node data structures
- vector_store: embedding storage
"""

from typing import Any, Dict, List, Optional, Set

from loggers.system_logger import SystemLogger

from ai.nodal_vectorization.code_node import CodeNode
from ai.nodal_vectorization.vector_store import VectorStore


class GraphBuilder:
    """Builds and maintains the nodal graph structure.

    Supports:
    - Incremental node/edge addition
    - Topological sort (Kahn's algorithm)
    - Cycle detection
    - Connected component analysis
    """

    def __init__(self, vector_store: Optional[VectorStore] = None) -> None:
        """Initialise graph builder.

        Args:
            vector_store: Optional VectorStore for embeddings.
        """
        self._logger = SystemLogger()
        self.nodes: Dict[str, CodeNode] = {}
        self.edges: Dict[str, Set[str]] = {}
        self.reverse_edges: Dict[str, Set[str]] = {}
        self.vector_store = vector_store

        self._logger.log("GraphBuilder initialized", level="INFO")

    def add_node(self, node: CodeNode) -> None:
        """Add a node to the graph.

        Args:
            node: CodeNode to add.
        """
        self.nodes[node.node_id] = node

        if node.node_id not in self.edges:
            self.edges[node.node_id] = set()
        if node.node_id not in self.reverse_edges:
            self.reverse_edges[node.node_id] = set()

        for dep_id in node.dependencies:
            if dep_id in self.nodes:
                self.add_edge(node.node_id, dep_id)

        if self.vector_store:
            self.vector_store.add_node(node, node.embedding)

        self._logger.log(f"Node added to graph: {node.node_id}", level="DEBUG")

    def add_edge(self, from_id: str, to_id: str) -> None:
        """Add a directed edge (dependency) from one node to another.

        Args:
            from_id: Dependent node ID.
            to_id: Dependency node ID.
        """
        if from_id not in self.edges:
            self.edges[from_id] = set()
        if to_id not in self.reverse_edges:
            self.reverse_edges[to_id] = set()

        self.edges[from_id].add(to_id)
        self.reverse_edges[to_id].add(from_id)

        self._logger.log(f"Edge added: {from_id} -> {to_id}", level="DEBUG")

    def get_node(self, node_id: str) -> Optional[CodeNode]:
        """Get node by ID."""
        return self.nodes.get(node_id)

    def get_dependencies(self, node_id: str) -> Set[str]:
        """Get direct dependencies of a node."""
        return self.edges.get(node_id, set()).copy()

    def get_dependents(self, node_id: str) -> Set[str]:
        """Get nodes that depend on this node."""
        return self.reverse_edges.get(node_id, set()).copy()

    def get_all_dependencies(
        self,
        node_id: str,
        visited: Optional[Set[str]] = None,
    ) -> Set[str]:
        """Get all transitive dependencies (recursive).

        Mathematical: D*(v) = D(v) union { D*(u) for u in D(v) }

        Args:
            node_id: Node ID.
            visited: Set of visited nodes (for cycle detection).

        Returns:
            Set of all transitive dependency node IDs.
        """
        if visited is None:
            visited = set()

        if node_id in visited:
            return set()

        visited.add(node_id)
        all_deps: Set[str] = set()

        direct_deps = self.get_dependencies(node_id)
        all_deps.update(direct_deps)

        for dep_id in direct_deps:
            transitive_deps = self.get_all_dependencies(dep_id, visited.copy())
            all_deps.update(transitive_deps)

        return all_deps

    def topological_sort(self) -> List[str]:
        """Compute topological ordering of nodes (Kahn's algorithm).

        Returns:
            List of node IDs in topological order.
        """
        in_degree: Dict[str, int] = {nid: 0 for nid in self.nodes}

        for deps in self.edges.values():
            for dep_id in deps:
                if dep_id in in_degree:
                    in_degree[dep_id] += 1

        queue = [nid for nid, degree in in_degree.items() if degree == 0]
        result: List[str] = []

        while queue:
            node_id = queue.pop(0)
            result.append(node_id)

            for dep_id in self.get_dependents(node_id):
                in_degree[dep_id] -= 1
                if in_degree[dep_id] == 0:
                    queue.append(dep_id)

        if len(result) != len(self.nodes):
            self._logger.log("Cycle detected in dependency graph", level="WARNING")
            remaining = set(self.nodes.keys()) - set(result)
            result.extend(remaining)

        return result

    def detect_cycles(self) -> List[List[str]]:
        """Detect cycles in the dependency graph.

        Returns:
            List of cycles (each cycle is a list of node IDs).
        """
        cycles: List[List[str]] = []
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def _dfs(node_id: str, path: List[str]) -> None:
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)

            for dep_id in self.get_dependencies(node_id):
                if dep_id not in visited:
                    _dfs(dep_id, path.copy())
                elif dep_id in rec_stack:
                    cycle_start = path.index(dep_id)
                    cycle = path[cycle_start:] + [dep_id]
                    cycles.append(cycle)

            rec_stack.remove(node_id)

        for node_id in self.nodes:
            if node_id not in visited:
                _dfs(node_id, [])

        return cycles

    def get_connected_components(self) -> List[Set[str]]:
        """Find connected components in the graph (undirected).

        Returns:
            List of sets, each containing node IDs in a component.
        """
        visited: Set[str] = set()
        components: List[Set[str]] = []

        def _dfs(node_id: str, component: Set[str]) -> None:
            visited.add(node_id)
            component.add(node_id)

            for dep_id in self.get_dependencies(node_id):
                if dep_id not in visited:
                    _dfs(dep_id, component)

            for dep_id in self.get_dependents(node_id):
                if dep_id not in visited:
                    _dfs(dep_id, component)

        for node_id in self.nodes:
            if node_id not in visited:
                component: Set[str] = set()
                _dfs(node_id, component)
                components.append(component)

        return components

    def get_statistics(self) -> Dict[str, Any]:
        """Return graph statistics."""
        num_nodes = len(self.nodes)
        num_edges = sum(len(deps) for deps in self.edges.values())

        avg_degree = num_edges / num_nodes if num_nodes > 0 else 0.0

        max_deps = 0
        max_deps_node: Optional[str] = None
        for node_id, deps in self.edges.items():
            if len(deps) > max_deps:
                max_deps = len(deps)
                max_deps_node = node_id

        max_dependents = 0
        max_dependents_node: Optional[str] = None
        for node_id, deps in self.reverse_edges.items():
            if len(deps) > max_dependents:
                max_dependents = len(deps)
                max_dependents_node = node_id

        cycles = self.detect_cycles()
        components = self.get_connected_components()

        return {
            "num_nodes": num_nodes,
            "num_edges": num_edges,
            "avg_degree": avg_degree,
            "max_dependencies": max_deps,
            "max_dependencies_node": max_deps_node,
            "max_dependents": max_dependents,
            "max_dependents_node": max_dependents_node,
            "num_cycles": len(cycles),
            "num_components": len(components),
            "cycles": cycles,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary representation."""
        return {
            "nodes": {nid: node.to_dict() for nid, node in self.nodes.items()},
            "edges": {nid: list(deps) for nid, deps in self.edges.items()},
            "statistics": self.get_statistics(),
        }
