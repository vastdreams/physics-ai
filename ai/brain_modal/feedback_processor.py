"""
PATH: ai/brain_modal/feedback_processor.py
PURPOSE: Process and integrate feedback into system state.

Inspired by DREAM architecture — feedback integration and processing.

FLOW:
┌──────────┐    ┌──────────┐    ┌─────────────┐    ┌────────┐
│ Feedback │ →  │ Analyse  │ →  │ Integration │ →  │ Action │
└──────────┘    └──────────┘    └─────────────┘    └────────┘

DEPENDENCIES:
- loggers.system_logger: structured logging
- utilities.cot_logging: chain-of-thought audit trail
- expert_feedback: feedback source types
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel

from .expert_feedback import ExpertFeedback, ExpertFeedbackSystem

# ---------------------------------------------------------------------------
# Priority scoring tables
# ---------------------------------------------------------------------------
_SEVERITY_SCORES: Dict[str, int] = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}

_TYPE_MULTIPLIERS: Dict[str, float] = {
    "gap": 1.0,
    "inconsistency": 1.5,
    "improvement": 0.8,
    "validation": 1.2,
}


class FeedbackProcessor:
    """Feedback processor for integrating feedback into system.

    Features:
    - Feedback analysis
    - Priority ranking
    - Integration into system
    - Action generation
    """

    def __init__(self, expert_feedback: Optional[ExpertFeedbackSystem] = None) -> None:
        """Initialise feedback processor.

        Args:
            expert_feedback: Optional expert feedback system.
        """
        self._logger = SystemLogger()
        self.expert_feedback = expert_feedback or ExpertFeedbackSystem()
        self.processed_feedback: List[Dict[str, Any]] = []

        self._logger.log("FeedbackProcessor initialized", level="INFO")

    def process_feedback(self, feedback: ExpertFeedback) -> Dict[str, Any]:
        """Process and integrate feedback.

        Args:
            feedback: ExpertFeedback instance.

        Returns:
            Processing result dictionary.
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="PROCESS_FEEDBACK",
            input_data={"feedback_id": feedback.feedback_id},
            level=LogLevel.INFO,
        )

        try:
            priority = self._calculate_priority(feedback)
            actions = self._generate_actions(feedback)
            integration_result = self._integrate_feedback(feedback, actions)

            result: Dict[str, Any] = {
                "feedback_id": feedback.feedback_id,
                "priority": priority,
                "actions": actions,
                "integration_result": integration_result,
                "processed_at": datetime.now().isoformat(),
            }

            self.processed_feedback.append(result)

            cot.end_step(
                step_id,
                output_data={"priority": priority, "num_actions": len(actions)},
                validation_passed=True,
            )

            self._logger.log(
                f"Feedback processed: {feedback.feedback_id} (priority={priority})",
                level="INFO",
            )

            return result

        except Exception as e:
            cot.end_step(step_id, output_data={"error": str(e)}, validation_passed=False)
            self._logger.log(f"Error processing feedback: {e}", level="ERROR")
            raise

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _calculate_priority(self, feedback: ExpertFeedback) -> int:
        """Calculate feedback priority.

        Args:
            feedback: ExpertFeedback instance.

        Returns:
            Priority score (higher = more important).
        """
        base_priority = _SEVERITY_SCORES.get(feedback.severity, 1)
        multiplier = _TYPE_MULTIPLIERS.get(feedback.feedback_type, 1.0)
        return int(base_priority * multiplier)

    def _generate_actions(self, feedback: ExpertFeedback) -> List[Dict[str, Any]]:
        """Generate actions from feedback.

        Args:
            feedback: ExpertFeedback instance.

        Returns:
            List of action dictionaries.
        """
        actions: List[Dict[str, Any]] = []

        for suggestion in feedback.suggestions:
            actions.append({
                "type": "suggestion",
                "action": suggestion,
                "source": feedback.feedback_id,
            })

        if feedback.feedback_type == "gap":
            actions.append({
                "type": "fill_gap",
                "target": feedback.target_id,
                "action": "Add missing validation or step",
            })
        elif feedback.feedback_type == "inconsistency":
            actions.append({
                "type": "resolve_inconsistency",
                "target": feedback.target_id,
                "action": "Review and correct inconsistency",
            })

        return actions

    def _integrate_feedback(
        self,
        feedback: ExpertFeedback,
        actions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Integrate feedback into system.

        Args:
            feedback: ExpertFeedback instance.
            actions: Generated actions.

        Returns:
            Integration result dictionary.
        """
        return {
            "integrated": True,
            "actions_taken": len(actions),
            "status": "pending",
        }

    def get_processed_feedback(self) -> List[Dict[str, Any]]:
        """Return a copy of the processed feedback history."""
        return self.processed_feedback.copy()
