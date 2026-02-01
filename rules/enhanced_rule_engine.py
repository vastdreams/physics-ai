# rules/
"""
Enhanced rule engine with physics-specific constraints and evolution.

First Principle Analysis:
- Rules: R = {(condition, action, constraints, priority)}
- Execution: Execute rules where condition(context) = True
- Physics constraints: Validate against first-principles Φ
- Evolution: Update rules based on performance P(R)
- Mathematical foundation: Production systems, constraint satisfaction, optimization
- Architecture: Enhanced rule engine with physics validation and evolution
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loggers.system_logger import SystemLogger
from loggers.evolution_logger import EvolutionLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from validators.rule_validator import RuleValidator
from validators.data_validator import DataValidator
from physics.validation.physics_validator import PhysicsValidator
from rules.rule_engine import RuleEngine


class RulePriority(Enum):
    """Rule priority levels."""
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class EnhancedRule:
    """Enhanced rule with physics constraints and metadata."""
    name: str
    condition: Callable[[Dict[str, Any]], bool]
    action: Callable[[Dict[str, Any]], Any]
    physics_constraints: List[str] = field(default_factory=list)  # List of constraint names
    priority: RulePriority = RulePriority.MEDIUM
    version: str = "1.0.0"
    description: str = ""
    tags: Set[str] = field(default_factory=set)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_executed: Optional[datetime] = None
    execution_count: int = 0
    success_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'priority': self.priority.value,
            'version': self.version,
            'description': self.description,
            'tags': list(self.tags),
            'physics_constraints': self.physics_constraints,
            'execution_count': self.execution_count,
            'success_count': self.success_count,
            'success_rate': self.success_count / self.execution_count if self.execution_count > 0 else 0.0
        }


class EnhancedRuleEngine(RuleEngine):
    """
    Enhanced rule engine with physics-specific constraints and evolution.
    
    Features:
    - First-principles rule validation
    - Rule evolution based on performance
    - Conflict resolution with physics constraints
    - Rule dependency tracking
    - CoT logging integration
    """
    
    def __init__(self):
        """Initialize enhanced rule engine."""
        super().__init__()
        self.evolution_logger = EvolutionLogger()
        self.physics_validator = PhysicsValidator()
        self.enhanced_rules: Dict[str, EnhancedRule] = {}
        self.rule_dependencies: Dict[str, Set[str]] = {}
        self.rule_performance: Dict[str, List[float]] = {}
        
        self.logger.log("EnhancedRuleEngine initialized", level="INFO")
    
    def add_enhanced_rule(self, rule: EnhancedRule) -> bool:
        """
        Add an enhanced rule to the engine.
        
        Args:
            rule: EnhancedRule to add
            
        Returns:
            True if added successfully
        """
        # Validate rule
        rule_dict = {
            'name': rule.name,
            'condition': rule.condition,
            'action': rule.action
        }
        
        if not self.validator.validate_rule(rule_dict):
            self.logger.log(f"Invalid rule: {rule.name}", level="WARNING")
            return False
        
        # Validate physics constraints
        if not self._validate_physics_constraints(rule):
            self.logger.log(f"Physics constraint validation failed for: {rule.name}", level="WARNING")
            return False
        
        # Add rule
        self.enhanced_rules[rule.name] = rule
        
        # Initialize performance tracking
        self.rule_performance[rule.name] = []
        
        # Convert to standard rule format for base engine
        standard_rule = {
            'name': rule.name,
            'condition': rule.condition,
            'action': rule.action,
            'priority': rule.priority.value
        }
        self.add_rule(standard_rule)
        
        self.logger.log(f"Enhanced rule added: {rule.name} (v{rule.version})", level="INFO")
        return True
    
    def _validate_physics_constraints(self, rule: EnhancedRule) -> bool:
        """
        Validate rule against physics constraints.
        
        Args:
            rule: Rule to validate
            
        Returns:
            True if valid
        """
        if not rule.physics_constraints:
            return True  # No constraints to check
        
        # Check each constraint
        for constraint_name in rule.physics_constraints:
            # This would check against physics validator
            # For now, just check that constraint name is valid
            valid_constraints = [
                'conservation_energy',
                'conservation_momentum',
                'conservation_charge',
                'causality',
                'unitarity',
                'energy_positivity'
            ]
            
            if constraint_name not in valid_constraints:
                self.logger.log(f"Unknown physics constraint: {constraint_name}", level="WARNING")
                return False
        
        return True
    
    def execute_enhanced(self,
                         context: Dict[str, Any],
                         validate_physics: bool = True,
                         use_cot: bool = True) -> List[Any]:
        """
        Execute enhanced rules with physics validation and CoT logging.
        
        Args:
            context: Execution context
            validate_physics: Whether to validate against physics constraints
            use_cot: Whether to use chain-of-thought logging
            
        Returns:
            List of execution results
        """
        cot = ChainOfThoughtLogger() if use_cot else None
        
        if cot:
            step_id = cot.start_step(
                action="EXECUTE_ENHANCED_RULES",
                input_data={'context_keys': list(context.keys())},
                level=LogLevel.INFO
            )
        
        try:
            # Find matching rules
            matching_rules = self._find_matching_enhanced_rules(context)
            
            if not matching_rules:
                if cot:
                    cot.end_step(step_id, output_data={'matched_rules': 0})
                return []
            
            # Resolve conflicts with priority and physics constraints
            selected_rules = self._resolve_conflicts_enhanced(
                matching_rules,
                context,
                validate_physics
            )
            
            # Execute rules
            results = []
            for rule in selected_rules:
                rule_result = self._execute_enhanced_rule(rule, context, cot)
                results.append(rule_result)
                
                # Update performance
                self._update_rule_performance(rule.name, rule_result.get('success', False))
            
            if cot:
                cot.end_step(
                    step_id,
                    output_data={
                        'matched_rules': len(matching_rules),
                        'executed_rules': len(selected_rules),
                        'results': results
                    }
                )
            
            self.logger.log(f"Executed {len(selected_rules)} enhanced rules", level="INFO")
            return results
        
        except Exception as e:
            if cot:
                cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error executing enhanced rules: {str(e)}", level="ERROR")
            raise
    
    def _find_matching_enhanced_rules(self, context: Dict[str, Any]) -> List[EnhancedRule]:
        """Find enhanced rules that match the context."""
        matching = []
        
        for rule in self.enhanced_rules.values():
            try:
                if rule.condition(context):
                    matching.append(rule)
            except Exception as e:
                self.logger.log(f"Error evaluating condition for {rule.name}: {str(e)}", level="WARNING")
                continue
        
        return matching
    
    def _resolve_conflicts_enhanced(self,
                                    rules: List[EnhancedRule],
                                    context: Dict[str, Any],
                                    validate_physics: bool) -> List[EnhancedRule]:
        """
        Resolve conflicts between matching rules.
        
        Strategy:
        1. Sort by priority
        2. Filter by physics constraints
        3. Select highest priority valid rules
        """
        # Sort by priority
        sorted_rules = sorted(rules, key=lambda r: r.priority.value)
        
        # Filter by physics constraints if requested
        if validate_physics:
            valid_rules = []
            for rule in sorted_rules:
                if self._check_physics_constraints_for_context(rule, context):
                    valid_rules.append(rule)
            sorted_rules = valid_rules
        
        # Select rules (can execute multiple if no conflicts)
        selected = []
        for rule in sorted_rules:
            # Check for conflicts with already selected rules
            if not self._has_conflict(rule, selected):
                selected.append(rule)
        
        return selected
    
    def _check_physics_constraints_for_context(self,
                                               rule: EnhancedRule,
                                               context: Dict[str, Any]) -> bool:
        """
        Check if rule's physics constraints are satisfied for context.
        
        Args:
            rule: Rule to check
            context: Execution context
            
        Returns:
            True if constraints satisfied
        """
        if not rule.physics_constraints:
            return True
        
        # Create mock system state from context
        system_state = context.get('system_state', {})
        
        # Validate against physics constraints
        for constraint_name in rule.physics_constraints:
            if constraint_name == 'conservation_energy':
                # Check energy conservation
                initial_energy = system_state.get('initial_energy')
                final_energy = system_state.get('final_energy')
                if initial_energy is not None and final_energy is not None:
                    # Allow small numerical errors
                    if abs(final_energy - initial_energy) > 1e-6:
                        return False
            
            elif constraint_name == 'causality':
                # Check causality
                velocity = system_state.get('velocity')
                if velocity is not None:
                    import numpy as np
                    speed = np.linalg.norm(velocity) if isinstance(velocity, (list, np.ndarray)) else abs(velocity)
                    c = 299792458.0  # Speed of light
                    if speed > c:
                        return False
        
        return True
    
    def _has_conflict(self, rule: EnhancedRule, selected_rules: List[EnhancedRule]) -> bool:
        """Check if rule conflicts with selected rules."""
        # Simple conflict detection: rules with same priority and overlapping actions
        for selected in selected_rules:
            if (rule.priority == selected.priority and
                rule.name != selected.name and
                rule.tags.intersection(selected.tags)):
                return True
        return False
    
    def _execute_enhanced_rule(self,
                               rule: EnhancedRule,
                               context: Dict[str, Any],
                               cot: Optional[ChainOfThoughtLogger] = None) -> Dict[str, Any]:
        """
        Execute a single enhanced rule.
        
        Args:
            rule: Rule to execute
            context: Execution context
            cot: Optional CoT logger
            
        Returns:
            Execution result
        """
        if cot:
            step_id = cot.start_step(
                action=f"EXECUTE_RULE: {rule.name}",
                input_data={'rule_name': rule.name, 'context_keys': list(context.keys())},
                level=LogLevel.DECISION
            )
        
        try:
            # Execute action
            result = rule.action(context)
            
            # Update rule statistics
            rule.last_executed = datetime.now()
            rule.execution_count += 1
            rule.success_count += 1
            
            execution_result = {
                'rule_name': rule.name,
                'success': True,
                'result': result
            }
            
            if cot:
                cot.end_step(step_id, output_data=execution_result, validation_passed=True)
            
            return execution_result
        
        except Exception as e:
            # Update statistics
            rule.execution_count += 1
            
            execution_result = {
                'rule_name': rule.name,
                'success': False,
                'error': str(e)
            }
            
            if cot:
                cot.end_step(step_id, output_data=execution_result, validation_passed=False)
            
            self.logger.log(f"Error executing rule {rule.name}: {str(e)}", level="ERROR")
            return execution_result
    
    def _update_rule_performance(self, rule_name: str, success: bool) -> None:
        """Update rule performance metrics."""
        if rule_name not in self.rule_performance:
            self.rule_performance[rule_name] = []
        
        score = 1.0 if success else 0.0
        self.rule_performance[rule_name].append(score)
        
        # Keep only recent performance (last 100)
        if len(self.rule_performance[rule_name]) > 100:
            self.rule_performance[rule_name] = self.rule_performance[rule_name][-100:]
    
    def evolve_rule(self, rule_name: str, improvement_spec: Dict[str, Any]) -> bool:
        """
        Evolve a rule based on performance and improvement specification.
        
        Args:
            rule_name: Name of rule to evolve
            improvement_spec: Specification for improvement
            
        Returns:
            True if evolved successfully
        """
        if rule_name not in self.enhanced_rules:
            self.logger.log(f"Rule not found: {rule_name}", level="WARNING")
            return False
        
        rule = self.enhanced_rules[rule_name]
        
        # Get performance
        performance = self.rule_performance.get(rule_name, [])
        avg_performance = sum(performance) / len(performance) if performance else 0.0
        
        # Evolve rule (simplified - would use more sophisticated evolution)
        new_version = self._increment_version(rule.version)
        rule.version = new_version
        
        # Update based on improvement spec
        if 'priority' in improvement_spec:
            rule.priority = RulePriority(improvement_spec['priority'])
        
        if 'description' in improvement_spec:
            rule.description = improvement_spec['description']
        
        self.evolution_logger.log_evolution("rule_evolution", {
            'rule_name': rule_name,
            'old_version': rule.version,
            'new_version': new_version,
            'avg_performance': avg_performance
        })
        
        self.logger.log(f"Rule evolved: {rule_name} -> v{new_version}", level="INFO")
        return True
    
    def _increment_version(self, version: str) -> str:
        """Increment version string."""
        parts = version.split('.')
        if len(parts) == 3:
            parts[2] = str(int(parts[2]) + 1)
            return '.'.join(parts)
        return "1.0.1"
    
    def get_rule_statistics(self) -> Dict[str, Any]:
        """Get statistics for all rules."""
        stats = {}
        
        for rule_name, rule in self.enhanced_rules.items():
            performance = self.rule_performance.get(rule_name, [])
            avg_performance = sum(performance) / len(performance) if performance else 0.0
            
            stats[rule_name] = {
                'version': rule.version,
                'execution_count': rule.execution_count,
                'success_count': rule.success_count,
                'success_rate': rule.success_count / rule.execution_count if rule.execution_count > 0 else 0.0,
                'avg_performance': avg_performance,
                'priority': rule.priority.value
            }
        
        return stats
    
    def list_rules(self) -> List[Dict[str, Any]]:
        """List all enhanced rules."""
        return [rule.to_dict() for rule in self.enhanced_rules.values()]

