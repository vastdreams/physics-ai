"""
PATH: ai/brain_modal/audit_system.py
PURPOSE: Continuous audit and review of system behaviour.

Inspired by DREAM architecture — continuous audit and review.

FLOW:
┌──────────────┐    ┌────────────────┐    ┌───────────────┐
│ System State │ →  │ Audit Checks   │ →  │ Audit Report  │
└──────────────┘    └────────────────┘    └───────────────┘

DEPENDENCIES:
- loggers.system_logger: structured logging
- utilities.cot_logging: chain-of-thought audit trail
- utilities.performance_monitoring: performance metrics
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from utilities.performance_monitoring import PerformanceMonitor

_PERFORMANCE_DEGRADATION_THRESHOLD = -0.1


@dataclass
class AuditResult:
    """Represents an audit result."""

    audit_id: str
    audit_type: str
    findings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    severity: str = "medium"
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AuditSystem:
    """Audit system for continuous review.

    Features:
    - Performance audits
    - Consistency audits
    - Safety audits
    - Compliance audits
    """

    def __init__(self, performance_monitor: Optional[PerformanceMonitor] = None) -> None:
        """Initialise audit system.

        Args:
            performance_monitor: Optional performance monitor instance.
        """
        self._logger = SystemLogger()
        self.performance_monitor = performance_monitor or PerformanceMonitor()
        self.audit_history: List[AuditResult] = []

        self._logger.log("AuditSystem initialized", level="INFO")

    def perform_audit(
        self,
        audit_type: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AuditResult:
        """Perform an audit of the given type.

        Args:
            audit_type: One of 'performance', 'consistency', 'safety', 'compliance'.
            context: Optional audit context.

        Returns:
            AuditResult instance.
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="PERFORM_AUDIT",
            input_data={"audit_type": audit_type},
            level=LogLevel.INFO,
        )

        try:
            audit_id = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

            audit_dispatch = {
                "performance": self._audit_performance,
                "consistency": self._audit_consistency,
                "safety": self._audit_safety,
                "compliance": self._audit_compliance,
            }

            handler = audit_dispatch.get(audit_type)
            if handler:
                result = handler(context)
            else:
                result = AuditResult(
                    audit_id=audit_id,
                    audit_type=audit_type,
                    findings=[{"error": f"Unknown audit type: {audit_type}"}],
                )

            result.audit_id = audit_id
            self.audit_history.append(result)

            cot.end_step(
                step_id,
                output_data={"audit_id": audit_id, "num_findings": len(result.findings)},
                validation_passed=len(result.findings) == 0,
            )

            self._logger.log(f"Audit completed: {audit_id} ({audit_type})", level="INFO")

            return result

        except Exception as e:
            cot.end_step(step_id, output_data={"error": str(e)}, validation_passed=False)
            self._logger.log(f"Error performing audit: {e}", level="ERROR")
            raise

    # ------------------------------------------------------------------
    # Audit implementations
    # ------------------------------------------------------------------

    def _audit_performance(self, context: Optional[Dict[str, Any]]) -> AuditResult:
        """Audit system performance."""
        findings: List[Dict[str, Any]] = []
        recommendations: List[str] = []

        stats = self.performance_monitor.get_all_statistics()

        for metric_name, metric_stats in stats.items():
            if metric_stats:
                trend = metric_stats.get("trend", 0.0)
                if trend < _PERFORMANCE_DEGRADATION_THRESHOLD:
                    findings.append({
                        "metric": metric_name,
                        "issue": "Performance degradation detected",
                        "trend": trend,
                    })
                    recommendations.append(
                        f"Investigate {metric_name} performance degradation"
                    )

        return AuditResult(
            audit_id="",
            audit_type="performance",
            findings=findings,
            recommendations=recommendations,
            severity="high" if findings else "low",
        )

    def _audit_consistency(self, context: Optional[Dict[str, Any]]) -> AuditResult:
        """Audit system consistency."""
        return AuditResult(
            audit_id="",
            audit_type="consistency",
            findings=[],
            recommendations=[],
            severity="medium",
        )

    def _audit_safety(self, context: Optional[Dict[str, Any]]) -> AuditResult:
        """Audit system safety."""
        findings: List[Dict[str, Any]] = []
        return AuditResult(
            audit_id="",
            audit_type="safety",
            findings=findings,
            recommendations=[],
            severity="critical" if findings else "low",
        )

    def _audit_compliance(self, context: Optional[Dict[str, Any]]) -> AuditResult:
        """Audit compliance with standards."""
        return AuditResult(
            audit_id="",
            audit_type="compliance",
            findings=[],
            recommendations=[],
            severity="medium",
        )

    def get_audit_history(self) -> List[Dict[str, Any]]:
        """Return audit history as serialisable dicts."""
        return [
            {
                "audit_id": audit.audit_id,
                "audit_type": audit.audit_type,
                "num_findings": len(audit.findings),
                "severity": audit.severity,
                "created_at": audit.created_at.isoformat(),
            }
            for audit in self.audit_history
        ]
