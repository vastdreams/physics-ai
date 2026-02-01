"""
PATH: substrate/skills/workflows.py
PURPOSE: Physics computation workflow engine inspired by OpenClaw's Lobster

WHY: Enables typed, composable pipelines for physics computations with
     approval gates for critical decisions (theory validation, experiment proposals).

REFERENCE: https://github.com/openclaw/lobster (MIT License)

FLOW:
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│ Define      │────>│ Execute      │────>│ Checkpoint &    │
│ Workflow    │     │ Steps        │     │ Approval Gates  │
└─────────────┘     └──────────────┘     └─────────────────┘

DEPENDENCIES:
- skill_registry: Skill execution
- dataclasses: Workflow definitions
"""

from typing import (
    Callable, Dict, List, Optional, Any, Union, TypeVar,
    Generic, Awaitable
)
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
import json
import logging
import uuid
import asyncio

logger = logging.getLogger(__name__)

T = TypeVar('T')


class StepStatus(Enum):
    """Workflow step status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalLevel(Enum):
    """Approval requirement levels."""
    NONE = "none"                    # No approval needed
    NOTIFY = "notify"                # Notify but continue
    SOFT = "soft"                    # Can be auto-approved after timeout
    REQUIRED = "required"            # Must be manually approved
    CRITICAL = "critical"            # Requires multiple approvers


@dataclass
class ApprovalGate:
    """
    Approval gate for critical workflow steps.
    
    Inspired by Lobster's approval mechanism for human-in-the-loop workflows.
    """
    level: ApprovalLevel
    reason: str
    
    # Auto-approval settings
    timeout_seconds: Optional[float] = None
    auto_approve_on_timeout: bool = False
    
    # Multi-approval settings
    required_approvers: int = 1
    approvers: List[str] = field(default_factory=list)
    
    # State
    approved: bool = False
    approved_by: List[str] = field(default_factory=list)
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    def approve(self, approver: str = "system") -> bool:
        """Approve this gate."""
        self.approved_by.append(approver)
        if len(self.approved_by) >= self.required_approvers:
            self.approved = True
            self.approved_at = datetime.now()
            return True
        return False
    
    def reject(self, reason: str, rejector: str = "system") -> None:
        """Reject this gate."""
        self.approved = False
        self.rejection_reason = f"{rejector}: {reason}"


@dataclass
class WorkflowStep:
    """
    A single step in a physics workflow.
    
    Steps can be:
    - Skill executions
    - Data transformations
    - Conditional branches
    - Approval gates
    """
    id: str
    name: str
    description: str
    
    # Execution
    skill_name: Optional[str] = None        # Name of skill to execute
    func: Optional[Callable] = None         # Or direct function
    args: Dict[str, Any] = field(default_factory=dict)
    
    # Input/output mapping
    input_from: Dict[str, str] = field(default_factory=dict)  # arg_name -> "$step_id.field"
    output_key: str = "result"
    
    # Control flow
    condition: Optional[str] = None         # Expression to evaluate
    on_failure: str = "fail"               # "fail", "skip", "retry"
    max_retries: int = 3
    
    # Approval
    approval: Optional[ApprovalGate] = None
    
    # State
    status: StepStatus = StepStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class WorkflowResult:
    """Result of workflow execution."""
    workflow_id: str
    workflow_name: str
    success: bool
    
    # Outputs
    final_result: Any = None
    step_results: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    total_time_ms: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Errors
    failed_step: Optional[str] = None
    error: Optional[str] = None
    
    # Provenance
    skills_used: List[str] = field(default_factory=list)
    equations_applied: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize result."""
        return {
            "workflow_id": self.workflow_id,
            "workflow_name": self.workflow_name,
            "success": self.success,
            "final_result": self.final_result,
            "step_results": self.step_results,
            "total_time_ms": self.total_time_ms,
            "failed_step": self.failed_step,
            "error": self.error,
            "skills_used": self.skills_used,
        }


@dataclass
class Workflow:
    """
    A composable physics computation workflow.
    
    Workflows chain skills together with data flow, conditions, and approval gates.
    
    Example:
        workflow = Workflow(
            name="analyze_spectrum",
            description="Analyze astronomical spectrum",
            steps=[
                WorkflowStep(id="load", skill_name="load_spectrum", args={"path": "$input.path"}),
                WorkflowStep(id="calibrate", skill_name="wavelength_calibration", 
                            input_from={"spectrum": "$load.result"}),
                WorkflowStep(id="analyze", skill_name="line_identification",
                            input_from={"calibrated": "$calibrate.result"},
                            approval=ApprovalGate(level=ApprovalLevel.SOFT, 
                                                 reason="Verify line identifications")),
            ]
        )
    """
    name: str
    description: str
    steps: List[WorkflowStep]
    
    # Metadata
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: str = "1.0.0"
    author: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    # Tags for discovery
    tags: List[str] = field(default_factory=list)
    domain: Optional[str] = None
    
    # Input/output schema
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    
    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """Get step by ID."""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None
    
    def to_yaml(self) -> str:
        """Export workflow as YAML (Lobster format)."""
        try:
            import yaml
            use_yaml = True
        except ImportError:
            use_yaml = False
        
        data = {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "steps": []
        }
        
        for step in self.steps:
            step_data = {
                "id": step.id,
                "name": step.name,
            }
            if step.skill_name:
                step_data["skill"] = step.skill_name
            if step.args:
                step_data["args"] = step.args
            if step.input_from:
                step_data["input_from"] = step.input_from
            if step.condition:
                step_data["condition"] = step.condition
            if step.approval:
                step_data["approval"] = step.approval.level.value
            
            data["steps"].append(step_data)
        
        if use_yaml:
            return yaml.dump(data, default_flow_style=False)
        else:
            # Fallback to JSON format
            return json.dumps(data, indent=2)


class WorkflowEngine:
    """
    Engine for executing physics workflows.
    
    Handles:
    - Step execution with dependency resolution
    - Data flow between steps
    - Approval gate management
    - Error handling and retry logic
    - Provenance tracking
    """
    
    def __init__(self, approval_handler: Optional[Callable[[ApprovalGate], bool]] = None):
        """
        Args:
            approval_handler: Function to handle approval gates
                             Returns True to approve, False to reject
        """
        self.approval_handler = approval_handler or self._default_approval_handler
        self._context: Dict[str, Any] = {}
        self._running_workflows: Dict[str, Workflow] = {}
    
    def _default_approval_handler(self, gate: ApprovalGate) -> bool:
        """Default approval handler - auto-approves SOFT, rejects REQUIRED."""
        if gate.level in [ApprovalLevel.NONE, ApprovalLevel.NOTIFY]:
            return True
        elif gate.level == ApprovalLevel.SOFT:
            logger.info(f"Auto-approving SOFT gate: {gate.reason}")
            return True
        else:
            logger.warning(f"REQUIRED approval gate needs manual intervention: {gate.reason}")
            return False
    
    def _resolve_reference(self, ref: str, context: Dict[str, Any]) -> Any:
        """
        Resolve a reference like "$step_id.field" or "$input.param".
        """
        if not ref.startswith("$"):
            return ref
        
        path = ref[1:].split(".")
        value = context
        
        for key in path:
            if isinstance(value, dict):
                value = value.get(key)
            elif hasattr(value, key):
                value = getattr(value, key)
            else:
                return None
        
        return value
    
    def _resolve_args(self, args: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve all references in arguments."""
        resolved = {}
        for key, value in args.items():
            if isinstance(value, str) and value.startswith("$"):
                resolved[key] = self._resolve_reference(value, context)
            elif isinstance(value, dict):
                resolved[key] = self._resolve_args(value, context)
            else:
                resolved[key] = value
        return resolved
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a condition expression."""
        if not condition:
            return True
        
        # Simple expression evaluation
        # Replace references with values
        expr = condition
        for match in set(s for s in condition.split() if s.startswith("$")):
            value = self._resolve_reference(match, context)
            if isinstance(value, bool):
                expr = expr.replace(match, str(value).lower())
            elif isinstance(value, (int, float)):
                expr = expr.replace(match, str(value))
            elif value is None:
                expr = expr.replace(match, "None")
            else:
                expr = expr.replace(match, f'"{value}"')
        
        try:
            return eval(expr, {"__builtins__": {}}, {})
        except Exception as e:
            logger.warning(f"Condition evaluation failed: {e}")
            return True
    
    def execute(
        self,
        workflow: Workflow,
        inputs: Dict[str, Any] = None,
    ) -> WorkflowResult:
        """
        Execute a workflow synchronously.
        
        Args:
            workflow: Workflow to execute
            inputs: Input parameters for the workflow
            
        Returns:
            WorkflowResult with outputs and provenance
        """
        import time
        
        start_time = time.perf_counter()
        inputs = inputs or {}
        
        # Initialize context
        context = {"input": inputs}
        skills_used = []
        
        result = WorkflowResult(
            workflow_id=workflow.id,
            workflow_name=workflow.name,
            success=False,
            started_at=datetime.now(),
        )
        
        self._running_workflows[workflow.id] = workflow
        
        try:
            for step in workflow.steps:
                step.started_at = datetime.now()
                step.status = StepStatus.RUNNING
                
                # Check condition
                if step.condition and not self._evaluate_condition(step.condition, context):
                    step.status = StepStatus.SKIPPED
                    logger.info(f"Skipping step {step.id}: condition not met")
                    continue
                
                # Handle approval gate
                if step.approval and step.approval.level != ApprovalLevel.NONE:
                    step.status = StepStatus.AWAITING_APPROVAL
                    
                    if not self.approval_handler(step.approval):
                        step.status = StepStatus.REJECTED
                        result.failed_step = step.id
                        result.error = f"Approval rejected: {step.approval.rejection_reason or 'No reason given'}"
                        return result
                    
                    step.approval.approve()
                    step.status = StepStatus.APPROVED
                
                # Resolve arguments
                resolved_args = self._resolve_args(step.args, context)
                
                # Add inputs from previous steps
                for arg_name, ref in step.input_from.items():
                    resolved_args[arg_name] = self._resolve_reference(ref, context)
                
                # Execute
                step_start = time.perf_counter()
                retry_count = 0
                
                while True:
                    try:
                        if step.skill_name:
                            # Execute skill - try multiple import strategies
                            skill = None
                            try:
                                from .skill_registry import get_registry
                                skill = get_registry().get(step.skill_name)
                            except ImportError:
                                # Try absolute import
                                try:
                                    from substrate.skills.skill_registry import get_registry
                                    skill = get_registry().get(step.skill_name)
                                except ImportError:
                                    pass
                            
                            if skill is None:
                                raise ValueError(f"Skill not found: {step.skill_name}")
                            
                            skill_result = skill(**resolved_args)
                            step.result = skill_result.value
                            skills_used.append(step.skill_name)
                            
                        elif step.func:
                            # Execute function directly
                            step.result = step.func(**resolved_args)
                        else:
                            # Pass-through step
                            step.result = resolved_args
                        
                        break  # Success
                        
                    except Exception as e:
                        retry_count += 1
                        if retry_count >= step.max_retries or step.on_failure == "fail":
                            raise
                        elif step.on_failure == "skip":
                            step.status = StepStatus.SKIPPED
                            break
                        # Retry
                        logger.warning(f"Step {step.id} failed, retrying ({retry_count}/{step.max_retries})")
                
                step.execution_time_ms = (time.perf_counter() - step_start) * 1000
                step.completed_at = datetime.now()
                step.status = StepStatus.COMPLETED
                
                # Store result in context
                context[step.id] = {step.output_key: step.result}
                result.step_results[step.id] = step.result
            
            # Success
            result.success = True
            result.final_result = workflow.steps[-1].result if workflow.steps else None
            result.skills_used = skills_used
            
        except Exception as e:
            logger.error(f"Workflow {workflow.name} failed: {e}")
            result.error = str(e)
            # Find failed step
            for step in workflow.steps:
                if step.status == StepStatus.RUNNING:
                    step.status = StepStatus.FAILED
                    step.error = str(e)
                    result.failed_step = step.id
                    break
        
        finally:
            result.completed_at = datetime.now()
            result.total_time_ms = (time.perf_counter() - start_time) * 1000
            del self._running_workflows[workflow.id]
        
        return result
    
    async def execute_async(
        self,
        workflow: Workflow,
        inputs: Dict[str, Any] = None,
    ) -> WorkflowResult:
        """Execute workflow asynchronously."""
        # For now, wrap sync execution
        # TODO: Implement true async execution with concurrent steps
        return await asyncio.to_thread(self.execute, workflow, inputs)


# ============================================================================
# PRE-BUILT PHYSICS WORKFLOWS
# ============================================================================

def create_quantum_analysis_workflow() -> Workflow:
    """Create workflow for analyzing quantum systems."""
    return Workflow(
        name="quantum_system_analysis",
        description="Analyze quantum system: solve eigenstates, compute observables, evolve in time",
        domain="quantum",
        tags=["quantum", "schrodinger", "dynamics"],
        steps=[
            WorkflowStep(
                id="solve_eigenstates",
                name="Solve Eigenstates",
                description="Solve time-independent Schrodinger equation",
                skill_name="solve_schrodinger",
                args={
                    "ndim": 1,
                    "grid_points": 256,
                    "n_states": 10,
                },
            ),
            WorkflowStep(
                id="analyze_spectrum",
                name="Analyze Energy Spectrum",
                description="Check energy level spacing and selection rules",
                func=lambda energies: {
                    "ground_state_energy": energies[0],
                    "level_spacings": [energies[i+1] - energies[i] for i in range(len(energies)-1)],
                    "is_harmonic": all(
                        abs(s - energies[1] + energies[0]) < 0.1 * (energies[1] - energies[0])
                        for s in [energies[i+1] - energies[i] for i in range(len(energies)-1)]
                    ) if len(energies) > 2 else False,
                },
                input_from={"energies": "$solve_eigenstates.result.energies"},
            ),
            WorkflowStep(
                id="validate_results",
                name="Validate Physical Consistency",
                description="Check that results are physically reasonable",
                approval=ApprovalGate(
                    level=ApprovalLevel.SOFT,
                    reason="Verify quantum solution is physically reasonable",
                    auto_approve_on_timeout=True,
                    timeout_seconds=30,
                ),
                func=lambda spectrum: {
                    "valid": spectrum["ground_state_energy"] > 0 if spectrum else False,
                    "spectrum": spectrum,
                },
                input_from={"spectrum": "$analyze_spectrum.result"},
            ),
        ],
    )


def create_cosmology_workflow() -> Workflow:
    """Create workflow for cosmological calculations."""
    return Workflow(
        name="cosmological_analysis",
        description="Calculate cosmological distances and properties for a target",
        domain="astrophysics",
        tags=["cosmology", "distance", "redshift"],
        steps=[
            WorkflowStep(
                id="calculate_distances",
                name="Calculate Distances",
                description="Compute cosmological distances",
                skill_name="cosmological_distance",
                args={"cosmology": "Planck18"},
            ),
            WorkflowStep(
                id="estimate_stellar_props",
                name="Estimate Host Properties",
                description="Estimate host galaxy stellar properties if applicable",
                skill_name="stellar_evolution",
                condition="$input.estimate_stellar",
                args={"mass_solar": 1.0},
            ),
        ],
    )
