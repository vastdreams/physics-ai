# PATH: substrate/memory/reasoning_trace.py
# PURPOSE:
#   - Hot memory for per-query reasoning
#   - Tracks every step of the AI's thinking process
#   - Enables auditing, debugging, and evolution
#
# ROLE IN ARCHITECTURE:
#   - Captures the chain-of-thought for each problem
#   - Fed to critics for analysis
#   - May be distilled into cold memory (FormulaGraph)
#
# MAIN EXPORTS:
#   - ReasoningTrace: Complete trace for a problem
#   - TraceStep: Single step in reasoning
#   - TraceStepType: Types of reasoning steps
#
# NON-RESPONSIBILITIES:
#   - Does NOT execute reasoning (that's the executor)
#   - Does NOT modify the graph (that's evolution)
#
# NOTES FOR FUTURE AI:
#   - Every decision must be recorded in the trace
#   - Traces are the raw material for self-evolution
#   - Include both successes and failures

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Union
from datetime import datetime
from enum import Enum, auto
import json
import uuid


class TraceStepType(Enum):
    """Types of steps in a reasoning trace."""
    
    # Problem understanding
    PROBLEM_RECEIVED = auto()       # Initial problem statement
    PROBLEM_PARSED = auto()         # Parsed into structured form
    CONTEXT_IDENTIFIED = auto()     # Domain/scale/regime identified
    
    # Planning
    PLAN_STARTED = auto()           # Planning phase began
    FORMULA_CONSIDERED = auto()     # A formula was considered
    FORMULA_REJECTED = auto()       # A formula was rejected (with reason)
    FORMULA_SELECTED = auto()       # A formula was selected
    PLAN_GENERATED = auto()         # Complete plan generated
    PLAN_VALIDATED = auto()         # Plan passed validation
    PLAN_INVALID = auto()           # Plan failed validation
    
    # Execution
    EXECUTION_STARTED = auto()      # Execution phase began
    STEP_EXECUTED = auto()          # A plan step was executed
    STEP_FAILED = auto()            # A plan step failed
    INTERMEDIATE_RESULT = auto()    # Intermediate computation result
    
    # Validation
    VALIDATION_STARTED = auto()     # Validation phase began
    CONSERVATION_CHECK = auto()     # Conservation law check
    DIMENSIONAL_CHECK = auto()      # Dimensional analysis
    LIMIT_CHECK = auto()            # Known limit check
    VALIDATION_PASSED = auto()      # All validations passed
    VALIDATION_FAILED = auto()      # Validation failed
    
    # Output
    RESULT_COMPUTED = auto()        # Final result computed
    EXPLANATION_GENERATED = auto()  # Natural language explanation
    
    # Critic feedback
    CRITIC_ANALYSIS = auto()        # Critic analyzed this trace
    CRITIC_ISSUE_FOUND = auto()     # Critic found an issue
    CRITIC_APPROVED = auto()        # Critic approved
    
    # Meta
    ERROR = auto()                  # An error occurred
    WARNING = auto()                # A warning was generated
    DEBUG = auto()                  # Debug information


@dataclass
class TraceStep:
    """A single step in a reasoning trace."""
    
    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    
    # What happened
    step_type: TraceStepType = TraceStepType.DEBUG
    description: str = ""
    
    # Data at this step
    data: Dict[str, Any] = field(default_factory=dict)
    
    # If formula-related
    formula_id: Optional[str] = None
    formula_name: Optional[str] = None
    
    # If computation-related
    inputs: Optional[Dict[str, Any]] = None
    outputs: Optional[Dict[str, Any]] = None
    
    # Assessment
    confidence: float = 1.0
    success: bool = True
    error_message: Optional[str] = None
    
    # Timing
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "step_type": self.step_type.name,
            "description": self.description,
            "data": self.data,
            "formula_id": self.formula_id,
            "formula_name": self.formula_name,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "confidence": self.confidence,
            "success": self.success,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
        }
    
    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> TraceStep:
        d = d.copy()
        d["step_type"] = TraceStepType[d["step_type"]]
        d["timestamp"] = datetime.fromisoformat(d["timestamp"]) if d.get("timestamp") else datetime.now()
        return cls(**d)


@dataclass
class CriticAnnotation:
    """Annotation added by a critic to a trace."""
    
    critic_id: str              # Which critic made this annotation
    critic_type: str            # "logic", "code", "meta"
    
    # What was analyzed
    step_ids: List[str]         # Which steps this relates to
    
    # The critique
    issue_type: Optional[str] = None    # "error", "inefficiency", "inconsistency", etc.
    severity: str = "info"              # "info", "warning", "error", "critical"
    message: str = ""
    
    # Suggestions
    suggestion: Optional[str] = None
    suggested_fix: Optional[Dict[str, Any]] = None
    
    # Assessment
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "critic_id": self.critic_id,
            "critic_type": self.critic_type,
            "step_ids": self.step_ids,
            "issue_type": self.issue_type,
            "severity": self.severity,
            "message": self.message,
            "suggestion": self.suggestion,
            "suggested_fix": self.suggested_fix,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ReasoningTrace:
    """
    Complete reasoning trace for a single problem.
    
    This is the "hot memory" - the per-episode state that captures
    everything the AI did while solving a problem. It includes:
    - The original problem
    - Every reasoning step
    - All intermediate results
    - Validation results
    - Critic annotations
    
    Traces are analyzed by critics and may be distilled into
    cold memory (new formulas, improved code) via evolution.
    """
    
    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # The problem
    problem: Dict[str, Any] = field(default_factory=dict)
    problem_text: str = ""
    
    # Context
    domain: str = "general"
    context: Dict[str, Any] = field(default_factory=dict)
    
    # The trace itself
    steps: List[TraceStep] = field(default_factory=list)
    
    # Results
    result: Optional[Dict[str, Any]] = None
    explanation: Optional[str] = None
    success: bool = False
    
    # Critic annotations
    annotations: List[CriticAnnotation] = field(default_factory=list)
    
    # Assessment
    overall_confidence: float = 1.0
    validation_passed: bool = False
    
    # Statistics
    total_formulas_used: int = 0
    total_steps: int = 0
    total_duration_ms: float = 0.0
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def add_step(
        self,
        step_type: TraceStepType,
        description: str,
        **kwargs
    ) -> TraceStep:
        """Add a step to the trace."""
        step = TraceStep(
            step_type=step_type,
            description=description,
            **kwargs
        )
        self.steps.append(step)
        self.total_steps += 1
        
        if step.duration_ms:
            self.total_duration_ms += step.duration_ms
        
        if step.formula_id:
            self.total_formulas_used += 1
        
        return step
    
    def add_annotation(self, annotation: CriticAnnotation):
        """Add a critic annotation."""
        self.annotations.append(annotation)
    
    def get_steps_by_type(self, step_type: TraceStepType) -> List[TraceStep]:
        """Get all steps of a specific type."""
        return [s for s in self.steps if s.step_type == step_type]
    
    def get_errors(self) -> List[TraceStep]:
        """Get all error steps."""
        return [s for s in self.steps if not s.success or s.step_type in {
            TraceStepType.ERROR,
            TraceStepType.STEP_FAILED,
            TraceStepType.PLAN_INVALID,
            TraceStepType.VALIDATION_FAILED,
        }]
    
    def get_formulas_used(self) -> List[str]:
        """Get list of formula IDs used in this trace."""
        return [s.formula_id for s in self.steps if s.formula_id]
    
    def get_issues(self) -> List[Dict[str, Any]]:
        """Get all issues (errors + critic annotations)."""
        issues = []
        
        # Errors from steps
        for step in self.get_errors():
            issues.append({
                "source": "execution",
                "step_id": step.id,
                "type": step.step_type.name,
                "message": step.error_message or step.description,
                "severity": "error",
            })
        
        # Critic annotations
        for ann in self.annotations:
            if ann.severity in {"warning", "error", "critical"}:
                issues.append({
                    "source": f"critic:{ann.critic_type}",
                    "step_ids": ann.step_ids,
                    "type": ann.issue_type,
                    "message": ann.message,
                    "severity": ann.severity,
                    "suggestion": ann.suggestion,
                })
        
        return issues
    
    def compute_overall_confidence(self) -> float:
        """Compute overall confidence from step confidences."""
        if not self.steps:
            return 0.0
        
        # Product of confidences (chain is as strong as weakest link)
        confidence = 1.0
        for step in self.steps:
            if step.success:
                confidence = min(confidence, step.confidence)
        
        # Penalize for errors
        error_count = len(self.get_errors())
        confidence *= (0.9 ** error_count)
        
        # Penalize for critic issues
        issue_counts = {"warning": 0, "error": 0, "critical": 0}
        for ann in self.annotations:
            if ann.severity in issue_counts:
                issue_counts[ann.severity] += 1
        
        confidence *= (0.95 ** issue_counts["warning"])
        confidence *= (0.8 ** issue_counts["error"])
        confidence *= (0.5 ** issue_counts["critical"])
        
        self.overall_confidence = max(0.0, min(1.0, confidence))
        return self.overall_confidence
    
    def complete(self, result: Optional[Dict[str, Any]] = None, success: bool = True):
        """Mark the trace as complete."""
        self.result = result
        self.success = success
        self.completed_at = datetime.now()
        self.compute_overall_confidence()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "problem": self.problem,
            "problem_text": self.problem_text,
            "domain": self.domain,
            "context": self.context,
            "steps": [s.to_dict() for s in self.steps],
            "result": self.result,
            "explanation": self.explanation,
            "success": self.success,
            "annotations": [a.to_dict() for a in self.annotations],
            "overall_confidence": self.overall_confidence,
            "validation_passed": self.validation_passed,
            "total_formulas_used": self.total_formulas_used,
            "total_steps": self.total_steps,
            "total_duration_ms": self.total_duration_ms,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
    
    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> ReasoningTrace:
        d = d.copy()
        d["steps"] = [TraceStep.from_dict(s) for s in d.get("steps", [])]
        d["created_at"] = datetime.fromisoformat(d["created_at"]) if d.get("created_at") else datetime.now()
        d["completed_at"] = datetime.fromisoformat(d["completed_at"]) if d.get("completed_at") else None
        # Note: annotations would need their own from_dict if we load them
        d["annotations"] = []
        return cls(**d)
    
    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)
    
    def summary(self) -> str:
        """Generate a human-readable summary."""
        lines = [
            f"=== Reasoning Trace {self.id[:8]} ===",
            f"Problem: {self.problem_text[:100]}..." if len(self.problem_text) > 100 else f"Problem: {self.problem_text}",
            f"Domain: {self.domain}",
            f"Success: {self.success}",
            f"Confidence: {self.overall_confidence:.2f}",
            f"Steps: {self.total_steps}",
            f"Formulas used: {self.total_formulas_used}",
            f"Duration: {self.total_duration_ms:.2f}ms",
        ]
        
        errors = self.get_errors()
        if errors:
            lines.append(f"Errors: {len(errors)}")
            for e in errors[:3]:  # Show first 3
                lines.append(f"  - {e.description}")
        
        issues = self.get_issues()
        if issues:
            lines.append(f"Issues: {len(issues)}")
            for i in issues[:3]:  # Show first 3
                lines.append(f"  - [{i['severity']}] {i['message']}")
        
        if self.result:
            lines.append(f"Result: {str(self.result)[:100]}...")
        
        return "\n".join(lines)


class TraceStore:
    """
    Storage for reasoning traces.
    
    Maintains a buffer of recent traces for analysis,
    and can distill important traces into reusable patterns
    that serve as "cold" memory snippets.
    """
    
    def __init__(self, max_buffer_size: int = 1000, max_patterns: int = 200):
        self._traces: Dict[str, ReasoningTrace] = {}
        self._buffer: List[str] = []  # Order by recency
        self._max_buffer_size = max_buffer_size
        self._patterns: List[Dict[str, Any]] = []
        self._max_patterns = max_patterns
    
    def store(self, trace: ReasoningTrace):
        """Store a trace."""
        self._traces[trace.id] = trace
        self._buffer.append(trace.id)
        
        # Evict old traces if buffer full
        while len(self._buffer) > self._max_buffer_size:
            old_id = self._buffer.pop(0)
            if old_id in self._traces:
                del self._traces[old_id]

        # Distill/promote high-quality traces into patterns (cold-ish memory)
        self._maybe_distill(trace)
    
    def get(self, trace_id: str) -> Optional[ReasoningTrace]:
        """Get a trace by ID."""
        return self._traces.get(trace_id)
    
    def get_recent(self, n: int = 10) -> List[ReasoningTrace]:
        """Get the n most recent traces."""
        recent_ids = self._buffer[-n:]
        return [self._traces[tid] for tid in reversed(recent_ids) if tid in self._traces]
    
    def get_failed(self) -> List[ReasoningTrace]:
        """Get all failed traces in buffer."""
        return [t for t in self._traces.values() if not t.success]
    
    def get_low_confidence(self, threshold: float = 0.5) -> List[ReasoningTrace]:
        """Get traces with confidence below threshold."""
        return [t for t in self._traces.values() if t.overall_confidence < threshold]
    
    def get_with_issues(self) -> List[ReasoningTrace]:
        """Get traces that have critic issues."""
        return [t for t in self._traces.values() if t.get_issues()]
    
    def get_patterns(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get distilled patterns (hot→cold promotions)."""
        return self._patterns[:limit]

    def statistics(self) -> Dict[str, Any]:
        """Get statistics about stored traces."""
        traces = list(self._traces.values())
        if not traces:
            return {"count": 0}
        
        successes = sum(1 for t in traces if t.success)
        confidences = [t.overall_confidence for t in traces]
        
        return {
            "count": len(traces),
            "success_rate": successes / len(traces),
            "avg_confidence": sum(confidences) / len(confidences),
            "min_confidence": min(confidences),
            "max_confidence": max(confidences),
            "traces_with_issues": len(self.get_with_issues()),
            "failed_traces": len(self.get_failed()),
            "patterns": len(self._patterns),
        }

    # ------------------------------------------------------------------
    # Distillation / promotion
    # ------------------------------------------------------------------
    def _maybe_distill(self, trace: ReasoningTrace):
        """Promote a high-quality trace into a distilled pattern."""
        # Criteria: success, reasonably high confidence
        if not trace.success:
            return
        confidence = trace.compute_overall_confidence()
        if confidence < 0.75:
            return

        pattern = self._distill_trace(trace, confidence)
        if pattern:
            self._patterns.insert(0, pattern)
            # Bound pattern storage
            if len(self._patterns) > self._max_patterns:
                self._patterns = self._patterns[: self._max_patterns]

    def _distill_trace(self, trace: ReasoningTrace, confidence: float) -> Optional[Dict[str, Any]]:
        """Create a compact pattern from a trace."""
        formulas_used = list(dict.fromkeys(trace.get_formulas_used()))
        assumptions = set()
        regimes = set()
        for step in trace.steps:
            step_assumptions = getattr(step, "assumptions_used", []) or []
            step_regimes = getattr(step, "regime_conditions", []) or []
            assumptions.update(step_assumptions)
            regimes.update(step_regimes)

        return {
            "pattern_id": f"pat_{trace.id[:8]}",
            "source_trace_id": trace.id,
            "domain": trace.domain,
            "confidence": confidence,
            "formulas_used": formulas_used,
            "assumptions": sorted(assumptions),
            "regimes": sorted(regimes),
            "summary": trace.summary(),
        }

