# api/services/
"""
Evolution Service - Business logic for code evolution.
"""

from typing import Any, Dict, List, Optional, Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from evolution.self_evolution import SelfEvolutionEngine
from ai.nodal_vectorization.graph_builder import GraphBuilder
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel


class EvolutionService:
    """
    Service for code evolution operations.
    
    Encapsulates business logic for evolution.
    """
    
    def __init__(self):
        """Initialize evolution service."""
        self.logger = SystemLogger()
        graph_builder = GraphBuilder()
        self.evolution_engine = SelfEvolutionEngine(graph_builder)
        
        self.logger.log("EvolutionService initialized", level="INFO")
    
    def analyze_codebase(self, directory_path: str) -> Dict[str, Any]:
        """
        Analyze codebase for evolution opportunities.
        
        Args:
            directory_path: Directory to analyze
            
        Returns:
            Analysis results
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="SERVICE_ANALYZE_CODEBASE",
            input_data={'directory': directory_path},
            level=LogLevel.INFO
        )
        
        try:
            analysis = self.evolution_engine.analyze_codebase(directory_path)
            
            cot.end_step(
                step_id,
                output_data={'analysis_keys': list(analysis.keys())},
                validation_passed=True
            )
            
            return analysis
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error in evolution service: {str(e)}", level="ERROR")
            raise
    
    def evolve_function(self,
                      file_path: str,
                      function_name: str,
                      improvement_spec: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Evolve function.
        
        Args:
            file_path: File path
            function_name: Function name
            improvement_spec: Improvement specification
            
        Returns:
            Tuple of (success, new_code)
        """
        return self.evolution_engine.evolve_function(
            file_path=file_path,
            function_name=function_name,
            improvement_spec=improvement_spec
        )
    
    def get_evolution_history(self) -> List[Dict[str, Any]]:
        """Get evolution history."""
        return self.evolution_engine.get_evolution_history()

