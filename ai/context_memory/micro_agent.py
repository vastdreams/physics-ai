"""
PATH: ai/context_memory/micro_agent.py
PURPOSE: Sub-agentic structure embedded within context bubbles.

Inspired by DREAM architecture — micro-agents in vectorised nodes.

Mathematical model:
- Micro-agent: A = {blueprint, state, pathway_map}
- Blueprint:   B = {instructions, constraints, dependencies}
- Pathway map: P = {pathway: confidence} for routing

DEPENDENCIES:
- loggers.system_logger: structured logging
- utilities.cot_logging: chain-of-thought audit trail
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel

if TYPE_CHECKING:
    from .context_bubble import ContextBubble

_DEFAULT_CONFIDENCE = 0.5
_CONSTRAINT_FAIL_PENALTY = 0.5
_KEYWORD_MATCH_CONFIDENCE = 0.7
_PATHWAY_KEYWORDS = ("simulation", "equation", "theory", "node", "rule", "evolution")


@dataclass
class MicroAgent:
    """Micro-agent within a context bubble.

    Processes context and manages pathway maps for intelligent routing.
    """

    agent_id: str
    blueprint: Dict[str, Any]
    state: Dict[str, Any] = field(default_factory=dict)
    pathway_map: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    execution_count: int = 0

    def __post_init__(self) -> None:
        """Auto-generate agent_id if empty."""
        if not self.agent_id:
            self.agent_id = f"agent_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

    def process(self, query: Dict[str, Any], bubble: "ContextBubble") -> Optional[Dict[str, Any]]:
        """Process query and update pathway map.

        Args:
            query: Query dictionary.
            bubble: Parent context bubble.

        Returns:
            Processing result with pathway suggestions, or None on error.
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="MICRO_AGENT_PROCESS",
            input_data={"agent_id": self.agent_id, "query_keys": list(query.keys())},
            level=LogLevel.INFO,
        )

        try:
            self.execution_count += 1
            self.updated_at = datetime.now()

            instructions = self.blueprint.get("instructions", {})
            constraints = self.blueprint.get("constraints", [])

            result = self._execute_blueprint(query, instructions, constraints)

            if result and "pathways" in result:
                for pathway, confidence in result["pathways"].items():
                    self.pathway_map[pathway] = confidence

            if self.pathway_map:
                bubble.update_traffic_signals(
                    {k: int(v * 100) for k, v in self.pathway_map.items()}
                )

            cot.end_step(
                step_id,
                output_data={"result_keys": list(result.keys()) if result else []},
                validation_passed=True,
            )

            return result

        except Exception as e:
            cot.end_step(step_id, output_data={"error": str(e)}, validation_passed=False)
            _logger = SystemLogger()
            _logger.log(f"Error in micro-agent process: {e}", level="ERROR")
            return None

    def _execute_blueprint(
        self,
        query: Dict[str, Any],
        instructions: Dict[str, Any],
        constraints: List[str],
    ) -> Optional[Dict[str, Any]]:
        """Execute blueprint instructions.

        Args:
            query: Query dictionary.
            instructions: Blueprint instructions.
            constraints: Blueprint constraints.

        Returns:
            Execution result dictionary.
        """
        result: Dict[str, Any] = {
            "agent_id": self.agent_id,
            "pathways": {},
            "confidence": _DEFAULT_CONFIDENCE,
        }

        for constraint in constraints:
            if not self._check_constraint(query, constraint):
                result["confidence"] *= _CONSTRAINT_FAIL_PENALTY

        instruction_type = instructions.get("type", "default")
        if instruction_type == "route":
            target_pathways = instructions.get("pathways", [])
            for pathway in target_pathways:
                result["pathways"][pathway] = result["confidence"]
        elif instruction_type == "analyze":
            suggested = self._analyze_query(query)
            for pathway, conf in suggested.items():
                result["pathways"][pathway] = conf

        return result

    @staticmethod
    def _check_constraint(query: Dict[str, Any], constraint: str) -> bool:
        """Check if *query* satisfies *constraint*."""
        if constraint.startswith("has_"):
            key = constraint[4:]
            return key in query
        return True

    @staticmethod
    def _analyze_query(query: Dict[str, Any]) -> Dict[str, float]:
        """Analyse query and suggest pathways based on keyword matching."""
        suggestions: Dict[str, float] = {}
        query_str = str(query).lower()

        for keyword in _PATHWAY_KEYWORDS:
            if keyword in query_str:
                suggestions[f"pathway_{keyword}"] = _KEYWORD_MATCH_CONFIDENCE

        return suggestions

    def get_next_pathway(self) -> Optional[str]:
        """Return the pathway with the highest confidence, or None."""
        if not self.pathway_map:
            return None
        return max(self.pathway_map.items(), key=lambda x: x[1])[0]

    def update_pathway_confidence(self, pathway: str, confidence: float) -> None:
        """Update pathway confidence (clamped to [0, 1]).

        Args:
            pathway: Pathway identifier.
            confidence: Confidence value.
        """
        self.pathway_map[pathway] = max(0.0, min(1.0, confidence))
        self.updated_at = datetime.now()

    def get_statistics(self) -> Dict[str, Any]:
        """Return agent statistics."""
        return {
            "agent_id": self.agent_id,
            "execution_count": self.execution_count,
            "num_pathways": len(self.pathway_map),
            "avg_confidence": (
                sum(self.pathway_map.values()) / len(self.pathway_map)
                if self.pathway_map
                else 0.0
            ),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
