# PATH: substrate/critics/logic_critic.py
# PURPOSE:
#   - Analyzes reasoning traces for logical and physics errors
#   - Checks derivations against the Formula Graph
#   - Identifies missing assumptions and regime violations
#
# ROLE IN ARCHITECTURE:
#   - First-line critic in the audit stack
#   - Focuses on physics correctness, not code
#
# MAIN EXPORTS:
#   - LogicCritic: Main critic class
#
# NON-RESPONSIBILITIES:
#   - Does NOT analyze code (that's CodeCritic)
#   - Does NOT modify the graph (that's evolution)
#
# NOTES FOR FUTURE AI:
#   - Use both LLM and programmatic checks
#   - Programmatic checks are more reliable for dimensional analysis, etc.
#   - LLM is better for subtle reasoning errors

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import json
import uuid

from substrate.critics.local_llm import LocalLLMBackend, LLMResponse
from substrate.graph.formula import Formula, FormulaStatus, Variable
from substrate.graph.formula_graph import FormulaGraph, EdgeType
from substrate.memory.reasoning_trace import (
    ReasoningTrace, TraceStep, TraceStepType, CriticAnnotation
)
try:
    import pint
    _HAS_PINT = True
except ImportError:  # pragma: no cover
    _HAS_PINT = False


@dataclass
class LogicIssue:
    """An issue found by the logic critic."""
    
    issue_type: str  # "derivation_error", "assumption_violation", "regime_mismatch", etc.
    severity: str    # "info", "warning", "error", "critical"
    message: str
    
    # Where the issue was found
    step_ids: List[str] = field(default_factory=list)
    formula_ids: List[str] = field(default_factory=list)
    
    # Evidence
    evidence: str = ""
    confidence: float = 1.0
    
    # Suggestions
    suggestion: Optional[str] = None
    alternative_formulas: List[str] = field(default_factory=list)
    
    def to_annotation(self, critic_id: str) -> CriticAnnotation:
        """Convert to CriticAnnotation."""
        return CriticAnnotation(
            critic_id=critic_id,
            critic_type="logic",
            step_ids=self.step_ids,
            issue_type=self.issue_type,
            severity=self.severity,
            message=self.message,
            suggestion=self.suggestion,
            confidence=self.confidence,
        )


class LogicCritic:
    """
    Critic that analyzes reasoning traces for logical and physics errors.
    
    Uses:
    - Programmatic checks (dimensional analysis, conservation laws, limits)
    - LLM analysis for subtle reasoning errors
    - FormulaGraph for cross-referencing derivations
    """
    
    def __init__(
        self,
        llm_backend: LocalLLMBackend,
        formula_graph: FormulaGraph,
        critic_id: Optional[str] = None
    ):
        self.llm = llm_backend
        self.graph = formula_graph
        self.critic_id = critic_id or f"logic_critic_{uuid.uuid4().hex[:8]}"
        self._analysis_count = 0
        self._ureg = pint.UnitRegistry() if _HAS_PINT else None
    
    def analyze(
        self,
        trace: ReasoningTrace,
        check_types: Optional[Set[str]] = None
    ) -> List[LogicIssue]:
        """
        Analyze a reasoning trace for logic issues.
        
        Args:
            trace: The trace to analyze
            check_types: Which checks to run (None = all)
            
        Returns:
            List of LogicIssues found
        """
        self._analysis_count += 1
        issues = []
        
        check_types = check_types or {
            "derivation", "assumptions", "regime", "conservation",
            "dimensional", "limits", "consistency", "llm"
        }
        
        # Programmatic checks
        if "derivation" in check_types:
            issues.extend(self._check_derivation_validity(trace))
        
        if "assumptions" in check_types:
            issues.extend(self._check_assumptions(trace))
        
        if "regime" in check_types:
            issues.extend(self._check_regime_validity(trace))
        
        if "conservation" in check_types:
            issues.extend(self._check_conservation_laws(trace))
        
        if "dimensional" in check_types:
            issues.extend(self._check_dimensional_consistency(trace))
        
        if "limits" in check_types:
            issues.extend(self._check_known_limits(trace))
        
        if "consistency" in check_types:
            issues.extend(self._check_internal_consistency(trace))
        
        # LLM-based analysis
        if "llm" in check_types:
            issues.extend(self._llm_analysis(trace))
        
        # Add annotations to trace
        for issue in issues:
            trace.add_annotation(issue.to_annotation(self.critic_id))
        
        return issues
    
    def _check_derivation_validity(self, trace: ReasoningTrace) -> List[LogicIssue]:
        """Check if derivation chain is valid in the graph."""
        issues = []
        
        formulas_used = trace.get_formulas_used()
        if len(formulas_used) < 2:
            return issues
        
        # Check each consecutive pair
        for i in range(len(formulas_used) - 1):
            f1_id = formulas_used[i]
            f2_id = formulas_used[i + 1]
            
            f1 = self.graph.get_formula(f1_id)
            f2 = self.graph.get_formula(f2_id)
            
            if not f1 or not f2:
                issues.append(LogicIssue(
                    issue_type="missing_formula",
                    severity="error",
                    message=f"Formula not found in graph: {f1_id if not f1 else f2_id}",
                    formula_ids=[f1_id if not f1 else f2_id],
                ))
                continue
            
            # Check if there's a valid connection
            edges_from_f1 = self.graph.get_edges_from(f1_id)
            connected_to_f2 = any(e.target_id == f2_id for e in edges_from_f1)
            
            edges_to_f2 = self.graph.get_edges_to(f2_id)
            connected_from_f1 = any(e.source_id == f1_id for e in edges_to_f2)
            
            if not connected_to_f2 and not connected_from_f1:
                # Check if they at least share domain
                if f1.domain != f2.domain:
                    issues.append(LogicIssue(
                        issue_type="unconnected_formulas",
                        severity="warning",
                        message=f"No established connection between {f1.name} and {f2.name}",
                        formula_ids=[f1_id, f2_id],
                        suggestion="Consider adding an edge or using intermediate formulas",
                    ))
        
        return issues
    
    def _check_assumptions(self, trace: ReasoningTrace) -> List[LogicIssue]:
        """Check if assumptions are consistent and satisfied."""
        issues = []
        
        all_assumptions = set()
        formulas_used = trace.get_formulas_used()
        
        for fid in formulas_used:
            formula = self.graph.get_formula(fid)
            if formula:
                all_assumptions.update(formula.assumptions)
        
        # Check for contradictory assumptions
        contradictions = [
            ("point mass", "extended body"),
            ("isolated system", "external forces"),
            ("equilibrium", "dynamic"),
            ("relativistic", "non-relativistic"),
            ("quantum", "classical"),
        ]
        
        for a1, a2 in contradictions:
            if a1 in all_assumptions and a2 in all_assumptions:
                issues.append(LogicIssue(
                    issue_type="contradictory_assumptions",
                    severity="error",
                    message=f"Contradictory assumptions: '{a1}' and '{a2}'",
                    confidence=1.0,
                ))
        
        # Check if assumptions match context
        context = trace.context
        for assumption in all_assumptions:
            assumption_key = assumption.lower().replace(" ", "_")
            if assumption_key in context:
                if not context[assumption_key]:
                    issues.append(LogicIssue(
                        issue_type="assumption_violated",
                        severity="error",
                        message=f"Assumption '{assumption}' is violated by context",
                        confidence=0.9,
                    ))
        
        return issues
    
    def _check_regime_validity(self, trace: ReasoningTrace) -> List[LogicIssue]:
        """Check if formulas are used within their valid regimes."""
        issues = []
        
        context = trace.context
        formulas_used = trace.get_formulas_used()
        
        for fid in formulas_used:
            formula = self.graph.get_formula(fid)
            if not formula:
                continue
            
            applicable, reasons = formula.is_applicable(context)
            if not applicable:
                issues.append(LogicIssue(
                    issue_type="regime_violation",
                    severity="error",
                    message=f"Formula {formula.name} used outside valid regime: {'; '.join(reasons)}",
                    formula_ids=[fid],
                    confidence=0.95,
                ))
        
        return issues
    
    def _check_conservation_laws(self, trace: ReasoningTrace) -> List[LogicIssue]:
        """Check if conservation laws are respected."""
        issues = []
        
        # Get all conservation law formulas
        conservation_formulas = self.graph.query(tags={"conservation"})
        
        # Check if relevant conservation laws were considered
        domain = trace.domain
        relevant_conservation = [
            f for f in conservation_formulas
            if domain in f.regime.domains or not f.regime.domains
        ]
        
        formulas_used = set(trace.get_formulas_used())
        
        # Check if conservation laws are at least referenced
        if relevant_conservation:
            conservation_ids = {f.id for f in relevant_conservation}
            used_conservation = formulas_used.intersection(conservation_ids)
            
            if not used_conservation and len(formulas_used) > 2:
                issues.append(LogicIssue(
                    issue_type="conservation_not_checked",
                    severity="info",
                    message="Derivation doesn't explicitly reference conservation laws",
                    suggestion="Consider verifying against energy/momentum conservation",
                    confidence=0.5,
                ))
        
        # Check result for conservation if we have before/after states
        result = trace.result
        if result:
            # Simple check: if we have energy_before and energy_after, they should match
            if "energy_before" in result and "energy_after" in result:
                e_before = result["energy_before"]
                e_after = result["energy_after"]
                if isinstance(e_before, (int, float)) and isinstance(e_after, (int, float)):
                    if abs(e_before - e_after) > 1e-6 * max(abs(e_before), abs(e_after), 1):
                        issues.append(LogicIssue(
                            issue_type="energy_not_conserved",
                            severity="error",
                            message=f"Energy not conserved: {e_before} → {e_after}",
                            confidence=1.0,
                        ))
        
        return issues
    
    def _check_dimensional_consistency(self, trace: ReasoningTrace) -> List[LogicIssue]:
        """Check dimensional consistency using pint when available."""
        issues: List[LogicIssue] = []

        # If pint not available, fall back to simple sanity checks
        if not _HAS_PINT or not self._ureg:
            return issues

        # Collect variables used in trace steps
        for step in trace.steps:
            if step.outputs and step.formula_id:
                formula = self.graph.get_formula(step.formula_id)
                if not formula:
                    continue
                try:
                    dim_ok = self._validate_formula_dimensions(formula)
                    if not dim_ok:
                        issues.append(LogicIssue(
                            issue_type="dimensional_inconsistency",
                            severity="error",
                            message=f"Formula {formula.name} may be dimensionally inconsistent",
                            formula_ids=[formula.id],
                            confidence=0.9,
                        ))
                except Exception:
                    # If we cannot validate, skip silently to avoid false positives
                    continue

        return issues

    def _validate_formula_dimensions(self, formula: Formula) -> bool:
        """Validate a single formula for dimensional consistency using pint."""
        if not self._ureg:
            return True

        expr_str = formula.sympy_expr or formula.symbolic_form
        if not expr_str:
            return True

        expr = sp.sympify(expr_str)

        # Build dummy values with units
        subs = {}
        for var in list(formula.inputs) + list(formula.parameters):
            unit = self._parse_unit(var)
            subs[sp.Symbol(var.symbol)] = 1 * unit

        # Handle outputs (for non-equality expressions)
        output_symbols = [sp.Symbol(v.symbol) for v in formula.outputs]

        if isinstance(expr, sp.Equality):
            lhs = expr.lhs.subs(subs)
            rhs = expr.rhs.subs(subs)
            try:
                return lhs.dimensionality == rhs.dimensionality  # type: ignore[attr-defined]
            except Exception:
                return False

        # If expression defines outputs directly, compare dimensionality to declared output unit
        try:
            val = expr.subs(subs)
        except Exception:
            return True  # If we cannot evaluate, don't block

        if not output_symbols:
            return True

        # Only check first output
        out_var = formula.outputs[0]
        out_unit = self._parse_unit(out_var)
        try:
            return val.dimensionality == out_unit.dimensionality  # type: ignore[attr-defined]
        except Exception:
            return False

    def _parse_unit(self, var: Variable):
        """Parse unit string to a pint unit; default to dimensionless."""
        if not self._ureg:
            return 1
        if var.units:
            try:
                return self._ureg(var.units)
            except Exception:
                return 1
        return 1
    
    def _check_known_limits(self, trace: ReasoningTrace) -> List[LogicIssue]:
        """Check results against known limiting cases."""
        issues = []
        
        # Get formulas used
        formulas_used = trace.get_formulas_used()
        result = trace.result
        context = trace.context
        
        if not result or not formulas_used:
            return issues
        
        # Check if result approaches correct limits
        # This would need specific limit data for each formula
        for fid in formulas_used:
            formula = self.graph.get_formula(fid)
            if not formula:
                continue
            
            # Get limit edges from this formula
            limit_edges = self.graph.get_edges_from(fid, EdgeType.LOW_ENERGY_LIMIT_OF)
            limit_edges.extend(self.graph.get_edges_from(fid, EdgeType.NON_RELATIVISTIC_LIMIT_OF))
            limit_edges.extend(self.graph.get_edges_from(fid, EdgeType.CLASSICAL_LIMIT_OF))
            
            # If we have limit formulas, check consistency
            # This is a placeholder for more sophisticated limit checking
            if limit_edges and "verify_limits" in context:
                issues.append(LogicIssue(
                    issue_type="limit_check_needed",
                    severity="info",
                    message=f"Formula {formula.name} has known limits that could be verified",
                    formula_ids=[fid],
                    confidence=0.5,
                ))
        
        return issues
    
    def _check_internal_consistency(self, trace: ReasoningTrace) -> List[LogicIssue]:
        """Check internal consistency of the trace."""
        issues = []
        
        # Check for repeated computations with different results
        computation_results: Dict[str, Any] = {}
        
        for step in trace.steps:
            if step.outputs:
                for key, value in step.outputs.items():
                    if key in computation_results:
                        old_value = computation_results[key]
                        if old_value != value:
                            # Allow for numerical tolerance
                            if isinstance(old_value, (int, float)) and isinstance(value, (int, float)):
                                if abs(old_value - value) > 1e-6 * max(abs(old_value), abs(value), 1):
                                    issues.append(LogicIssue(
                                        issue_type="inconsistent_computation",
                                        severity="warning",
                                        message=f"Variable {key} computed twice with different values: {old_value} vs {value}",
                                        step_ids=[step.id],
                                        confidence=0.8,
                                    ))
                            elif old_value != value:
                                issues.append(LogicIssue(
                                    issue_type="inconsistent_computation",
                                    severity="warning",
                                    message=f"Variable {key} computed twice with different values",
                                    step_ids=[step.id],
                                    confidence=0.9,
                                ))
                    computation_results[key] = value
        
        return issues
    
    def _llm_analysis(self, trace: ReasoningTrace) -> List[LogicIssue]:
        """Use LLM to analyze for subtle reasoning errors."""
        issues = []
        
        # Build prompt
        trace_summary = self._summarize_trace_for_llm(trace)
        
        prompt = f"""Analyze this physics derivation for logical errors, incorrect assumptions, or physics mistakes.

Trace Summary:
{trace_summary}

Look for:
1. Incorrect application of formulas
2. Missing or violated assumptions
3. Regime violations (using non-relativistic formula at high speeds, etc.)
4. Logical gaps in the derivation
5. Physically impossible results

Respond with JSON:
{{
    "issues": [
        {{
            "type": "error_type",
            "severity": "warning|error|critical",
            "message": "description",
            "suggestion": "how to fix"
        }}
    ],
    "overall_assessment": "valid|questionable|invalid",
    "confidence": 0.0 to 1.0
}}

If no issues found, return {{"issues": [], "overall_assessment": "valid", "confidence": 0.9}}"""

        system_prompt = """You are a physics expert reviewing derivations for errors.
Be precise and specific. Only flag real issues, not stylistic preferences.
Focus on physics correctness, not code or presentation."""

        response = self.llm.generate(prompt, system_prompt=system_prompt)
        
        # Parse response
        try:
            # Extract JSON from response
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            
            data = json.loads(text)
            
            for issue_data in data.get("issues", []):
                issues.append(LogicIssue(
                    issue_type=issue_data.get("type", "llm_detected"),
                    severity=issue_data.get("severity", "warning"),
                    message=issue_data.get("message", "LLM detected an issue"),
                    suggestion=issue_data.get("suggestion"),
                    confidence=data.get("confidence", 0.7) * 0.8,  # Discount LLM confidence
                ))
        except (json.JSONDecodeError, KeyError, TypeError):
            # LLM didn't return valid JSON, skip
            pass
        
        return issues
    
    def _summarize_trace_for_llm(self, trace: ReasoningTrace) -> str:
        """Create a summary of the trace for LLM analysis."""
        lines = [
            f"Problem: {trace.problem_text}",
            f"Domain: {trace.domain}",
            f"Context: {json.dumps(trace.context)}",
            "",
            "Derivation Steps:",
        ]
        
        for step in trace.steps:
            if step.step_type in {TraceStepType.FORMULA_SELECTED, TraceStepType.STEP_EXECUTED}:
                formula_info = f" (Formula: {step.formula_name})" if step.formula_name else ""
                lines.append(f"  {step.order}. {step.description}{formula_info}")
                if step.inputs:
                    lines.append(f"     Inputs: {step.inputs}")
                if step.outputs:
                    lines.append(f"     Outputs: {step.outputs}")
        
        if trace.result:
            lines.append("")
            lines.append(f"Result: {json.dumps(trace.result)}")
        
        return "\n".join(lines)
    
    def quick_check(self, formula_sequence: List[str], context: Dict[str, Any]) -> List[LogicIssue]:
        """Quick check on a formula sequence without a full trace."""
        issues = []
        
        # Check each formula
        for fid in formula_sequence:
            formula = self.graph.get_formula(fid)
            if not formula:
                issues.append(LogicIssue(
                    issue_type="missing_formula",
                    severity="error",
                    message=f"Formula not found: {fid}",
                    formula_ids=[fid],
                ))
                continue
            
            # Check applicability
            applicable, reasons = formula.is_applicable(context)
            if not applicable:
                issues.append(LogicIssue(
                    issue_type="regime_violation",
                    severity="error",
                    message=f"Formula {formula.name}: {'; '.join(reasons)}",
                    formula_ids=[fid],
                ))
        
        return issues
    
    def statistics(self) -> Dict[str, Any]:
        """Get critic statistics."""
        return {
            "critic_id": self.critic_id,
            "analysis_count": self._analysis_count,
            "llm_stats": self.llm.statistics(),
        }

