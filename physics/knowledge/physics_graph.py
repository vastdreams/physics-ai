"""
PATH: physics/knowledge/physics_graph.py
PURPOSE: Legacy physics knowledge graph implementation

Stores physics laws, equations, and relationships in a directed graph.
Uses breadth-first search (BFS) for shortest derivation-path finding.

FLOW:
┌────────────┐    ┌───────────────┐    ┌─────────────┐
│ Add nodes/ │ →  │ Build graph   │ →  │ Query/Find  │
│ edges      │    │ with indices  │    │ paths       │
└────────────┘    └───────────────┘    └─────────────┘

DEPENDENCIES:
- validators.data_validator: Input validation
- loggers.system_logger: Structured logging
"""

from typing import Any, Dict, List, Optional, Set, Tuple

from loggers.system_logger import SystemLogger
from validators.data_validator import DataValidator


class PhysicsKnowledgeGraph:
    """
    Physics knowledge graph implementation.

    Stores physics laws, equations, and relationships in a graph structure
    for querying and reasoning about physics knowledge.
    """

    def __init__(self) -> None:
        """Initialize physics knowledge graph."""
        self.validator = DataValidator()
        self._logger = SystemLogger()

        # Graph structure: {node_id: {properties, edges}}
        self.nodes: Dict[int, Dict[str, Any]] = {}
        self.edges: Dict[Tuple[int, int, str], Dict[str, Any]] = {}
        self.node_counter: int = 0

        # Index for fast lookup
        self.name_to_id: Dict[str, int] = {}

        self._logger.log("PhysicsKnowledgeGraph initialized", level="INFO")

    def add_node(self,
                  name: str,
                  node_type: str,
                  properties: Optional[Dict[str, Any]] = None) -> int:
        """
        Add a node to the knowledge graph.

        Args:
            name: Node name (e.g., "Schrödinger Equation")
            node_type: Type (e.g., "equation", "law", "theory", "experiment")
            properties: Additional properties dictionary

        Returns:
            Node ID
        """
        if properties is None:
            properties = {}

        node_id = self.node_counter
        self.node_counter += 1

        self.nodes[node_id] = {
            'id': node_id,
            'name': name,
            'type': node_type,
            'properties': properties
        }

        self.name_to_id[name] = node_id

        self._logger.log(f"Node added: {name} (type: {node_type})", level="DEBUG")
        return node_id

    def add_edge(self,
                  source_name: str,
                  target_name: str,
                  relation_type: str,
                  properties: Optional[Dict[str, Any]] = None) -> None:
        """
        Add an edge to the knowledge graph.

        Args:
            source_name: Source node name
            target_name: Target node name
            relation_type: Relation type (e.g., "derives_from", "validates", "connects_to")
            properties: Additional edge properties
        """
        if properties is None:
            properties = {}

        source_id = self.name_to_id.get(source_name)
        target_id = self.name_to_id.get(target_name)

        if source_id is None or target_id is None:
            self._logger.log(f"Invalid node names: {source_name}, {target_name}", level="ERROR")
            raise ValueError("Both source and target nodes must exist")

        edge_key = (source_id, target_id, relation_type)
        self.edges[edge_key] = {
            'source': source_id,
            'target': target_id,
            'relation': relation_type,
            'properties': properties
        }

        self._logger.log(
            f"Edge added: {source_name} --[{relation_type}]--> {target_name}",
            level="DEBUG"
        )

    def get_node(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get node by name.

        Args:
            name: Node name

        Returns:
            Node dictionary or None
        """
        node_id = self.name_to_id.get(name)
        if node_id is None:
            return None
        return self.nodes.get(node_id)

    def get_related_nodes(self,
                          node_name: str,
                          relation_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get nodes related to a given node.

        Args:
            node_name: Node name
            relation_type: Filter by relation type (None = all)

        Returns:
            List of related nodes
        """
        node_id = self.name_to_id.get(node_name)
        if node_id is None:
            return []

        related: List[Dict[str, Any]] = []
        for (source_id, target_id, rel_type), _edge_props in self.edges.items():
            if relation_type is None or rel_type == relation_type:
                if source_id == node_id:
                    related.append(self.nodes[target_id])
                elif target_id == node_id:
                    related.append(self.nodes[source_id])

        return related

    def find_derivation_path(self,
                              start_name: str,
                              end_name: str,
                              max_depth: int = 10) -> Optional[List[str]]:
        """
        Find shortest derivation path between two nodes using BFS.

        Args:
            start_name: Starting node name
            end_name: Ending node name
            max_depth: Maximum search depth

        Returns:
            List of node names in path or None
        """
        start_id = self.name_to_id.get(start_name)
        end_id = self.name_to_id.get(end_name)

        if start_id is None or end_id is None:
            return None

        if start_id == end_id:
            return [start_name]

        # BFS
        queue: List[Tuple[int, List[str]]] = [(start_id, [start_name])]
        visited: Set[int] = {start_id}

        while queue:
            current_id, path = queue.pop(0)
            depth = len(path) - 1

            if depth >= max_depth:
                continue

            for (source_id, target_id, _rel_type), _ in self.edges.items():
                if source_id == current_id and target_id not in visited:
                    target_name = self.nodes[target_id]['name']
                    new_path = path + [target_name]

                    if target_id == end_id:
                        return new_path

                    visited.add(target_id)
                    queue.append((target_id, new_path))

        return None

    def add_physics_law(self,
                        law_name: str,
                        equation: str,
                        domain: str,
                        derived_from: Optional[List[str]] = None) -> int:
        """
        Add a physics law to the knowledge graph.

        Args:
            law_name: Name of the law
            equation: Mathematical equation
            domain: Physics domain (e.g., "classical", "quantum")
            derived_from: List of laws this derives from

        Returns:
            Node ID
        """
        properties = {
            'equation': equation,
            'domain': domain
        }

        node_id = self.add_node(law_name, 'law', properties)

        if derived_from:
            for source_law in derived_from:
                if source_law in self.name_to_id:
                    self.add_edge(source_law, law_name, 'derives_from')

        self._logger.log(f"Physics law added: {law_name}", level="INFO")
        return node_id

    def query_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """
        Query nodes by physics domain.

        Args:
            domain: Physics domain name

        Returns:
            List of nodes in that domain
        """
        results: List[Dict[str, Any]] = []
        for _node_id, node_data in self.nodes.items():
            if node_data.get('properties', {}).get('domain') == domain:
                results.append(node_data)

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get knowledge graph statistics.

        Returns:
            Dictionary with node/edge counts grouped by type
        """
        node_types: Dict[str, int] = {}
        relation_types: Dict[str, int] = {}

        for _node_id, node_data in self.nodes.items():
            node_type = node_data.get('type', 'unknown')
            node_types[node_type] = node_types.get(node_type, 0) + 1

        for (_, _, rel_type), _ in self.edges.items():
            relation_types[rel_type] = relation_types.get(rel_type, 0) + 1

        stats = {
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'node_types': node_types,
            'relation_types': relation_types
        }

        self._logger.log(f"Knowledge graph statistics: {stats}", level="INFO")
        return stats
