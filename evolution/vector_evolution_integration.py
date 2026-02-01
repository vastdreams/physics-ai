# evolution/
"""
VECTOR Framework Integration with Self-Evolution Engine.

Integrates VECTOR for safe code evolution with variance control.
"""

from typing import Any, Dict, Optional, Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from evolution.self_evolution import SelfEvolutionEngine
from utilities.vector_framework import VECTORFramework, DeltaFactor
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from loggers.system_logger import SystemLogger


class VectorIntegratedEvolutionEngine(SelfEvolutionEngine):
    """
    Self-evolution engine with VECTOR framework integration.
    
    Features:
    - Variance throttling for code generation parameters
    - Overlay validation of evolved code
    - Bayesian updates for evolution parameters
    """
    
    def __init__(self, graph_builder=None):
        """Initialize vector-integrated evolution engine."""
        super().__init__(graph_builder)
        self.vector = VECTORFramework(v_max=50.0, lambda_penalty=1.0)
        self.logger.log("VectorIntegratedEvolutionEngine initialized", level="INFO")
    
    def evolve_function(self,
                       file_path: str,
                       function_name: str,
                       improvement_spec: Dict[str, Any],
                       use_vector: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Evolve function with VECTOR framework.
        
        Args:
            file_path: File path
            function_name: Function name
            improvement_spec: Improvement specification
            use_vector: Use VECTOR framework
            
        Returns:
            Tuple of (success, new_code)
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="VECTOR_EVOLVE_FUNCTION",
            input_data={
                'file_path': file_path,
                'function_name': function_name,
                'use_vector': use_vector
            },
            level=LogLevel.DECISION
        )
        
        try:
            # Extract evolution parameters as delta factors
            if use_vector:
                self._extract_evolution_parameters(improvement_spec)
                
                # Throttle variance
                throttled = self.vector.throttle_variance()
                if throttled:
                    self.logger.log("Evolution variance throttled", level="WARNING")
            
            # Evolve function (parent class method)
            success, new_code = super().evolve_function(
                file_path=file_path,
                function_name=function_name,
                improvement_spec=improvement_spec
            )
            
            # Overlay validation: compare evolved vs original
            if use_vector and success and new_code:
                validation_passed = self._validate_evolved_code(file_path, new_code)
                
                if not validation_passed:
                    self.logger.log("Evolved code failed overlay validation", level="WARNING")
                    cot.end_step(step_id, output_data={'validation_passed': False}, validation_passed=False)
                    return False, None
            
            cot.end_step(
                step_id,
                output_data={'success': success, 'validation_passed': True},
                validation_passed=success
            )
            
            return success, new_code
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error in vector evolution: {str(e)}", level="ERROR")
            return False, None
    
    def _extract_evolution_parameters(self, improvement_spec: Dict[str, Any]) -> None:
        """Extract evolution parameters as delta factors."""
        # Extract complexity change
        if 'complexity_target' in improvement_spec:
            self.vector.add_delta_factor(DeltaFactor(
                name="complexity_change",
                value=improvement_spec['complexity_target'],
                variance=0.2
            ))
        
        # Extract performance target
        if 'performance_target' in improvement_spec:
            self.vector.add_delta_factor(DeltaFactor(
                name="performance_target",
                value=improvement_spec['performance_target'],
                variance=0.1
            ))
    
    def _validate_evolved_code(self, file_path: str, new_code: str) -> bool:
        """
        Validate evolved code using overlay validation.
        
        Args:
            file_path: File path
            new_code: New code
            
        Returns:
            True if validation passed
        """
        try:
            # Read original code
            with open(file_path, 'r', encoding='utf-8') as f:
                original_code = f.read()
            
            # Simple metrics comparison
            original_lines = len(original_code.splitlines())
            new_lines = len(new_code.splitlines())
            
            simple_output = {'lines': original_lines, 'complexity': 1.0}
            complex_output = {'lines': new_lines, 'complexity': 1.1}
            
            is_valid, deviation = self.vector.overlay_validation(
                simple_output,
                complex_output,
                epsilon_limit=0.2
            )
            
            return is_valid
        
        except Exception as e:
            self.logger.log(f"Error validating evolved code: {str(e)}", level="ERROR")
            return False

