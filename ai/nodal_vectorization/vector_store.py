"""
PATH: ai/nodal_vectorization/vector_store.py
PURPOSE: In-memory vector store for node embeddings with similarity search.

Mathematical model:
- Embeddings: E = {v_i | v_i in R^d, i in V}
- Similarity: sim(i, j) = cos(v_i, v_j)
- Nearest neighbour: NN(q, k) = {i | sim(v_i, q) in top k}

DEPENDENCIES:
- loggers.system_logger: structured logging
- code_node: node data structures
"""

from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from loggers.system_logger import SystemLogger

from ai.nodal_vectorization.code_node import CodeNode

_DEFAULT_EMBEDDING_DIM = 384


class VectorStore:
    """Stores and manages vector embeddings for code nodes.

    Supports cosine-similarity nearest-neighbour search.
    """

    def __init__(self, embedding_dim: int = _DEFAULT_EMBEDDING_DIM) -> None:
        """Initialise vector store.

        Args:
            embedding_dim: Dimension of embeddings (default: 384 for sentence-transformers).
        """
        self.embedding_dim = embedding_dim
        self._logger = SystemLogger()
        self.embeddings: Dict[str, np.ndarray] = {}
        self.nodes: Dict[str, CodeNode] = {}

        self._logger.log(f"VectorStore initialized (dim={embedding_dim})", level="INFO")

    def add_node(self, node: CodeNode, embedding: Optional[List[float]] = None) -> None:
        """Add a node to the store.

        Args:
            node: CodeNode to add.
            embedding: Optional embedding vector (padded/truncated if dim mismatches).
        """
        self.nodes[node.node_id] = node

        if embedding:
            if len(embedding) != self.embedding_dim:
                self._logger.log(
                    f"Embedding dimension mismatch: {len(embedding)} != {self.embedding_dim}",
                    level="WARNING",
                )
                if len(embedding) < self.embedding_dim:
                    embedding = embedding + [0.0] * (self.embedding_dim - len(embedding))
                else:
                    embedding = embedding[: self.embedding_dim]

            self.embeddings[node.node_id] = np.array(embedding, dtype=np.float32)
            node.set_embedding(embedding)

        self._logger.log(f"Node added to store: {node.node_id}", level="DEBUG")

    def get_embedding(self, node_id: str) -> Optional[np.ndarray]:
        """Get embedding for a node."""
        return self.embeddings.get(node_id)

    def get_node(self, node_id: str) -> Optional[CodeNode]:
        """Get node by ID."""
        return self.nodes.get(node_id)

    def similarity(self, node_id1: str, node_id2: str) -> float:
        """Compute cosine similarity between two nodes.

        Mathematical: sim(i, j) = (v_i . v_j) / (||v_i|| ||v_j||)

        Args:
            node_id1: First node ID.
            node_id2: Second node ID.

        Returns:
            Cosine similarity normalised to [0, 1].
        """
        v1 = self.embeddings.get(node_id1)
        v2 = self.embeddings.get(node_id2)

        if v1 is None or v2 is None:
            return 0.0

        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        cosine = dot_product / (norm1 * norm2)
        return float((cosine + 1.0) / 2.0)

    def find_similar(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10,
        threshold: float = 0.0,
    ) -> List[Tuple[str, float]]:
        """Find most similar nodes to a query embedding.

        Mathematical: NN(q, k) = argmax_{i in V} sim(v_i, q)

        Args:
            query_embedding: Query vector.
            top_k: Number of results to return.
            threshold: Minimum similarity threshold.

        Returns:
            List of (node_id, similarity) tuples sorted descending.
        """
        if query_embedding.shape[0] != self.embedding_dim:
            self._logger.log("Query embedding dimension mismatch", level="ERROR")
            return []

        query_norm = np.linalg.norm(query_embedding)
        if query_norm == 0:
            return []

        similarities: List[Tuple[str, float]] = []

        for node_id, embedding in self.embeddings.items():
            embedding_norm = np.linalg.norm(embedding)
            if embedding_norm == 0:
                continue

            dot_product = np.dot(query_embedding, embedding)
            cosine = dot_product / (query_norm * embedding_norm)
            sim_normalized = float((cosine + 1.0) / 2.0)

            if sim_normalized >= threshold:
                similarities.append((node_id, sim_normalized))

        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]

    def find_similar_to_node(
        self,
        node_id: str,
        top_k: int = 10,
        threshold: float = 0.0,
    ) -> List[Tuple[str, float]]:
        """Find nodes similar to a given node.

        Args:
            node_id: Reference node ID.
            top_k: Number of results.
            threshold: Minimum similarity.

        Returns:
            List of (node_id, similarity) tuples.
        """
        embedding = self.embeddings.get(node_id)
        if embedding is None:
            self._logger.log(f"Node not found: {node_id}", level="WARNING")
            return []

        results = self.find_similar(embedding, top_k + 1, threshold)
        results = [(nid, sim) for nid, sim in results if nid != node_id]

        return results[:top_k]

    def get_all_nodes(self) -> List[CodeNode]:
        """Get all nodes in the store."""
        return list(self.nodes.values())

    def get_all_node_ids(self) -> List[str]:
        """Get all node IDs."""
        return list(self.nodes.keys())

    def size(self) -> int:
        """Get number of nodes in the store."""
        return len(self.nodes)

    def clear(self) -> None:
        """Clear all nodes and embeddings."""
        self.embeddings.clear()
        self.nodes.clear()
        self._logger.log("VectorStore cleared", level="INFO")
