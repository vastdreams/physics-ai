"""
PATH: physics/knowledge/base/loader.py
PURPOSE: Auto-discover and load physics knowledge nodes from modular files

DESIGN PRINCIPLES:
- Nodes are discovered automatically from module exports
- Graph is built lazily on first access
- Supports hot-reloading for AI evolution
- Validates node integrity on load
"""

import importlib
import pkgutil
from typing import Dict, List, Set, Optional, Type
from pathlib import Path

from .node import KnowledgeNode, ConstantNode, EquationNode, TheoremNode, PrincipleNode
from .relation import Relation, RelationType


class NodeLoader:
    """
    Discovers and loads knowledge nodes from Python modules.
    
    Modules should export:
    - NODES: List of KnowledgeNode instances
    - RELATIONS: List of Relation instances (optional)
    """
    
    def __init__(self, base_package: str = "physics.knowledge"):
        self.base_package = base_package
        self._nodes: Dict[str, KnowledgeNode] = {}
        self._relations: Dict[str, Relation] = {}
        self._loaded_modules: Set[str] = set()
    
    def discover_modules(self, subpackage: str) -> List[str]:
        """
        Discover all modules in a subpackage.
        
        Args:
            subpackage: Subpackage name (e.g., "constants", "equations.classical")
            
        Returns:
            List of module names
        """
        full_package = f"{self.base_package}.{subpackage}"
        try:
            package = importlib.import_module(full_package)
            modules = []
            
            if hasattr(package, '__path__'):
                for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):
                    if not modname.startswith('_'):
                        modules.append(f"{full_package}.{modname}")
                        if ispkg:
                            # Recursively discover submodules
                            sub_modules = self.discover_modules(f"{subpackage}.{modname}")
                            modules.extend(sub_modules)
            
            return modules
        except ImportError:
            return []
    
    def load_module(self, module_name: str) -> tuple:
        """
        Load nodes and relations from a module.
        
        Args:
            module_name: Full module path
            
        Returns:
            Tuple of (nodes_loaded, relations_loaded)
        """
        if module_name in self._loaded_modules:
            return (0, 0)
        
        try:
            module = importlib.import_module(module_name)
            nodes_loaded = 0
            relations_loaded = 0
            
            # Load NODES if defined
            if hasattr(module, 'NODES'):
                for node in module.NODES:
                    if isinstance(node, KnowledgeNode):
                        self._nodes[node.id] = node
                        nodes_loaded += 1
            
            # Load RELATIONS if defined
            if hasattr(module, 'RELATIONS'):
                for relation in module.RELATIONS:
                    if isinstance(relation, Relation):
                        self._relations[relation.id] = relation
                        relations_loaded += 1
            
            self._loaded_modules.add(module_name)
            return (nodes_loaded, relations_loaded)
            
        except ImportError as e:
            print(f"Warning: Could not load module {module_name}: {e}")
            return (0, 0)
    
    def load_all(self, subpackages: List[str] = None) -> Dict[str, int]:
        """
        Load all nodes from specified subpackages.
        
        Args:
            subpackages: List of subpackages to load (default: all)
            
        Returns:
            Statistics dict
        """
        if subpackages is None:
            subpackages = ['constants', 'equations', 'theorems', 'principles']
        
        total_nodes = 0
        total_relations = 0
        
        for subpkg in subpackages:
            modules = self.discover_modules(subpkg)
            for module_name in modules:
                nodes, relations = self.load_module(module_name)
                total_nodes += nodes
                total_relations += relations
        
        return {
            'nodes_loaded': total_nodes,
            'relations_loaded': total_relations,
            'modules_loaded': len(self._loaded_modules)
        }
    
    @property
    def nodes(self) -> Dict[str, KnowledgeNode]:
        """Get all loaded nodes."""
        return self._nodes.copy()
    
    @property
    def relations(self) -> Dict[str, Relation]:
        """Get all loaded relations."""
        return self._relations.copy()
    
    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """Get a node by ID."""
        return self._nodes.get(node_id)
    
    def get_nodes_by_type(self, node_type: Type[KnowledgeNode]) -> List[KnowledgeNode]:
        """Get all nodes of a specific type."""
        return [n for n in self._nodes.values() if isinstance(n, node_type)]
    
    def get_nodes_by_domain(self, domain: str) -> List[KnowledgeNode]:
        """Get all nodes in a domain."""
        return [n for n in self._nodes.values() if n.domain == domain]


class GraphBuilder:
    """
    Builds a complete physics knowledge graph from loaded nodes.
    
    Resolves relations declared in nodes and creates the graph structure.
    """
    
    def __init__(self, loader: NodeLoader):
        self.loader = loader
    
    def build_graph(self) -> Dict[str, any]:
        """
        Build the complete knowledge graph.
        
        Returns:
            Graph structure with nodes, edges, and indices
        """
        nodes = self.loader.nodes
        relations = self.loader.relations
        
        # Build adjacency lists
        outgoing: Dict[str, List[str]] = {nid: [] for nid in nodes}
        incoming: Dict[str, List[str]] = {nid: [] for nid in nodes}
        
        # Process explicit relations
        for rel in relations.values():
            if rel.source_id in nodes and rel.target_id in nodes:
                outgoing[rel.source_id].append(rel.target_id)
                incoming[rel.target_id].append(rel.source_id)
                if rel.bidirectional:
                    outgoing[rel.target_id].append(rel.source_id)
                    incoming[rel.source_id].append(rel.target_id)
        
        # Process implicit relations declared in nodes
        for node in nodes.values():
            # derives_from
            for source_id in node.derives_from:
                if source_id in nodes:
                    rel = Relation(
                        source_id=node.id,
                        target_id=source_id,
                        relation_type=RelationType.DERIVES_FROM
                    )
                    relations[rel.id] = rel
                    incoming[node.id].append(source_id)
                    outgoing[source_id].append(node.id)
            
            # leads_to
            for target_id in node.leads_to:
                if target_id in nodes:
                    rel = Relation(
                        source_id=node.id,
                        target_id=target_id,
                        relation_type=RelationType.LEADS_TO
                    )
                    relations[rel.id] = rel
                    outgoing[node.id].append(target_id)
                    incoming[target_id].append(node.id)
            
            # uses
            for used_id in node.uses:
                if used_id in nodes:
                    rel = Relation(
                        source_id=node.id,
                        target_id=used_id,
                        relation_type=RelationType.USES
                    )
                    relations[rel.id] = rel
                    outgoing[node.id].append(used_id)
                    incoming[used_id].append(node.id)
        
        # Build domain index
        domains: Dict[str, List[str]] = {}
        for node in nodes.values():
            if node.domain not in domains:
                domains[node.domain] = []
            domains[node.domain].append(node.id)
        
        return {
            'nodes': nodes,
            'relations': relations,
            'outgoing': outgoing,
            'incoming': incoming,
            'domains': domains,
            'statistics': {
                'total_nodes': len(nodes),
                'total_relations': len(relations),
                'total_domains': len(domains),
                'nodes_by_type': self._count_by_type(nodes),
            }
        }
    
    def _count_by_type(self, nodes: Dict[str, KnowledgeNode]) -> Dict[str, int]:
        """Count nodes by type."""
        counts = {}
        for node in nodes.values():
            type_name = node.node_type.value
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts
    
    def find_path(self, start_id: str, end_id: str, graph: Dict) -> Optional[List[str]]:
        """
        Find shortest path between two nodes using BFS.
        """
        if start_id not in graph['nodes'] or end_id not in graph['nodes']:
            return None
        
        if start_id == end_id:
            return [start_id]
        
        visited = {start_id}
        queue = [(start_id, [start_id])]
        
        while queue:
            current, path = queue.pop(0)
            
            for neighbor in graph['outgoing'].get(current, []):
                if neighbor == end_id:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def get_derivation_tree(self, node_id: str, graph: Dict, depth: int = 3) -> Dict:
        """
        Get the derivation tree for a node (what it derives from).
        """
        if node_id not in graph['nodes']:
            return {}
        
        node = graph['nodes'][node_id]
        tree = {
            'id': node_id,
            'name': node.name,
            'type': node.node_type.value,
            'sources': []
        }
        
        if depth > 0:
            for source_id in node.derives_from:
                if source_id in graph['nodes']:
                    subtree = self.get_derivation_tree(source_id, graph, depth - 1)
                    tree['sources'].append(subtree)
        
        return tree
