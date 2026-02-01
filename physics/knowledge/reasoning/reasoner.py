"""
PATH: physics/knowledge/reasoning/reasoner.py
PURPOSE: LLM-based reasoning for physics knowledge navigation

PAGEINDEX APPROACH:
Instead of: query → embed → cosine similarity → chunks
We use:     query → reason about structure → navigate tree → relevant nodes

The LLM acts like a physicist navigating a textbook:
1. "What domain does this question belong to?"
2. "Which subtopic is most relevant?"
3. "What equations/concepts apply?"
4. "What are the derivation sources?"
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Callable
from enum import Enum
import json

from .tree_index import PhysicsTreeIndex, TreeNode, NodeType


class ReasoningStep(Enum):
    """Types of reasoning steps during navigation."""
    DOMAIN_SELECTION = "domain_selection"
    TOPIC_NARROWING = "topic_narrowing"
    CONCEPT_IDENTIFICATION = "concept_identification"
    RELATION_FOLLOWING = "relation_following"
    BACKTRACK = "backtrack"
    FOUND = "found"


@dataclass
class ReasoningPath:
    """
    Records the reasoning path taken during retrieval.
    
    Unlike vector RAG which just returns chunks, we return
    the full reasoning trace - explainable and debuggable.
    """
    query: str
    steps: List[Dict[str, Any]] = field(default_factory=list)
    final_nodes: List[str] = field(default_factory=list)
    confidence: float = 0.0
    
    def add_step(self, step_type: ReasoningStep, node_id: str, 
                 reasoning: str, options_considered: List[str] = None):
        """Record a reasoning step."""
        self.steps.append({
            'type': step_type.value,
            'node_id': node_id,
            'reasoning': reasoning,
            'options': options_considered or []
        })
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'query': self.query,
            'steps': self.steps,
            'final_nodes': self.final_nodes,
            'confidence': self.confidence,
            'path_length': len(self.steps)
        }
    
    def explain(self) -> str:
        """Generate human-readable explanation of the reasoning."""
        lines = [f"Query: {self.query}", ""]
        
        for i, step in enumerate(self.steps, 1):
            lines.append(f"Step {i} ({step['type']}):")
            lines.append(f"  At: {step['node_id']}")
            lines.append(f"  Reasoning: {step['reasoning']}")
            if step.get('options'):
                lines.append(f"  Considered: {', '.join(step['options'][:5])}")
            lines.append("")
        
        lines.append(f"Found: {', '.join(self.final_nodes)}")
        lines.append(f"Confidence: {self.confidence:.2f}")
        
        return "\n".join(lines)


class PhysicsReasoner:
    """
    Reasoning-based retrieval over the physics knowledge tree.
    
    This replaces vector similarity with explicit reasoning:
    - Understands the query's physics domain
    - Navigates the tree structure logically
    - Follows derivation chains when needed
    - Provides explainable retrieval paths
    """
    
    def __init__(self, tree_index: PhysicsTreeIndex, 
                 llm_func: Optional[Callable[[str], str]] = None):
        """
        Args:
            tree_index: The physics knowledge tree
            llm_func: Optional LLM function for complex reasoning
                      Signature: (prompt: str) -> str
        """
        self.tree = tree_index
        self.llm = llm_func
        
        # Domain keyword mappings for fast initial routing
        self.domain_keywords = {
            'classical_mechanics': {
                'force', 'newton', 'momentum', 'energy', 'kinetic', 'potential',
                'acceleration', 'velocity', 'mass', 'gravity', 'pendulum',
                'spring', 'oscillation', 'harmonic', 'work', 'power'
            },
            'electromagnetism': {
                'electric', 'magnetic', 'charge', 'current', 'field', 'maxwell',
                'coulomb', 'ampere', 'faraday', 'gauss', 'wave', 'light',
                'capacitor', 'inductor', 'circuit', 'resistance'
            },
            'quantum_mechanics': {
                'quantum', 'wave function', 'schrodinger', 'heisenberg',
                'uncertainty', 'probability', 'eigenvalue', 'operator',
                'planck', 'photon', 'electron', 'atom'
            },
            'special_relativity': {
                'relativity', 'lorentz', 'time dilation', 'length contraction',
                'e=mc', 'mass energy', 'speed of light', 'relativistic'
            },
            'general_relativity': {
                'gravity', 'spacetime', 'curvature', 'einstein', 'tensor',
                'black hole', 'geodesic', 'schwarzschild', 'metric'
            },
            'thermodynamics': {
                'heat', 'temperature', 'entropy', 'thermal', 'carnot',
                'gas law', 'pressure', 'volume', 'equilibrium'
            },
            'statistical_mechanics': {
                'boltzmann', 'partition', 'statistics', 'distribution',
                'ensemble', 'microstate', 'macrostate', 'maxwell'
            }
        }
    
    def reason(self, query: str, max_depth: int = 3) -> ReasoningPath:
        """
        Perform reasoning-based retrieval.
        
        Args:
            query: Natural language physics question
            max_depth: Maximum tree traversal depth
            
        Returns:
            ReasoningPath with steps and results
        """
        path = ReasoningPath(query=query)
        query_lower = query.lower()
        
        # Step 1: Domain selection (like PageIndex first navigation)
        domain_scores = self._score_domains(query_lower)
        best_domain = max(domain_scores, key=domain_scores.get)
        
        path.add_step(
            ReasoningStep.DOMAIN_SELECTION,
            "root",
            f"Query relates to {best_domain} based on keywords",
            list(domain_scores.keys())[:5]
        )
        
        # Step 2: Navigate within domain
        domain_node = self.tree.get_node(best_domain)
        if not domain_node:
            path.confidence = 0.1
            return path
        
        # Step 3: Find relevant concepts within domain
        relevant_nodes = self._find_relevant_in_subtree(
            domain_node, query_lower, path, depth=0, max_depth=max_depth
        )
        
        path.final_nodes = [n.node_id for n in relevant_nodes]
        path.confidence = min(1.0, len(relevant_nodes) * 0.3)
        
        return path
    
    def _score_domains(self, query: str) -> Dict[str, float]:
        """Score domains by keyword overlap."""
        scores = {}
        query_words = set(query.split())
        
        for domain, keywords in self.domain_keywords.items():
            # Count keyword matches
            matches = sum(1 for kw in keywords if kw in query)
            word_matches = len(query_words & keywords)
            scores[domain] = matches + word_matches * 0.5
        
        # Ensure all domains have a score
        for domain_id in self.tree.domain_trees:
            if domain_id not in scores:
                scores[domain_id] = 0.0
        
        return scores
    
    def _find_relevant_in_subtree(self, node: TreeNode, query: str,
                                   path: ReasoningPath, depth: int,
                                   max_depth: int) -> List[TreeNode]:
        """Recursively find relevant nodes in subtree."""
        if depth >= max_depth:
            return []
        
        relevant = []
        
        for child in node.children:
            # Score this child's relevance
            score = self._relevance_score(child, query)
            
            if score > 0.3:
                path.add_step(
                    ReasoningStep.CONCEPT_IDENTIFICATION,
                    child.node_id,
                    f"'{child.title}' matches query (score: {score:.2f})",
                    [c.node_id for c in node.children[:5]]
                )
                relevant.append(child)
                
                # Also check if we should follow derivation chains
                if child.derivation_sources:
                    for source_id in child.derivation_sources[:2]:
                        source_node = self.tree.get_node(source_id)
                        if source_node:
                            path.add_step(
                                ReasoningStep.RELATION_FOLLOWING,
                                source_id,
                                f"Following derivation source: {source_id}"
                            )
                            relevant.append(source_node)
            
            # Recurse into children
            if child.children:
                relevant.extend(
                    self._find_relevant_in_subtree(
                        child, query, path, depth + 1, max_depth
                    )
                )
        
        return relevant
    
    def _relevance_score(self, node: TreeNode, query: str) -> float:
        """Score node relevance to query."""
        score = 0.0
        
        # Check title
        if any(word in node.title.lower() for word in query.split()):
            score += 0.5
        
        # Check keywords
        for keyword in node.keywords:
            if keyword.lower() in query:
                score += 0.3
        
        # Check summary
        if node.summary:
            summary_lower = node.summary.lower()
            query_words = query.split()
            matches = sum(1 for w in query_words if w in summary_lower)
            score += matches * 0.1
        
        return min(1.0, score)
    
    def explain_concept(self, node_id: str) -> str:
        """
        Generate explanation for a concept, including its derivation path.
        
        This is the "human-like retrieval" aspect - providing context
        like a textbook would, not just isolated chunks.
        """
        node = self.tree.get_node(node_id)
        if not node:
            return f"Concept '{node_id}' not found."
        
        lines = [
            f"# {node.title}",
            "",
            f"**Domain**: {node.domain}",
            f"**Type**: {node.node_type.value}",
            "",
            f"## Summary",
            node.summary or "No summary available.",
            ""
        ]
        
        # Add derivation context
        if node.derivation_sources:
            lines.append("## Derives From")
            for source_id in node.derivation_sources:
                source = self.tree.get_node(source_id)
                if source:
                    lines.append(f"- **{source.title}**: {source.summary[:100]}...")
            lines.append("")
        
        # Add what it leads to
        if node.leads_to:
            lines.append("## Leads To")
            for target_id in node.leads_to:
                target = self.tree.get_node(target_id)
                if target:
                    lines.append(f"- **{target.title}**: {target.summary[:100]}...")
            lines.append("")
        
        # Navigation hints
        if node.reasoning_hints:
            lines.append("## Connection Hints")
            lines.append(node.reasoning_hints)
        
        return "\n".join(lines)
    
    def get_derivation_chain(self, node_id: str, 
                             max_depth: int = 5) -> List[TreeNode]:
        """
        Get the full derivation chain for a concept.
        
        Traces back through 'derives_from' relations to find
        the foundational concepts.
        """
        chain = []
        visited = set()
        
        def trace_back(nid: str, depth: int):
            if depth > max_depth or nid in visited:
                return
            visited.add(nid)
            
            node = self.tree.get_node(nid)
            if not node:
                return
            
            chain.append(node)
            
            for source_id in node.derivation_sources:
                trace_back(source_id, depth + 1)
        
        trace_back(node_id, 0)
        return chain
