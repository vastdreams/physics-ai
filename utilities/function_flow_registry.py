# utilities/
"""
Function Flow Registry for Traceability.

Inspired by DREAM architecture - register_function_flow and log_node patterns.

First Principle Analysis:
- Function flows: F = {f_1 → f_2 → ... → f_n}
- Node logging: Log each function call as a node
- Traceability: Track complete execution paths
- Mathematical foundation: Graph theory, execution traces
- Architecture: Registry pattern with automatic logging
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import functools
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from ai.nodal_vectorization.code_node import CodeNode


@dataclass
class FunctionFlowNode:
    """Represents a node in a function flow."""
    node_id: str
    function_name: str
    input_data: Any
    output_data: Any
    timestamp: datetime = field(default_factory=datetime.now)
    execution_time: float = 0.0
    parent_nodes: List[str] = field(default_factory=list)
    child_nodes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class FunctionFlowRegistry:
    """
    Registry for function flows with automatic logging.
    
    Features:
    - Function registration with flow tracking
    - Automatic node logging
    - Execution trace generation
    - Dependency graph construction
    """
    
    _instance: Optional['FunctionFlowRegistry'] = None
    _initialized: bool = False
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize registry (only once)."""
        if FunctionFlowRegistry._initialized:
            return
        
        self.logger = SystemLogger()
        self.flows: Dict[str, List[FunctionFlowNode]] = {}  # flow_id -> nodes
        self.nodes: Dict[str, FunctionFlowNode] = {}  # node_id -> node
        self.function_registry: Dict[str, Callable] = {}
        self.node_counter = 0
        
        FunctionFlowRegistry._initialized = True
        self.logger.log("FunctionFlowRegistry initialized", level="INFO")
    
    def register_function_flow(self,
                               function: Callable,
                               flow_id: Optional[str] = None,
                               dependencies: Optional[List[str]] = None) -> str:
        """
        Register a function for flow tracking.
        
        Args:
            function: Function to register
            flow_id: Optional flow identifier
            dependencies: List of function names this depends on
            
        Returns:
            Flow ID
        """
        if flow_id is None:
            flow_id = f"flow_{function.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Wrap function with logging
        @functools.wraps(function)
        def wrapped(*args, **kwargs):
            return self._execute_with_logging(function, flow_id, dependencies, *args, **kwargs)
        
        self.function_registry[function.__name__] = wrapped
        
        if flow_id not in self.flows:
            self.flows[flow_id] = []
        
        self.logger.log(f"Function flow registered: {flow_id} - {function.__name__}", level="INFO")
        
        return flow_id
    
    def _execute_with_logging(self,
                              function: Callable,
                              flow_id: str,
                              dependencies: Optional[List[str]],
                              *args,
                              **kwargs) -> Any:
        """Execute function with automatic logging."""
        import time
        
        self.node_counter += 1
        node_id = f"{flow_id}_node_{self.node_counter}"
        
        # Find parent nodes (from dependencies)
        parent_nodes = []
        if dependencies:
            for dep in dependencies:
                # Find most recent node for this dependency
                for flow_nodes in self.flows.values():
                    for node in reversed(flow_nodes):
                        if node.function_name == dep:
                            parent_nodes.append(node.node_id)
                            break
        
        # Create node
        node = FunctionFlowNode(
            node_id=node_id,
            function_name=function.__name__,
            input_data={'args': str(args)[:100], 'kwargs': str(kwargs)[:100]},
            parent_nodes=parent_nodes
        )
        
        # Execute function
        start_time = time.time()
        try:
            output = function(*args, **kwargs)
            node.output_data = str(output)[:200] if output else None
            node.metadata['success'] = True
        except Exception as e:
            node.output_data = f"Error: {str(e)}"
            node.metadata['success'] = False
            node.metadata['error'] = str(e)
            raise
        finally:
            node.execution_time = time.time() - start_time
            node.timestamp = datetime.now()
            
            # Store node
            self.nodes[node_id] = node
            self.flows[flow_id].append(node)
            
            # Update parent-child relationships
            for parent_id in parent_nodes:
                if parent_id in self.nodes:
                    if node_id not in self.nodes[parent_id].child_nodes:
                        self.nodes[parent_id].child_nodes.append(node_id)
            
            # Log node
            self.log_node(node)
        
        return output
    
    def log_node(self, node: FunctionFlowNode) -> None:
        """
        Log a function flow node.
        
        Args:
            node: Node to log
        """
        self.logger.log(
            f"Function flow node: {node.node_id} - {node.function_name} "
            f"({node.execution_time:.4f}s, success={node.metadata.get('success', False)})",
            level="DEBUG"
        )
    
    def get_flow_trace(self, flow_id: str) -> List[FunctionFlowNode]:
        """Get complete trace for a flow."""
        return self.flows.get(flow_id, [])
    
    def get_execution_graph(self, flow_id: str) -> Dict[str, Any]:
        """
        Get execution graph for a flow.
        
        Returns:
            Graph structure with nodes and edges
        """
        nodes = self.flows.get(flow_id, [])
        
        graph = {
            'nodes': [
                {
                    'id': node.node_id,
                    'function': node.function_name,
                    'execution_time': node.execution_time,
                    'success': node.metadata.get('success', False)
                }
                for node in nodes
            ],
            'edges': [
                {
                    'from': parent_id,
                    'to': node.node_id
                }
                for node in nodes
                for parent_id in node.parent_nodes
            ]
        }
        
        return graph
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        total_nodes = len(self.nodes)
        total_flows = len(self.flows)
        
        # Average execution time
        execution_times = [node.execution_time for node in self.nodes.values()]
        avg_time = sum(execution_times) / len(execution_times) if execution_times else 0.0
        
        # Success rate
        successful = sum(1 for node in self.nodes.values() if node.metadata.get('success', False))
        success_rate = successful / total_nodes if total_nodes > 0 else 0.0
        
        return {
            'total_nodes': total_nodes,
            'total_flows': total_flows,
            'avg_execution_time': avg_time,
            'success_rate': success_rate
        }

