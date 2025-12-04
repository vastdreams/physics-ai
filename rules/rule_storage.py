# rules/
"""
Rule storage module.

Stores and retrieves rules from persistent storage.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from validators.rule_validator import RuleValidator
from loggers.system_logger import SystemLogger


class RuleStorage:
    """
    Stores and retrieves rules.
    """
    
    def __init__(self, storage_path: str = "data/rules"):
        """
        Initialize rule storage.
        
        Args:
            storage_path: Path to store rules
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.validator = RuleValidator()
        self.logger = SystemLogger()
        
        self.logger.log(f"RuleStorage initialized at {storage_path}", level="INFO")
    
    def save_rule(self, rule: Dict[str, Any]) -> bool:
        """
        Save a rule to storage.
        
        Args:
            rule: Rule to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        if not self.validator.validate_rule(rule):
            self.logger.log("Invalid rule provided", level="WARNING")
            return False
        
        rule_file = self.storage_path / f"{rule.get('name', 'rule')}.json"
        with open(rule_file, 'w') as f:
            json.dump(rule, f, indent=2)
        
        self.logger.log(f"Rule saved: {rule_file}", level="INFO")
        return True
    
    def load_rule(self, rule_name: str) -> Optional[Dict[str, Any]]:
        """
        Load a rule from storage.
        
        Args:
            rule_name: Name of rule to load
            
        Returns:
            Rule dictionary or None if not found
        """
        rule_file = self.storage_path / f"{rule_name}.json"
        if not rule_file.exists():
            self.logger.log(f"Rule not found: {rule_name}", level="WARNING")
            return None
        
        with open(rule_file, 'r') as f:
            rule = json.load(f)
        
        self.logger.log(f"Rule loaded: {rule_name}", level="INFO")
        return rule
    
    def list_rules(self) -> List[str]:
        """
        List all stored rules.
        
        Returns:
            List of rule names
        """
        rules = [f.stem for f in self.storage_path.glob("*.json")]
        self.logger.log(f"Found {len(rules)} rules", level="DEBUG")
        return rules

