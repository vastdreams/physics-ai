# validators/
"""
Data validation module.

First Principle Analysis:
- Validation ensures data integrity and system reliability
- Must validate inputs, outputs, and intermediate states
- Mathematical foundation: type theory, constraint satisfaction
- Architecture: modular validators for different data types

Planning:
1. Implement type validation
2. Create constraint validation
3. Add format validation
4. Design for extensibility
"""

import logging
from typing import Any, Dict, List, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loggers.system_logger import SystemLogger


class DataValidator:
    """
    Validates data for type, format, and constraints.
    
    Provides comprehensive validation to ensure system reliability
    and enable future AI self-validation.
    """
    
    def __init__(self):
        """Initialize data validator."""
        self.logger = SystemLogger()
        self.logger.log("DataValidator initialized", level="INFO")
    
    def validate_input(self, data: Any) -> bool:
        """
        Validate input data.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid, False otherwise
        """
        if data is None:
            self.logger.log("Input data is None", level="WARNING")
            return False
        
        # Basic validation
        if not isinstance(data, (str, int, float, list, dict, bool)):
            self.logger.log(f"Invalid input type: {type(data)}", level="WARNING")
            return False
        
        self.logger.log("Input validation passed", level="DEBUG")
        return True
    
    def validate_output(self, data: Any) -> bool:
        """
        Validate output data.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid, False otherwise
        """
        if data is None:
            self.logger.log("Output data is None", level="WARNING")
            return False
        
        # Basic validation
        if not isinstance(data, (str, int, float, list, dict, bool)):
            self.logger.log(f"Invalid output type: {type(data)}", level="WARNING")
            return False
        
        self.logger.log("Output validation passed", level="DEBUG")
        return True
    
    def validate_dict(self, data: Dict[str, Any]) -> bool:
        """
        Validate dictionary structure.
        
        Args:
            data: Dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(data, dict):
            self.logger.log("Data is not a dictionary", level="WARNING")
            return False
        
        if len(data) == 0:
            self.logger.log("Dictionary is empty", level="WARNING")
            return False
        
        self.logger.log("Dictionary validation passed", level="DEBUG")
        return True
    
    def validate_list(self, data: List[Any]) -> bool:
        """
        Validate list structure.
        
        Args:
            data: List to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(data, list):
            self.logger.log("Data is not a list", level="WARNING")
            return False
        
        self.logger.log("List validation passed", level="DEBUG")
        return True
    
    def validate_type(self, data: Any, expected_type: type) -> bool:
        """
        Validate data type.
        
        Args:
            data: Data to validate
            expected_type: Expected type
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(data, expected_type):
            self.logger.log(f"Type mismatch: expected {expected_type}, got {type(data)}", level="WARNING")
            return False
        
        self.logger.log("Type validation passed", level="DEBUG")
        return True

