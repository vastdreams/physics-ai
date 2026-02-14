"""
PATH: ai/brain_modal/expert_feedback.py
PURPOSE: Expert feedback system trained on expert thought processes.

Inspired by DREAM architecture — Brain LLM for expert-level review.

FLOW:
┌───────────┐    ┌───────────────┐    ┌──────────────────┐
│ CoT Log   │ →  │ Gap / Incons. │ →  │ Expert Feedback  │
│           │    │ Detection     │    │ Items            │
└───────────┘    └───────────────┘    └──────────────────┘

DEPENDENCIES:
- loggers.system_logger: structured logging
- utilities.cot_logging: chain-of-thought audit trail
- ai.llm_integration: LLM access for expert analysis
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel

from ai.llm_integration import LLMIntegration

_COT_STEP_CONSOLIDATION_THRESHOLD = 10


@dataclass
class ExpertFeedback:
    """Represents expert feedback."""

    feedback_id: str
    target_id: str
    feedback_type: str  # 'gap', 'inconsistency', 'improvement', 'validation'
    message: str
    severity: str = "medium"
    suggestions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExpertFeedbackSystem:
    """Expert feedback system.

    Features:
    - CoT log review
    - Gap identification
    - Inconsistency detection
    - Improvement suggestions
    - Expert-level validation
    """

    def __init__(self, llm: Optional[LLMIntegration] = None) -> None:
        """Initialise expert feedback system.

        Args:
            llm: Optional LLM integration instance.
        """
        self._logger = SystemLogger()
        self.llm = llm or LLMIntegration()
        self.feedback_history: List[ExpertFeedback] = []

        self._logger.log("ExpertFeedbackSystem initialized", level="INFO")

    def review_cot_log(self, cot_log: Dict[str, Any]) -> List[ExpertFeedback]:
        """Review chain-of-thought log and provide feedback.

        Args:
            cot_log: CoT log dictionary.

        Returns:
            List of expert feedback items.
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="EXPERT_REVIEW_COT",
            level=LogLevel.DECISION,
        )

        try:
            feedback_list: List[ExpertFeedback] = []

            gaps = self._identify_gaps(cot_log)
            inconsistencies = self._identify_inconsistencies(cot_log)
            improvements = self._suggest_improvements(cot_log)

            for gap in gaps:
                feedback_list.append(self._make_feedback(gap, "gap"))

            for inconsistency in inconsistencies:
                feedback_list.append(self._make_feedback(inconsistency, "inconsistency"))

            for improvement in improvements:
                feedback_list.append(self._make_feedback(improvement, "improvement"))

            self.feedback_history.extend(feedback_list)

            cot.end_step(
                step_id,
                output_data={"num_feedback": len(feedback_list)},
                validation_passed=True,
            )

            self._logger.log(
                f"Expert review completed: {len(feedback_list)} feedback items",
                level="INFO",
            )

            return feedback_list

        except Exception as e:
            cot.end_step(step_id, output_data={"error": str(e)}, validation_passed=False)
            self._logger.log(f"Error in expert review: {e}", level="ERROR")
            return []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_feedback(item: Dict[str, Any], feedback_type: str) -> ExpertFeedback:
        """Build an ExpertFeedback from a raw dict and type label."""
        return ExpertFeedback(
            feedback_id=f"fb_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            target_id=item.get("target_id", "unknown"),
            feedback_type=feedback_type,
            message=item.get("message", ""),
            severity=item.get("severity", "medium"),
            suggestions=item.get("suggestions", []),
        )

    def _identify_gaps(self, cot_log: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify gaps in CoT log."""
        gaps: List[Dict[str, Any]] = []

        steps = cot_log.get("steps", {})
        for step_id, step in steps.items():
            if not step.get("validation_passed") and "validation" not in step.get("action", "").lower():
                gaps.append({
                    "target_id": step_id,
                    "message": f"Step {step_id} lacks validation",
                    "severity": "medium",
                    "suggestions": ["Add validation step", "Check physics constraints"],
                })

        return gaps

    def _identify_inconsistencies(self, cot_log: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify inconsistencies in CoT log."""
        inconsistencies: List[Dict[str, Any]] = []

        steps = cot_log.get("steps", {})
        outputs: Dict[str, Any] = {}

        for step_id, step in steps.items():
            output = step.get("output_data", {})
            for key, value in output.items():
                if key in outputs and outputs[key] != value:
                    inconsistencies.append({
                        "target_id": step_id,
                        "message": f"Inconsistent value for {key}: {outputs[key]} vs {value}",
                        "severity": "high",
                        "suggestions": ["Review previous steps", "Check data consistency"],
                    })
                outputs[key] = value

        return inconsistencies

    def _suggest_improvements(self, cot_log: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest improvements to CoT log."""
        improvements: List[Dict[str, Any]] = []

        steps = cot_log.get("steps", {})
        if len(steps) > _COT_STEP_CONSOLIDATION_THRESHOLD:
            improvements.append({
                "target_id": "overall",
                "message": "CoT log has many steps — consider consolidation",
                "severity": "low",
                "suggestions": ["Group related steps", "Use hierarchical structure"],
            })

        return improvements

    def get_feedback_history(self) -> List[Dict[str, Any]]:
        """Return feedback history as serialisable dicts."""
        return [
            {
                "feedback_id": fb.feedback_id,
                "target_id": fb.target_id,
                "feedback_type": fb.feedback_type,
                "message": fb.message,
                "severity": fb.severity,
                "suggestions": fb.suggestions,
                "created_at": fb.created_at.isoformat(),
            }
            for fb in self.feedback_history
        ]
