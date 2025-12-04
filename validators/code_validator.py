# validators/
"""
Code validation module.

Validates generated code for syntax, safety, and correctness.
"""

import logging
import ast
from typing import Any, Dict, List, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loggers.system_logger import SystemLogger


class CodeValidator:
    """
    Validates generated code.
    """
    
    def __init__(self):
        """Initialize code validator."""
        self.logger = SystemLogger()
        self.logger.log("CodeValidator initialized", level="INFO")
    
    def validate_syntax(self, code: str) -> bool:
        """
        Validate Python code syntax.
        
        Args:
            code: Code string to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(code, str):
            self.logger.log("Code is not a string", level="WARNING")
            return False
        
        try:
            ast.parse(code)
            self.logger.log("Syntax validation passed", level="DEBUG")
            return True
        except SyntaxError as e:
            self.logger.log(f"Syntax error: {str(e)}", level="WARNING")
            return False
    
    def validate_safety(self, code: str) -> bool:
        """
        Validate code for safety (no dangerous operations).
        
        Args:
            code: Code string to validate
            
        Returns:
            True if safe, False otherwise
        """
        # Check for dangerous operations
        dangerous_patterns = ['__import__', 'eval', 'exec', 'open', 'file']
        
        for pattern in dangerous_patterns:
            if pattern in code:
                self.logger.log(f"Potentially dangerous pattern found: {pattern}", level="WARNING")
                return False
        
        self.logger.log("Safety validation passed", level="DEBUG")
        return True

