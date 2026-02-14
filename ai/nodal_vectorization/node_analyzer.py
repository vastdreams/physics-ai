"""
PATH: ai/nodal_vectorization/node_analyzer.py
PURPOSE: Analyse code files and extract structure for node creation.

FLOW:
┌─────────────┐    ┌─────────┐    ┌──────────┐
│ Python File │ →  │ AST     │ →  │ CodeNode │
└─────────────┘    └─────────┘    └──────────┘

DEPENDENCIES:
- loggers.system_logger: structured logging
- code_node: node data structures
"""

import ast
from pathlib import Path
from typing import Any, Dict, List, Set

from loggers.system_logger import SystemLogger

from ai.nodal_vectorization.code_node import CodeNode

_BASE_COMPLEXITY = 1


class NodeAnalyzer:
    """Analyses code files and extracts structure for node creation.

    Extracts:
    - Functions and classes
    - Imports and dependencies
    - Code complexity metrics
    - Relationships between modules
    """

    def __init__(self) -> None:
        """Initialise node analyser."""
        self._logger = SystemLogger()
        self._logger.log("NodeAnalyzer initialized", level="INFO")

    def analyze_file(self, file_path: str) -> CodeNode:
        """Analyse a Python file and create a CodeNode.

        Args:
            file_path: Path to Python file.

        Returns:
            CodeNode with extracted information.

        Raises:
            FileNotFoundError: If the file does not exist.
            SyntaxError: If the file has invalid Python syntax.
        """
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            self._logger.log(f"File not found: {file_path}", level="ERROR")
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            self._logger.log(f"Error reading file {file_path}: {e}", level="ERROR")
            raise

        try:
            tree = ast.parse(content, filename=file_path)
        except SyntaxError as e:
            self._logger.log(f"Syntax error in {file_path}: {e}", level="ERROR")
            raise

        functions = self._extract_functions(tree)
        classes = self._extract_classes(tree)
        imports = self._extract_imports(tree)
        dependencies = self._extract_dependencies(imports)

        node = CodeNode(
            file_path=str(file_path_obj.absolute()),
            functions=functions,
            classes=classes,
        )

        for imp in imports:
            node.add_import(imp)

        for dep in dependencies:
            node.add_dependency(dep)

        metadata: Dict[str, Any] = {
            "line_count": len(content.splitlines()),
            "function_count": len(functions),
            "class_count": len(classes),
            "import_count": len(imports),
            "complexity": self._compute_complexity(tree),
        }

        for key, value in metadata.items():
            node.update_metadata(key, value)

        self._logger.log(
            f"Analyzed file: {file_path} ({len(functions)} functions, {len(classes)} classes)",
            level="INFO",
        )

        return node

    # ------------------------------------------------------------------
    # AST extraction helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_functions(tree: ast.AST) -> List[str]:
        """Extract function names from AST."""
        functions: List[str] = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(node.name)

        return functions

    @staticmethod
    def _extract_classes(tree: ast.AST) -> List[str]:
        """Extract class names from AST."""
        return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

    @staticmethod
    def _extract_imports(tree: ast.AST) -> Set[str]:
        """Extract import statements from AST."""
        imports: Set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)

        return imports

    @staticmethod
    def _extract_dependencies(imports: Set[str]) -> Set[str]:
        """Convert import names to potential node IDs for internal dependencies."""
        dependencies: Set[str] = set()

        for imp in imports:
            if imp.startswith(("physics", "core", "rules")):
                node_id = f"node_{imp.replace('.', '_')}"
                dependencies.add(node_id)

        return dependencies

    @staticmethod
    def _compute_complexity(tree: ast.AST) -> int:
        """Compute cyclomatic complexity.

        Mathematical: C = 1 + number of decision points.
        """
        complexity = _BASE_COMPLEXITY

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.Try):
                complexity += 1
            elif isinstance(node, (ast.With, ast.AsyncWith)):
                complexity += 1

        return complexity

    def analyze_directory(self, directory: str, pattern: str = "*.py") -> List[CodeNode]:
        """Analyse all Python files in a directory.

        Args:
            directory: Directory path.
            pattern: File pattern to match.

        Returns:
            List of CodeNodes.
        """
        dir_path = Path(directory)

        if not dir_path.exists():
            self._logger.log(f"Directory not found: {directory}", level="ERROR")
            raise FileNotFoundError(f"Directory not found: {directory}")

        nodes: List[CodeNode] = []
        for file_path in dir_path.rglob(pattern):
            try:
                node = self.analyze_file(str(file_path))
                nodes.append(node)
            except Exception as e:
                self._logger.log(f"Error analyzing {file_path}: {e}", level="WARNING")
                continue

        self._logger.log(f"Analyzed {len(nodes)} files in {directory}", level="INFO")
        return nodes
