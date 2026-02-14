"""Tests for evolution module."""

from __future__ import annotations

import unittest

from evolution.code_generator import CodeGenerator


class TestCodeGenerator(unittest.TestCase):
    """Tests for CodeGenerator."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.generator = CodeGenerator()

    def test_initialization(self) -> None:
        """Test code generator initialization."""
        self.assertIsNotNone(self.generator)

    def test_generate_function(self) -> None:
        """Test function generation."""
        spec = {
            "name": "test_function",
            "parameters": ["x", "y"],
            "body": "return x + y",
        }
        code = self.generator.generate_function(spec)
        self.assertIn("def test_function", code)
        self.assertIn("x, y", code)


if __name__ == "__main__":
    unittest.main()
