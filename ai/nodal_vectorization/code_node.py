# ai/nodal_vectorization/
"""
Code node representation.

First Principle Analysis:
- Each code file/module is a node in graph G = (V, E)
- Node attributes: file_path, dependencies, embeddings, metadata
- Mathematical foundation: Graph theory, information theory
- Architecture: Immutable node structure with computed properties
"""

from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
import hashlib
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from loggers.system_logger import SystemLogger


@dataclass
class CodeNode:
    """
    Represents a code file/module as a node in the nodal graph.
    
    Mathematical representation:
    - Node: v_i ∈ V where V is set of all code nodes
    - Attributes: A(v_i) = {file_path, dependencies, embedding, metadata}
    - Edges: E(v_i) = {(v_i, v_j) | v_j ∈ dependencies(v_i)}
    """
    
    file_path: str
    node_id: str = field(default="")
    dependencies: Set[str] = field(default_factory=set)
    imports: Set[str] = field(default_factory=set)
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"
    hash: str = field(default="")
    
    def __post_init__(self):
        """Initialize node after creation."""
        self.logger = SystemLogger()
        
        # Generate node_id if not provided
        if not self.node_id:
            self.node_id = self._generate_node_id()
        
        # Compute hash if not provided
        if not self.hash:
            self.hash = self._compute_hash()
        
        self.logger.log(f"CodeNode created: {self.node_id} ({self.file_path})", level="DEBUG")
    
    def _generate_node_id(self) -> str:
        """Generate unique node ID from file path."""
        # Use normalized file path as base
        normalized = Path(self.file_path).as_posix().replace('/', '_').replace('.', '_')
        return f"node_{normalized}"
    
    def _compute_hash(self) -> str:
        """Compute hash of node content for change detection."""
        # Hash based on file path and key attributes
        content = f"{self.file_path}{sorted(self.dependencies)}{sorted(self.imports)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def add_dependency(self, dependency: str) -> None:
        """Add a dependency to this node."""
        if dependency != self.node_id:  # Avoid self-dependencies
            self.dependencies.add(dependency)
            self.logger.log(f"Dependency added: {dependency} -> {self.node_id}", level="DEBUG")
    
    def add_import(self, import_name: str) -> None:
        """Add an import to this node."""
        self.imports.add(import_name)
        self.logger.log(f"Import added: {import_name} -> {self.node_id}", level="DEBUG")
    
    def set_embedding(self, embedding: List[float]) -> None:
        """Set vector embedding for this node."""
        if embedding:
            self.embedding = embedding
            self.metadata['embedding_dim'] = len(embedding)
            self.logger.log(f"Embedding set for {self.node_id} (dim={len(embedding)})", level="DEBUG")
    
    def update_metadata(self, key: str, value: Any) -> None:
        """Update node metadata."""
        self.metadata[key] = value
        self.logger.log(f"Metadata updated: {key} for {self.node_id}", level="DEBUG")
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self.metadata.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation."""
        return {
            'node_id': self.node_id,
            'file_path': self.file_path,
            'dependencies': list(self.dependencies),
            'imports': list(self.imports),
            'functions': self.functions,
            'classes': self.classes,
            'embedding_dim': len(self.embedding) if self.embedding else 0,
            'version': self.version,
            'hash': self.hash,
            'metadata': self.metadata
        }
    
    def similarity(self, other: 'CodeNode') -> float:
        """
        Compute cosine similarity with another node.
        
        Mathematical: sim(i,j) = cos(v_i, v_j) = (v_i · v_j) / (||v_i|| ||v_j||)
        
        Args:
            other: Another CodeNode
            
        Returns:
            Cosine similarity in [0, 1]
        """
        if not self.embedding or not other.embedding:
            return 0.0
        
        if len(self.embedding) != len(other.embedding):
            self.logger.log("Embedding dimension mismatch", level="WARNING")
            return 0.0
        
        # Cosine similarity
        import numpy as np
        v1 = np.array(self.embedding)
        v2 = np.array(other.embedding)
        
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        # Normalize to [0, 1] from [-1, 1]
        return (similarity + 1.0) / 2.0
    
    def has_dependency(self, node_id: str) -> bool:
        """Check if node has a specific dependency."""
        return node_id in self.dependencies
    
    def get_dependency_depth(self, all_nodes: Dict[str, 'CodeNode']) -> int:
        """
        Compute maximum dependency depth.
        
        Mathematical: depth(v_i) = 1 + max(depth(v_j) for v_j ∈ dependencies(v_i))
        
        Args:
            all_nodes: Dictionary of all nodes in graph
            
        Returns:
            Maximum dependency depth
        """
        if not self.dependencies:
            return 0
        
        max_depth = 0
        for dep_id in self.dependencies:
            if dep_id in all_nodes:
                dep_depth = all_nodes[dep_id].get_dependency_depth(all_nodes)
                max_depth = max(max_depth, dep_depth)
        
        return 1 + max_depth

