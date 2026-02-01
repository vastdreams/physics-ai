# evolution/
"""
Self-evolution engine for AI system.

First Principle Analysis:
- Code generation: Generate code C from specification S
- Validation: Validate C against constraints Φ (first-principles)
- Selection: Select best code based on performance P(C)
- Rollback: Revert if P(C) < P(C_old)
- Mathematical foundation: Program synthesis, genetic algorithms, validation logic
- Architecture: Safe code generation with validation and rollback
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import ast
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loggers.system_logger import SystemLogger
from loggers.evolution_logger import EvolutionLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from validators.code_validator import CodeValidator
from validators.data_validator import DataValidator
from evolution.code_generator import CodeGenerator
from evolution.performance_evaluator import PerformanceEvaluator
from ai.nodal_vectorization.graph_builder import GraphBuilder
from ai.nodal_vectorization.code_node import CodeNode
from ai.nodal_vectorization.node_analyzer import NodeAnalyzer


@dataclass
class EvolutionCandidate:
    """Represents a code evolution candidate."""
    code: str
    file_path: str
    version: str
    performance_score: float = 0.0
    validation_passed: bool = False
    metadata: Dict[str, Any] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()


class SelfEvolutionEngine:
    """
    Self-evolution engine that can modify and improve its own codebase.
    
    Features:
    - Code analysis and pattern recognition
    - Safe code generation with validation
    - Performance-based selection
    - Rollback mechanisms
    - Integration with nodal graph
    """
    
    def __init__(self, graph_builder: Optional[GraphBuilder] = None):
        """
        Initialize self-evolution engine.
        
        Args:
            graph_builder: Optional GraphBuilder for nodal analysis
        """
        self.logger = SystemLogger()
        self.evolution_logger = EvolutionLogger()
        self.code_validator = CodeValidator()
        self.data_validator = DataValidator()
        self.code_generator = CodeGenerator()
        self.performance_evaluator = PerformanceEvaluator()
        self.graph_builder = graph_builder
        self.node_analyzer = NodeAnalyzer() if graph_builder else None
        
        # Evolution history
        self.evolution_history: List[EvolutionCandidate] = []
        self.rollback_stack: List[Tuple[str, str]] = []  # (file_path, old_code)
        
        self.logger.log("SelfEvolutionEngine initialized", level="INFO")
    
    def analyze_codebase(self, directory: str) -> Dict[str, Any]:
        """
        Analyze codebase structure and identify improvement opportunities.
        
        Args:
            directory: Directory to analyze
            
        Returns:
            Analysis results with opportunities
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="ANALYZE_CODEBASE",
            input_data={'directory': directory},
            level=LogLevel.INFO
        )
        
        try:
            # Analyze directory
            if self.node_analyzer:
                nodes = self.node_analyzer.analyze_directory(directory)
                
                # Build graph
                if self.graph_builder:
                    for node in nodes:
                        self.graph_builder.add_node(node)
                
                # Identify opportunities
                opportunities = self._identify_opportunities(nodes)
                
                cot.end_step(
                    step_id,
                    output_data={
                        'nodes_analyzed': len(nodes),
                        'opportunities': opportunities
                    }
                )
                
                return {
                    'nodes': [node.to_dict() for node in nodes],
                    'opportunities': opportunities,
                    'statistics': self.graph_builder.get_statistics() if self.graph_builder else {}
                }
            else:
                cot.end_step(step_id, output_data={'error': 'Node analyzer not available'})
                return {'error': 'Node analyzer not available'}
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error analyzing codebase: {str(e)}", level="ERROR")
            raise
    
    def _identify_opportunities(self, nodes: List[CodeNode]) -> List[Dict[str, Any]]:
        """
        Identify code improvement opportunities.
        
        Args:
            nodes: List of code nodes
            
        Returns:
            List of opportunities
        """
        opportunities = []
        
        # Check for high complexity
        for node in nodes:
            complexity = node.get_metadata('complexity', 0)
            if complexity > 20:
                opportunities.append({
                    'type': 'high_complexity',
                    'file': node.file_path,
                    'complexity': complexity,
                    'suggestion': 'Refactor to reduce cyclomatic complexity'
                })
            
            # Check for many dependencies
            if len(node.dependencies) > 10:
                opportunities.append({
                    'type': 'many_dependencies',
                    'file': node.file_path,
                    'dependencies': len(node.dependencies),
                    'suggestion': 'Consider breaking into smaller modules'
                })
        
        return opportunities
    
    def evolve_function(self,
                       file_path: str,
                       function_name: str,
                       improvement_spec: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Evolve a specific function based on improvement specification.
        
        Args:
            file_path: Path to file containing function
            function_name: Name of function to evolve
            improvement_spec: Specification for improvement
            
        Returns:
            Tuple of (success, new_code)
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="EVOLVE_FUNCTION",
            input_data={
                'file_path': file_path,
                'function_name': function_name,
                'improvement_spec': improvement_spec
            },
            level=LogLevel.DECISION
        )
        
        try:
            # Read current code
            with open(file_path, 'r', encoding='utf-8') as f:
                current_code = f.read()
            
            # Backup current code
            self.rollback_stack.append((file_path, current_code))
            
            # Generate improved code
            new_code = self._generate_improved_code(
                current_code,
                function_name,
                improvement_spec
            )
            
            # Validate new code
            validation_result = self._validate_code(new_code, file_path)
            
            if not validation_result[0]:
                cot.end_step(
                    step_id,
                    output_data={'error': validation_result[1]},
                    validation_passed=False
                )
                return False, None
            
            # Evaluate performance
            performance = self._evaluate_performance(new_code, current_code)
            
            # Create candidate
            candidate = EvolutionCandidate(
                code=new_code,
                file_path=file_path,
                version=self._increment_version(),
                performance_score=performance,
                validation_passed=True,
                metadata=improvement_spec
            )
            
            self.evolution_history.append(candidate)
            
            cot.end_step(
                step_id,
                output_data={
                    'new_code': new_code,
                    'performance_score': performance
                },
                validation_passed=True,
                performance_metrics={'score': performance}
            )
            
            self.evolution_logger.log_evolution("function_evolution", {
                'file_path': file_path,
                'function_name': function_name,
                'performance_score': performance
            })
            
            return True, new_code
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error evolving function: {str(e)}", level="ERROR")
            return False, None
    
    def _generate_improved_code(self,
                                current_code: str,
                                function_name: str,
                                improvement_spec: Dict[str, Any]) -> str:
        """
        Generate improved code based on specification.
        
        Args:
            current_code: Current code
            function_name: Function to improve
            improvement_spec: Improvement specification
            
        Returns:
            Improved code
        """
        # Parse current code
        try:
            tree = ast.parse(current_code)
        except SyntaxError as e:
            raise ValueError(f"Invalid current code: {str(e)}")
        
        # Extract function
        function_node = None
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == function_name:
                    function_node = node
                    break
        
        if not function_node:
            raise ValueError(f"Function {function_name} not found")
        
        # Generate improved version
        # This is a simplified version - in practice, would use more sophisticated code generation
        improvement_type = improvement_spec.get('type', 'optimize')
        
        if improvement_type == 'optimize':
            # Add optimization comments
            new_code = current_code.replace(
                f"def {function_name}",
                f"# Optimized version\n# Performance: {improvement_spec.get('target', 'improved')}\ndef {function_name}"
            )
        elif improvement_type == 'refactor':
            # Add refactoring
            new_code = current_code.replace(
                f"def {function_name}",
                f"# Refactored for clarity\n# Complexity reduced\ndef {function_name}"
            )
        else:
            # Use code generator
            function_spec = {
                'name': function_name,
                'parameters': [arg.arg for arg in function_node.args.args],
                'body': improvement_spec.get('new_body', 'pass')
            }
            generated = self.code_generator.generate_function(function_spec)
            # Replace function in code
            new_code = self._replace_function_in_code(current_code, function_name, generated)
        
        return new_code
    
    def _replace_function_in_code(self, code: str, function_name: str, new_function: str) -> str:
        """Replace a function in code."""
        # Simplified implementation - would need proper AST manipulation
        lines = code.split('\n')
        new_lines = []
        in_function = False
        indent_level = 0
        
        for line in lines:
            if f"def {function_name}" in line:
                # Insert new function
                new_lines.append(new_function)
                in_function = True
                indent_level = len(line) - len(line.lstrip())
            elif in_function:
                current_indent = len(line) - len(line.lstrip()) if line.strip() else indent_level + 1
                if line.strip() and current_indent <= indent_level:
                    in_function = False
                    new_lines.append(line)
                # Skip old function body
            else:
                new_lines.append(line)
        
        return '\n'.join(new_lines)
    
    def _validate_code(self, code: str, file_path: str) -> Tuple[bool, str]:
        """
        Validate generated code.
        
        Args:
            code: Code to validate
            file_path: File path for context
            
        Returns:
            Tuple of (is_valid, message)
        """
        # Syntax validation
        if not self.code_validator.validate_syntax(code):
            return False, "Syntax validation failed"
        
        # Safety validation
        if not self.code_validator.validate_safety(code):
            return False, "Safety validation failed"
        
        # Physics constraints (if applicable)
        # This would check against first-principles constraints
        
        return True, "Validation passed"
    
    def _evaluate_performance(self, new_code: str, old_code: str) -> float:
        """
        Evaluate performance improvement.
        
        Args:
            new_code: New code
            old_code: Old code
            
        Returns:
            Performance score (0.0 to 1.0)
        """
        # Simplified performance evaluation
        # In practice, would run benchmarks
        
        # Heuristic: compare code metrics
        new_lines = len(new_code.splitlines())
        old_lines = len(old_code.splitlines())
        
        # Prefer shorter code (if functionality preserved)
        if new_lines < old_lines:
            score = 0.7 + 0.3 * (1.0 - new_lines / old_lines)
        else:
            score = 0.5
        
        return min(1.0, max(0.0, score))
    
    def apply_evolution(self, candidate: EvolutionCandidate, backup: bool = True) -> bool:
        """
        Apply an evolution candidate to the codebase.
        
        Args:
            candidate: Evolution candidate
            backup: Whether to create backup
            
        Returns:
            True if applied successfully
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="APPLY_EVOLUTION",
            input_data={'candidate': candidate.file_path},
            level=LogLevel.DECISION
        )
        
        try:
            # Backup if requested
            if backup:
                with open(candidate.file_path, 'r', encoding='utf-8') as f:
                    old_code = f.read()
                self.rollback_stack.append((candidate.file_path, old_code))
            
            # Write new code
            with open(candidate.file_path, 'w', encoding='utf-8') as f:
                f.write(candidate.code)
            
            cot.end_step(step_id, output_data={'success': True}, validation_passed=True)
            
            self.logger.log(f"Evolution applied: {candidate.file_path}", level="INFO")
            return True
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error applying evolution: {str(e)}", level="ERROR")
            return False
    
    def rollback(self, file_path: Optional[str] = None) -> bool:
        """
        Rollback last evolution.
        
        Args:
            file_path: Specific file to rollback (if None, rollback most recent)
            
        Returns:
            True if rolled back successfully
        """
        if not self.rollback_stack:
            self.logger.log("No rollback available", level="WARNING")
            return False
        
        if file_path:
            # Find matching backup
            for i, (path, code) in enumerate(reversed(self.rollback_stack)):
                if path == file_path:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(code)
                    self.rollback_stack.pop(len(self.rollback_stack) - 1 - i)
                    self.logger.log(f"Rolled back: {file_path}", level="INFO")
                    return True
            return False
        else:
            # Rollback most recent
            path, code = self.rollback_stack.pop()
            with open(path, 'w', encoding='utf-8') as f:
                f.write(code)
            self.logger.log(f"Rolled back: {path}", level="INFO")
            return True
    
    def _increment_version(self) -> str:
        """Increment version string."""
        if not self.evolution_history:
            return "1.0.1"
        
        last_version = self.evolution_history[-1].version
        parts = last_version.split('.')
        if len(parts) == 3:
            parts[2] = str(int(parts[2]) + 1)
            return '.'.join(parts)
        return "1.0.1"
    
    def get_evolution_history(self) -> List[Dict[str, Any]]:
        """Get evolution history."""
        return [
            {
                'file_path': c.file_path,
                'version': c.version,
                'performance_score': c.performance_score,
                'validation_passed': c.validation_passed,
                'timestamp': c.timestamp.isoformat()
            }
            for c in self.evolution_history
        ]

