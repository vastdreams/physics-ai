# ai/equational/
"""
Equation Store - Knowledge base for physics equations.

Inspired by DREAM architecture - structured equation knowledge base.

First Principle Analysis:
- Store: S = {equations, relationships, metadata}
- Relationships: Link equations to theories, domains, variables
- Mathematical foundation: Knowledge graphs, relational databases
- Architecture: Structured storage with query capabilities
"""

from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from .equation_extractor import ExtractedEquation
from physics.knowledge.physics_graph import PhysicsKnowledgeGraph


@dataclass
class StoredEquation:
    """Stored equation with relationships."""
    equation: ExtractedEquation
    theory_links: List[str] = field(default_factory=list)
    domain_links: List[str] = field(default_factory=list)
    related_equations: List[str] = field(default_factory=list)
    validated: bool = False
    stored_at: datetime = field(default_factory=datetime.now)


class EquationStore:
    """
    Equation knowledge base.
    
    Features:
    - Equation storage
    - Relationship tracking
    - Query capabilities
    - Integration with physics knowledge graph
    """
    
    def __init__(self, physics_graph: Optional[PhysicsKnowledgeGraph] = None):
        """
        Initialize equation store.
        
        Args:
            physics_graph: Optional physics knowledge graph
        """
        self.logger = SystemLogger()
        self.equations: Dict[str, StoredEquation] = {}
        self.physics_graph = physics_graph or PhysicsKnowledgeGraph()
        
        self.logger.log("EquationStore initialized", level="INFO")
    
    def store_equation(self,
                      equation: ExtractedEquation,
                      theory_links: Optional[List[str]] = None,
                      domain_links: Optional[List[str]] = None) -> bool:
        """
        Store equation in knowledge base.
        
        Args:
            equation: ExtractedEquation instance
            theory_links: Optional theory links
            domain_links: Optional domain links
            
        Returns:
            True if stored successfully
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="STORE_EQUATION",
            input_data={'equation_id': equation.equation_id},
            level=LogLevel.INFO
        )
        
        try:
            stored = StoredEquation(
                equation=equation,
                theory_links=theory_links or [],
                domain_links=domain_links or []
            )
            
            self.equations[equation.equation_id] = stored
            
            # Add to physics knowledge graph
            node_id = self.physics_graph.add_node(
                name=equation.equation_id,
                node_type='equation',
                properties={
                    'equation': equation.equation,
                    'domain': equation.domain,
                    'variables': equation.variables
                }
            )
            
            # Link to theories if provided
            for theory in theory_links or []:
                theory_node_id = self.physics_graph.name_to_id.get(theory)
                if theory_node_id is not None:
                    self.physics_graph.add_edge(
                        source_name=equation.equation_id,
                        target_name=theory,
                        relation_type='belongs_to'
                    )
            
            cot.end_step(
                step_id,
                output_data={'stored': True, 'node_id': node_id},
                validation_passed=True
            )
            
            self.logger.log(f"Equation stored: {equation.equation_id}", level="INFO")
            
            return True
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error storing equation: {str(e)}", level="ERROR")
            return False
    
    def query_equations(self,
                       domain: Optional[str] = None,
                       variables: Optional[List[str]] = None,
                       theory: Optional[str] = None) -> List[StoredEquation]:
        """
        Query equations by criteria.
        
        Args:
            domain: Physics domain filter
            variables: Variables filter
            theory: Theory filter
            
        Returns:
            List of matching equations
        """
        results = []
        
        for stored in self.equations.values():
            eq = stored.equation
            
            # Domain filter
            if domain and eq.domain != domain:
                continue
            
            # Variables filter
            if variables:
                if not any(v in eq.variables for v in variables):
                    continue
            
            # Theory filter
            if theory and theory not in stored.theory_links:
                continue
            
            results.append(stored)
        
        return results
    
    def link_equations(self, eq_id1: str, eq_id2: str, relation_type: str = 'related') -> bool:
        """
        Link two equations.
        
        Args:
            eq_id1: First equation ID
            eq_id2: Second equation ID
            relation_type: Type of relationship
            
        Returns:
            True if linked successfully
        """
        if eq_id1 not in self.equations or eq_id2 not in self.equations:
            return False
        
        self.equations[eq_id1].related_equations.append(eq_id2)
        self.equations[eq_id2].related_equations.append(eq_id1)
        
        # Add edge to physics graph
        self.physics_graph.add_edge(
            source_name=eq_id1,
            target_name=eq_id2,
            relation_type=relation_type
        )
        
        self.logger.log(f"Equations linked: {eq_id1} <-> {eq_id2}", level="DEBUG")
        
        return True
    
    def get_equation(self, equation_id: str) -> Optional[StoredEquation]:
        """Get stored equation by ID."""
        return self.equations.get(equation_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get store statistics."""
        domains = {}
        for stored in self.equations.values():
            domain = stored.equation.domain or 'unknown'
            domains[domain] = domains.get(domain, 0) + 1
        
        return {
            'total_equations': len(self.equations),
            'validated_equations': sum(1 for s in self.equations.values() if s.validated),
            'domains': domains,
            'avg_relationships': sum(len(s.related_equations) for s in self.equations.values()) / len(self.equations) if self.equations else 0.0
        }

