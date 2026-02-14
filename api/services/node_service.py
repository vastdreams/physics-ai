"""
PATH: api/services/node_service.py
PURPOSE: Business logic for nodal graph operations.
"""

from typing import Any, Dict, List, Optional

from ai.nodal_vectorization.graph_builder import GraphBuilder
from ai.nodal_vectorization.node_analyzer import NodeAnalyzer
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel


class NodeService:
    """Service layer for nodal graph management."""

    def __init__(self) -> None:
        """Initialise the graph builder and node analyser."""
        self._logger = SystemLogger()
        self.graph_builder = GraphBuilder()
        self.node_analyzer = NodeAnalyzer()
        self._logger.log("NodeService initialized", level="INFO")

    def analyze_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Analyse a directory and add discovered nodes to the graph.

        Args:
            directory_path: Filesystem path to analyse.

        Returns:
            A dictionary containing ``num_nodes`` and ``statistics``.
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="SERVICE_ANALYZE_DIRECTORY",
            input_data={"directory": directory_path},
            level=LogLevel.INFO,
        )

        try:
            nodes = self.node_analyzer.analyze_directory(directory_path)

            for node in nodes:
                self.graph_builder.add_node(node)

            stats = self.graph_builder.get_statistics()

            cot.end_step(
                step_id,
                output_data={"num_nodes": len(nodes), "stats": stats},
                validation_passed=True,
            )
            return {"num_nodes": len(nodes), "statistics": stats}
        except Exception as e:
            cot.end_step(step_id, output_data={"error": str(e)}, validation_passed=False)
            self._logger.log(f"Error in node service: {e}", level="ERROR")
            raise

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Return a single node by ID, or ``None`` if not found."""
        node = self.graph_builder.get_node(node_id)
        if not node:
            return None

        return {
            "node_id": node.node_id,
            "file_path": node.file_path,
            "dependencies": list(node.dependencies),
            "metadata": node.metadata,
        }

    def list_nodes(self) -> List[Dict[str, Any]]:
        """Return a summary list of all nodes in the graph."""
        nodes = self.graph_builder.get_all_nodes()
        return [
            {
                "node_id": node.node_id,
                "file_path": node.file_path,
                "num_dependencies": len(node.dependencies),
            }
            for node in nodes
        ]
