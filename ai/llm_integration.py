# ai/
"""
LLM Integration for Dynamic Discovery.

Inspired by DREAM architecture - LLM for synergy discovery and reflection.

First Principle Analysis:
- LLM queries: Q(query, context) -> response
- Synergy discovery: Discover new relationships from literature
- Reflection: Explain decisions and reasoning
- Mathematical foundation: Natural language processing, knowledge extraction
- Architecture: Modular LLM interface with validation
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from validators.data_validator import DataValidator


@dataclass
class LLMQuery:
    """Represents an LLM query."""
    query: str
    context: Dict[str, Any]
    response: Optional[str] = None
    confidence: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class LLMIntegration:
    """
    LLM integration for dynamic discovery and reflection.
    
    Features:
    - Synergy discovery from literature
    - Decision explanation
    - Relationship extraction
    - Validation against first-principles
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        llm_backend: Optional[Any] = None,
    ):
        """
        Initialize LLM integration.
        
        Args:
            api_key: Optional API key (would use environment variable in production)
            model: LLM model to use
        """
        self.logger = SystemLogger()
        self.validator = DataValidator()
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.query_history: List[LLMQuery] = []
        self.llm_backend = llm_backend  # Optional LocalLLMBackend/Throttled client
        
        self.logger.log(f"LLMIntegration initialized (model={model})", level="INFO")
    
    def discover_synergy(self,
                        theory1: str,
                        theory2: str,
                        context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Discover synergy between two theories using LLM.
        
        Args:
            theory1: First theory name
            theory2: Second theory name
            context: Additional context
            
        Returns:
            Dictionary with synergy information
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="LLM_DISCOVER_SYNERGY",
            input_data={'theory1': theory1, 'theory2': theory2},
            level=LogLevel.DECISION
        )
        
        try:
            query = f"""
            What is the coupling or synergy between {theory1} and {theory2} in physics?
            Consider:
            - Mathematical relationships
            - Energy scales where both apply
            - Known coupling constants
            - Experimental evidence
            
            Provide a quantitative estimate if possible.
            """
            
            # In production, would call actual LLM API
            # For now, return structured response
            response = self._call_llm(query, context)
            
            # Extract synergy information
            synergy_info = self._extract_synergy_info(response, theory1, theory2)
            
            # Validate against first-principles
            is_valid = self._validate_synergy(synergy_info)
            
            query_obj = LLMQuery(
                query=query,
                context=context or {},
                response=response,
                confidence=0.7 if is_valid else 0.3
            )
            self.query_history.append(query_obj)
            
            cot.end_step(
                step_id,
                output_data={'synergy_info': synergy_info, 'is_valid': is_valid},
                validation_passed=is_valid
            )
            
            return synergy_info
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error in synergy discovery: {str(e)}", level="ERROR")
            return {'error': str(e)}
    
    def explain_decision(self,
                        decision: str,
                        context: Dict[str, Any],
                        reasoning: Optional[str] = None) -> str:
        """
        Use LLM to explain a decision.
        
        Args:
            decision: Decision description
            context: Decision context
            reasoning: Optional initial reasoning
            
        Returns:
            Explanation string
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="LLM_EXPLAIN_DECISION",
            input_data={'decision': decision},
            level=LogLevel.INFO
        )
        
        try:
            query = f"""
            Explain why this decision was made: {decision}
            
            Context: {context}
            Initial reasoning: {reasoning or 'None provided'}
            
            Provide a clear, physics-based explanation.
            """
            
            response = self._call_llm(query, context)
            
            query_obj = LLMQuery(
                query=query,
                context=context,
                response=response,
                confidence=0.8
            )
            self.query_history.append(query_obj)
            
            cot.end_step(step_id, output_data={'explanation': response}, validation_passed=True)
            
            return response
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error explaining decision: {str(e)}", level="ERROR")
            return f"Error: {str(e)}"
    
    def extract_relationships(self,
                             text: str,
                             entities: List[str]) -> Dict[str, List[str]]:
        """
        Extract relationships between entities from text.
        
        Args:
            text: Text to analyze
            entities: List of entity names
            
        Returns:
            Dictionary mapping entities to related entities
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="LLM_EXTRACT_RELATIONSHIPS",
            input_data={'entities': entities},
            level=LogLevel.INFO
        )
        
        try:
            query = f"""
            Extract relationships between these physics entities: {', '.join(entities)}
            
            Text: {text}
            
            For each entity, list related entities and the type of relationship.
            """
            
            response = self._call_llm(query, {'entities': entities})
            
            relationships = self._parse_relationships(response, entities)
            
            cot.end_step(step_id, output_data={'relationships': relationships}, validation_passed=True)
            
            return relationships
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error extracting relationships: {str(e)}", level="ERROR")
            return {}
    
    def _call_llm(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Call LLM API (placeholder - would use actual API in production).
        
        Args:
            query: Query string
            context: Optional context
            
        Returns:
            LLM response
        """
        # If a backend is provided, use it
        if self.llm_backend:
            try:
                response = self.llm_backend.generate(
                    prompt=query,
                    system_prompt="You are a physics reasoning assistant.",
                    max_tokens=512,
                    temperature=0.6,
                )
                return response.text
            except Exception as e:
                self.logger.log(f"LLM backend error: {e}", level="ERROR")
                return f"LLM backend error: {e}"

        # Fallback placeholder
        self.logger.log(f"LLM query (stub): {query[:100]}...", level="DEBUG")
        return f"LLM response to: {query[:50]}... (placeholder - no backend)"
    
    def _extract_synergy_info(self, response: str, theory1: str, theory2: str) -> Dict[str, Any]:
        """Extract synergy information from LLM response."""
        # Simplified extraction - would use more sophisticated parsing
        return {
            'theory1': theory1,
            'theory2': theory2,
            'coupling_strength': 0.1,  # Would extract from response
            'energy_scale': 'medium',
            'description': response[:200],
            'confidence': 0.7
        }
    
    def _validate_synergy(self, synergy_info: Dict[str, Any]) -> bool:
        """Validate synergy information against first-principles."""
        # Check coupling strength is reasonable
        coupling = synergy_info.get('coupling_strength', 0.0)
        if coupling < 0 or coupling > 10.0:
            return False
        
        return True
    
    def _parse_relationships(self, response: str, entities: List[str]) -> Dict[str, List[str]]:
        """Parse relationships from LLM response."""
        # Simplified parsing - would use more sophisticated extraction
        relationships = {}
        for entity in entities:
            relationships[entity] = [e for e in entities if e != entity]
        return relationships
    
    def get_query_history(self) -> List[Dict[str, Any]]:
        """Get query history."""
        return [
            {
                'query': q.query,
                'response': q.response,
                'confidence': q.confidence,
                'timestamp': q.timestamp.isoformat()
            }
            for q in self.query_history
        ]

