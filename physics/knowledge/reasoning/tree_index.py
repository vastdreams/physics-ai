"""
PATH: physics/knowledge/reasoning/tree_index.py
PURPOSE: Build PageIndex-style tree structure from physics knowledge graph

APPROACH (inspired by PageIndex):
Instead of flat vector embeddings, we build a hierarchical tree:

Physics Knowledge
├── Classical Mechanics
│   ├── Newton's Laws
│   │   ├── First Law (Inertia)
│   │   ├── Second Law (F=ma)
│   │   └── Third Law (Action-Reaction)
│   ├── Energy
│   │   ├── Kinetic Energy
│   │   ├── Potential Energy
│   │   └── Conservation Laws
│   └── ...
├── Electromagnetism
│   ├── Maxwell's Equations
│   └── ...
└── ...

Navigation uses LLM reasoning to traverse, not similarity search.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import json


class NodeType(Enum):
    ROOT = "root"
    DOMAIN = "domain"
    SUBDOMAIN = "subdomain"
    CONCEPT = "concept"
    EQUATION = "equation"
    CONSTANT = "constant"
    PRINCIPLE = "principle"


@dataclass
class TreeNode:
    """
    A node in the physics knowledge tree.
    
    Similar to PageIndex's tree structure, but specialized for physics.
    """
    node_id: str
    title: str
    node_type: NodeType
    summary: str = ""
    
    # Tree structure
    parent_id: Optional[str] = None
    children: List['TreeNode'] = field(default_factory=list)
    
    # Physics-specific
    domain: str = ""
    related_concepts: List[str] = field(default_factory=list)
    derivation_sources: List[str] = field(default_factory=list)
    leads_to: List[str] = field(default_factory=list)
    
    # For reasoning
    keywords: List[str] = field(default_factory=list)
    reasoning_hints: str = ""  # Hints for LLM navigation
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for JSON export (PageIndex compatible format)."""
        return {
            "node_id": self.node_id,
            "title": self.title,
            "type": self.node_type.value,
            "summary": self.summary,
            "domain": self.domain,
            "keywords": self.keywords,
            "reasoning_hints": self.reasoning_hints,
            "related_concepts": self.related_concepts,
            "derivation_sources": self.derivation_sources,
            "leads_to": self.leads_to,
            "nodes": [child.to_dict() for child in self.children]
        }
    
    def get_path(self) -> str:
        """Get the path from root to this node."""
        # This would be populated during tree building
        return f"{self.domain}/{self.node_type.value}/{self.title}"


class PhysicsTreeIndex:
    """
    Hierarchical tree index for physics knowledge.
    
    Enables PageIndex-style reasoning-based retrieval:
    1. Start at root
    2. LLM reasons about which domain is relevant
    3. Navigate to subdomain
    4. Find specific equations/concepts
    
    No vector similarity - pure reasoning over structure.
    """
    
    def __init__(self):
        self.root = TreeNode(
            node_id="root",
            title="Physics Knowledge Base",
            node_type=NodeType.ROOT,
            summary="Complete physics knowledge organized by domain"
        )
        self.node_index: Dict[str, TreeNode] = {"root": self.root}
        self.domain_trees: Dict[str, TreeNode] = {}
    
    def add_domain(self, domain_id: str, title: str, summary: str, 
                   keywords: List[str] = None) -> TreeNode:
        """Add a top-level domain node."""
        node = TreeNode(
            node_id=domain_id,
            title=title,
            node_type=NodeType.DOMAIN,
            summary=summary,
            domain=domain_id,
            parent_id="root",
            keywords=keywords or []
        )
        self.root.children.append(node)
        self.node_index[domain_id] = node
        self.domain_trees[domain_id] = node
        return node
    
    def add_node(self, node_id: str, title: str, node_type: NodeType,
                 parent_id: str, summary: str = "", domain: str = "",
                 keywords: List[str] = None, 
                 reasoning_hints: str = "",
                 related: List[str] = None,
                 derives_from: List[str] = None,
                 leads_to: List[str] = None) -> Optional[TreeNode]:
        """Add a node to the tree."""
        if parent_id not in self.node_index:
            return None
        
        parent = self.node_index[parent_id]
        
        node = TreeNode(
            node_id=node_id,
            title=title,
            node_type=node_type,
            summary=summary,
            domain=domain or parent.domain,
            parent_id=parent_id,
            keywords=keywords or [],
            reasoning_hints=reasoning_hints,
            related_concepts=related or [],
            derivation_sources=derives_from or [],
            leads_to=leads_to or []
        )
        
        parent.children.append(node)
        self.node_index[node_id] = node
        return node
    
    def get_node(self, node_id: str) -> Optional[TreeNode]:
        """Get a node by ID."""
        return self.node_index.get(node_id)
    
    def get_children(self, node_id: str) -> List[TreeNode]:
        """Get children of a node."""
        node = self.node_index.get(node_id)
        return node.children if node else []
    
    def get_path_to_root(self, node_id: str) -> List[TreeNode]:
        """Get path from a node back to root."""
        path = []
        current_id = node_id
        
        while current_id:
            node = self.node_index.get(current_id)
            if not node:
                break
            path.append(node)
            current_id = node.parent_id
        
        return list(reversed(path))
    
    def to_dict(self) -> Dict[str, Any]:
        """Export entire tree as dictionary (PageIndex format)."""
        return {
            "title": self.root.title,
            "description": "Physics knowledge tree for reasoning-based retrieval",
            "domains": [child.to_dict() for child in self.root.children],
            "statistics": {
                "total_nodes": len(self.node_index),
                "domains": len(self.domain_trees)
            }
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Export as JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    def get_navigation_context(self, node_id: str) -> str:
        """
        Get context for LLM navigation from a node.
        
        Returns a structured prompt showing:
        - Current location
        - Available children (options)
        - Related concepts
        """
        node = self.node_index.get(node_id)
        if not node:
            return ""
        
        lines = [
            f"CURRENT LOCATION: {node.title}",
            f"TYPE: {node.node_type.value}",
            f"DOMAIN: {node.domain}",
            f"SUMMARY: {node.summary}",
            ""
        ]
        
        if node.keywords:
            lines.append(f"KEYWORDS: {', '.join(node.keywords)}")
        
        if node.reasoning_hints:
            lines.append(f"HINTS: {node.reasoning_hints}")
        
        if node.children:
            lines.append("")
            lines.append("AVAILABLE SUB-TOPICS:")
            for i, child in enumerate(node.children, 1):
                lines.append(f"  [{i}] {child.title}: {child.summary[:100]}...")
        
        if node.related_concepts:
            lines.append("")
            lines.append(f"RELATED: {', '.join(node.related_concepts)}")
        
        return "\n".join(lines)


def build_domain_tree(knowledge_graph: Dict) -> PhysicsTreeIndex:
    """
    Build a PhysicsTreeIndex from the knowledge graph.
    
    Transforms the flat node structure into a hierarchical tree
    suitable for reasoning-based navigation.
    """
    tree = PhysicsTreeIndex()
    nodes = knowledge_graph.get('nodes', {})
    domains = knowledge_graph.get('domains', {})
    
    # Domain metadata for better summaries
    domain_info = {
        'classical_mechanics': {
            'title': 'Classical Mechanics',
            'summary': 'Newton\'s laws, energy, momentum, oscillations. '
                      'Valid for macroscopic objects at non-relativistic speeds.',
            'keywords': ['force', 'motion', 'energy', 'momentum', 'newton', 'oscillation'],
            'hints': 'Start here for everyday physics, projectiles, springs, pendulums.'
        },
        'electromagnetism': {
            'title': 'Electromagnetism',
            'summary': 'Electric and magnetic fields, Maxwell\'s equations, waves. '
                      'Governs light, circuits, and electromagnetic interactions.',
            'keywords': ['electric', 'magnetic', 'field', 'maxwell', 'wave', 'light'],
            'hints': 'For charges, currents, fields, circuits, and light.'
        },
        'quantum_mechanics': {
            'title': 'Quantum Mechanics',
            'summary': 'Wave functions, uncertainty, Schrödinger equation. '
                      'Describes atomic and subatomic phenomena.',
            'keywords': ['quantum', 'wave', 'uncertainty', 'schrodinger', 'probability'],
            'hints': 'For atomic scales, particle behavior, wave-particle duality.'
        },
        'special_relativity': {
            'title': 'Special Relativity',
            'summary': 'Time dilation, length contraction, E=mc². '
                      'Physics at high speeds approaching light.',
            'keywords': ['relativity', 'time', 'energy', 'mass', 'lorentz', 'speed of light'],
            'hints': 'For high-speed phenomena, mass-energy equivalence.'
        },
        'general_relativity': {
            'title': 'General Relativity',
            'summary': 'Gravity as spacetime curvature, Einstein field equations. '
                      'Describes gravity, black holes, cosmology.',
            'keywords': ['gravity', 'spacetime', 'curvature', 'einstein', 'black hole'],
            'hints': 'For gravity, large masses, cosmological scales.'
        },
        'thermodynamics': {
            'title': 'Thermodynamics',
            'summary': 'Heat, work, entropy, and the laws governing energy transfer. '
                      'Describes macroscopic thermal phenomena.',
            'keywords': ['heat', 'entropy', 'temperature', 'energy', 'equilibrium'],
            'hints': 'For heat engines, thermal processes, entropy.'
        },
        'statistical_mechanics': {
            'title': 'Statistical Mechanics',
            'summary': 'Microscopic foundations of thermodynamics. '
                      'Connects particle statistics to bulk properties.',
            'keywords': ['statistics', 'partition', 'boltzmann', 'distribution', 'ensemble'],
            'hints': 'For connecting micro to macro, deriving thermo from particles.'
        },
        'universal': {
            'title': 'Universal Constants',
            'summary': 'Fundamental constants that appear across all physics. '
                      'c, h, G and derived Planck units.',
            'keywords': ['constant', 'speed of light', 'planck', 'gravitational'],
            'hints': 'For fundamental constants and natural units.'
        },
        'atomic': {
            'title': 'Atomic Physics',
            'summary': 'Atomic structure, spectra, and derived constants. '
                      'Bohr model to quantum atomic theory.',
            'keywords': ['atom', 'bohr', 'rydberg', 'spectrum', 'electron'],
            'hints': 'For atomic structure, spectroscopy, atomic constants.'
        },
        'particle_physics': {
            'title': 'Particle Physics',
            'summary': 'Fundamental particles and their properties. '
                      'Leptons, quarks, bosons, and the Standard Model.',
            'keywords': ['particle', 'mass', 'electron', 'proton', 'boson', 'quark'],
            'hints': 'For particle masses, Standard Model, fundamental particles.'
        },
        'waves': {
            'title': 'Wave Physics',
            'summary': 'Wave equations, properties, and phenomena. '
                      'Applies to mechanical, EM, and matter waves.',
            'keywords': ['wave', 'frequency', 'wavelength', 'propagation'],
            'hints': 'For wave behavior, interference, propagation.'
        }
    }
    
    # Add domains
    for domain_name, node_ids in domains.items():
        info = domain_info.get(domain_name, {
            'title': domain_name.replace('_', ' ').title(),
            'summary': f'Physics concepts in {domain_name}',
            'keywords': [domain_name],
            'hints': ''
        })
        
        tree.add_domain(
            domain_id=domain_name,
            title=info['title'],
            summary=info['summary'],
            keywords=info['keywords']
        )
        
        # Add nodes under domain
        for node_id in node_ids:
            if node_id not in nodes:
                continue
            
            node = nodes[node_id]
            
            # Determine node type
            node_type_map = {
                'constant': NodeType.CONSTANT,
                'equation': NodeType.EQUATION,
                'principle': NodeType.PRINCIPLE,
                'theorem': NodeType.CONCEPT,
                'law': NodeType.CONCEPT,
            }
            n_type = node_type_map.get(node.node_type.value, NodeType.CONCEPT)
            
            # Extract keywords from tags
            keywords = list(node.tags) if hasattr(node, 'tags') else []
            
            # Build reasoning hints
            hints = ""
            if hasattr(node, 'derives_from') and node.derives_from:
                hints += f"Derives from: {', '.join(node.derives_from)}. "
            if hasattr(node, 'leads_to') and node.leads_to:
                hints += f"Leads to: {', '.join(node.leads_to)}. "
            
            tree.add_node(
                node_id=node_id,
                title=node.name,
                node_type=n_type,
                parent_id=domain_name,
                summary=node.description if hasattr(node, 'description') else '',
                domain=domain_name,
                keywords=keywords,
                reasoning_hints=hints,
                derives_from=list(node.derives_from) if hasattr(node, 'derives_from') else [],
                leads_to=list(node.leads_to) if hasattr(node, 'leads_to') else []
            )
    
    return tree
