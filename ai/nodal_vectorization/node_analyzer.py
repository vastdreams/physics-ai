# ai/nodal_vectorization/
"""
Node analyzer for code structure extraction.

First Principle Analysis:
- Code analysis requires parsing syntax and semantics
- Extract: functions, classes, imports, dependencies
- Mathematical foundation: Abstract syntax trees (AST), graph parsing
- Architecture: Modular analyzer with pluggable extractors
"""

import ast
from typing import Any, Dict, List, Set, Tuple
from pathlib import Path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from loggers.system_logger import SystemLogger
from ai.nodal_vectorization.code_node import CodeNode


class NodeAnalyzer:
    """
    Analyzes code files and extracts structure for node creation.
    
    Extracts:
    - Functions and classes
    - Imports and dependencies
    - Code complexity metrics
    - Relationships between modules
    """
    
    def __init__(self):
        """Initialize node analyzer."""
        self.logger = SystemLogger()
        self.logger.log("NodeAnalyzer initialized", level="INFO")
    
    def analyze_file(self, file_path: str) -> CodeNode:
        """
        Analyze a Python file and create a CodeNode.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            CodeNode with extracted information
        """
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            self.logger.log(f"File not found: {file_path}", level="ERROR")
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.logger.log(f"Error reading file {file_path}: {str(e)}", level="ERROR")
            raise
        
        # Parse AST
        try:
            tree = ast.parse(content, filename=file_path)
        except SyntaxError as e:
            self.logger.log(f"Syntax error in {file_path}: {str(e)}", level="ERROR")
            raise
        
        # Extract information
        functions = self._extract_functions(tree)
        classes = self._extract_classes(tree)
        imports = self._extract_imports(tree)
        dependencies = self._extract_dependencies(imports)
        
        # Create node
        node = CodeNode(
            file_path=str(file_path_obj.absolute()),
            functions=functions,
            classes=classes
        )
        
        # Add imports and dependencies
        for imp in imports:
            node.add_import(imp)
        
        for dep in dependencies:
            node.add_dependency(dep)
        
        # Extract metadata
        metadata = {
            'line_count': len(content.splitlines()),
            'function_count': len(functions),
            'class_count': len(classes),
            'import_count': len(imports),
            'complexity': self._compute_complexity(tree)
        }
        
        for key, value in metadata.items():
            node.update_metadata(key, value)
        
        self.logger.log(f"Analyzed file: {file_path} ({len(functions)} functions, {len(classes)} classes)", level="INFO")
        
        return node
    
    def _extract_functions(self, tree: ast.AST) -> List[str]:
        """Extract function names from AST."""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.AsyncFunctionDef):
                functions.append(node.name)
        
        return functions
    
    def _extract_classes(self, tree: ast.AST) -> List[str]:
        """Extract class names from AST."""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
        
        return classes
    
    def _extract_imports(self, tree: ast.AST) -> Set[str]:
        """Extract import statements from AST."""
        imports = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
        
        return imports
    
    def _extract_dependencies(self, imports: Set[str]) -> Set[str]:
        """
        Extract dependencies from imports.
        
        Converts import names to potential node IDs.
        For example: 'physics.domains.classical' -> 'node_physics_domains_classical'
        """
        dependencies = set()
        
        for imp in imports:
            # Convert import to potential node ID
            # This is a heuristic - actual mapping depends on project structure
            if imp.startswith('physics') or imp.startswith('core') or imp.startswith('rules'):
                # Internal dependency
                node_id = f"node_{imp.replace('.', '_')}"
                dependencies.add(node_id)
        
        return dependencies
    
    def _compute_complexity(self, tree: ast.AST) -> int:
        """
        Compute cyclomatic complexity.
        
        Mathematical: C = 1 + number of decision points
        """
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            # Count decision points
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.Try):
                complexity += 1
            elif isinstance(node, ast.With, ast.AsyncWith):
                complexity += 1
        
        return complexity
    
    def analyze_directory(self, directory: str, pattern: str = "*.py") -> List[CodeNode]:
        """
        Analyze all Python files in a directory.
        
        Args:
            directory: Directory path
            pattern: File pattern to match
            
        Returns:
            List of CodeNodes
        """
        dir_path = Path(directory)
        
        if not dir_path.exists():
            self.logger.log(f"Directory not found: {directory}", level="ERROR")
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        nodes = []
        for file_path in dir_path.rglob(pattern):
            try:
                node = self.analyze_file(str(file_path))
                nodes.append(node)
            except Exception as e:
                self.logger.log(f"Error analyzing {file_path}: {str(e)}", level="WARNING")
                continue
        
        self.logger.log(f"Analyzed {len(nodes)} files in {directory}", level="INFO")
        return nodes

