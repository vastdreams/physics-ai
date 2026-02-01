# utilities/
"""
Enhanced layer registry with dependency tracking and versioning.

First Principle Analysis:
- Function registry: R = {(name, func, deps, version, metadata)}
- Dependency graph: D = {(func_i, func_j) | func_i depends on func_j}
- Version tracking: V(func) = (major, minor, patch)
- Mathematical foundation: Graph theory, version control systems
- Architecture: Global registry with automatic dependency resolution
"""

from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loggers.system_logger import SystemLogger


@dataclass
class FunctionMetadata:
    """Metadata for a registered function."""
    name: str
    function: Callable
    dependencies: Set[str] = field(default_factory=set)
    version: str = "1.0.0"
    description: str = ""
    tags: Set[str] = field(default_factory=set)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    usage_count: int = 0


class EnhancedRegistry:
    """
    Enhanced layer registry for physics simulation functions.
    
    Features:
    - Function registration with dependencies
    - Automatic dependency resolution
    - Version tracking
    - Performance metrics
    - Dependency graph analysis
    """
    
    _instance: Optional['EnhancedRegistry'] = None
    _initialized: bool = False
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize registry (only once)."""
        if EnhancedRegistry._initialized:
            return
        
        self.logger = SystemLogger()
        self.functions: Dict[str, FunctionMetadata] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.reverse_dependency_graph: Dict[str, Set[str]] = {}
        
        EnhancedRegistry._initialized = True
        self.logger.log("EnhancedRegistry initialized", level="INFO")
    
    def register(self,
                 name: str,
                 function: Callable,
                 dependencies: Optional[List[str]] = None,
                 version: str = "1.0.0",
                 description: str = "",
                 tags: Optional[List[str]] = None) -> bool:
        """
        Register a function with metadata.
        
        Args:
            name: Function name (must be unique)
            function: Function to register
            dependencies: List of function names this depends on
            version: Version string (semantic versioning)
            description: Function description
            tags: List of tags for categorization
            
        Returns:
            True if registered successfully, False otherwise
        """
        if name in self.functions:
            self.logger.log(f"Function already registered: {name}", level="WARNING")
            return False
        
        # Validate dependencies exist
        deps_set = set(dependencies or [])
        for dep in deps_set:
            if dep not in self.functions:
                self.logger.log(f"Dependency not found: {dep} for {name}", level="WARNING")
                # Allow registration but warn
        
        # Create metadata
        metadata = FunctionMetadata(
            name=name,
            function=function,
            dependencies=deps_set,
            version=version,
            description=description,
            tags=set(tags or [])
        )
        
        # Register function
        self.functions[name] = metadata
        
        # Update dependency graphs
        self.dependency_graph[name] = deps_set.copy()
        for dep in deps_set:
            if dep not in self.reverse_dependency_graph:
                self.reverse_dependency_graph[dep] = set()
            self.reverse_dependency_graph[dep].add(name)
        
        self.logger.log(f"Function registered: {name} (v{version}, deps={len(deps_set)})", level="INFO")
        return True
    
    def get(self, name: str) -> Optional[Callable]:
        """
        Get function by name.
        
        Args:
            name: Function name
            
        Returns:
            Function if found, None otherwise
        """
        if name not in self.functions:
            self.logger.log(f"Function not found: {name}", level="WARNING")
            return None
        
        # Update usage statistics
        metadata = self.functions[name]
        metadata.last_used = datetime.now()
        metadata.usage_count += 1
        
        return metadata.function
    
    def get_metadata(self, name: str) -> Optional[FunctionMetadata]:
        """Get function metadata."""
        return self.functions.get(name)
    
    def get_dependencies(self, name: str, recursive: bool = False) -> Set[str]:
        """
        Get dependencies of a function.
        
        Args:
            name: Function name
            recursive: If True, return transitive dependencies
            
        Returns:
            Set of dependency names
        """
        if name not in self.functions:
            return set()
        
        deps = self.dependency_graph.get(name, set()).copy()
        
        if recursive:
            # Get transitive dependencies
            all_deps = deps.copy()
            visited = {name}
            
            def collect_deps(func_name: str):
                if func_name in visited:
                    return
                visited.add(func_name)
                
                func_deps = self.dependency_graph.get(func_name, set())
                all_deps.update(func_deps)
                
                for dep in func_deps:
                    collect_deps(dep)
            
            for dep in deps:
                collect_deps(dep)
            
            return all_deps
        
        return deps
    
    def get_dependents(self, name: str) -> Set[str]:
        """Get functions that depend on this function."""
        return self.reverse_dependency_graph.get(name, set()).copy()
    
    def resolve_execution_order(self, function_names: List[str]) -> List[str]:
        """
        Resolve execution order based on dependencies.
        
        Mathematical: Topological sort of dependency graph
        
        Args:
            function_names: List of function names to execute
            
        Returns:
            List of function names in execution order
        """
        # Build subgraph for requested functions
        subgraph: Dict[str, Set[str]] = {}
        for name in function_names:
            if name in self.functions:
                subgraph[name] = self.dependency_graph.get(name, set()).intersection(set(function_names))
        
        # Topological sort (Kahn's algorithm)
        in_degree = {name: 0 for name in function_names if name in self.functions}
        
        for name, deps in subgraph.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[dep] += 1
        
        queue = [name for name, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            name = queue.pop(0)
            result.append(name)
            
            for dep in subgraph.get(name, set()):
                if dep in in_degree:
                    in_degree[dep] -= 1
                    if in_degree[dep] == 0:
                        queue.append(dep)
        
        # Add any remaining functions (cycles or missing deps)
        remaining = set(function_names) - set(result)
        result.extend(remaining)
        
        return result
    
    def update_performance(self, name: str, metrics: Dict[str, Any]) -> None:
        """
        Update performance metrics for a function.
        
        Args:
            name: Function name
            metrics: Performance metrics dictionary
        """
        if name not in self.functions:
            self.logger.log(f"Function not found: {name}", level="WARNING")
            return
        
        self.functions[name].performance_metrics.update(metrics)
        self.logger.log(f"Performance updated for {name}: {metrics}", level="DEBUG")
    
    def search_by_tag(self, tag: str) -> List[str]:
        """Find functions by tag."""
        return [name for name, metadata in self.functions.items() if tag in metadata.tags]
    
    def search_by_name(self, pattern: str) -> List[str]:
        """Find functions by name pattern."""
        return [name for name in self.functions.keys() if pattern.lower() in name.lower()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        num_functions = len(self.functions)
        total_deps = sum(len(deps) for deps in self.dependency_graph.values())
        
        # Average dependencies
        avg_deps = total_deps / num_functions if num_functions > 0 else 0.0
        
        # Most used functions
        most_used = sorted(
            self.functions.items(),
            key=lambda x: x[1].usage_count,
            reverse=True
        )[:10]
        
        # Functions by tag
        tag_counts: Dict[str, int] = {}
        for metadata in self.functions.values():
            for tag in metadata.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        return {
            'num_functions': num_functions,
            'total_dependencies': total_deps,
            'avg_dependencies': avg_deps,
            'most_used': [(name, meta.usage_count) for name, meta in most_used],
            'tag_counts': tag_counts
        }
    
    def list_all(self) -> List[str]:
        """List all registered function names."""
        return list(self.functions.keys())
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a function.
        
        Args:
            name: Function name
            
        Returns:
            True if unregistered, False if not found
        """
        if name not in self.functions:
            return False
        
        # Remove from dependency graphs
        deps = self.dependency_graph.pop(name, set())
        for dep in deps:
            if dep in self.reverse_dependency_graph:
                self.reverse_dependency_graph[dep].discard(name)
        
        if name in self.reverse_dependency_graph:
            dependents = self.reverse_dependency_graph.pop(name, set())
            for dependent in dependents:
                if dependent in self.dependency_graph:
                    self.dependency_graph[dependent].discard(name)
        
        # Remove function
        del self.functions[name]
        
        self.logger.log(f"Function unregistered: {name}", level="INFO")
        return True

