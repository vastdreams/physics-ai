"""
PATH: ai/evolution/tracker.py
PURPOSE: Track evolution history and learn from past proposals
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import json
import os

from .proposal import EvolutionProposal, ProposalStatus, ProposalType


@dataclass
class EvolutionMetrics:
    """Metrics about system evolution."""
    total_proposals: int = 0
    approved_proposals: int = 0
    rejected_proposals: int = 0
    applied_proposals: int = 0
    rolled_back: int = 0
    
    # By type
    by_type: Dict[str, int] = field(default_factory=dict)
    
    # Success rates
    approval_rate: float = 0.0
    application_rate: float = 0.0
    
    # Averages
    avg_rating: float = 0.0
    avg_changes_per_proposal: float = 0.0
    
    def update(self, proposals: List[EvolutionProposal]):
        """Update metrics from proposal list."""
        self.total_proposals = len(proposals)
        
        self.approved_proposals = sum(
            1 for p in proposals if p.status == ProposalStatus.APPROVED
        )
        self.rejected_proposals = sum(
            1 for p in proposals if p.status == ProposalStatus.REJECTED
        )
        self.applied_proposals = sum(
            1 for p in proposals if p.status == ProposalStatus.APPLIED
        )
        self.rolled_back = sum(
            1 for p in proposals if p.status == ProposalStatus.ROLLED_BACK
        )
        
        # By type
        self.by_type = {}
        for p in proposals:
            t = p.proposal_type.value
            self.by_type[t] = self.by_type.get(t, 0) + 1
        
        # Rates
        if self.total_proposals > 0:
            self.approval_rate = (self.approved_proposals + self.applied_proposals) / self.total_proposals
        if self.approved_proposals > 0:
            self.application_rate = self.applied_proposals / self.approved_proposals
        
        # Averages
        rated = [p for p in proposals if p.rating is not None]
        if rated:
            self.avg_rating = sum(p.rating for p in rated) / len(rated)
        
        if proposals:
            self.avg_changes_per_proposal = sum(len(p.changes) for p in proposals) / len(proposals)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_proposals": self.total_proposals,
            "approved_proposals": self.approved_proposals,
            "rejected_proposals": self.rejected_proposals,
            "applied_proposals": self.applied_proposals,
            "rolled_back": self.rolled_back,
            "by_type": self.by_type,
            "approval_rate": self.approval_rate,
            "application_rate": self.application_rate,
            "avg_rating": self.avg_rating,
            "avg_changes_per_proposal": self.avg_changes_per_proposal,
        }


class EvolutionTracker:
    """
    Tracks evolution history and provides insights.
    
    Maintains a history of all proposals and their outcomes
    to enable learning and improvement over time.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize tracker.
        
        Args:
            storage_path: Path to store evolution history
        """
        self.storage_path = storage_path or "/tmp/physics_ai_evolution"
        self.proposals: Dict[str, EvolutionProposal] = {}
        self.metrics = EvolutionMetrics()
        
        # Ensure storage directory exists
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Load existing history
        self._load_history()
    
    def _load_history(self):
        """Load evolution history from storage."""
        history_file = os.path.join(self.storage_path, "history.json")
        if os.path.exists(history_file):
            try:
                with open(history_file, "r") as f:
                    data = json.load(f)
                for prop_data in data.get("proposals", []):
                    prop = EvolutionProposal.from_dict(prop_data)
                    self.proposals[prop.id] = prop
                self._update_metrics()
            except Exception as e:
                print(f"Warning: Could not load evolution history: {e}")
    
    def _save_history(self):
        """Save evolution history to storage."""
        history_file = os.path.join(self.storage_path, "history.json")
        try:
            data = {
                "proposals": [p.to_dict() for p in self.proposals.values()],
                "metrics": self.metrics.to_dict(),
                "saved_at": datetime.now().isoformat(),
            }
            with open(history_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save evolution history: {e}")
    
    def _update_metrics(self):
        """Update metrics from current proposals."""
        self.metrics.update(list(self.proposals.values()))
    
    def add_proposal(self, proposal: EvolutionProposal) -> str:
        """Add a new proposal to tracking."""
        self.proposals[proposal.id] = proposal
        self._update_metrics()
        self._save_history()
        return proposal.id
    
    def get_proposal(self, proposal_id: str) -> Optional[EvolutionProposal]:
        """Get a proposal by ID."""
        return self.proposals.get(proposal_id)
    
    def update_proposal(self, proposal: EvolutionProposal):
        """Update an existing proposal."""
        if proposal.id in self.proposals:
            self.proposals[proposal.id] = proposal
            self._update_metrics()
            self._save_history()
    
    def get_all_proposals(
        self,
        status: Optional[ProposalStatus] = None,
        proposal_type: Optional[ProposalType] = None,
        limit: int = 100,
    ) -> List[EvolutionProposal]:
        """Get proposals with optional filtering."""
        proposals = list(self.proposals.values())
        
        if status:
            proposals = [p for p in proposals if p.status == status]
        if proposal_type:
            proposals = [p for p in proposals if p.proposal_type == proposal_type]
        
        # Sort by creation date (newest first)
        proposals.sort(key=lambda p: p.created_at, reverse=True)
        
        return proposals[:limit]
    
    def get_pending_proposals(self) -> List[EvolutionProposal]:
        """Get all pending proposals."""
        return self.get_all_proposals(status=ProposalStatus.PENDING)
    
    def get_metrics(self) -> EvolutionMetrics:
        """Get current evolution metrics."""
        return self.metrics
    
    def get_successful_patterns(self) -> List[Dict[str, Any]]:
        """
        Analyze successful proposals to find patterns.
        
        Returns insights about what types of changes succeed.
        """
        successful = [
            p for p in self.proposals.values()
            if p.status == ProposalStatus.APPLIED and p.rating and p.rating >= 4
        ]
        
        patterns = []
        
        # Analyze by type
        type_success = {}
        for p in successful:
            t = p.proposal_type.value
            type_success[t] = type_success.get(t, 0) + 1
        
        if type_success:
            best_type = max(type_success, key=type_success.get)
            patterns.append({
                "pattern": "successful_type",
                "type": best_type,
                "count": type_success[best_type],
            })
        
        # Analyze change size
        small_changes = [p for p in successful if len(p.changes) <= 2]
        large_changes = [p for p in successful if len(p.changes) > 5]
        
        if len(small_changes) > len(large_changes):
            patterns.append({
                "pattern": "change_size",
                "insight": "Small, focused changes tend to succeed more",
                "small_success": len(small_changes),
                "large_success": len(large_changes),
            })
        
        return patterns
    
    def get_failure_patterns(self) -> List[Dict[str, Any]]:
        """
        Analyze failed proposals to find patterns.
        
        Returns insights about what causes rejections.
        """
        failed = [
            p for p in self.proposals.values()
            if p.status == ProposalStatus.REJECTED
        ]
        
        patterns = []
        
        # Common errors
        error_counts = {}
        for p in failed:
            if p.validation_result:
                for error in p.validation_result.errors:
                    # Extract error category
                    category = error.split(":")[0] if ":" in error else "Other"
                    error_counts[category] = error_counts.get(category, 0) + 1
        
        if error_counts:
            most_common = max(error_counts, key=error_counts.get)
            patterns.append({
                "pattern": "common_error",
                "error_type": most_common,
                "count": error_counts[most_common],
            })
        
        return patterns
    
    def get_timeline(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get evolution timeline for the last N days."""
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        timeline = []
        for p in self.proposals.values():
            if p.created_at.timestamp() >= cutoff:
                timeline.append({
                    "date": p.created_at.isoformat(),
                    "id": p.id,
                    "title": p.title,
                    "type": p.proposal_type.value,
                    "status": p.status.value,
                })
        
        timeline.sort(key=lambda x: x["date"])
        return timeline
