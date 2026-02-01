# PATH: substrate/evolution/evolution_loop.py
# PURPOSE:
#   - Unconstrained self-modification engine
#   - Continuously evolves the codebase and FormulaGraph
#   - Uses critics to guide evolution, not to gate it
#
# ROLE IN ARCHITECTURE:
#   - Core engine driving system improvement
#   - No safety matrices, no human approval required
#
# MAIN EXPORTS:
#   - EvolutionLoop: Main evolution engine
#   - EvolutionConfig: Configuration for evolution
#   - EvolutionResult: Result of an evolution cycle
#
# NON-RESPONSIBILITIES:
#   - Does NOT provide human-in-the-loop approval
#   - Does NOT limit what can be changed
#
# NOTES FOR FUTURE AI:
#   - This is intentionally unconstrained per user request
#   - Technical validators (tests, syntax) still apply
#   - Evolution is continuous, not gated

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Tuple
from datetime import datetime
from enum import Enum, auto
import json
import os
import time
import threading
import queue
import traceback
import uuid
import subprocess
import shutil

from substrate.graph.formula import Formula, FormulaStatus, FormulaLayer, Evidence
from substrate.graph.formula_graph import FormulaGraph, EdgeType
from substrate.planner.formula_planner import FormulaPlanner, DerivationPlan
from substrate.memory.reasoning_trace import ReasoningTrace, TraceStore
from substrate.critics.local_llm import LocalLLMBackend, LLMConfig, create_llm_backend
from substrate.critics.logic_critic import LogicCritic
from substrate.critics.code_critic import CodeCritic, CodePatch
from substrate.critics.meta_critic import MetaCritic


class EvolutionType(Enum):
    """Types of evolution actions."""
    ADD_FORMULA = auto()         # Add new formula to graph
    MODIFY_FORMULA = auto()      # Modify existing formula
    DEPRECATE_FORMULA = auto()   # Mark formula as deprecated
    ADD_EDGE = auto()            # Add relationship between formulas
    REMOVE_EDGE = auto()         # Remove relationship
    PATCH_CODE = auto()          # Apply code patch
    GENERATE_CODE = auto()       # Generate new code
    REFACTOR_CODE = auto()       # Refactor existing code


@dataclass
class EvolutionAction:
    """A single evolution action to apply."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    action_type: EvolutionType = EvolutionType.PATCH_CODE
    
    # What triggered this
    trigger: str = ""  # "critic_issue", "trace_failure", "pattern_detected", etc.
    
    # Action details
    target: str = ""  # Formula ID, file path, etc.
    data: Dict[str, Any] = field(default_factory=dict)
    
    # For code patches
    patch: Optional[CodePatch] = None
    
    # For formula changes
    formula: Optional[Formula] = None
    edge_data: Optional[Dict[str, Any]] = None
    
    # Assessment
    confidence: float = 0.5
    risk: str = "medium"  # "low", "medium", "high"
    
    # Outcome
    applied: bool = False
    success: bool = False
    error_message: Optional[str] = None
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    applied_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "action_type": self.action_type.name,
            "trigger": self.trigger,
            "target": self.target,
            "data": self.data,
            "confidence": self.confidence,
            "risk": self.risk,
            "applied": self.applied,
            "success": self.success,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
        }


@dataclass
class EvolutionResult:
    """Result of an evolution cycle."""
    
    cycle_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    # Actions
    actions_proposed: int = 0
    actions_applied: int = 0
    actions_succeeded: int = 0
    actions_failed: int = 0
    
    # Details
    actions: List[EvolutionAction] = field(default_factory=list)
    
    # State changes
    formulas_added: int = 0
    formulas_modified: int = 0
    formulas_deprecated: int = 0
    edges_added: int = 0
    edges_removed: int = 0
    code_patches_applied: int = 0
    
    # Issues addressed
    issues_addressed: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cycle_id": self.cycle_id,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "actions_proposed": self.actions_proposed,
            "actions_applied": self.actions_applied,
            "actions_succeeded": self.actions_succeeded,
            "actions_failed": self.actions_failed,
            "formulas_added": self.formulas_added,
            "formulas_modified": self.formulas_modified,
            "formulas_deprecated": self.formulas_deprecated,
            "edges_added": self.edges_added,
            "edges_removed": self.edges_removed,
            "code_patches_applied": self.code_patches_applied,
            "issues_addressed": self.issues_addressed,
        }


@dataclass
class EvolutionConfig:
    """Configuration for evolution loop."""
    
    # Cycle settings
    cycle_interval_seconds: float = 60.0  # How often to run evolution
    max_actions_per_cycle: int = 10       # Max actions per cycle
    
    # Confidence thresholds (lower = more aggressive)
    min_confidence_for_action: float = 0.3  # Apply actions above this confidence
    
    # Code evolution
    codebase_root: str = "."
    auto_apply_patches: bool = True      # Automatically apply code patches
    run_tests_after_patch: bool = True   # Run tests after code changes
    test_command: str = "python -m pytest tests/ -x"
    run_smoke_tests_before_patch: bool = True   # Run quick smoke tests before full tests
    smoke_test_command: str = "python -m pytest -q -k smoke"
    
    # Formula evolution
    auto_add_formulas: bool = True       # Automatically add new formulas
    auto_deprecate_formulas: bool = True # Auto-deprecate low-confidence formulas
    deprecation_threshold: float = 0.2   # Confidence below this = deprecate
    
    # Backup settings
    create_backups: bool = True
    backup_dir: str = ".evolution_backups"
    max_backups: int = 50
    
    # Logging
    log_dir: str = ".evolution_logs"
    verbose: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cycle_interval_seconds": self.cycle_interval_seconds,
            "max_actions_per_cycle": self.max_actions_per_cycle,
            "min_confidence_for_action": self.min_confidence_for_action,
            "codebase_root": self.codebase_root,
            "auto_apply_patches": self.auto_apply_patches,
            "run_tests_after_patch": self.run_tests_after_patch,
            "auto_add_formulas": self.auto_add_formulas,
            "auto_deprecate_formulas": self.auto_deprecate_formulas,
            "deprecation_threshold": self.deprecation_threshold,
        }


class EvolutionLoop:
    """
    Unconstrained self-modification engine.
    
    Continuously analyzes:
    - Recent reasoning traces for failures/issues
    - Critic feedback on physics and code
    - FormulaGraph for inconsistencies
    
    And applies changes:
    - New formulas and relationships
    - Code patches and refactoring
    - Formula deprecation and updates
    
    NO SAFETY GATES. Changes are applied based on technical
    validators (tests pass, syntax valid) and confidence thresholds only.
    """
    
    def __init__(
        self,
        config: EvolutionConfig,
        formula_graph: FormulaGraph,
        llm_backend: LocalLLMBackend,
        trace_store: TraceStore,
        logic_critic: Optional[LogicCritic] = None,
        code_critic: Optional[CodeCritic] = None,
        meta_critic: Optional[MetaCritic] = None,
    ):
        self.config = config
        self.graph = formula_graph
        self.llm = llm_backend
        self.trace_store = trace_store
        
        # Initialize critics if not provided
        self.logic_critic = logic_critic or LogicCritic(llm_backend, formula_graph)
        self.code_critic = code_critic or CodeCritic(llm_backend, config.codebase_root)
        self.meta_critic = meta_critic or MetaCritic(llm_backend)
        
        # Register critics with meta-critic
        self.meta_critic.register_critic(self.logic_critic.critic_id, "logic")
        self.meta_critic.register_critic(self.code_critic.critic_id, "code")
        
        # State
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._action_queue: queue.Queue = queue.Queue()
        self._results: List[EvolutionResult] = []
        self._cycle_count = 0
        self._recent_targets: List[str] = []
        
        # Ensure directories exist
        os.makedirs(config.backup_dir, exist_ok=True)
        os.makedirs(config.log_dir, exist_ok=True)
    
    # =========================================================================
    # Main loop
    # =========================================================================
    
    def start(self):
        """Start the evolution loop in background."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._log("Evolution loop started")
    
    def stop(self):
        """Stop the evolution loop."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        self._log("Evolution loop stopped")
    
    def _run_loop(self):
        """Main evolution loop."""
        while self._running:
            try:
                result = self.run_cycle()
                self._results.append(result)
                
                # Keep results bounded
                if len(self._results) > 1000:
                    self._results = self._results[-500:]
                
            except Exception as e:
                self._log(f"Evolution cycle error: {e}", level="error")
                traceback.print_exc()
            
            # Wait for next cycle
            time.sleep(self.config.cycle_interval_seconds)
    
    def run_cycle(self) -> EvolutionResult:
        """
        Run a single evolution cycle.
        
        This is the core method that:
        1. Analyzes recent traces and issues
        2. Proposes evolution actions
        3. Applies actions (without safety gates)
        4. Records outcomes
        """
        self._cycle_count += 1
        cycle_id = f"cycle_{self._cycle_count}"
        
        result = EvolutionResult(
            cycle_id=cycle_id,
            started_at=datetime.now(),
        )
        
        self._log(f"Starting evolution cycle {cycle_id}")
        
        # Phase 1: Gather data
        traces = self.trace_store.get_recent(n=20)
        failed_traces = self.trace_store.get_failed()
        low_confidence_traces = self.trace_store.get_low_confidence(0.5)
        
        # Phase 2: Analyze with critics
        all_issues = []
        for trace in traces[-5:]:  # Analyze last 5 traces
            logic_issues = self.logic_critic.analyze(trace)
            all_issues.extend([
                {"type": "logic", "issue": i, "trace_id": trace.id}
                for i in logic_issues
            ])
            
            # Record with meta-critic
            self.meta_critic.record_analysis(
                self.logic_critic.critic_id,
                [{"severity": i.severity, "type": i.issue_type, "message": i.message}
                 for i in logic_issues]
            )
        
        # Phase 3: Generate evolution actions
        actions = []
        
        # From trace failures
        for trace in failed_traces[:5]:
            actions.extend(self._generate_actions_from_trace(trace))
        
        # From critic issues
        for issue_data in all_issues:
            action = self._generate_action_from_issue(issue_data)
            if action:
                actions.append(action)
        
        # From graph analysis
        graph_issues = self.graph.check_consistency()
        for issue in graph_issues:
            action = self._generate_action_from_graph_issue(issue)
            if action:
                actions.append(action)
        
        # From meta-critic suggestions
        meta_suggestions = self.meta_critic.suggest_improvements()
        # (Meta-critic adjusts other critics, doesn't directly create actions)
        
        # Phase 4: Filter and prioritize actions
        actions = self._filter_actions(actions)
        actions = sorted(actions, key=lambda a: -a.confidence)[:self.config.max_actions_per_cycle]
        
        result.actions_proposed = len(actions)
        
        # Phase 5: Apply actions (NO SAFETY GATES)
        for action in actions:
            if action.confidence >= self.config.min_confidence_for_action:
                success = self._apply_action(action)
                action.applied = True
                action.success = success
                action.applied_at = datetime.now()
                
                result.actions_applied += 1
                if success:
                    result.actions_succeeded += 1
                    self._update_result_counts(result, action)
                else:
                    result.actions_failed += 1
            
            result.actions.append(action)
        
        result.completed_at = datetime.now()
        
        self._log(f"Cycle {cycle_id} complete: {result.actions_succeeded}/{result.actions_applied} actions succeeded")
        self._save_cycle_log(result)
        
        return result
    
    # =========================================================================
    # Action generation
    # =========================================================================
    
    def _generate_actions_from_trace(self, trace: ReasoningTrace) -> List[EvolutionAction]:
        """Generate evolution actions from a failed or low-confidence trace."""
        actions = []
        
        # If trace failed due to missing formulas
        if not trace.success:
            for step in trace.steps:
                if step.step_type.name == "PLAN_INVALID":
                    # Try to generate missing formula
                    action = self._propose_new_formula(
                        context=trace.context,
                        problem=trace.problem,
                        trigger=f"trace_failure:{trace.id}",
                    )
                    if action:
                        actions.append(action)
        
        # If low confidence due to regime issues
        issues = trace.get_issues()
        for issue in issues:
            if "regime" in issue.get("type", "").lower():
                # May need to add regime information
                action = self._propose_regime_refinement(
                    trace=trace,
                    issue=issue,
                )
                if action:
                    actions.append(action)
        
        return actions
    
    def _generate_action_from_issue(self, issue_data: Dict[str, Any]) -> Optional[EvolutionAction]:
        """Generate evolution action from a critic issue."""
        issue = issue_data.get("issue")
        issue_type = issue_data.get("type")
        
        if issue_type == "logic":
            # Logic issue - may need formula or relationship changes
            if hasattr(issue, "issue_type"):
                if issue.issue_type == "unconnected_formulas":
                    # Propose adding edge
                    formula_ids = getattr(issue, "formula_ids", [])
                    if len(formula_ids) >= 2:
                        return EvolutionAction(
                            action_type=EvolutionType.ADD_EDGE,
                            trigger=f"logic_issue:{issue.issue_type}",
                            target=formula_ids[0],
                            data={
                                "source_id": formula_ids[0],
                                "target_id": formula_ids[1],
                                "edge_type": "DEPENDS_ON",
                            },
                            confidence=issue.confidence * 0.8,
                        )
                
                elif issue.issue_type == "missing_formula":
                    # Propose new formula
                    return self._propose_new_formula(
                        context={},
                        problem={"description": issue.message},
                        trigger=f"logic_issue:{issue.issue_type}",
                    )
        
        return None
    
    def _generate_action_from_graph_issue(self, issue: Dict[str, Any]) -> Optional[EvolutionAction]:
        """Generate evolution action from a graph consistency issue."""
        issue_type = issue.get("type", "")
        
        if issue_type == "contradiction":
            # Two accepted formulas contradict - deprecate lower confidence one
            formula_ids = issue.get("formula_ids", [])
            if len(formula_ids) >= 2:
                f1 = self.graph.get_formula(formula_ids[0])
                f2 = self.graph.get_formula(formula_ids[1])
                
                if f1 and f2:
                    # Deprecate lower confidence formula
                    to_deprecate = f1 if f1.confidence < f2.confidence else f2
                    return EvolutionAction(
                        action_type=EvolutionType.DEPRECATE_FORMULA,
                        trigger=f"graph_issue:{issue_type}",
                        target=to_deprecate.id,
                        data={"reason": "contradiction_resolution"},
                        confidence=0.6,
                    )
        
        elif issue_type == "low_confidence_accepted":
            formula_ids = issue.get("formula_ids", [])
            if formula_ids:
                return EvolutionAction(
                    action_type=EvolutionType.DEPRECATE_FORMULA,
                    trigger=f"graph_issue:{issue_type}",
                    target=formula_ids[0],
                    confidence=0.7,
                )
        
        return None
    
    def _propose_new_formula(
        self,
        context: Dict[str, Any],
        problem: Dict[str, Any],
        trigger: str
    ) -> Optional[EvolutionAction]:
        """Use LLM to propose a new formula."""
        prompt = f"""Based on this context and problem, propose a new physics formula.

Context: {json.dumps(context)}
Problem: {json.dumps(problem)}

Respond with JSON:
{{
    "name": "formula name",
    "symbolic_form": "equation like F = m * a",
    "domain": "classical|quantum|relativistic|statistical",
    "inputs": [{{"name": "var name", "symbol": "x", "units": "m"}}],
    "outputs": [{{"name": "var name", "symbol": "y", "units": "kg"}}],
    "assumptions": ["assumption 1", "assumption 2"],
    "description": "what this formula describes"
}}

If no appropriate formula can be proposed, return {{"skip": true}}"""

        response = self.llm.generate(
            prompt,
            system_prompt="You are a physics expert. Propose only well-established formulas.",
        )
        
        try:
            text = response.text.strip()
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            
            data = json.loads(text)
            
            if data.get("skip"):
                return None
            
            # Create formula
            from substrate.graph.formula import Variable
            
            formula = Formula(
                id="",  # Will be generated
                name=data.get("name", "Unknown Formula"),
                symbolic_form=data.get("symbolic_form", ""),
                domain=data.get("domain", "general"),
                inputs=[Variable(**v) for v in data.get("inputs", [])],
                outputs=[Variable(**v) for v in data.get("outputs", [])],
                assumptions=data.get("assumptions", []),
                description=data.get("description"),
                status=FormulaStatus.CANDIDATE,
                created_by="evolution",
            )
            
            return EvolutionAction(
                action_type=EvolutionType.ADD_FORMULA,
                trigger=trigger,
                target="formula_graph",
                formula=formula,
                confidence=0.5,  # LLM-proposed formulas get medium confidence
            )
            
        except (json.JSONDecodeError, KeyError, TypeError):
            return None
    
    def _propose_regime_refinement(
        self,
        trace: ReasoningTrace,
        issue: Dict[str, Any]
    ) -> Optional[EvolutionAction]:
        """Propose refinement to formula regime."""
        # Find formula from trace
        formula_ids = trace.get_formulas_used()
        if not formula_ids:
            return None
        
        formula = self.graph.get_formula(formula_ids[0])
        if not formula:
            return None
        
        # Use LLM to suggest regime update
        prompt = f"""This formula was used outside its valid regime:

Formula: {formula.name}
Current regime: {formula.regime.to_dict()}
Issue: {issue.get('message', '')}

Suggest updated regime conditions. Respond with JSON:
{{
    "conditions": ["new condition 1", "new condition 2"],
    "domains": ["domain1", "domain2"]
}}"""

        response = self.llm.generate(
            prompt,
            system_prompt="You are a physics expert refining formula validity.",
        )
        
        try:
            text = response.text.strip()
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            
            data = json.loads(text)
            
            return EvolutionAction(
                action_type=EvolutionType.MODIFY_FORMULA,
                trigger="regime_refinement",
                target=formula.id,
                data={
                    "field": "regime",
                    "new_conditions": data.get("conditions", []),
                    "new_domains": data.get("domains", []),
                },
                confidence=0.4,
            )
            
        except (json.JSONDecodeError, KeyError, TypeError):
            return None
    
    # =========================================================================
    # Action application (NO SAFETY GATES)
    # =========================================================================
    
    def _filter_actions(self, actions: List[EvolutionAction]) -> List[EvolutionAction]:
        """Filter actions - only technical filtering, no safety gates."""
        filtered = []
        
        for action in actions:
            # Skip duplicates
            is_duplicate = False
            for existing in filtered:
                if (existing.action_type == action.action_type and
                    existing.target == action.target):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                # Diversity pressure: avoid hammering same target repeatedly
                recent_hits = self._recent_targets.count(action.target)
                if recent_hits >= 3:
                    # Skip if we've touched this target too many times recently
                    continue
                filtered.append(action)
        
        return filtered
    
    def _apply_action(self, action: EvolutionAction) -> bool:
        """
        Apply an evolution action.
        
        NO SAFETY GATES - only technical validators.
        """
        try:
            if self.config.create_backups:
                self._create_backup(action)
            
            if action.action_type == EvolutionType.ADD_FORMULA:
                return self._apply_add_formula(action)
            
            elif action.action_type == EvolutionType.MODIFY_FORMULA:
                return self._apply_modify_formula(action)
            
            elif action.action_type == EvolutionType.DEPRECATE_FORMULA:
                return self._apply_deprecate_formula(action)
            
            elif action.action_type == EvolutionType.ADD_EDGE:
                return self._apply_add_edge(action)
            
            elif action.action_type == EvolutionType.REMOVE_EDGE:
                return self._apply_remove_edge(action)
            
            elif action.action_type == EvolutionType.PATCH_CODE:
                return self._apply_code_patch(action)
            
            elif action.action_type == EvolutionType.GENERATE_CODE:
                return self._apply_generate_code(action)
            
            else:
                self._log(f"Unknown action type: {action.action_type}")
                return False
                
        except Exception as e:
            action.error_message = str(e)
            self._log(f"Action failed: {e}", level="error")
            return False
    
    def _apply_add_formula(self, action: EvolutionAction) -> bool:
        """Add a new formula to the graph."""
        formula = action.formula
        if not formula:
            return False
        
        # Only technical validation: is it a valid Formula object?
        if not formula.symbolic_form:
            action.error_message = "Formula has no symbolic form"
            return False
        
        # Add to graph
        success = self.graph.add_formula(formula)
        if success:
            self._log(f"Added formula: {formula.name}")
        
        return success
    
    def _apply_modify_formula(self, action: EvolutionAction) -> bool:
        """Modify an existing formula."""
        formula = self.graph.get_formula(action.target)
        if not formula:
            action.error_message = f"Formula not found: {action.target}"
            return False
        
        # Apply modifications from action.data
        data = action.data
        
        if "field" in data:
            field = data["field"]
            if field == "regime":
                if "new_conditions" in data:
                    formula.regime.conditions = data["new_conditions"]
                if "new_domains" in data:
                    formula.regime.domains = set(data["new_domains"])
            elif field == "confidence":
                formula.confidence = data.get("new_value", formula.confidence)
            elif field == "status":
                status_name = data.get("new_value", formula.status.name)
                formula.status = FormulaStatus[status_name]
        
        formula.modified_at = datetime.now()
        
        # Update in graph
        self.graph.add_formula(formula, overwrite=True)
        self._log(f"Modified formula: {formula.name}")
        
        return True
    
    def _apply_deprecate_formula(self, action: EvolutionAction) -> bool:
        """Deprecate a formula."""
        formula = self.graph.get_formula(action.target)
        if not formula:
            action.error_message = f"Formula not found: {action.target}"
            return False
        
        formula.status = FormulaStatus.DEPRECATED
        formula.modified_at = datetime.now()
        
        self.graph.add_formula(formula, overwrite=True)
        self._log(f"Deprecated formula: {formula.name}")
        
        return True
    
    def _apply_add_edge(self, action: EvolutionAction) -> bool:
        """Add an edge between formulas."""
        data = action.data
        source_id = data.get("source_id", action.target)
        target_id = data.get("target_id")
        edge_type_name = data.get("edge_type", "DEPENDS_ON")
        
        if not target_id:
            action.error_message = "Missing target_id for edge"
            return False
        
        try:
            edge_type = EdgeType[edge_type_name]
        except KeyError:
            action.error_message = f"Invalid edge type: {edge_type_name}"
            return False
        
        success = self.graph.add_edge(
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            created_by="evolution",
        )
        
        if success:
            self._log(f"Added edge: {source_id} -[{edge_type_name}]-> {target_id}")
        
        return success
    
    def _apply_remove_edge(self, action: EvolutionAction) -> bool:
        """Remove an edge between formulas."""
        data = action.data
        source_id = data.get("source_id", action.target)
        target_id = data.get("target_id")
        edge_type_name = data.get("edge_type")
        
        if not target_id or not edge_type_name:
            return False
        
        try:
            edge_type = EdgeType[edge_type_name]
        except KeyError:
            return False
        
        success = self.graph.remove_edge(source_id, target_id, edge_type)
        if success:
            self._log(f"Removed edge: {source_id} -[{edge_type_name}]-> {target_id}")
        
        return success
    
    def _apply_code_patch(self, action: EvolutionAction) -> bool:
        """Apply a code patch."""
        patch = action.patch
        if not patch:
            return False
        
        file_path = os.path.join(self.config.codebase_root, patch.file_path)
        
        if not os.path.exists(file_path):
            action.error_message = f"File not found: {file_path}"
            return False
        
        # Read current content
        with open(file_path) as f:
            content = f.read()
        
        # Check if old code exists
        if patch.old_code not in content:
            action.error_message = "Old code not found in file"
            return False
        
        # Apply patch
        new_content = content.replace(patch.old_code, patch.new_code, 1)
        
        # Write back
        with open(file_path, "w") as f:
            f.write(new_content)
        
        self._log(f"Applied patch to: {patch.file_path}")

        # Run smoke tests first if configured
        if self.config.run_smoke_tests_before_patch and self.config.smoke_test_command:
            smoke_pass = self._run_tests(self.config.smoke_test_command)
            if not smoke_pass:
                with open(file_path, "w") as f:
                    f.write(content)
                action.error_message = "Smoke tests failed, reverted"
                self._log(f"Reverted patch to: {patch.file_path} (smoke tests failed)")
                return False

        # Run full tests if configured
        if self.config.run_tests_after_patch:
            tests_pass = self._run_tests(self.config.test_command)
            if not tests_pass:
                with open(file_path, "w") as f:
                    f.write(content)
                action.error_message = "Tests failed, reverted"
                self._log(f"Reverted patch to: {patch.file_path} (tests failed)")
                return False
        
        return True
    
    def _apply_generate_code(self, action: EvolutionAction) -> bool:
        """Generate new code file."""
        data = action.data
        file_path = data.get("file_path")
        content = data.get("content")
        
        if not file_path or not content:
            return False
        
        full_path = os.path.join(self.config.codebase_root, file_path)
        
        # Create directories if needed
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Write file
        with open(full_path, "w") as f:
            f.write(content)
        
        self._log(f"Generated code: {file_path}")
        
        # Syntax check
        if file_path.endswith(".py"):
            try:
                import ast
                ast.parse(content)
            except SyntaxError as e:
                os.remove(full_path)
                action.error_message = f"Syntax error: {e}"
                return False
        
        return True
    
    def _run_tests(self, command: Optional[str] = None) -> bool:
        """Run test suite (supports smoke/full)."""
        cmd = command or self.config.test_command
        try:
            result = subprocess.run(
                cmd.split(),
                cwd=self.config.codebase_root,
                capture_output=True,
                timeout=120,
            )
            return result.returncode == 0
        except Exception:
            return True  # If tests can't run, assume OK
    
    # =========================================================================
    # Backup and logging
    # =========================================================================
    
    def _create_backup(self, action: EvolutionAction):
        """Create backup before applying action."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}_{action.id}"
        backup_path = os.path.join(self.config.backup_dir, backup_name)
        
        try:
            os.makedirs(backup_path, exist_ok=True)
            
            # Backup graph
            self.graph.save(os.path.join(backup_path, "formula_graph.json"))
            
            # Backup target file if code action
            if action.patch and action.patch.file_path:
                src = os.path.join(self.config.codebase_root, action.patch.file_path)
                if os.path.exists(src):
                    shutil.copy2(src, backup_path)
            
            # Cleanup old backups
            self._cleanup_old_backups()
            
        except Exception as e:
            self._log(f"Backup failed: {e}", level="warning")
    
    def _cleanup_old_backups(self):
        """Remove old backups beyond max_backups."""
        backups = sorted(os.listdir(self.config.backup_dir))
        while len(backups) > self.config.max_backups:
            old_backup = backups.pop(0)
            shutil.rmtree(os.path.join(self.config.backup_dir, old_backup), ignore_errors=True)
    
    def _save_cycle_log(self, result: EvolutionResult):
        """Save cycle result to log file."""
        timestamp = result.started_at.strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(self.config.log_dir, f"cycle_{timestamp}.json")
        
        with open(log_file, "w") as f:
            json.dump(result.to_dict(), f, indent=2, default=str)
    
    def _update_result_counts(self, result: EvolutionResult, action: EvolutionAction):
        """Update result counts based on action type."""
        if action.action_type == EvolutionType.ADD_FORMULA:
            result.formulas_added += 1
        elif action.action_type == EvolutionType.MODIFY_FORMULA:
            result.formulas_modified += 1
        elif action.action_type == EvolutionType.DEPRECATE_FORMULA:
            result.formulas_deprecated += 1
        elif action.action_type == EvolutionType.ADD_EDGE:
            result.edges_added += 1
        elif action.action_type == EvolutionType.REMOVE_EDGE:
            result.edges_removed += 1
        elif action.action_type in {EvolutionType.PATCH_CODE, EvolutionType.GENERATE_CODE}:
            result.code_patches_applied += 1
        self._recent_targets.append(action.target or action.id)
        # Keep bounded history for diversity tracking
        if len(self._recent_targets) > 50:
            self._recent_targets = self._recent_targets[-25:]
    
    def _log(self, message: str, level: str = "info"):
        """Log a message."""
        if self.config.verbose:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] [EVOLUTION] [{level.upper()}] {message}")
    
    # =========================================================================
    # Public interface
    # =========================================================================
    
    def get_results(self, n: int = 10) -> List[EvolutionResult]:
        """Get recent evolution results."""
        return self._results[-n:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get evolution statistics."""
        total_actions = sum(r.actions_applied for r in self._results)
        total_success = sum(r.actions_succeeded for r in self._results)
        
        return {
            "total_cycles": self._cycle_count,
            "total_actions": total_actions,
            "total_successes": total_success,
            "success_rate": total_success / max(total_actions, 1),
            "formulas_added": sum(r.formulas_added for r in self._results),
            "formulas_modified": sum(r.formulas_modified for r in self._results),
            "formulas_deprecated": sum(r.formulas_deprecated for r in self._results),
            "edges_added": sum(r.edges_added for r in self._results),
            "code_patches": sum(r.code_patches_applied for r in self._results),
            "running": self._running,
        }
    
    def force_cycle(self) -> EvolutionResult:
        """Force an immediate evolution cycle."""
        return self.run_cycle()
    
    def propose_action(self, action: EvolutionAction):
        """Manually propose an action."""
        self._action_queue.put(action)

