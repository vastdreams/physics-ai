# ai/nodal_vectorization/
"""
Nodal vectorization system for code files and AI components.

First Principle Analysis:
- Code files can be represented as nodes in a graph G = (V, E)
- Each node has vector embeddings v_i ∈ R^d
- Relationships (dependencies, imports, calls) form edges E
- Similarity: sim(i,j) = cos(v_i, v_j)
- Mathematical foundation: Graph theory, vector embeddings, information theory

Planning:
1. Code node representation with metadata
2. Graph builder for dependency tracking
3. Vector store for embeddings
4. Node analyzer for code structure extraction
"""

from .code_node import CodeNode
from .graph_builder import GraphBuilder
from .vector_store import VectorStore
from .node_analyzer import NodeAnalyzer

__all__ = ['CodeNode', 'GraphBuilder', 'VectorStore', 'NodeAnalyzer']

