# utilities/
"""
State Graph for Time-State Transitions and Scenario Testing.

Inspired by DREAM architecture Section 1.3 - branching possibilities and state graphs.

First Principle Analysis:
- State graph: G = (S, T) where S = states, T = transitions
- Transitions: t = (s_i, s_j, condition, action)
- Scenario testing: Explore multiple paths through state space
- Mathematical foundation: Graph theory, state machines, path finding
- Architecture: Graph-based state exploration with constraint checking
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel


class TransitionType(Enum):
    """Types of state transitions."""
    DETERMINISTIC = "deterministic"
    PROBABILISTIC = "probabilistic"
    CONDITIONAL = "conditional"
    TEMPORAL = "temporal"


@dataclass
class State:
    """Represents a state in the state graph."""
    state_id: str
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Transition:
    """Represents a transition between states."""
    from_state: str
    to_state: str
    condition: Callable[[Dict[str, Any]], bool]
    action: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None
    transition_type: TransitionType = TransitionType.CONDITIONAL
    probability: float = 1.0
    cost: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class StateGraph:
    """
    State graph for tracking transitions and scenario testing.
    
    Features:
    - State representation
    - Transition tracking
    - Path finding
    - Scenario exploration
    - Constraint validation
    """
    
    def __init__(self):
        """Initialize state graph."""
        self.logger = SystemLogger()
        self.states: Dict[str, State] = {}
        self.transitions: Dict[str, List[Transition]] = {}  # from_state -> list of transitions
        self.reverse_transitions: Dict[str, List[Transition]] = {}  # to_state -> list of transitions
        self.current_state: Optional[str] = None
        self.history: List[Tuple[str, str, datetime]] = []  # (from_state, to_state, timestamp)
        
        self.logger.log("StateGraph initialized", level="INFO")
    
    def add_state(self, state: State) -> None:
        """Add a state to the graph."""
        self.states[state.state_id] = state
        if state.state_id not in self.transitions:
            self.transitions[state.state_id] = []
        if state.state_id not in self.reverse_transitions:
            self.reverse_transitions[state.state_id] = []
        
        self.logger.log(f"State added: {state.state_id}", level="DEBUG")
    
    def add_transition(self, transition: Transition) -> None:
        """Add a transition to the graph."""
        if transition.from_state not in self.transitions:
            self.transitions[transition.from_state] = []
        if transition.to_state not in self.reverse_transitions:
            self.reverse_transitions[transition.to_state] = []
        
        self.transitions[transition.from_state].append(transition)
        self.reverse_transitions[transition.to_state].append(transition)
        
        self.logger.log(
            f"Transition added: {transition.from_state} -> {transition.to_state}",
            level="DEBUG"
        )
    
    def get_state(self, state_id: str) -> Optional[State]:
        """Get state by ID."""
        return self.states.get(state_id)
    
    def get_transitions_from(self, state_id: str) -> List[Transition]:
        """Get all transitions from a state."""
        return self.transitions.get(state_id, [])
    
    def get_transitions_to(self, state_id: str) -> List[Transition]:
        """Get all transitions to a state."""
        return self.reverse_transitions.get(state_id, [])
    
    def find_paths(self,
                   from_state: str,
                   to_state: str,
                   max_depth: int = 10,
                   context: Optional[Dict[str, Any]] = None) -> List[List[str]]:
        """
        Find all paths from one state to another.
        
        Mathematical: Path finding in graph G = (S, T)
        
        Args:
            from_state: Starting state
            to_state: Target state
            max_depth: Maximum path length
            context: Context for condition evaluation
            
        Returns:
            List of paths (each path is a list of state IDs)
        """
        if from_state not in self.states or to_state not in self.states:
            return []
        
        paths = []
        visited = set()
        
        def dfs(current: str, path: List[str], depth: int):
            if depth > max_depth:
                return
            
            if current == to_state:
                paths.append(path.copy())
                return
            
            visited.add(current)
            
            for transition in self.get_transitions_from(current):
                if transition.to_state not in visited:
                    # Check condition
                    if context is None or transition.condition(context):
                        path.append(transition.to_state)
                        dfs(transition.to_state, path, depth + 1)
                        path.pop()
            
            visited.remove(current)
        
        dfs(from_state, [from_state], 0)
        
        self.logger.log(f"Found {len(paths)} paths from {from_state} to {to_state}", level="DEBUG")
        return paths
    
    def explore_scenarios(self,
                         initial_state: str,
                         target_properties: Dict[str, Any],
                         max_steps: int = 10,
                         context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Explore scenarios to reach target properties.
        
        Args:
            initial_state: Starting state
            target_properties: Desired properties
            max_steps: Maximum exploration steps
            context: Context for transitions
            
        Returns:
            List of scenario paths
        """
        scenarios = []
        
        def explore(current_state: str, path: List[str], step: int, properties: Dict[str, Any]):
            if step >= max_steps:
                return
            
            # Check if target properties reached
            if self._properties_match(properties, target_properties):
                scenarios.append({
                    'path': path.copy(),
                    'final_state': current_state,
                    'properties': properties.copy()
                })
                return
            
            # Explore transitions
            for transition in self.get_transitions_from(current_state):
                if context is None or transition.condition(context):
                    new_properties = properties.copy()
                    
                    # Apply transition action if available
                    if transition.action:
                        new_properties = transition.action(new_properties)
                    
                    new_path = path + [transition.to_state]
                    explore(transition.to_state, new_path, step + 1, new_properties)
        
        initial_properties = self.states[initial_state].properties.copy() if initial_state in self.states else {}
        explore(initial_state, [initial_state], 0, initial_properties)
        
        self.logger.log(f"Explored {len(scenarios)} scenarios", level="INFO")
        return scenarios
    
    def _properties_match(self, properties: Dict[str, Any], target: Dict[str, Any]) -> bool:
        """Check if properties match target."""
        for key, value in target.items():
            if key not in properties:
                return False
            if properties[key] != value:
                return False
        return True
    
    def transition(self,
                   from_state: str,
                   to_state: str,
                   context: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Execute a state transition.
        
        Args:
            from_state: Current state
            to_state: Target state
            context: Transition context
            
        Returns:
            Tuple of (success, new_context)
        """
        transitions = self.get_transitions_from(from_state)
        
        for transition in transitions:
            if transition.to_state == to_state:
                if transition.condition(context):
                    # Execute action if available
                    new_context = context.copy()
                    if transition.action:
                        new_context = transition.action(new_context)
                    
                    # Record transition
                    self.history.append((from_state, to_state, datetime.now()))
                    self.current_state = to_state
                    
                    self.logger.log(
                        f"Transition executed: {from_state} -> {to_state}",
                        level="INFO"
                    )
                    
                    return True, new_context
        
        self.logger.log(f"Transition failed: {from_state} -> {to_state}", level="WARNING")
        return False, None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics."""
        num_states = len(self.states)
        num_transitions = sum(len(trans) for trans in self.transitions.values())
        
        # Average transitions per state
        avg_transitions = num_transitions / num_states if num_states > 0 else 0.0
        
        # States with most transitions
        max_transitions = 0
        max_state = None
        for state_id, trans in self.transitions.items():
            if len(trans) > max_transitions:
                max_transitions = len(trans)
                max_state = state_id
        
        return {
            'num_states': num_states,
            'num_transitions': num_transitions,
            'avg_transitions': avg_transitions,
            'max_transitions': max_transitions,
            'max_transitions_state': max_state,
            'history_length': len(self.history)
        }

