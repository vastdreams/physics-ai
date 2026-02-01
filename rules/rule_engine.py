# rules/
"""
PATH: rules/rule_engine.py
PURPOSE: Execute rules in a rule-based system with pattern matching and conflict resolution.

FLOW:
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│   Context   │───▶│   Pattern    │───▶│  Conflict   │───▶│   Execute    │
│             │    │   Matching   │    │  Resolution │    │   Actions    │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘

First Principle Analysis:
- Rules represent knowledge as condition-action pairs
- Execution requires pattern matching and conflict resolution
- Mathematical foundation: production systems, forward/backward chaining
- Architecture: modular rule engine with pluggable strategies

Planning:
1. Implement rule matching algorithm with variable binding
2. Create execution pipeline with proper condition evaluation
3. Add conflict resolution strategies (priority, specificity, recency)
4. Design for rule evolution

DEPENDENCIES:
- validators: Rule validation
- loggers: System logging
"""

from typing import Any, Dict, List, Optional, Tuple, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import operator
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from validators.rule_validator import RuleValidator
from loggers.system_logger import SystemLogger


class ConflictResolutionStrategy(Enum):
    """Strategy for resolving conflicts between matching rules."""
    PRIORITY = "priority"           # Higher priority wins
    SPECIFICITY = "specificity"     # More specific conditions win
    RECENCY = "recency"            # Most recently added/fired wins
    FIRST_MATCH = "first_match"    # First matching rule wins
    ALL = "all"                     # Execute all matching rules


@dataclass
class Rule:
    """Represents a rule in the rule-based system."""
    name: str
    condition: Dict[str, Any]  # Pattern to match
    action: Dict[str, Any]     # Action to execute
    priority: int = 0
    specificity: int = 0       # Calculated based on condition complexity
    created_at: datetime = field(default_factory=datetime.now)
    last_fired: Optional[datetime] = None
    fire_count: int = 0
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        # Calculate specificity based on condition complexity
        self.specificity = self._calculate_specificity()
    
    def _calculate_specificity(self) -> int:
        """Calculate rule specificity based on condition complexity."""
        specificity = 0
        
        def count_conditions(obj: Any, depth: int = 0) -> int:
            if isinstance(obj, dict):
                count = len(obj)
                for v in obj.values():
                    count += count_conditions(v, depth + 1)
                return count
            elif isinstance(obj, list):
                return sum(count_conditions(item, depth + 1) for item in obj)
            else:
                return 1
        
        specificity = count_conditions(self.condition)
        return specificity
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'condition': self.condition,
            'action': self.action,
            'priority': self.priority,
            'specificity': self.specificity,
            'created_at': self.created_at.isoformat(),
            'last_fired': self.last_fired.isoformat() if self.last_fired else None,
            'fire_count': self.fire_count,
            'enabled': self.enabled,
            'metadata': self.metadata
        }


@dataclass
class RuleMatch:
    """Represents a successful rule match with variable bindings."""
    rule: Rule
    bindings: Dict[str, Any]  # Variable bindings from pattern matching
    match_score: float = 1.0  # How well the rule matched (1.0 = perfect)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'rule_name': self.rule.name,
            'bindings': self.bindings,
            'match_score': self.match_score
        }


@dataclass
class ExecutionResult:
    """Result of executing a rule."""
    rule_name: str
    success: bool
    output: Any
    bindings: Dict[str, Any]
    error: Optional[str] = None
    execution_time_ms: float = 0.0


class PatternMatcher:
    """
    Pattern matching engine for rule conditions.
    
    Supports:
    - Exact value matching
    - Variable binding (using $var syntax)
    - Comparison operators (>, <, >=, <=, !=)
    - Logical operators (and, or, not)
    - Regular expressions
    - Nested structure matching
    """
    
    # Comparison operator mapping
    OPERATORS = {
        '$gt': operator.gt,
        '$gte': operator.ge,
        '$lt': operator.lt,
        '$lte': operator.le,
        '$ne': operator.ne,
        '$eq': operator.eq,
        '$in': lambda x, y: x in y,
        '$nin': lambda x, y: x not in y,
        '$regex': lambda x, pattern: bool(re.match(pattern, str(x))) if x else False,
        '$exists': lambda x, should_exist: (x is not None) == should_exist,
        '$type': lambda x, t: type(x).__name__ == t
    }
    
    def __init__(self):
        self.logger = SystemLogger()
    
    def match(self, pattern: Dict[str, Any], context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Match a pattern against a context.
        
        Args:
            pattern: Pattern to match (condition)
            context: Context to match against
            
        Returns:
            Tuple of (matches, bindings)
        """
        bindings = {}
        matches = self._match_recursive(pattern, context, bindings)
        return matches, bindings
    
    def _match_recursive(self, pattern: Any, value: Any, bindings: Dict[str, Any]) -> bool:
        """
        Recursively match pattern against value.
        
        Args:
            pattern: Pattern to match
            value: Value to match against
            bindings: Dictionary to store variable bindings
            
        Returns:
            True if pattern matches value
        """
        # Handle None pattern
        if pattern is None:
            return value is None
        
        # Handle variable binding ($var syntax)
        if isinstance(pattern, str) and pattern.startswith('$') and not pattern.startswith('$gt'):
            # This is a variable binding, not an operator
            if pattern not in self.OPERATORS:
                var_name = pattern[1:]  # Remove $ prefix
                if var_name in bindings:
                    # Variable already bound, check consistency
                    return bindings[var_name] == value
                else:
                    # Bind the variable
                    bindings[var_name] = value
                    return True
        
        # Handle operator patterns
        if isinstance(pattern, dict):
            # Check for operator keys
            for key, op_value in pattern.items():
                if key in self.OPERATORS:
                    op_func = self.OPERATORS[key]
                    if not op_func(value, op_value):
                        return False
                elif key == '$and':
                    # All conditions must match
                    if not isinstance(op_value, list):
                        return False
                    for sub_pattern in op_value:
                        if not self._match_recursive(sub_pattern, value, bindings):
                            return False
                elif key == '$or':
                    # At least one condition must match
                    if not isinstance(op_value, list):
                        return False
                    for sub_pattern in op_value:
                        if self._match_recursive(sub_pattern, value, bindings):
                            break
                    else:
                        return False
                elif key == '$not':
                    # Condition must NOT match
                    if self._match_recursive(op_value, value, bindings):
                        return False
                else:
                    # Regular key - match against context
                    if not isinstance(value, dict):
                        return False
                    if key not in value:
                        return False
                    if not self._match_recursive(op_value, value[key], bindings):
                        return False
            return True
        
        # Handle list patterns
        if isinstance(pattern, list):
            if not isinstance(value, list):
                return False
            if len(pattern) != len(value):
                return False
            for p, v in zip(pattern, value):
                if not self._match_recursive(p, v, bindings):
                    return False
            return True
        
        # Handle exact value matching
        return pattern == value
    
    def calculate_match_score(self, pattern: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Calculate how well a pattern matches a context.
        
        Returns a score between 0 and 1.
        
        Args:
            pattern: Pattern that matched
            context: Context that was matched
            
        Returns:
            Match score
        """
        if not pattern:
            return 0.0
        
        matched_keys = 0
        total_keys = 0
        
        def count_keys(obj: Any) -> Tuple[int, int]:
            if isinstance(obj, dict):
                total = len(obj)
                matched = 0
                for k, v in obj.items():
                    if not k.startswith('$'):  # Skip operators
                        sub_matched, sub_total = count_keys(v)
                        matched += sub_matched
                        total += sub_total
                        if isinstance(context, dict) and k in context:
                            matched += 1
                return matched, total
            return 0, 0
        
        matched_keys, total_keys = count_keys(pattern)
        
        if total_keys == 0:
            return 1.0
        
        return matched_keys / total_keys


class ActionExecutor:
    """
    Executes rule actions with variable substitution.
    
    Supports:
    - Set values
    - Compute expressions
    - Call functions
    - Modify context
    """
    
    def __init__(self):
        self.logger = SystemLogger()
        self.custom_actions: Dict[str, Callable] = {}
    
    def register_action(self, name: str, func: Callable) -> None:
        """Register a custom action function."""
        self.custom_actions[name] = func
    
    def execute(self, action: Dict[str, Any], context: Dict[str, Any], 
                bindings: Dict[str, Any]) -> Tuple[Any, Dict[str, Any]]:
        """
        Execute an action.
        
        Args:
            action: Action specification
            context: Current context
            bindings: Variable bindings from pattern matching
            
        Returns:
            Tuple of (result, modified_context)
        """
        result = {}
        modified_context = dict(context)
        
        for key, value in action.items():
            if key == '$set':
                # Set values in context
                for set_key, set_value in value.items():
                    resolved_value = self._resolve_value(set_value, context, bindings)
                    modified_context[set_key] = resolved_value
                    result[set_key] = resolved_value
            
            elif key == '$compute':
                # Compute expression
                expression = value.get('expression', '')
                target = value.get('target', 'result')
                computed = self._evaluate_expression(expression, context, bindings)
                modified_context[target] = computed
                result[target] = computed
            
            elif key == '$call':
                # Call a registered function
                func_name = value.get('function')
                args = value.get('args', [])
                kwargs = value.get('kwargs', {})
                
                resolved_args = [self._resolve_value(a, context, bindings) for a in args]
                resolved_kwargs = {k: self._resolve_value(v, context, bindings) for k, v in kwargs.items()}
                
                if func_name in self.custom_actions:
                    call_result = self.custom_actions[func_name](*resolved_args, **resolved_kwargs)
                    result['call_result'] = call_result
                else:
                    result['call_error'] = f"Unknown function: {func_name}"
            
            elif key == '$remove':
                # Remove keys from context
                keys_to_remove = value if isinstance(value, list) else [value]
                for k in keys_to_remove:
                    modified_context.pop(k, None)
                result['removed'] = keys_to_remove
            
            elif key == '$return':
                # Return a specific value
                result['return'] = self._resolve_value(value, context, bindings)
            
            else:
                # Direct assignment
                result[key] = self._resolve_value(value, context, bindings)
        
        return result, modified_context
    
    def _resolve_value(self, value: Any, context: Dict[str, Any], 
                       bindings: Dict[str, Any]) -> Any:
        """
        Resolve a value, substituting variables.
        
        Args:
            value: Value to resolve
            context: Current context
            bindings: Variable bindings
            
        Returns:
            Resolved value
        """
        if isinstance(value, str):
            # Check for variable reference
            if value.startswith('$'):
                var_name = value[1:]
                if var_name in bindings:
                    return bindings[var_name]
                elif var_name in context:
                    return context[var_name]
            
            # Check for expression syntax: ${expression}
            if '${' in value:
                def replace_expr(match):
                    expr = match.group(1)
                    try:
                        return str(self._evaluate_expression(expr, context, bindings))
                    except:
                        return match.group(0)
                
                return re.sub(r'\$\{([^}]+)\}', replace_expr, value)
            
            return value
        
        elif isinstance(value, dict):
            return {k: self._resolve_value(v, context, bindings) for k, v in value.items()}
        
        elif isinstance(value, list):
            return [self._resolve_value(item, context, bindings) for item in value]
        
        return value
    
    def _evaluate_expression(self, expression: str, context: Dict[str, Any], 
                            bindings: Dict[str, Any]) -> Any:
        """
        Evaluate a mathematical/logical expression.
        
        Args:
            expression: Expression string
            context: Current context
            bindings: Variable bindings
            
        Returns:
            Evaluated result
        """
        # Create safe evaluation context
        safe_context = {
            'True': True,
            'False': False,
            'None': None,
            'abs': abs,
            'min': min,
            'max': max,
            'sum': sum,
            'len': len,
            'round': round,
            'int': int,
            'float': float,
            'str': str,
            **bindings,
            **context
        }
        
        try:
            return eval(expression, {"__builtins__": {}}, safe_context)
        except Exception as e:
            self.logger.log(f"Error evaluating expression '{expression}': {e}", level="WARNING")
            return None


class RuleEngine:
    """
    Executes rules in the rule-based system.
    
    Features:
    - Pattern matching with variable binding
    - Multiple conflict resolution strategies
    - Rule lifecycle management
    - Execution statistics
    """
    
    def __init__(self, strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.PRIORITY):
        """
        Initialize rule engine.
        
        Args:
            strategy: Conflict resolution strategy to use
        """
        self.validator = RuleValidator()
        self.logger = SystemLogger()
        self.pattern_matcher = PatternMatcher()
        self.action_executor = ActionExecutor()
        
        self.rules: List[Rule] = []
        self.strategy = strategy
        self.execution_history: List[ExecutionResult] = []
        
        self.logger.log("RuleEngine initialized", level="INFO")
    
    def add_rule(self, rule: Dict[str, Any]) -> bool:
        """
        Add a rule to the engine.
        
        Args:
            rule: Rule dictionary with 'name', 'condition', 'action'
            
        Returns:
            True if added successfully, False otherwise
        """
        if not self.validator.validate_rule(rule):
            self.logger.log("Invalid rule provided", level="WARNING")
            return False
        
        # Create Rule object
        new_rule = Rule(
            name=rule.get('name', f'rule_{len(self.rules)}'),
            condition=rule.get('condition', {}),
            action=rule.get('action', {}),
            priority=rule.get('priority', 0),
            enabled=rule.get('enabled', True),
            metadata=rule.get('metadata', {})
        )
        
        self.rules.append(new_rule)
        self.logger.log(f"Rule added: {new_rule.name}", level="INFO")
        return True
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove a rule by name."""
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                self.rules.pop(i)
                self.logger.log(f"Rule removed: {rule_name}", level="INFO")
                return True
        return False
    
    def enable_rule(self, rule_name: str) -> bool:
        """Enable a rule by name."""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = True
                return True
        return False
    
    def disable_rule(self, rule_name: str) -> bool:
        """Disable a rule by name."""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = False
                return True
        return False
    
    def execute(self, context: Dict[str, Any]) -> List[ExecutionResult]:
        """
        Execute rules on given context.
        
        Mathematical approach:
        - Pattern matching: find rules where condition(context) = True
        - Conflict resolution: select best rule(s) to execute
        - Action execution: execute selected rule actions
        
        Args:
            context: Execution context
            
        Returns:
            List of execution results
        """
        if not isinstance(context, dict):
            self.logger.log("Invalid context provided", level="ERROR")
            raise ValueError("Context must be a dictionary")
        
        self.logger.log(f"Executing rules on context with {len(self.rules)} rules", level="DEBUG")
        
        # Find matching rules
        matching_rules = self._find_matching_rules(context)
        
        if not matching_rules:
            self.logger.log("No matching rules found", level="DEBUG")
            return []
        
        # Resolve conflicts
        selected_rules = self._resolve_conflicts(matching_rules, context)
        
        # Execute rules
        results = []
        current_context = dict(context)
        
        for match in selected_rules:
            import time
            start_time = time.time()
            
            try:
                output, current_context = self.action_executor.execute(
                    match.rule.action,
                    current_context,
                    match.bindings
                )
                
                # Update rule statistics
                match.rule.last_fired = datetime.now()
                match.rule.fire_count += 1
                
                result = ExecutionResult(
                    rule_name=match.rule.name,
                    success=True,
                    output=output,
                    bindings=match.bindings,
                    execution_time_ms=(time.time() - start_time) * 1000
                )
            except Exception as e:
                result = ExecutionResult(
                    rule_name=match.rule.name,
                    success=False,
                    output=None,
                    bindings=match.bindings,
                    error=str(e),
                    execution_time_ms=(time.time() - start_time) * 1000
                )
            
            results.append(result)
            self.execution_history.append(result)
        
        self.logger.log(f"Executed {len(results)} rules", level="INFO")
        return results
    
    def _find_matching_rules(self, context: Dict[str, Any]) -> List[RuleMatch]:
        """
        Find rules that match the context.
        
        Args:
            context: Context to match against
            
        Returns:
            List of RuleMatch objects
        """
        matching = []
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            matches, bindings = self.pattern_matcher.match(rule.condition, context)
            
            if matches:
                score = self.pattern_matcher.calculate_match_score(rule.condition, context)
                matching.append(RuleMatch(rule=rule, bindings=bindings, match_score=score))
        
        return matching
    
    def _resolve_conflicts(self, matches: List[RuleMatch], context: Dict[str, Any]) -> List[RuleMatch]:
        """
        Resolve conflicts between matching rules.
        
        Args:
            matches: List of matching rules
            context: Current context
            
        Returns:
            List of rules to execute (filtered/ordered)
        """
        if not matches:
            return []
        
        if self.strategy == ConflictResolutionStrategy.ALL:
            # Execute all matching rules, sorted by priority
            return sorted(matches, key=lambda m: m.rule.priority, reverse=True)
        
        elif self.strategy == ConflictResolutionStrategy.FIRST_MATCH:
            # Execute only the first matching rule
            return [matches[0]]
        
        elif self.strategy == ConflictResolutionStrategy.PRIORITY:
            # Execute highest priority rule(s)
            max_priority = max(m.rule.priority for m in matches)
            highest_priority = [m for m in matches if m.rule.priority == max_priority]
            
            # If tie, use specificity
            if len(highest_priority) > 1:
                max_specificity = max(m.rule.specificity for m in highest_priority)
                return [m for m in highest_priority if m.rule.specificity == max_specificity][:1]
            
            return highest_priority
        
        elif self.strategy == ConflictResolutionStrategy.SPECIFICITY:
            # Execute most specific rule(s)
            max_specificity = max(m.rule.specificity for m in matches)
            most_specific = [m for m in matches if m.rule.specificity == max_specificity]
            
            # If tie, use priority
            if len(most_specific) > 1:
                max_priority = max(m.rule.priority for m in most_specific)
                return [m for m in most_specific if m.rule.priority == max_priority][:1]
            
            return most_specific
        
        elif self.strategy == ConflictResolutionStrategy.RECENCY:
            # Execute most recently fired/created rule
            def recency_key(m: RuleMatch):
                if m.rule.last_fired:
                    return m.rule.last_fired
                return m.rule.created_at
            
            return [max(matches, key=recency_key)]
        
        return matches
    
    def register_action(self, name: str, func: Callable) -> None:
        """Register a custom action function."""
        self.action_executor.register_action(name, func)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get rule engine statistics."""
        total_fires = sum(r.fire_count for r in self.rules)
        
        return {
            'total_rules': len(self.rules),
            'enabled_rules': sum(1 for r in self.rules if r.enabled),
            'total_executions': len(self.execution_history),
            'total_fires': total_fires,
            'success_rate': (
                sum(1 for e in self.execution_history if e.success) / 
                len(self.execution_history) if self.execution_history else 0
            ),
            'avg_execution_time_ms': (
                sum(e.execution_time_ms for e in self.execution_history) /
                len(self.execution_history) if self.execution_history else 0
            ),
            'strategy': self.strategy.value
        }
    
    def get_rule(self, name: str) -> Optional[Rule]:
        """Get a rule by name."""
        for rule in self.rules:
            if rule.name == name:
                return rule
        return None
    
    def list_rules(self) -> List[Dict[str, Any]]:
        """List all rules."""
        return [rule.to_dict() for rule in self.rules]
