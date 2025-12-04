# tests/
"""
Tests for rules module.
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rules.rule_engine import RuleEngine


class TestRuleEngine(unittest.TestCase):
    """Tests for RuleEngine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = RuleEngine()
    
    def test_initialization(self):
        """Test rule engine initialization."""
        self.assertIsNotNone(self.engine)
        self.assertEqual(len(self.engine.rules), 0)
    
    def test_add_rule(self):
        """Test adding a rule."""
        rule = {
            "name": "test_rule",
            "condition": {"type": "test"},
            "action": {"type": "test_action"}
        }
        result = self.engine.add_rule(rule)
        self.assertTrue(result)
        self.assertEqual(len(self.engine.rules), 1)


if __name__ == '__main__':
    unittest.main()

