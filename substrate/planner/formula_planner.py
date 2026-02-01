# PATH: substrate/planner/formula_planner.py
# PURPOSE:
#   - Plans derivation paths through the Formula Graph
#   - Finds sequences of formulas that transform inputs to outputs
#   - Respects regime of validity and assumptions
#
# ROLE IN ARCHITECTURE:
#   - Bridge between problem specification and formula execution
#   - Uses the FormulaGraph to find derivation chains
#
# MAIN EXPORTS:
#   - FormulaPlanner: Main planner class
#   - DerivationPlan: A planned sequence of formula applications
#   - PlanStep: Single step in a derivation plan
#
# NON-RESPONSIBILITIES:
#   - Does NOT execute plans (that's the executor)
#   - Does NOT modify the graph (that's evolution)
#
# NOTES FOR FUTURE AI:
#   - Plans should be minimal (fewest steps)
#   - Plans should respect validity regimes
#   - Multiple plans may be valid - return all for selection

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Tuple
from datetime import datetime
import heapq
from enum import Enum, auto

from substrate.graph.formula import Formula, FormulaStatus
from substrate.graph.formula_graph import FormulaGraph, EdgeType


class PlanStatus(Enum):
    """Status of a derivation plan."""
    CANDIDATE = auto()     # Proposed but not validated
    VALIDATED = auto()     # Passed consistency checks
    EXECUTING = auto()     # Currently being executed
    COMPLETED = auto()     # Successfully executed
    FAILED = auto()        # Execution failed


@dataclass
class PlanStep:
    """A single step in a derivation plan."""
    
    # Which formula to apply
    formula_id: str
    formula_name: str
    
    # What this step computes
    inputs: Dict[str, str]   # variable_symbol -> source (input/step_n)
    outputs: List[str]       # variable_symbols produced
    
    # Execution info
    order: int               # Execution order (0-indexed)
    estimated_cost: float = 0.0  # Computational cost estimate
    
    # Assumptions and conditions
    assumptions_used: List[str] = field(default_factory=list)
    regime_conditions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "formula_id": self.formula_id,
            "formula_name": self.formula_name,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "order": self.order,
            "estimated_cost": self.estimated_cost,
            "assumptions_used": self.assumptions_used,
            "regime_conditions": self.regime_conditions,
        }


@dataclass
class DerivationPlan:
    """
    A complete plan for deriving outputs from inputs.
    
    Contains a sequence of formula applications that transform
    the given inputs into the required outputs.
    """
    
    # Identity
    id: str
    
    # Problem specification
    problem_inputs: Dict[str, Any]   # Input variables and values
    problem_outputs: List[str]       # Required output variables
    context: Dict[str, Any]          # Additional context (domain, scale, etc.)
    
    # The plan itself
    steps: List[PlanStep] = field(default_factory=list)
    
    # Metadata
    status: PlanStatus = PlanStatus.CANDIDATE
    confidence: float = 1.0
    total_cost: float = 0.0
    
    # Provenance
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "planner"
    
    # Validation
    assumptions_required: Set[str] = field(default_factory=set)
    regime_constraints: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_step(self, step: PlanStep):
        """Add a step to the plan."""
        step.order = len(self.steps)
        self.steps.append(step)
        self.total_cost += step.estimated_cost
        self.assumptions_required.update(step.assumptions_used)
        self.regime_constraints.extend(step.regime_conditions)
    
    def get_formula_sequence(self) -> List[str]:
        """Get ordered list of formula IDs."""
        return [s.formula_id for s in sorted(self.steps, key=lambda s: s.order)]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "problem_inputs": self.problem_inputs,
            "problem_outputs": self.problem_outputs,
            "context": self.context,
            "steps": [s.to_dict() for s in self.steps],
            "status": self.status.name,
            "confidence": self.confidence,
            "total_cost": self.total_cost,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "assumptions_required": list(self.assumptions_required),
            "regime_constraints": self.regime_constraints,
            "warnings": self.warnings,
        }
    
    def __repr__(self):
        steps_str = " -> ".join(s.formula_name for s in self.steps)
        return f"DerivationPlan({steps_str})"


class FormulaPlanner:
    """
    Plans derivation paths through the Formula Graph.
    
    Given a problem (inputs, desired outputs, context), finds one or more
    sequences of formula applications that derive the outputs from inputs.
    
    Uses:
    - A* search for optimal paths
    - Regime checking for validity
    - Cost estimation for efficiency and regime/physics alignment
    """
    
    def __init__(
        self,
        graph: FormulaGraph,
        regime_penalty: float = 1.5,
        conservation_bonus: float = 0.3,
    ):
        """
        Initialize the planner.
        
        Args:
            graph: The FormulaGraph to plan over
            regime_penalty: Cost added when domain/regime mismatches the context
            conservation_bonus: Cost subtracted for conservation-law formulas (preferred)
        """
        self.graph = graph
        self._plan_counter = 0
        self._regime_penalty = regime_penalty
        self._conservation_bonus = conservation_bonus
    
    def plan(
        self,
        inputs: Dict[str, Any],
        outputs: List[str],
        context: Optional[Dict[str, Any]] = None,
        max_plans: int = 5,
        max_steps: int = 10,
        prefer_fundamental: bool = True
    ) -> List[DerivationPlan]:
        """
        Find derivation plans for a physics problem.
        
        Args:
            inputs: Dict of input variables and their values
            outputs: List of output variable names to derive
            context: Additional context (domain, scale, conditions)
            max_plans: Maximum number of plans to return
            max_steps: Maximum steps per plan
            prefer_fundamental: Prefer fundamental formulas over approximations
            
        Returns:
            List of DerivationPlans, ordered by confidence/cost
        """
        context = context or {}
        input_vars = set(inputs.keys())
        output_vars = set(outputs)
        
        # Find all plans using modified A* search
        plans = self._search_plans(
            input_vars=input_vars,
            output_vars=output_vars,
            context=context,
            max_plans=max_plans,
            max_steps=max_steps,
            prefer_fundamental=prefer_fundamental,
        )
        
        # Build DerivationPlan objects
        result_plans = []
        for formula_sequence, cost in plans:
            plan = self._build_plan(
                formula_sequence=formula_sequence,
                inputs=inputs,
                outputs=outputs,
                context=context,
                cost=cost,
            )
            result_plans.append(plan)
        
        # Sort by confidence (descending) then cost (ascending)
        result_plans.sort(key=lambda p: (-p.confidence, p.total_cost))
        
        return result_plans[:max_plans]
    
    def _search_plans(
        self,
        input_vars: Set[str],
        output_vars: Set[str],
        context: Dict[str, Any],
        max_plans: int,
        max_steps: int,
        prefer_fundamental: bool
    ) -> List[Tuple[List[str], float]]:
        """
        Search for formula sequences using A*.
        
        Returns list of (formula_id_sequence, total_cost).
        """
        plans = []
        
        # State: (available_vars, formulas_used)
        # Priority queue: (cost, state, formula_sequence)
        initial_state = (frozenset(input_vars), frozenset())
        pq = [(0.0, initial_state, [])]
        visited = set()
        
        while pq and len(plans) < max_plans:
            cost, state, sequence = heapq.heappop(pq)
            available_vars, used_formulas = state
            
            # Check if we have all outputs
            if output_vars.issubset(available_vars):
                plans.append((sequence.copy(), cost))
                continue
            
            # Skip if visited
            state_key = (available_vars, used_formulas)
            if state_key in visited:
                continue
            visited.add(state_key)
            
            # Skip if too many steps
            if len(sequence) >= max_steps:
                continue
            
            # Find applicable formulas
            for formula in self.graph.get_all_formulas():
                if formula.id in used_formulas:
                    continue
                
                # Check applicability
                applicable, reasons = formula.is_applicable(context)
                if not applicable:
                    continue
                
                # Check if we have the required inputs
                formula_inputs = {v.symbol for v in formula.inputs}
                if not formula_inputs.issubset(available_vars):
                    continue
                
                # Check if this formula provides something new
                formula_outputs = {v.symbol for v in formula.outputs}
                new_outputs = formula_outputs - available_vars
                if not new_outputs and not formula_outputs.intersection(output_vars):
                    continue
                
                # Compute cost
                step_cost = self._compute_step_cost(formula, prefer_fundamental, context)
                new_cost = cost + step_cost
                
                # Add to queue
                new_available = available_vars | formula_outputs
                new_used = used_formulas | {formula.id}
                new_state = (frozenset(new_available), frozenset(new_used))
                new_sequence = sequence + [formula.id]
                
                heapq.heappush(pq, (new_cost, new_state, new_sequence))
        
        return plans
    
    def _compute_step_cost(
        self,
        formula: Formula,
        prefer_fundamental: bool,
        context: Optional[Dict[str, Any]] = None,
    ) -> float:
        """Compute cost of using a formula (lower is better)."""
        cost = 1.0
        context = context or {}
        
        # Prefer higher-confidence formulas
        cost += (1.0 - formula.confidence) * 2.0
        
        # Prefer fundamental over approximations
        if prefer_fundamental:
            layer_costs = {
                formula.layer.AXIOM: 0.0,
                formula.layer.FUNDAMENTAL: 0.5,
                formula.layer.EFFECTIVE: 1.0,
                formula.layer.PHENOMENOLOGICAL: 1.5,
                formula.layer.APPROXIMATION: 2.0,
                formula.layer.NUMERICAL: 2.5,
            }
            cost += layer_costs.get(formula.layer, 1.0)
        
        # Penalize contested/deprecated formulas
        if formula.status == FormulaStatus.CONTESTED:
            cost += 3.0
        elif formula.status == FormulaStatus.DEPRECATED:
            cost += 10.0

        # Regime/domain alignment: penalize mismatch, reward match
        ctx_domain = context.get("domain")
        if ctx_domain:
            domains = set(formula.regime.domains) if formula.regime.domains else set()
            domains.add(formula.domain)
            if ctx_domain not in domains:
                cost += self._regime_penalty
            else:
                cost -= 0.2  # small reward for domain match

        # Prefer conservation laws
        if "conservation" in formula.tags:
            cost -= self._conservation_bonus

        # Keep cost bounded below
        cost = max(0.1, cost)
        
        return cost
    
    def _build_plan(
        self,
        formula_sequence: List[str],
        inputs: Dict[str, Any],
        outputs: List[str],
        context: Dict[str, Any],
        cost: float
    ) -> DerivationPlan:
        """Build a DerivationPlan from a formula sequence."""
        self._plan_counter += 1
        plan_id = f"plan_{self._plan_counter}"
        
        plan = DerivationPlan(
            id=plan_id,
            problem_inputs=inputs,
            problem_outputs=outputs,
            context=context,
            total_cost=cost,
        )
        
        # Track what's available at each step
        available_vars = set(inputs.keys())
        var_sources: Dict[str, str] = {v: "input" for v in inputs.keys()}
        
        for i, formula_id in enumerate(formula_sequence):
            formula = self.graph.get_formula(formula_id)
            if not formula:
                continue
            
            # Build input mapping
            step_inputs = {}
            for var in formula.inputs:
                if var.symbol in var_sources:
                    step_inputs[var.symbol] = var_sources[var.symbol]
            
            # Build output list
            step_outputs = [v.symbol for v in formula.outputs]
            
            # Create step
            step = PlanStep(
                formula_id=formula_id,
                formula_name=formula.name,
                inputs=step_inputs,
                outputs=step_outputs,
                order=i,
                estimated_cost=self._compute_step_cost(formula, True),
                assumptions_used=formula.assumptions.copy(),
                regime_conditions=formula.regime.conditions.copy(),
            )
            
            plan.add_step(step)
            
            # Update available vars
            for out_var in step_outputs:
                var_sources[out_var] = f"step_{i}"
            available_vars.update(step_outputs)
        
        # Compute overall confidence
        if formula_sequence:
            confidences = []
            for fid in formula_sequence:
                f = self.graph.get_formula(fid)
                if f:
                    confidences.append(f.confidence)
            if confidences:
                plan.confidence = min(confidences)  # Chain is as weak as weakest link
        
        plan.status = PlanStatus.VALIDATED
        return plan
    
    def validate_plan(self, plan: DerivationPlan) -> Tuple[bool, List[str]]:
        """
        Validate a derivation plan.
        
        Checks:
        - All formulas exist
        - Input/output compatibility between steps
        - Regime compatibility
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        # Check all formulas exist
        for step in plan.steps:
            formula = self.graph.get_formula(step.formula_id)
            if not formula:
                issues.append(f"Formula not found: {step.formula_id}")
        
        if issues:
            return False, issues
        
        # Check input/output compatibility
        available = set(plan.problem_inputs.keys())
        for step in sorted(plan.steps, key=lambda s: s.order):
            formula = self.graph.get_formula(step.formula_id)
            required = {v.symbol for v in formula.inputs}
            
            missing = required - available
            if missing:
                issues.append(f"Step {step.order}: missing inputs {missing}")
            
            available.update(v.symbol for v in formula.outputs)
        
        # Check all outputs are produced
        missing_outputs = set(plan.problem_outputs) - available
        if missing_outputs:
            issues.append(f"Plan does not produce outputs: {missing_outputs}")
        
        # Check regime compatibility across steps
        all_conditions = []
        for step in plan.steps:
            all_conditions.extend(step.regime_conditions)
        
        # Simple contradiction check (would need NLP for real check)
        condition_set = set(all_conditions)
        contradictions = [
            ("relativistic", "non-relativistic"),
            ("quantum", "classical"),
            ("strong field", "weak field"),
        ]
        for c1, c2 in contradictions:
            if c1 in condition_set and c2 in condition_set:
                issues.append(f"Contradictory conditions: {c1} and {c2}")
        
        return len(issues) == 0, issues
    
    def suggest_missing_formulas(
        self,
        inputs: Dict[str, Any],
        outputs: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Suggest what formulas are needed if no plan can be found.
        
        Returns list of suggestions for new formulas.
        """
        context = context or {}
        input_vars = set(inputs.keys())
        output_vars = set(outputs)
        
        # Find what we can reach from inputs
        reachable = input_vars.copy()
        frontier = input_vars.copy()
        
        while frontier:
            new_reachable = set()
            for formula in self.graph.get_all_formulas():
                formula_inputs = {v.symbol for v in formula.inputs}
                if formula_inputs.issubset(reachable):
                    formula_outputs = {v.symbol for v in formula.outputs}
                    new_outputs = formula_outputs - reachable
                    new_reachable.update(new_outputs)
            
            if not new_reachable:
                break
            
            frontier = new_reachable
            reachable.update(new_reachable)
        
        # What outputs are we missing?
        missing_outputs = output_vars - reachable
        
        suggestions = []
        if missing_outputs:
            # Find formulas that could provide missing outputs
            # but have inputs we can't reach
            for formula in self.graph.get_all_formulas():
                formula_outputs = {v.symbol for v in formula.outputs}
                if formula_outputs.intersection(missing_outputs):
                    formula_inputs = {v.symbol for v in formula.inputs}
                    missing_inputs = formula_inputs - reachable
                    if missing_inputs:
                        suggestions.append({
                            "type": "missing_bridge",
                            "message": f"Need formula connecting {reachable} to {missing_inputs}",
                            "to_provide": list(missing_inputs),
                            "would_enable": formula.name,
                        })
            
            # Suggest completely new formulas
            suggestions.append({
                "type": "new_formula_needed",
                "message": f"Need formula(s) to derive {missing_outputs} from {reachable}",
                "inputs_available": list(reachable),
                "outputs_needed": list(missing_outputs),
            })
        
        return suggestions

