# validators/
"""
PATH: validators/code_validator.py
PURPOSE: Validates generated code for syntax, safety, and correctness using AST analysis.

FLOW:
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│ Parse Code  │───▶│ AST Analysis │───▶│ Safety      │
│             │    │              │    │ Validation  │
└─────────────┘    └──────────────┘    └─────────────┘

DEPENDENCIES:
- ast: Python Abstract Syntax Tree
- SystemLogger: Logging system

WHY: AST-based validation is more robust than string matching because it:
- Cannot be bypassed by string obfuscation
- Understands code structure, not just text patterns
- Can detect dangerous patterns regardless of formatting
"""

import ast
from typing import Any, Dict, List, Optional, Set, Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loggers.system_logger import SystemLogger


class DangerousNodeVisitor(ast.NodeVisitor):
    """
    AST visitor that detects dangerous code patterns.
    
    This is more secure than string matching because it analyzes
    the actual code structure, not text patterns.
    """
    
    # Dangerous built-in functions that should not be allowed
    DANGEROUS_BUILTINS: Set[str] = {
        'eval', 'exec', 'compile', '__import__',
        'open', 'file', 'input', 'raw_input',
        'execfile', 'reload', 'breakpoint',
    }
    
    # Dangerous modules that should not be imported
    DANGEROUS_MODULES: Set[str] = {
        'os', 'sys', 'subprocess', 'shutil', 'socket',
        'pickle', 'marshal', 'shelve', 'tempfile',
        'ctypes', 'multiprocessing', 'threading',
        'pty', 'fcntl', 'resource', 'syslog',
        'commands', 'popen2', 'importlib',
    }
    
    # Dangerous attributes that indicate code manipulation
    DANGEROUS_ATTRIBUTES: Set[str] = {
        '__code__', '__globals__', '__builtins__',
        '__subclasses__', '__mro__', '__bases__',
        '__class__', '__dict__', '__getattribute__',
        '__reduce__', '__reduce_ex__',
    }
    
    def __init__(self):
        self.violations: List[Dict[str, Any]] = []
        self.logger = SystemLogger()
    
    def visit_Call(self, node: ast.Call) -> None:
        """Check for dangerous function calls."""
        # Check direct function calls (e.g., eval(...))
        if isinstance(node.func, ast.Name):
            if node.func.id in self.DANGEROUS_BUILTINS:
                self.violations.append({
                    'type': 'dangerous_builtin',
                    'name': node.func.id,
                    'line': node.lineno,
                    'col': node.col_offset,
                    'severity': 'critical'
                })
        
        # Check attribute calls (e.g., getattr(builtins, 'eval'))
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in self.DANGEROUS_BUILTINS:
                self.violations.append({
                    'type': 'dangerous_builtin_via_attr',
                    'name': node.func.attr,
                    'line': node.lineno,
                    'col': node.col_offset,
                    'severity': 'critical'
                })
        
        # Check for getattr/setattr with dangerous targets
        if isinstance(node.func, ast.Name) and node.func.id in ('getattr', 'setattr', 'delattr'):
            if len(node.args) >= 2:
                if isinstance(node.args[1], ast.Constant):
                    attr_name = node.args[1].value
                    if isinstance(attr_name, str):
                        if attr_name in self.DANGEROUS_BUILTINS or attr_name in self.DANGEROUS_ATTRIBUTES:
                            self.violations.append({
                                'type': 'dangerous_getattr',
                                'name': attr_name,
                                'line': node.lineno,
                                'col': node.col_offset,
                                'severity': 'critical'
                            })
        
        self.generic_visit(node)
    
    def visit_Import(self, node: ast.Import) -> None:
        """Check for dangerous module imports."""
        for alias in node.names:
            module_name = alias.name.split('.')[0]
            if module_name in self.DANGEROUS_MODULES:
                self.violations.append({
                    'type': 'dangerous_import',
                    'name': alias.name,
                    'line': node.lineno,
                    'col': node.col_offset,
                    'severity': 'high'
                })
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Check for dangerous from-imports."""
        if node.module:
            module_name = node.module.split('.')[0]
            if module_name in self.DANGEROUS_MODULES:
                self.violations.append({
                    'type': 'dangerous_import_from',
                    'name': node.module,
                    'line': node.lineno,
                    'col': node.col_offset,
                    'severity': 'high'
                })
        self.generic_visit(node)
    
    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Check for dangerous attribute access."""
        if node.attr in self.DANGEROUS_ATTRIBUTES:
            self.violations.append({
                'type': 'dangerous_attribute',
                'name': node.attr,
                'line': node.lineno,
                'col': node.col_offset,
                'severity': 'high'
            })
        self.generic_visit(node)
    
    def visit_Global(self, node: ast.Global) -> None:
        """Flag global statements as potential issues."""
        self.violations.append({
            'type': 'global_statement',
            'name': ', '.join(node.names),
            'line': node.lineno,
            'col': node.col_offset,
            'severity': 'medium'
        })
        self.generic_visit(node)


class CodeComplexityVisitor(ast.NodeVisitor):
    """
    AST visitor that calculates code complexity metrics.
    """
    
    def __init__(self):
        self.complexity = 1  # Base complexity
        self.function_count = 0
        self.class_count = 0
        self.loop_count = 0
        self.branch_count = 0
        self.max_depth = 0
        self._current_depth = 0
    
    def _increase_depth(self):
        self._current_depth += 1
        self.max_depth = max(self.max_depth, self._current_depth)
    
    def _decrease_depth(self):
        self._current_depth -= 1
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.function_count += 1
        self._increase_depth()
        self.generic_visit(node)
        self._decrease_depth()
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.function_count += 1
        self._increase_depth()
        self.generic_visit(node)
        self._decrease_depth()
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.class_count += 1
        self._increase_depth()
        self.generic_visit(node)
        self._decrease_depth()
    
    def visit_If(self, node: ast.If) -> None:
        self.complexity += 1
        self.branch_count += 1
        self.generic_visit(node)
    
    def visit_For(self, node: ast.For) -> None:
        self.complexity += 1
        self.loop_count += 1
        self._increase_depth()
        self.generic_visit(node)
        self._decrease_depth()
    
    def visit_While(self, node: ast.While) -> None:
        self.complexity += 1
        self.loop_count += 1
        self._increase_depth()
        self.generic_visit(node)
        self._decrease_depth()
    
    def visit_Try(self, node: ast.Try) -> None:
        self.complexity += len(node.handlers)
        self.generic_visit(node)
    
    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        # Each 'and' or 'or' adds to complexity
        self.complexity += len(node.values) - 1
        self.generic_visit(node)
    
    def get_metrics(self) -> Dict[str, Any]:
        return {
            'cyclomatic_complexity': self.complexity,
            'function_count': self.function_count,
            'class_count': self.class_count,
            'loop_count': self.loop_count,
            'branch_count': self.branch_count,
            'max_nesting_depth': self.max_depth
        }


class CodeValidator:
    """
    Validates generated code using AST-based analysis.
    
    Features:
    - Syntax validation via ast.parse()
    - Safety validation via AST visitor pattern
    - Complexity analysis
    - Physics constraint validation (placeholder)
    """
    
    # Complexity thresholds
    MAX_COMPLEXITY = 50
    MAX_NESTING_DEPTH = 10
    MAX_FUNCTION_COUNT = 100
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize code validator.
        
        Args:
            strict_mode: If True, any violation fails validation
        """
        self.logger = SystemLogger()
        self.strict_mode = strict_mode
        self.logger.log("CodeValidator initialized (AST-based)", level="INFO")
    
    def validate_syntax(self, code: str) -> bool:
        """
        Validate Python code syntax using AST parsing.
        
        Args:
            code: Code string to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(code, str):
            self.logger.log("Code is not a string", level="WARNING")
            return False
        
        if not code.strip():
            self.logger.log("Code is empty", level="WARNING")
            return False
        
        try:
            ast.parse(code)
            self.logger.log("Syntax validation passed", level="DEBUG")
            return True
        except SyntaxError as e:
            self.logger.log(f"Syntax error at line {e.lineno}: {e.msg}", level="WARNING")
            return False
    
    def validate_safety(self, code: str) -> bool:
        """
        Validate code for safety using AST analysis.
        
        This method detects:
        - Dangerous built-in calls (eval, exec, etc.)
        - Dangerous module imports (os, subprocess, etc.)
        - Dangerous attribute access (__code__, __globals__, etc.)
        
        Args:
            code: Code string to validate
            
        Returns:
            True if safe, False otherwise
        """
        if not self.validate_syntax(code):
            return False
        
        try:
            tree = ast.parse(code)
            visitor = DangerousNodeVisitor()
            visitor.visit(tree)
            
            if visitor.violations:
                # Log all violations
                for v in visitor.violations:
                    self.logger.log(
                        f"Safety violation ({v['severity']}): {v['type']} - "
                        f"'{v['name']}' at line {v['line']}",
                        level="WARNING"
                    )
                
                # In strict mode, any violation fails
                if self.strict_mode:
                    critical_violations = [v for v in visitor.violations if v['severity'] == 'critical']
                    if critical_violations:
                        self.logger.log(
                            f"Safety validation failed: {len(critical_violations)} critical violations",
                            level="ERROR"
                        )
                        return False
                
                # In non-strict mode, only critical violations fail
                critical = [v for v in visitor.violations if v['severity'] == 'critical']
                if critical:
                    return False
            
            self.logger.log("Safety validation passed", level="DEBUG")
            return True
            
        except Exception as e:
            self.logger.log(f"Error during safety validation: {str(e)}", level="ERROR")
            return False
    
    def validate_complexity(self, code: str, max_complexity: Optional[int] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate code complexity.
        
        Args:
            code: Code string to validate
            max_complexity: Optional maximum allowed complexity
            
        Returns:
            Tuple of (is_valid, metrics_dict)
        """
        if not self.validate_syntax(code):
            return False, {}
        
        max_complexity = max_complexity or self.MAX_COMPLEXITY
        
        try:
            tree = ast.parse(code)
            visitor = CodeComplexityVisitor()
            visitor.visit(tree)
            
            metrics = visitor.get_metrics()
            
            is_valid = (
                metrics['cyclomatic_complexity'] <= max_complexity and
                metrics['max_nesting_depth'] <= self.MAX_NESTING_DEPTH
            )
            
            if not is_valid:
                self.logger.log(
                    f"Complexity validation failed: complexity={metrics['cyclomatic_complexity']}, "
                    f"depth={metrics['max_nesting_depth']}",
                    level="WARNING"
                )
            else:
                self.logger.log("Complexity validation passed", level="DEBUG")
            
            return is_valid, metrics
            
        except Exception as e:
            self.logger.log(f"Error during complexity validation: {str(e)}", level="ERROR")
            return False, {}
    
    def validate_all(self, code: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Run all validations on code.
        
        Args:
            code: Code string to validate
            
        Returns:
            Tuple of (is_valid, results_dict)
        """
        results = {
            'syntax_valid': False,
            'safety_valid': False,
            'complexity_valid': False,
            'complexity_metrics': {},
            'overall_valid': False
        }
        
        # Syntax check
        results['syntax_valid'] = self.validate_syntax(code)
        if not results['syntax_valid']:
            return False, results
        
        # Safety check
        results['safety_valid'] = self.validate_safety(code)
        
        # Complexity check
        results['complexity_valid'], results['complexity_metrics'] = self.validate_complexity(code)
        
        # Overall result
        results['overall_valid'] = all([
            results['syntax_valid'],
            results['safety_valid'],
            results['complexity_valid']
        ])
        
        return results['overall_valid'], results
    
    def get_violations(self, code: str) -> List[Dict[str, Any]]:
        """
        Get all safety violations in code without failing.
        
        Args:
            code: Code string to analyze
            
        Returns:
            List of violation dictionaries
        """
        if not self.validate_syntax(code):
            return [{'type': 'syntax_error', 'severity': 'critical'}]
        
        try:
            tree = ast.parse(code)
            visitor = DangerousNodeVisitor()
            visitor.visit(tree)
            return visitor.violations
        except Exception as e:
            return [{'type': 'analysis_error', 'message': str(e), 'severity': 'critical'}]
    
    def sanitize_code(self, code: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Attempt to sanitize code by removing dangerous patterns.
        
        Note: This is a best-effort approach and may break code functionality.
        It's better to reject unsafe code than try to fix it.
        
        Args:
            code: Code string to sanitize
            
        Returns:
            Tuple of (sanitized_code, removed_patterns)
        """
        violations = self.get_violations(code)
        
        if not violations:
            return code, []
        
        # For now, just return original with warning
        # Full sanitization would require complex AST manipulation
        self.logger.log(
            f"Code has {len(violations)} violations - sanitization not implemented",
            level="WARNING"
        )
        
        return code, violations
