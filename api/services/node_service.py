# api/services/
"""
Node Service - Business logic for nodal operations.
"""

from typing import Any, Dict, List, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ai.nodal_vectorization.graph_builder import GraphBuilder
from ai.nodal_vectorization.node_analyzer import NodeAnalyzer
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel


class NodeService:
    """
    Service for nodal graph operations.
    
    Encapsulates business logic for node management.
    """
    
    def __init__(self):
        """Initialize node service."""
        self.logger = SystemLogger()
        self.graph_builder = GraphBuilder()
        self.node_analyzer = NodeAnalyzer()
        
        self.logger.log("NodeService initialized", level="INFO")
    
    def analyze_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Analyze directory and add nodes.
        
        Args:
            directory_path: Directory path to analyze
            
        Returns:
            Analysis results
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="SERVICE_ANALYZE_DIRECTORY",
            input_data={'directory': directory_path},
            level=LogLevel.INFO
        )
        
        try:
            # Analyze directory
            nodes = self.node_analyzer.analyze_directory(directory_path)
            
            # Add to graph
            for node in nodes:
                self.graph_builder.add_node(node)
            
            stats = self.graph_builder.get_statistics()
            
            cot.end_step(
                step_id,
                output_data={'num_nodes': len(nodes), 'stats': stats},
                validation_passed=True
            )
            
            return {
                'num_nodes': len(nodes),
                'statistics': stats
            }
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error in node service: {str(e)}", level="ERROR")
            raise
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get node by ID."""
        node = self.graph_builder.get_node(node_id)
        if not node:
            return None
        
        return {
            'node_id': node.node_id,
            'file_path': node.file_path,
            'dependencies': list(node.dependencies),
            'metadata': node.metadata
        }
    
    def list_nodes(self) -> List[Dict[str, Any]]:
        """List all nodes."""
        nodes = self.graph_builder.get_all_nodes()
        return [
            {
                'node_id': node.node_id,
                'file_path': node.file_path,
                'num_dependencies': len(node.dependencies)
            }
            for node in nodes
        ]

