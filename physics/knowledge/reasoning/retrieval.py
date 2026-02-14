"""
PATH: physics/knowledge/reasoning/retrieval.py
PURPOSE: Main retrieval interface using reasoning-based approach

COMPARISON TO VECTOR RAG:

Traditional Vector RAG:
    query → embed(query) → cosine_similarity(embeddings) → top_k chunks
    
    Problems:
    - "similarity ≠ relevance" (PageIndex insight)
    - No understanding of physics structure
    - Can't follow derivation chains
    - Black-box retrieval

Reasoning-based Retrieval (PageIndex-inspired):
    query → understand_domain → navigate_tree → follow_relations → relevant_nodes
    
    Benefits:
    - Explainable paths
    - Domain-aware navigation
    - Follows physics relationships
    - Traceable derivations
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .tree_index import PhysicsTreeIndex, TreeNode, build_domain_tree
from .reasoner import PhysicsReasoner, ReasoningPath


@dataclass
class RetrievalResult:
    """
    Result from reasoning-based retrieval.
    
    Unlike vector RAG which returns similarity scores,
    we return reasoning traces and structured results.
    """
    query: str
    nodes: List[Dict[str, Any]]
    reasoning_path: ReasoningPath
    domain: str
    confidence: float
    
    # For PageIndex-style explainability
    explanation: str = ""
    derivation_chains: Dict[str, List[str]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'query': self.query,
            'nodes': self.nodes,
            'reasoning': self.reasoning_path.to_dict(),
            'domain': self.domain,
            'confidence': self.confidence,
            'explanation': self.explanation,
            'derivation_chains': self.derivation_chains
        }


class ReasoningRetriever:
    """
    Main interface for reasoning-based physics knowledge retrieval.
    
    Usage:
        retriever = ReasoningRetriever.from_knowledge_graph()
        result = retriever.retrieve("What is the relationship between force and acceleration?")
        print(result.explanation)
    """
    
    def __init__(self, tree: PhysicsTreeIndex, 
                 knowledge_graph: Dict = None,
                 llm_func: Optional[Callable[[str], str]] = None):
        self.tree = tree
        self.knowledge_graph = knowledge_graph or {}
        self.reasoner = PhysicsReasoner(tree, llm_func)
    
    @classmethod
    def from_knowledge_graph(cls, llm_func: Optional[Callable] = None) -> 'ReasoningRetriever':
        """
        Create retriever from the physics knowledge graph.
        """
        from physics.knowledge import get_knowledge_graph
        
        graph = get_knowledge_graph()
        tree = build_domain_tree(graph)
        
        return cls(tree, graph, llm_func)
    
    def retrieve(self, query: str, 
                 max_results: int = 5,
                 include_derivations: bool = True) -> RetrievalResult:
        """
        Retrieve relevant physics knowledge using reasoning.
        
        Args:
            query: Natural language physics question
            max_results: Maximum number of nodes to return
            include_derivations: Whether to include derivation chains
            
        Returns:
            RetrievalResult with nodes, reasoning path, and explanation
        """
        # Perform reasoning-based navigation
        path = self.reasoner.reason(query)
        
        # Get the actual node data
        nodes = []
        derivation_chains = {}
        
        for node_id in path.final_nodes[:max_results]:
            tree_node = self.tree.get_node(node_id)
            if not tree_node:
                continue
            
            # Get full node data from knowledge graph if available
            kg_node = self.knowledge_graph.get('nodes', {}).get(node_id)
            
            node_data = {
                'id': node_id,
                'title': tree_node.title,
                'type': tree_node.node_type.value,
                'domain': tree_node.domain,
                'summary': tree_node.summary,
                'keywords': tree_node.keywords
            }
            
            # Add extra data from knowledge graph
            if kg_node and hasattr(kg_node, 'to_dict'):
                node_data.update(kg_node.to_dict())
            
            nodes.append(node_data)
            
            # Get derivation chain if requested
            if include_derivations:
                chain = self.reasoner.get_derivation_chain(node_id)
                derivation_chains[node_id] = [n.node_id for n in chain]
        
        # Determine primary domain
        domain = ""
        if path.steps:
            for step in path.steps:
                if step['type'] == 'domain_selection':
                    # Extract domain from reasoning
                    domain = step.get('node_id', '')
                    break
        
        if not domain and nodes:
            domain = nodes[0].get('domain', '')
        
        # Generate explanation
        explanation = self._generate_explanation(query, path, nodes)
        
        return RetrievalResult(
            query=query,
            nodes=nodes,
            reasoning_path=path,
            domain=domain,
            confidence=path.confidence,
            explanation=explanation,
            derivation_chains=derivation_chains
        )
    
    def _generate_explanation(self, query: str, 
                              path: ReasoningPath, 
                              nodes: List[Dict]) -> str:
        """Generate human-readable explanation of retrieval."""
        lines = [
            f"## Query Analysis",
            f"**Question**: {query}",
            ""
        ]
        
        # Explain reasoning steps
        if path.steps:
            lines.append("## Reasoning Path")
            for i, step in enumerate(path.steps, 1):
                step_type = step['type'].replace('_', ' ').title()
                lines.append(f"{i}. **{step_type}**: {step['reasoning']}")
            lines.append("")
        
        # List found nodes
        if nodes:
            lines.append("## Relevant Concepts")
            for node in nodes:
                lines.append(f"- **{node['title']}** ({node['domain']})")
                if node.get('summary'):
                    lines.append(f"  {node['summary'][:150]}...")
            lines.append("")
        
        lines.append(f"**Confidence**: {path.confidence:.0%}")
        
        return "\n".join(lines)
    
    def answer_question(self, query: str) -> str:
        """
        Answer a physics question using retrieved knowledge.
        
        This combines retrieval with answer generation.
        """
        result = self.retrieve(query, include_derivations=True)
        
        if not result.nodes:
            return f"I couldn't find relevant physics concepts for: {query}"
        
        # Build answer from retrieved nodes
        lines = [
            f"# Answer to: {query}",
            "",
            result.explanation,
            "",
            "## Detailed Information",
            ""
        ]
        
        for node in result.nodes[:3]:
            lines.append(f"### {node['title']}")
            
            if node.get('latex'):
                lines.append(f"$$${node['latex']}$$$")
            
            if node.get('description'):
                lines.append(node['description'])
            
            if node.get('derivation_steps'):
                lines.append("")
                lines.append("**Derivation:**")
                for step in node['derivation_steps']:
                    lines.append(f"- {step}")
            
            lines.append("")
        
        # Add derivation context
        if result.derivation_chains:
            lines.append("## Related Concepts (Derivation Chain)")
            for node_id, chain in result.derivation_chains.items():
                if len(chain) > 1:
                    lines.append(f"- {' → '.join(chain)}")
        
        return "\n".join(lines)
    
    def get_tree_json(self) -> str:
        """Export the tree index as JSON (PageIndex format)."""
        return self.tree.to_json()
    
    def explain_reasoning(self, query: str) -> str:
        """
        Get detailed explanation of reasoning process.
        
        Useful for debugging and understanding retrieval.
        """
        path = self.reasoner.reason(query)
        return path.explain()
