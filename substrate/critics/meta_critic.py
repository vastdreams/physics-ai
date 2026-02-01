# PATH: substrate/critics/meta_critic.py
# PURPOSE:
#   - Evaluates the performance of other critics
#   - Identifies blind spots and over-flagging patterns
#   - Tunes critic behavior over time
#
# ROLE IN ARCHITECTURE:
#   - Top of the audit stack
#   - Ensures critics are useful, not just noisy
#
# MAIN EXPORTS:
#   - MetaCritic: Main meta-critic class
#
# NON-RESPONSIBILITIES:
#   - Does NOT directly analyze physics or code
#   - Does NOT apply changes (that's evolution)
#
# NOTES FOR FUTURE AI:
#   - Track critic accuracy over time
#   - Penalize critics that always/never find issues
#   - Learn from resolved vs dismissed issues

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
from collections import defaultdict
import json
import uuid

from substrate.critics.local_llm import LocalLLMBackend, LLMResponse
from substrate.critics.logic_critic import LogicCritic, LogicIssue
from substrate.critics.code_critic import CodeCritic, CodeIssue
from substrate.memory.reasoning_trace import ReasoningTrace, CriticAnnotation


@dataclass
class CriticPerformance:
    """Performance metrics for a critic."""
    
    critic_id: str
    critic_type: str  # "logic", "code"
    
    # Counts
    total_analyses: int = 0
    total_issues_found: int = 0
    
    # Outcome tracking
    issues_confirmed: int = 0      # Issues that were validated/fixed
    issues_dismissed: int = 0      # Issues that were false positives
    issues_pending: int = 0        # Issues not yet resolved
    
    # By severity
    by_severity: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    # By type
    by_type: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    # Recent history for pattern detection
    recent_issues: List[Dict[str, Any]] = field(default_factory=list)
    
    def precision(self) -> float:
        """Compute precision (true positives / all positives)."""
        total = self.issues_confirmed + self.issues_dismissed
        if total == 0:
            return 0.5  # Unknown
        return self.issues_confirmed / total
    
    def issue_rate(self) -> float:
        """Compute average issues per analysis."""
        if self.total_analyses == 0:
            return 0.0
        return self.total_issues_found / self.total_analyses
    
    def severity_distribution(self) -> Dict[str, float]:
        """Compute distribution of issue severities."""
        total = sum(self.by_severity.values())
        if total == 0:
            return {}
        return {k: v / total for k, v in self.by_severity.items()}
    
    def record_analysis(self, num_issues: int, issues: List[Dict[str, Any]]):
        """Record an analysis."""
        self.total_analyses += 1
        self.total_issues_found += num_issues
        self.issues_pending += num_issues
        
        for issue in issues:
            severity = issue.get("severity", "warning")
            issue_type = issue.get("type", "unknown")
            self.by_severity[severity] += 1
            self.by_type[issue_type] += 1
            
            self.recent_issues.append({
                "timestamp": datetime.now().isoformat(),
                "severity": severity,
                "type": issue_type,
                "message": issue.get("message", "")[:100],
            })
        
        # Keep recent history bounded
        if len(self.recent_issues) > 500:
            self.recent_issues = self.recent_issues[-250:]
    
    def record_outcome(self, confirmed: bool):
        """Record the outcome of an issue."""
        self.issues_pending = max(0, self.issues_pending - 1)
        if confirmed:
            self.issues_confirmed += 1
        else:
            self.issues_dismissed += 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "critic_id": self.critic_id,
            "critic_type": self.critic_type,
            "total_analyses": self.total_analyses,
            "total_issues_found": self.total_issues_found,
            "issues_confirmed": self.issues_confirmed,
            "issues_dismissed": self.issues_dismissed,
            "issues_pending": self.issues_pending,
            "precision": self.precision(),
            "issue_rate": self.issue_rate(),
            "by_severity": dict(self.by_severity),
            "by_type": dict(self.by_type),
        }


@dataclass
class MetaIssue:
    """An issue found with a critic's behavior."""
    
    issue_type: str  # "over_flagging", "under_flagging", "inconsistent", etc.
    severity: str
    message: str
    
    critic_id: str
    
    # Evidence
    evidence: str = ""
    confidence: float = 1.0
    
    # Suggestions
    suggestion: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "issue_type": self.issue_type,
            "severity": self.severity,
            "message": self.message,
            "critic_id": self.critic_id,
            "evidence": self.evidence,
            "confidence": self.confidence,
            "suggestion": self.suggestion,
        }


class MetaCritic:
    """
    Meta-critic that evaluates and tunes other critics.
    
    Responsibilities:
    - Track critic performance over time
    - Identify over-flagging and under-flagging patterns
    - Detect inconsistencies between critics
    - Suggest prompt/parameter adjustments
    - Learn from issue resolution outcomes
    """
    
    def __init__(
        self,
        llm_backend: LocalLLMBackend,
        critic_id: Optional[str] = None
    ):
        self.llm = llm_backend
        self.critic_id = critic_id or f"meta_critic_{uuid.uuid4().hex[:8]}"
        
        # Track critic performance
        self._critic_performance: Dict[str, CriticPerformance] = {}
        
        # Track issue patterns
        self._issue_patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Configuration recommendations
        self._recommendations: List[Dict[str, Any]] = []
    
    def register_critic(self, critic_id: str, critic_type: str):
        """Register a critic to track."""
        if critic_id not in self._critic_performance:
            self._critic_performance[critic_id] = CriticPerformance(
                critic_id=critic_id,
                critic_type=critic_type,
            )
    
    def record_analysis(
        self,
        critic_id: str,
        issues: List[Dict[str, Any]]
    ):
        """Record that a critic performed an analysis."""
        if critic_id in self._critic_performance:
            self._critic_performance[critic_id].record_analysis(
                num_issues=len(issues),
                issues=issues,
            )
    
    def record_outcome(self, critic_id: str, confirmed: bool):
        """Record whether an issue was confirmed or dismissed."""
        if critic_id in self._critic_performance:
            self._critic_performance[critic_id].record_outcome(confirmed)
    
    def evaluate_critics(self) -> List[MetaIssue]:
        """
        Evaluate all registered critics for problems.
        
        Returns:
            List of MetaIssues found
        """
        issues = []
        
        for critic_id, perf in self._critic_performance.items():
            issues.extend(self._evaluate_critic(perf))
        
        # Cross-critic analysis
        issues.extend(self._cross_critic_analysis())
        
        return issues
    
    def _evaluate_critic(self, perf: CriticPerformance) -> List[MetaIssue]:
        """Evaluate a single critic's performance."""
        issues = []
        
        # Check for over-flagging
        if perf.total_analyses >= 10:
            precision = perf.precision()
            if precision < 0.3:
                issues.append(MetaIssue(
                    issue_type="over_flagging",
                    severity="warning",
                    message=f"Critic {perf.critic_id} has low precision ({precision:.2f})",
                    critic_id=perf.critic_id,
                    evidence=f"Confirmed: {perf.issues_confirmed}, Dismissed: {perf.issues_dismissed}",
                    suggestion="Consider raising severity thresholds or improving prompts",
                ))
            
            # Check for under-flagging (never finds anything)
            issue_rate = perf.issue_rate()
            if issue_rate < 0.1 and perf.total_analyses > 20:
                issues.append(MetaIssue(
                    issue_type="under_flagging",
                    severity="info",
                    message=f"Critic {perf.critic_id} rarely finds issues ({issue_rate:.2f} per analysis)",
                    critic_id=perf.critic_id,
                    suggestion="May need more aggressive checking or expanded scope",
                ))
            
            # Check for severity inflation
            severity_dist = perf.severity_distribution()
            if severity_dist.get("critical", 0) > 0.3:
                issues.append(MetaIssue(
                    issue_type="severity_inflation",
                    severity="warning",
                    message=f"Critic {perf.critic_id} marks too many issues as critical",
                    critic_id=perf.critic_id,
                    evidence=f"Critical: {severity_dist.get('critical', 0):.1%}",
                    suggestion="Recalibrate severity thresholds",
                ))
            
            # Check for type concentration
            if perf.by_type:
                total_typed = sum(perf.by_type.values())
                for issue_type, count in perf.by_type.items():
                    if count / total_typed > 0.7 and total_typed > 10:
                        issues.append(MetaIssue(
                            issue_type="type_concentration",
                            severity="info",
                            message=f"Critic {perf.critic_id} mostly finds '{issue_type}' issues ({count}/{total_typed})",
                            critic_id=perf.critic_id,
                            suggestion="May be too narrowly focused",
                        ))
        
        return issues
    
    def _cross_critic_analysis(self) -> List[MetaIssue]:
        """Analyze patterns across critics."""
        issues = []
        
        # Group by type
        logic_critics = [p for p in self._critic_performance.values() if p.critic_type == "logic"]
        code_critics = [p for p in self._critic_performance.values() if p.critic_type == "code"]
        
        # Check for inconsistency between similar critics
        for group in [logic_critics, code_critics]:
            if len(group) < 2:
                continue
            
            precisions = [c.precision() for c in group if c.total_analyses >= 10]
            if precisions:
                max_p, min_p = max(precisions), min(precisions)
                if max_p - min_p > 0.4:
                    issues.append(MetaIssue(
                        issue_type="critic_inconsistency",
                        severity="warning",
                        message=f"Large precision variance among {group[0].critic_type} critics",
                        critic_id="meta",
                        evidence=f"Precision range: {min_p:.2f} to {max_p:.2f}",
                        suggestion="Standardize critic configurations",
                    ))
        
        return issues
    
    def analyze_trace_critiques(
        self,
        trace: ReasoningTrace,
        logic_issues: List[LogicIssue],
        code_issues: List[CodeIssue]
    ) -> List[MetaIssue]:
        """
        Analyze the critiques made on a trace for meta-issues.
        
        This checks if critics are being consistent and useful.
        """
        issues = []
        
        # Check for contradiction between critics
        logic_severities = {i.severity for i in logic_issues}
        code_severities = {i.severity for i in code_issues}
        
        # If logic says critical but code says nothing, might be missing something
        if "critical" in logic_severities and not code_issues:
            issues.append(MetaIssue(
                issue_type="potential_gap",
                severity="info",
                message="Logic critic found critical issue but code critic found nothing",
                critic_id="meta",
                suggestion="Code implementation of critical logic issue may need review",
            ))
        
        # Check for redundant issues
        all_messages = [i.message.lower() for i in logic_issues] + [i.message.lower() for i in code_issues]
        seen_messages = set()
        duplicates = 0
        for msg in all_messages:
            # Simple similarity check
            msg_key = " ".join(sorted(msg.split()[:5]))
            if msg_key in seen_messages:
                duplicates += 1
            seen_messages.add(msg_key)
        
        if duplicates > 2:
            issues.append(MetaIssue(
                issue_type="redundant_issues",
                severity="info",
                message=f"Multiple critics flagging similar issues ({duplicates} potential duplicates)",
                critic_id="meta",
                suggestion="Consider deduplication or critic scope separation",
            ))
        
        return issues
    
    def suggest_improvements(self) -> List[Dict[str, Any]]:
        """
        Generate suggestions for improving critics.
        
        Uses LLM to analyze patterns and suggest prompt/config changes.
        """
        suggestions = []
        
        # Gather performance data
        perf_summaries = [p.to_dict() for p in self._critic_performance.values()]
        
        if not perf_summaries:
            return suggestions
        
        prompt = f"""Analyze these critic performance metrics and suggest improvements:

{json.dumps(perf_summaries, indent=2)}

Consider:
1. Critics with low precision need stricter criteria
2. Critics that rarely find issues may need broader scope
3. Severity distributions should match actual impact

Respond with JSON:
{{
    "suggestions": [
        {{
            "critic_id": "which critic",
            "change_type": "prompt|threshold|scope|disable",
            "description": "what to change",
            "rationale": "why this helps"
        }}
    ]
}}"""

        response = self.llm.generate(
            prompt,
            system_prompt="You are an expert at tuning automated review systems. Be specific and actionable.",
        )
        
        try:
            text = response.text.strip()
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            
            data = json.loads(text)
            suggestions = data.get("suggestions", [])
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
        
        self._recommendations = suggestions
        return suggestions
    
    def get_critic_config_adjustment(
        self,
        critic_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get recommended configuration adjustments for a critic.
        
        Returns adjustment parameters or None if no adjustment needed.
        """
        perf = self._critic_performance.get(critic_id)
        if not perf or perf.total_analyses < 10:
            return None
        
        adjustments = {}
        
        precision = perf.precision()
        issue_rate = perf.issue_rate()
        
        # Adjust based on precision
        if precision < 0.3:
            adjustments["raise_threshold"] = True
            adjustments["min_confidence"] = 0.8
        elif precision > 0.9:
            adjustments["lower_threshold"] = True
            adjustments["min_confidence"] = 0.5
        
        # Adjust based on issue rate
        if issue_rate < 0.1:
            adjustments["expand_checks"] = True
        elif issue_rate > 5.0:
            adjustments["reduce_checks"] = True
        
        # Specific type adjustments
        if perf.by_type:
            total = sum(perf.by_type.values())
            for issue_type, count in perf.by_type.items():
                if count / total > 0.5:
                    adjustments["focus_type"] = issue_type
        
        return adjustments if adjustments else None
    
    def generate_report(self) -> str:
        """Generate a human-readable report on critic performance."""
        lines = ["=" * 60, "META-CRITIC REPORT", "=" * 60, ""]
        
        for critic_id, perf in self._critic_performance.items():
            lines.append(f"Critic: {critic_id} ({perf.critic_type})")
            lines.append(f"  Analyses: {perf.total_analyses}")
            lines.append(f"  Issues found: {perf.total_issues_found}")
            lines.append(f"  Precision: {perf.precision():.2f}")
            lines.append(f"  Issue rate: {perf.issue_rate():.2f}")
            
            if perf.by_severity:
                lines.append(f"  By severity: {dict(perf.by_severity)}")
            
            lines.append("")
        
        # Add meta-issues
        meta_issues = self.evaluate_critics()
        if meta_issues:
            lines.append("META-ISSUES FOUND:")
            for issue in meta_issues:
                lines.append(f"  [{issue.severity}] {issue.issue_type}: {issue.message}")
            lines.append("")
        
        # Add recommendations
        if self._recommendations:
            lines.append("RECOMMENDATIONS:")
            for rec in self._recommendations:
                lines.append(f"  - {rec.get('critic_id', 'unknown')}: {rec.get('description', '')}")
            lines.append("")
        
        lines.append("=" * 60)
        return "\n".join(lines)
    
    def statistics(self) -> Dict[str, Any]:
        """Get meta-critic statistics."""
        return {
            "critic_id": self.critic_id,
            "tracked_critics": len(self._critic_performance),
            "total_recommendations": len(self._recommendations),
            "critic_summaries": {
                k: v.to_dict() for k, v in self._critic_performance.items()
            },
        }

