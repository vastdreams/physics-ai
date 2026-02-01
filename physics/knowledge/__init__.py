"""
PATH: physics/knowledge/__init__.py
PURPOSE: Physics knowledge graph module with micro-modular architecture

ARCHITECTURE:
├── base/               # Core node and relation types
│   ├── node.py        # KnowledgeNode, ConstantNode, EquationNode, etc.
│   ├── relation.py    # Relation types and factory functions
│   └── loader.py      # Auto-discovery and graph building
├── constants/          # Physical constants by category
│   ├── universal.py   # c, h, G, Planck units
│   ├── electromagnetic.py
│   ├── particle.py    # Masses
│   ├── thermodynamic.py
│   └── atomic.py      # Bohr radius, Rydberg, etc.
├── equations/          # Equations by domain
│   ├── classical/     # Newton, energy, momentum, oscillations
│   ├── electromagnetism/  # Maxwell, Coulomb, waves
│   ├── quantum/       # Schrödinger, uncertainty
│   ├── relativity/    # Special and general
│   └── thermodynamics/# Laws, statistical mechanics
└── physics_graph.py   # Legacy graph implementation

USAGE:
    from physics.knowledge import get_knowledge_graph
    
    graph = get_knowledge_graph()
    print(graph['statistics'])
    
    # Get a specific node
    node = graph['nodes']['newton_second_law']
    
    # Find derivation path
    from physics.knowledge.base import GraphBuilder
    builder = GraphBuilder(loader)
    path = builder.find_path('newton_second_law', 'escape_velocity', graph)
"""

# Legacy import for backwards compatibility
from .physics_graph import PhysicsKnowledgeGraph

# New micro-modular imports
from .base import (
    KnowledgeNode,
    ConstantNode,
    EquationNode,
    TheoremNode,
    PrincipleNode,
    NodeType,
    NodeStatus,
    Relation,
    RelationType,
    DerivesFrom,
    LeadsTo,
    Uses,
    Requires,
    NodeLoader,
    GraphBuilder,
)

# Singleton instances
_loader = None
_graph = None


def get_loader() -> NodeLoader:
    """Get or create the singleton node loader."""
    global _loader
    if _loader is None:
        _loader = NodeLoader()
        _loader.load_all()
    return _loader


def get_knowledge_graph() -> dict:
    """
    Get the complete physics knowledge graph.
    
    Returns:
        Dictionary with:
        - nodes: Dict[str, KnowledgeNode]
        - relations: Dict[str, Relation]
        - outgoing: Dict[str, List[str]]
        - incoming: Dict[str, List[str]]
        - domains: Dict[str, List[str]]
        - statistics: Dict[str, Any]
    """
    global _graph
    if _graph is None:
        loader = get_loader()
        builder = GraphBuilder(loader)
        _graph = builder.build_graph()
    return _graph


def reload_knowledge():
    """Force reload of all knowledge (for development/evolution)."""
    global _loader, _graph
    _loader = None
    _graph = None
    return get_knowledge_graph()


__all__ = [
    # Legacy
    'PhysicsKnowledgeGraph',
    
    # Node types
    'KnowledgeNode',
    'ConstantNode',
    'EquationNode',
    'TheoremNode',
    'PrincipleNode',
    'NodeType',
    'NodeStatus',
    
    # Relations
    'Relation',
    'RelationType',
    'DerivesFrom',
    'LeadsTo',
    'Uses',
    'Requires',
    
    # Loaders
    'NodeLoader',
    'GraphBuilder',
    
    # Functions
    'get_loader',
    'get_knowledge_graph',
    'reload_knowledge',
]
