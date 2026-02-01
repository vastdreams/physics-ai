# ai/context_memory/
"""
Micro-Agent - Sub-agentic structure within context bubbles.

Inspired by DREAM architecture - micro-agents embedded in vectorized nodes.

First Principle Analysis:
- Micro-agent: A = {blueprint, state, pathway_map}
- Blueprint: B = {instructions, constraints, dependencies}
- Pathway map: P = {pathway: confidence} for routing
- Mathematical foundation: State machines, decision trees, attention
- Architecture: Lightweight agent within context bubble
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel

if TYPE_CHECKING:
    from .context_bubble import ContextBubble


@dataclass
class MicroAgent:
    """
    Micro-agent within context bubble.
    
    Processes context and manages pathway maps for intelligent routing.
    """
    agent_id: str
    blueprint: Dict[str, Any]
    state: Dict[str, Any] = field(default_factory=dict)
    pathway_map: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    execution_count: int = 0
    
    def __post_init__(self):
        """Initialize micro-agent."""
        if not self.agent_id:
            self.agent_id = f"agent_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    def process(self, query: Dict[str, Any], bubble: "ContextBubble") -> Optional[Dict[str, Any]]:
        """
        Process query and update pathway map.
        
        Mathematical: Update pathway confidence based on query relevance
        
        Args:
            query: Query dictionary
            bubble: Parent context bubble
            
        Returns:
            Processing result with pathway suggestions
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="MICRO_AGENT_PROCESS",
            input_data={'agent_id': self.agent_id, 'query_keys': list(query.keys())},
            level=LogLevel.INFO
        )
        
        try:
            self.execution_count += 1
            self.updated_at = datetime.now()
            
            # Extract blueprint instructions
            instructions = self.blueprint.get('instructions', {})
            constraints = self.blueprint.get('constraints', [])
            
            # Process query based on blueprint
            result = self._execute_blueprint(query, instructions, constraints)
            
            # Update pathway map based on result
            if result and 'pathways' in result:
                for pathway, confidence in result['pathways'].items():
                    self.pathway_map[pathway] = confidence
            
            # Update bubble traffic signals
            if self.pathway_map:
                bubble.update_traffic_signals(
                    {k: int(v * 100) for k, v in self.pathway_map.items()}
                )
            
            cot.end_step(
                step_id,
                output_data={'result_keys': list(result.keys()) if result else []},
                validation_passed=True
            )
            
            return result
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            logger = SystemLogger()
            logger.log(f"Error in micro-agent process: {str(e)}", level="ERROR")
            return None
    
    def _execute_blueprint(self,
                          query: Dict[str, Any],
                          instructions: Dict[str, Any],
                          constraints: List[str]) -> Optional[Dict[str, Any]]:
        """
        Execute blueprint instructions.
        
        Args:
            query: Query dictionary
            instructions: Blueprint instructions
            constraints: Blueprint constraints
            
        Returns:
            Execution result
        """
        # Simple blueprint execution (can be extended)
        result = {
            'agent_id': self.agent_id,
            'pathways': {},
            'confidence': 0.5
        }
        
        # Check constraints
        for constraint in constraints:
            if not self._check_constraint(query, constraint):
                result['confidence'] *= 0.5  # Reduce confidence if constraint fails
        
        # Execute instructions
        instruction_type = instructions.get('type', 'default')
        if instruction_type == 'route':
            # Route to specific pathways
            target_pathways = instructions.get('pathways', [])
            for pathway in target_pathways:
                result['pathways'][pathway] = result['confidence']
        elif instruction_type == 'analyze':
            # Analyze query and suggest pathways
            suggested = self._analyze_query(query)
            for pathway, conf in suggested.items():
                result['pathways'][pathway] = conf
        
        return result
    
    def _check_constraint(self, query: Dict[str, Any], constraint: str) -> bool:
        """Check if query satisfies constraint."""
        # Simple constraint checking (can be extended)
        if constraint.startswith('has_'):
            key = constraint[4:]
            return key in query
        return True
    
    def _analyze_query(self, query: Dict[str, Any]) -> Dict[str, float]:
        """Analyze query and suggest pathways."""
        suggestions = {}
        
        # Simple keyword-based analysis
        keywords = ['simulation', 'equation', 'theory', 'node', 'rule', 'evolution']
        for keyword in keywords:
            if keyword in str(query).lower():
                suggestions[f'pathway_{keyword}'] = 0.7
        
        return suggestions
    
    def get_next_pathway(self) -> Optional[str]:
        """
        Get next pathway based on pathway map.
        
        Returns:
            Pathway identifier with highest confidence
        """
        if not self.pathway_map:
            return None
        
        return max(self.pathway_map.items(), key=lambda x: x[1])[0]
    
    def update_pathway_confidence(self, pathway: str, confidence: float) -> None:
        """
        Update pathway confidence.
        
        Args:
            pathway: Pathway identifier
            confidence: Confidence value [0, 1]
        """
        self.pathway_map[pathway] = max(0.0, min(1.0, confidence))
        self.updated_at = datetime.now()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return {
            'agent_id': self.agent_id,
            'execution_count': self.execution_count,
            'num_pathways': len(self.pathway_map),
            'avg_confidence': sum(self.pathway_map.values()) / len(self.pathway_map) if self.pathway_map else 0.0,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

