"""
PATH: ai/rubric/quality_gate.py
PURPOSE: Quality Gate that enforces rubric-based quality standards on AI responses

WHY: Quality gates prevent low-quality responses from reaching users.
Unlike binary pass/fail validators, the quality gate uses rubric scores
to make nuanced decisions: pass, improve (retry with feedback), or
escalate (to a higher-tier agent or human review).

This is the enforcement layer that connects rubric evaluation to
the DREAM agent pipeline.

FLOW:
┌─────────────┐    ┌──────────────┐    ┌─────────────────────┐
│  Response    │───▶│  Rubric      │───▶│  Gate Decision      │
│  from Agent  │    │  Evaluator   │    │                     │
└─────────────┘    └──────────────┘    │  ┌─────┐            │
                                       │  │PASS │→ Return    │
                                       │  └─────┘            │
                                       │  ┌───────┐          │
                                       │  │IMPROVE│→ Retry   │
                                       │  └───────┘ w/hints  │
                                       │  ┌────────┐         │
                                       │  │ESCALATE│→ Higher │
                                       │  └────────┘ tier    │
                                       └─────────────────────┘

DEPENDENCIES:
- ai.rubric.evaluator: RubricEvaluator, RubricReport
- ai.rubric.definitions: Rubric, RubricDimension
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from ai.rubric.definitions import Rubric, RubricDimension, PHYSICS_RUBRIC, get_rubric_for_domain
from ai.rubric.evaluator import RubricEvaluator, RubricReport


class GateVerdict(Enum):
    """Decision made by the quality gate."""
    PASS = "pass"           # Response meets quality standards
    IMPROVE = "improve"     # Response should be retried with feedback
    ESCALATE = "escalate"   # Response needs a higher-tier agent
    REJECT = "reject"       # Response is fundamentally flawed


@dataclass
class GateDecision:
    """Complete quality gate decision with reasoning."""
    verdict: GateVerdict
    report: RubricReport
    
    # Feedback for improvement (when verdict is IMPROVE)
    improvement_hints: List[str] = field(default_factory=list)
    
    # Escalation info (when verdict is ESCALATE)
    escalation_reason: Optional[str] = None
    recommended_tier: Optional[str] = None
    
    # How many times this response has been through the gate
    attempt_number: int = 1
    max_attempts: int = 2
    
    # Timing
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "verdict": self.verdict.value,
            "report": self.report.to_dict(),
            "improvement_hints": self.improvement_hints,
            "escalation_reason": self.escalation_reason,
            "recommended_tier": self.recommended_tier,
            "attempt": self.attempt_number,
            "max_attempts": self.max_attempts,
        }


class QualityGate:
    """
    Quality gate for Beyond Frontier responses.
    
    Evaluates responses against rubrics and makes pass/improve/escalate
    decisions based on configurable thresholds. Integrates with the
    DREAM agent pipeline to enable automatic quality enforcement.
    
    Key design decisions:
    1. PASS threshold is strict (0.65) -- we want quality
    2. IMPROVE gives the same tier a second chance with feedback
    3. ESCALATE sends to a higher tier only after improve fails
    4. Max 2 attempts before escalating (cost-conscious)
    """
    
    # Thresholds for gate decisions
    PASS_THRESHOLD = 0.65
    ESCALATE_THRESHOLD = 0.35
    
    # Critical dimension failures that force escalation regardless of overall score
    CRITICAL_DIMENSIONS = [
        RubricDimension.PHYSICS_ACCURACY,
    ]
    CRITICAL_DIMENSION_MIN = 0.4
    
    def __init__(
        self,
        rubric: Optional[Rubric] = None,
        pass_threshold: float = PASS_THRESHOLD,
        escalate_threshold: float = ESCALATE_THRESHOLD,
        max_attempts: int = 2,
    ):
        """
        Initialize quality gate.
        
        Args:
            rubric: Rubric to evaluate against
            pass_threshold: Minimum overall score to pass (0-1)
            escalate_threshold: Score below which to escalate (0-1)
            max_attempts: Max retry attempts before escalating
        """
        self.rubric = rubric or PHYSICS_RUBRIC
        self.evaluator = RubricEvaluator(self.rubric)
        self.pass_threshold = pass_threshold
        self.escalate_threshold = escalate_threshold
        self.max_attempts = max_attempts
        
        # Track gate statistics
        self._stats = {
            "total_evaluations": 0,
            "passed": 0,
            "improved": 0,
            "escalated": 0,
            "rejected": 0,
            "avg_score": 0.0,
            "score_history": [],
        }
    
    def evaluate(
        self,
        content: str,
        query: str = "",
        code: Optional[str] = None,
        artefacts: Optional[List[Dict]] = None,
        reasoning: Optional[Any] = None,
        attempt_number: int = 1,
        domain: str = "general",
    ) -> GateDecision:
        """
        Evaluate a response through the quality gate.
        
        Args:
            content: Response content
            query: Original user query
            code: Generated code (if any)
            artefacts: Artefact references
            reasoning: Chain of thought data
            attempt_number: Which attempt this is (1-based)
            domain: Physics domain for rubric selection
        
        Returns:
            GateDecision with verdict and detailed report
        """
        # Run rubric evaluation
        report = self.evaluator.evaluate(
            content=content,
            query=query,
            code=code,
            artefacts=artefacts,
            reasoning=reasoning,
        )
        
        # Make gate decision
        verdict = self._decide(report, attempt_number)
        
        # Generate improvement hints if needed
        improvement_hints = []
        escalation_reason = None
        recommended_tier = None
        
        if verdict == GateVerdict.IMPROVE:
            improvement_hints = self._generate_improvement_hints(report)
        elif verdict == GateVerdict.ESCALATE:
            escalation_reason, recommended_tier = self._generate_escalation_info(report)
        
        # Update statistics
        self._update_stats(report, verdict)
        
        return GateDecision(
            verdict=verdict,
            report=report,
            improvement_hints=improvement_hints,
            escalation_reason=escalation_reason,
            recommended_tier=recommended_tier,
            attempt_number=attempt_number,
            max_attempts=self.max_attempts,
        )
    
    def _decide(self, report: RubricReport, attempt_number: int) -> GateVerdict:
        """
        Make the gate decision based on report and attempt history.
        
        Decision logic:
        1. Check for critical dimension failures (force escalate)
        2. If overall score >= pass_threshold AND all gates pass: PASS
        3. If overall score < escalate_threshold: ESCALATE
        4. If attempt < max_attempts: IMPROVE (retry)
        5. Otherwise: ESCALATE
        """
        overall = report.overall_score
        
        # Check critical dimensions
        for critical_dim in self.CRITICAL_DIMENSIONS:
            dim_key = critical_dim.value
            if dim_key in report.dimensions:
                dim_score = report.dimensions[dim_key].score
                if dim_score < self.CRITICAL_DIMENSION_MIN:
                    # Physics accuracy too low -- must escalate
                    if attempt_number >= self.max_attempts:
                        return GateVerdict.ESCALATE
                    return GateVerdict.IMPROVE
        
        # High quality: pass
        if overall >= self.pass_threshold and report.all_gates_passed:
            return GateVerdict.PASS
        
        # Borderline pass (score okay but some gates failed)
        if overall >= self.pass_threshold and len(report.failed_gates) <= 1:
            return GateVerdict.PASS
        
        # Very low quality: escalate immediately
        if overall < self.escalate_threshold:
            return GateVerdict.ESCALATE
        
        # Medium quality: try to improve if attempts remain
        if attempt_number < self.max_attempts:
            return GateVerdict.IMPROVE
        
        # Out of attempts: escalate
        return GateVerdict.ESCALATE
    
    def _generate_improvement_hints(self, report: RubricReport) -> List[str]:
        """
        Generate specific hints for improving the response.
        
        These hints are fed back to the agent as additional
        context for a retry attempt.
        """
        hints = []
        
        # Add suggestions from the report
        hints.extend(report.suggestions)
        
        # Add dimension-specific hints
        for dim_name, summary in report.dimensions.items():
            if not summary.passed_gate:
                if dim_name == "physics_accuracy":
                    hints.append(
                        "IMPROVE: Explicitly cite the fundamental physics laws being used. "
                        "State assumptions and their domains of validity."
                    )
                elif dim_name == "mathematical_rigor":
                    hints.append(
                        "IMPROVE: Show each derivation step explicitly. "
                        "Define all variables at first use."
                    )
                elif dim_name == "explanation_clarity":
                    hints.append(
                        "IMPROVE: Build from first principles. Add plain language "
                        "explanations alongside mathematical notation."
                    )
                elif dim_name == "provenance_completeness":
                    hints.append(
                        "IMPROVE: Reference artefact IDs for all numeric claims. "
                        "Cite equations and known results."
                    )
                elif dim_name == "code_quality":
                    hints.append(
                        "IMPROVE: Add docstrings, input validation, and comments "
                        "explaining the physics behind the code."
                    )
                elif dim_name == "pedagogical_value":
                    hints.append(
                        "IMPROVE: Add physical interpretation of results. "
                        "Connect to broader physics concepts. Include verification methods."
                    )
        
        # Find worst questions
        all_scores = []
        for summary in report.dimensions.values():
            all_scores.extend(summary.question_scores)
        
        worst = sorted(all_scores, key=lambda s: s.score)[:2]
        for s in worst:
            if s.score < 0.5:
                hints.append(f"FOCUS: {s.question_text}")
        
        return hints[:5]  # Cap at 5 hints
    
    def _generate_escalation_info(self, report: RubricReport) -> Tuple[str, str]:
        """Generate escalation reason and recommended tier."""
        reasons = []
        
        if report.overall_score < self.escalate_threshold:
            reasons.append(
                f"Overall quality score ({report.overall_score:.2f}) "
                f"below escalation threshold ({self.escalate_threshold})"
            )
        
        for gate in report.failed_gates:
            dim_summary = report.dimensions.get(gate)
            if dim_summary:
                reasons.append(
                    f"{gate} failed quality gate "
                    f"(score: {dim_summary.score:.2f}, "
                    f"threshold: {dim_summary.gate_threshold:.2f})"
                )
        
        reason = "; ".join(reasons) if reasons else "Quality below acceptable threshold"
        
        # Recommend tier based on what failed
        if "physics_accuracy" in report.failed_gates:
            recommended = "orchestrator"  # Complex physics needs deep reasoning
        elif "mathematical_rigor" in report.failed_gates:
            recommended = "orchestrator"  # Math rigor needs careful work
        else:
            recommended = "workhorse"  # Other failures can be handled by workhorse
        
        return reason, recommended
    
    def _update_stats(self, report: RubricReport, verdict: GateVerdict):
        """Update gate statistics."""
        self._stats["total_evaluations"] += 1
        self._stats[verdict.value + ("" if verdict.value == "passed" else "ed" if verdict.value != "pass" else "")] = \
            self._stats.get(verdict.value, 0)
        
        if verdict == GateVerdict.PASS:
            self._stats["passed"] += 1
        elif verdict == GateVerdict.IMPROVE:
            self._stats["improved"] += 1
        elif verdict == GateVerdict.ESCALATE:
            self._stats["escalated"] += 1
        elif verdict == GateVerdict.REJECT:
            self._stats["rejected"] += 1
        
        # Track score history (keep last 100)
        self._stats["score_history"].append(report.overall_score)
        if len(self._stats["score_history"]) > 100:
            self._stats["score_history"] = self._stats["score_history"][-100:]
        
        # Running average
        history = self._stats["score_history"]
        self._stats["avg_score"] = sum(history) / len(history) if history else 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get gate statistics."""
        total = self._stats["total_evaluations"]
        return {
            "total_evaluations": total,
            "passed": self._stats["passed"],
            "improved": self._stats["improved"],
            "escalated": self._stats["escalated"],
            "rejected": self._stats["rejected"],
            "pass_rate": self._stats["passed"] / total if total > 0 else 0.0,
            "avg_score": round(self._stats["avg_score"], 3),
        }


# Module-level singleton for convenience
_default_gate: Optional[QualityGate] = None

def get_quality_gate() -> QualityGate:
    """Get or create the default quality gate singleton."""
    global _default_gate
    if _default_gate is None:
        _default_gate = QualityGate()
    return _default_gate
