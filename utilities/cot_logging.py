# utilities/
"""
Chain-of-Thought (CoT) logging system.

First Principle Analysis:
- CoT logging tracks reasoning steps: S = {s_1, s_2, ..., s_n}
- Each step: s_i = (action, input, output, reasoning, timestamp)
- Decision tree: T = (nodes, edges) where nodes = decisions, edges = outcomes
- Mathematical foundation: Decision trees, information theory, traceability
- Architecture: Hierarchical logging with validation checkpoints
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loggers.system_logger import SystemLogger


class LogLevel(Enum):
    """Log levels for CoT steps."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DECISION = "DECISION"
    VALIDATION = "VALIDATION"


@dataclass
class CoTStep:
    """A single step in the chain of thought."""
    step_id: str
    action: str
    input_data: Any = None
    output_data: Any = None
    reasoning: str = ""
    level: LogLevel = LogLevel.INFO
    timestamp: datetime = field(default_factory=datetime.now)
    parent_step_id: Optional[str] = None
    child_step_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    validation_passed: Optional[bool] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['level'] = self.level.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


class ChainOfThoughtLogger:
    """
    Comprehensive chain-of-thought logging system.

    Features:
    - Step-by-step reasoning logs
    - Decision trees
    - Validation checkpoints
    - Performance tracking
    - Hierarchical structure (parent-child relationships)
    """

    _global_sinks: List[Any] = []

    @classmethod
    def register_sink(cls, sink_fn: Any) -> None:
        """Register a callback to receive step entries when end_step is called."""
        if sink_fn not in cls._global_sinks:
            cls._global_sinks.append(sink_fn)

    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize CoT logger.
        
        Args:
            session_id: Optional session identifier
        """
        self.logger = SystemLogger()
        self.session_id = session_id or f"cot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.steps: Dict[str, CoTStep] = {}
        self.root_steps: List[str] = []  # Steps with no parent
        self.current_step_id: Optional[str] = None
        self.step_counter = 0
        
        self.logger.log(f"ChainOfThoughtLogger initialized: {self.session_id}", level="INFO")
    
    def start_step(self,
                   action: str,
                   input_data: Any = None,
                   reasoning: str = "",
                   level: LogLevel = LogLevel.INFO,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Start a new CoT step.
        
        Args:
            action: Action description
            input_data: Input data for this step
            reasoning: Reasoning for this step
            level: Log level
            metadata: Additional metadata
            
        Returns:
            Step ID
        """
        self.step_counter += 1
        step_id = f"{self.session_id}_step_{self.step_counter}"
        
        parent_id = self.current_step_id
        
        step = CoTStep(
            step_id=step_id,
            action=action,
            input_data=input_data,
            reasoning=reasoning,
            level=level,
            parent_step_id=parent_id,
            metadata=metadata or {}
        )
        
        self.steps[step_id] = step
        
        # Update parent-child relationships
        if parent_id:
            if parent_id in self.steps:
                self.steps[parent_id].child_step_ids.append(step_id)
        else:
            self.root_steps.append(step_id)
        
        self.current_step_id = step_id
        
        self.logger.log(f"CoT step started: {step_id} - {action}", level="DEBUG")
        
        return step_id
    
    def end_step(self,
                 step_id: Optional[str] = None,
                 output_data: Any = None,
                 reasoning: str = "",
                 validation_passed: Optional[bool] = None,
                 performance_metrics: Optional[Dict[str, Any]] = None) -> None:
        """
        End a CoT step.
        
        Args:
            step_id: Step ID (if None, uses current step)
            output_data: Output data
            reasoning: Additional reasoning
            validation_passed: Validation result
            performance_metrics: Performance metrics
        """
        if step_id is None:
            step_id = self.current_step_id
        
        if step_id not in self.steps:
            self.logger.log(f"Step not found: {step_id}", level="WARNING")
            return
        
        step = self.steps[step_id]
        step.output_data = output_data
        
        if reasoning:
            step.reasoning += f"\n{reasoning}"
        
        if validation_passed is not None:
            step.validation_passed = validation_passed
        
        if performance_metrics:
            step.performance_metrics.update(performance_metrics)
        
        # Move to parent step
        if step.parent_step_id:
            self.current_step_id = step.parent_step_id
        else:
            self.current_step_id = None

        # Push to global sinks (e.g. API log buffer)
        for sink in ChainOfThoughtLogger._global_sinks:
            try:
                entry = {
                    "type": "cot_step",
                    "action": step.action,
                    "message": step.action,
                    "timestamp": step.timestamp.isoformat(),
                    "step_id": step_id,
                    "validation_passed": step.validation_passed,
                }
                if step.output_data is not None:
                    entry["output"] = str(step.output_data)[:200]
                sink(entry)
            except Exception:
                pass

        self.logger.log(f"CoT step ended: {step_id}", level="DEBUG")
    
    def log_decision(self,
                     decision: str,
                     options: List[str],
                     chosen_option: str,
                     reasoning: str,
                     input_data: Any = None) -> str:
        """
        Log a decision point.
        
        Args:
            decision: Decision description
            options: Available options
            chosen_option: Chosen option
            reasoning: Reasoning for choice
            input_data: Input data
            
        Returns:
            Step ID
        """
        step_id = self.start_step(
            action=f"DECISION: {decision}",
            input_data={
                'input': input_data,
                'options': options,
                'chosen': chosen_option
            },
            reasoning=reasoning,
            level=LogLevel.DECISION
        )
        
        self.end_step(step_id, output_data={'chosen_option': chosen_option})
        
        return step_id
    
    def log_validation(self,
                       validation_name: str,
                       input_data: Any,
                       validation_result: bool,
                       details: str = "") -> str:
        """
        Log a validation checkpoint.
        
        Args:
            validation_name: Validation name
            input_data: Input data being validated
            validation_result: Validation result
            details: Additional details
            
        Returns:
            Step ID
        """
        step_id = self.start_step(
            action=f"VALIDATION: {validation_name}",
            input_data=input_data,
            reasoning=details,
            level=LogLevel.VALIDATION
        )
        
        self.end_step(
            step_id,
            output_data={'result': validation_result},
            validation_passed=validation_result
        )
        
        return step_id
    
    def log_performance(self,
                        operation: str,
                        metrics: Dict[str, Any],
                        input_data: Any = None) -> str:
        """
        Log performance metrics.
        
        Args:
            operation: Operation name
            metrics: Performance metrics
            input_data: Input data
            
        Returns:
            Step ID
        """
        step_id = self.start_step(
            action=f"PERFORMANCE: {operation}",
            input_data=input_data,
            level=LogLevel.INFO
        )
        
        self.end_step(step_id, performance_metrics=metrics)
        
        return step_id
    
    def get_step(self, step_id: str) -> Optional[CoTStep]:
        """Get a step by ID."""
        return self.steps.get(step_id)
    
    def get_step_tree(self, step_id: str) -> Dict[str, Any]:
        """
        Get step and all descendants as a tree.
        
        Args:
            step_id: Root step ID
            
        Returns:
            Tree structure
        """
        if step_id not in self.steps:
            return {}
        
        step = self.steps[step_id]
        tree = step.to_dict()
        
        # Add children recursively
        tree['children'] = [
            self.get_step_tree(child_id)
            for child_id in step.child_step_ids
        ]
        
        return tree
    
    def get_full_tree(self) -> Dict[str, Any]:
        """Get complete CoT tree starting from root steps."""
        return {
            'session_id': self.session_id,
            'roots': [self.get_step_tree(root_id) for root_id in self.root_steps],
            'statistics': self.get_statistics()
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get logging statistics."""
        total_steps = len(self.steps)
        decision_steps = sum(1 for s in self.steps.values() if s.level == LogLevel.DECISION)
        validation_steps = sum(1 for s in self.steps.values() if s.level == LogLevel.VALIDATION)
        
        passed_validations = sum(
            1 for s in self.steps.values()
            if s.validation_passed is True
        )
        failed_validations = sum(
            1 for s in self.steps.values()
            if s.validation_passed is False
        )
        
        return {
            'total_steps': total_steps,
            'decision_steps': decision_steps,
            'validation_steps': validation_steps,
            'passed_validations': passed_validations,
            'failed_validations': failed_validations,
            'root_steps': len(self.root_steps)
        }
    
    def export_json(self, filepath: str) -> None:
        """Export CoT log to JSON file."""
        tree = self.get_full_tree()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(tree, f, indent=2, default=str)
        
        self.logger.log(f"CoT log exported to {filepath}", level="INFO")
    
    def get_decision_path(self, step_id: str) -> List[CoTStep]:
        """
        Get path from root to step (decision path).
        
        Args:
            step_id: Target step ID
            
        Returns:
            List of steps from root to target
        """
        path = []
        current_id = step_id
        
        while current_id:
            if current_id in self.steps:
                step = self.steps[current_id]
                path.insert(0, step)
                current_id = step.parent_step_id
            else:
                break
        
        return path
    
    def filter_steps(self,
                     level: Optional[LogLevel] = None,
                     action_pattern: Optional[str] = None,
                     validation_passed: Optional[bool] = None) -> List[CoTStep]:
        """
        Filter steps by criteria.
        
        Args:
            level: Filter by log level
            action_pattern: Filter by action pattern
            validation_passed: Filter by validation result
            
        Returns:
            List of matching steps
        """
        filtered = []
        
        for step in self.steps.values():
            if level and step.level != level:
                continue
            if action_pattern and action_pattern.lower() not in step.action.lower():
                continue
            if validation_passed is not None and step.validation_passed != validation_passed:
                continue
            
            filtered.append(step)
        
        return filtered

