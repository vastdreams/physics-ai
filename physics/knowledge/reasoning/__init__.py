"""
PATH: physics/knowledge/reasoning/__init__.py
PURPOSE: Reasoning-based retrieval for physics knowledge graph

INSPIRED BY: PageIndex (https://github.com/VectifyAI/PageIndex)
- Vectorless retrieval using LLM reasoning
- Tree-structured navigation
- Human-like knowledge exploration

KEY DIFFERENCES FROM VECTOR RAG:
- No embedding similarity search
- Reasoning over explicit relations
- Traceable derivation paths
- Domain-aware navigation
"""

from .tree_index import PhysicsTreeIndex, build_domain_tree
from .reasoner import PhysicsReasoner, ReasoningPath
from .retrieval import ReasoningRetriever

__all__ = [
    'PhysicsTreeIndex',
    'build_domain_tree',
    'PhysicsReasoner',
    'ReasoningPath',
    'ReasoningRetriever',
]
