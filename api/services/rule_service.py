# api/services/
"""
Rule Service - Business logic for rule operations.
"""

from typing import Any, Dict, List, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from rules.enhanced_rule_engine import EnhancedRuleEngine, EnhancedRule, RulePriority
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel


class RuleService:
    """
    Service for rule operations.
    
    Encapsulates business logic for rule management.
    """
    
    def __init__(self):
        """Initialize rule service."""
        self.logger = SystemLogger()
        self.rule_engine = EnhancedRuleEngine()
        
        self.logger.log("RuleService initialized", level="INFO")
    
    def add_rule(self, rule_data: Dict[str, Any]) -> bool:
        """
        Add rule.
        
        Args:
            rule_data: Rule data dictionary
            
        Returns:
            True if added successfully
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="SERVICE_ADD_RULE",
            input_data={'rule_name': rule_data.get('name')},
            level=LogLevel.INFO
        )
        
        try:
            # Create rule from data
            rule = EnhancedRule(
                name=rule_data['name'],
                condition=rule_data.get('condition'),
                action=rule_data.get('action'),
                priority=RulePriority[rule_data.get('priority', 'MEDIUM')],
                description=rule_data.get('description', '')
            )
            
            success = self.rule_engine.add_enhanced_rule(rule)
            
            cot.end_step(step_id, output_data={'success': success}, validation_passed=success)
            
            return success
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error in rule service: {str(e)}", level="ERROR")
            raise
    
    def execute_rules(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute rules on context.
        
        Args:
            context: Execution context
            
        Returns:
            Execution results
        """
        results = self.rule_engine.execute_enhanced(
            context=context,
            validate_physics=True,
            use_cot=True
        )
        
        return [
            {
                'rule_name': r.get('rule_name'),
                'success': r.get('success', False),
                'result': r.get('result')
            }
            for r in results
        ]
    
    def get_rule(self, rule_name: str) -> Optional[Dict[str, Any]]:
        """Get rule by name."""
        rule = self.rule_engine.get_enhanced_rule(rule_name)
        if not rule:
            return None
        
        return {
            'name': rule.name,
            'description': rule.description,
            'priority': rule.priority.value,
            'performance': rule.performance
        }
    
    def list_rules(self) -> List[Dict[str, Any]]:
        """List all rules."""
        rules = self.rule_engine.get_all_enhanced_rules()
        return [
            {
                'name': rule.name,
                'description': rule.description,
                'priority': rule.priority.value
            }
            for rule in rules
        ]

