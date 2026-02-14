"""
PATH: api/services/rule_service.py
PURPOSE: Business logic for rule management operations.
"""

from typing import Any, Dict, List, Optional

from loggers.system_logger import SystemLogger
from rules.enhanced_rule_engine import EnhancedRule, EnhancedRuleEngine, RulePriority
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel


class RuleService:
    """Service layer for rule management."""

    def __init__(self) -> None:
        """Initialise the enhanced rule engine."""
        self._logger = SystemLogger()
        self.rule_engine = EnhancedRuleEngine()
        self._logger.log("RuleService initialized", level="INFO")

    def add_rule(self, rule_data: Dict[str, Any]) -> bool:
        """
        Create and register a new rule.

        Args:
            rule_data: Dictionary with keys ``name``, ``condition``, ``action``,
                       ``priority`` (optional), and ``description`` (optional).

        Returns:
            ``True`` if the rule was added successfully.
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="SERVICE_ADD_RULE",
            input_data={"rule_name": rule_data.get("name")},
            level=LogLevel.INFO,
        )

        try:
            rule = EnhancedRule(
                name=rule_data["name"],
                condition=rule_data.get("condition"),
                action=rule_data.get("action"),
                priority=RulePriority[rule_data.get("priority", "MEDIUM")],
                description=rule_data.get("description", ""),
            )

            success = self.rule_engine.add_enhanced_rule(rule)
            cot.end_step(step_id, output_data={"success": success}, validation_passed=success)
            return success
        except Exception as e:
            cot.end_step(step_id, output_data={"error": str(e)}, validation_passed=False)
            self._logger.log(f"Error in rule service: {e}", level="ERROR")
            raise

    def execute_rules(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute all matching rules against the given context.

        Args:
            context: Data context to evaluate rules against.

        Returns:
            A list of result dictionaries with ``rule_name``, ``success``, and ``result``.
        """
        results = self.rule_engine.execute_enhanced(
            context=context,
            validate_physics=True,
            use_cot=True,
        )
        return [
            {
                "rule_name": r.get("rule_name"),
                "success": r.get("success", False),
                "result": r.get("result"),
            }
            for r in results
        ]

    def get_rule(self, rule_name: str) -> Optional[Dict[str, Any]]:
        """Return details for a single rule, or ``None`` if not found."""
        rule = self.rule_engine.get_enhanced_rule(rule_name)
        if not rule:
            return None

        return {
            "name": rule.name,
            "description": rule.description,
            "priority": rule.priority.value,
            "performance": rule.performance,
        }

    def list_rules(self) -> List[Dict[str, Any]]:
        """Return a summary list of all registered rules."""
        rules = self.rule_engine.get_all_enhanced_rules()
        return [
            {
                "name": rule.name,
                "description": rule.description,
                "priority": rule.priority.value,
            }
            for rule in rules
        ]
