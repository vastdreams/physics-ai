# tests/
"""
Tests for core module.
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import NeurosymboticEngine
from core.reasoning import ReasoningEngineImpl, ReasoningType


class TestNeurosymboticEngine(unittest.TestCase):
    """Tests for NeurosymboticEngine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = NeurosymboticEngine()
    
    def test_initialization(self):
        """Test engine initialization."""
        self.assertIsNotNone(self.engine)
        self.assertIsNotNone(self.engine.validator)
        self.assertIsNotNone(self.engine.logger)
    
    def test_process(self):
        """Test processing functionality."""
        input_data = {"test": "data"}
        result = self.engine.process(input_data)
        self.assertIsNotNone(result)
        self.assertIn("integrated", result)


class TestReasoningEngine(unittest.TestCase):
    """Tests for ReasoningEngine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = ReasoningEngineImpl(ReasoningType.DEDUCTIVE)
    
    def test_initialization(self):
        """Test reasoning engine initialization."""
        self.assertIsNotNone(self.engine)
        self.assertEqual(self.engine.reasoning_type, ReasoningType.DEDUCTIVE)
    
    def test_reason(self):
        """Test reasoning functionality."""
        premises = ["premise1", "premise2"]
        result = self.engine.reason(premises)
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()

