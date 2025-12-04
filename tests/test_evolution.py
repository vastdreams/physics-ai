# tests/
"""
Tests for evolution module.
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evolution.code_generator import CodeGenerator


class TestCodeGenerator(unittest.TestCase):
    """Tests for CodeGenerator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = CodeGenerator()
    
    def test_initialization(self):
        """Test code generator initialization."""
        self.assertIsNotNone(self.generator)
    
    def test_generate_function(self):
        """Test function generation."""
        spec = {
            "name": "test_function",
            "parameters": ["x", "y"],
            "body": "return x + y"
        }
        code = self.generator.generate_function(spec)
        self.assertIn("def test_function", code)
        self.assertIn("x, y", code)


if __name__ == '__main__':
    unittest.main()

