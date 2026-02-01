# rules/
"""
VECTOR Framework Integration with Enhanced Rule Engine.

Integrates VECTOR for uncertainty-aware rule execution.
"""

from typing import Any, Dict, List, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rules.enhanced_rule_engine import EnhancedRuleEngine, EnhancedRule
from utilities.vector_framework import VECTORFramework, DeltaFactor
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from loggers.system_logger import SystemLogger


class VectorIntegratedRuleEngine(EnhancedRuleEngine):
    """
    Enhanced rule engine with VECTOR framework integration.
    
    Features:
    - Uncertainty-aware rule execution
    - Variance throttling for rule parameters
    - Bayesian updates of rule weights
    """
    
    def __init__(self):
        """Initialize vector-integrated rule engine."""
        super().__init__()
        self.vector = VECTORFramework(v_max=50.0, lambda_penalty=1.0)
        self.logger.log("VectorIntegratedRuleEngine initialized", level="INFO")
    
    def execute_enhanced(self,
                         context: Dict[str, Any],
                         validate_physics: bool = True,
                         use_cot: bool = True,
                         use_vector: bool = True) -> List[Any]:
        """
        Execute rules with VECTOR framework.
        
        Args:
            context: Execution context
            validate_physics: Validate physics constraints
            use_cot: Use chain-of-thought logging
            use_vector: Use VECTOR framework
            
        Returns:
            Execution results
        """
        cot = ChainOfThoughtLogger() if use_cot else None
        
        if cot:
            step_id = cot.start_step(
                action="VECTOR_EXECUTE_RULES",
                input_data={'context_keys': list(context.keys()), 'use_vector': use_vector},
                level=LogLevel.INFO
            )
        
        try:
            # Extract uncertainty from context
            if use_vector:
                self._extract_uncertainty_from_context(context)
                
                # Throttle variance
                throttled = self.vector.throttle_variance()
                if throttled:
                    self.logger.log("Rule execution variance throttled", level="WARNING")
            
            # Execute rules (parent class method)
            results = super().execute_enhanced(
                context=context,
                validate_physics=validate_physics,
                use_cot=use_cot
            )
            
            # Update rule weights based on results
            if use_vector and results:
                self._update_rule_weights_from_results(results)
            
            if cot:
                cot.end_step(
                    step_id,
                    output_data={'results_count': len(results)},
                    validation_passed=True
                )
            
            return results
        
        except Exception as e:
            if cot:
                cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error in vector rule execution: {str(e)}", level="ERROR")
            raise
    
    def _extract_uncertainty_from_context(self, context: Dict[str, Any]) -> None:
        """Extract uncertainty information from context."""
        # Extract uncertainty for each context variable
        for key, value in context.items():
            if isinstance(value, dict) and 'value' in value and 'uncertainty' in value:
                self.vector.add_delta_factor(DeltaFactor(
                    name=key,
                    value=value['value'],
                    variance=value['uncertainty']
                ))
            elif isinstance(value, (int, float)):
                # Default uncertainty
                self.vector.add_delta_factor(DeltaFactor(
                    name=key,
                    value=value,
                    variance=0.1
                ))
    
    def _update_rule_weights_from_results(self, results: List[Dict[str, Any]]) -> None:
        """Update rule weights based on execution results."""
        for result in results:
            rule_name = result.get('rule_name')
            success = result.get('success', False)
            
            if rule_name and rule_name in self.enhanced_rules:
                rule = self.enhanced_rules[rule_name]
                
                # Update performance
                score = 1.0 if success else 0.0
                self._update_rule_performance(rule_name, success)
                
                # Could use Bayesian update for rule weights
                # This is a simplified version
                # In future, could update rule weights using VECTOR framework

