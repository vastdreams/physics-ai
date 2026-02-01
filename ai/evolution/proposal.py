"""
PATH: ai/evolution/proposal.py
PURPOSE: Evolution proposal data structures

An EvolutionProposal represents a suggested improvement to the system,
which must be validated before being applied.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
import json


class ProposalType(Enum):
    """Types of evolution proposals."""
    NEW_EQUATION = "new_equation"           # Add new physics equation
    EQUATION_CORRECTION = "equation_fix"    # Fix existing equation
    NEW_RULE = "new_rule"                   # Add inference rule
    RULE_OPTIMIZATION = "rule_opt"          # Optimize rule
    CODE_IMPROVEMENT = "code_improvement"   # General code improvement
    ALGORITHM_ENHANCEMENT = "algorithm"     # Better algorithm
    NEW_FEATURE = "new_feature"             # New capability
    BUG_FIX = "bug_fix"                     # Fix a bug
    PERFORMANCE = "performance"             # Performance improvement
    DOCUMENTATION = "documentation"         # Doc improvement


class ProposalStatus(Enum):
    """Status of an evolution proposal."""
    DRAFT = "draft"                 # Being formulated
    PENDING = "pending"             # Awaiting validation
    VALIDATING = "validating"       # Under validation
    APPROVED = "approved"           # Passed validation
    REJECTED = "rejected"           # Failed validation
    APPLIED = "applied"             # Successfully applied
    ROLLED_BACK = "rolled_back"     # Was applied but reverted


@dataclass
class CodeChange:
    """A specific code change within a proposal."""
    file_path: str
    change_type: str  # "add", "modify", "delete"
    old_content: Optional[str] = None
    new_content: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "change_type": self.change_type,
            "old_content": self.old_content,
            "new_content": self.new_content,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "description": self.description,
        }


@dataclass
class ValidationResult:
    """Result of validating a proposal."""
    passed: bool
    checks: Dict[str, bool] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "checks": self.checks,
            "errors": self.errors,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
            "confidence": self.confidence,
        }


@dataclass
class EvolutionProposal:
    """
    A proposal for system evolution.
    
    The AI generates proposals which are then validated
    before being applied to the system.
    """
    # Identity
    id: str = field(default_factory=lambda: f"prop_{uuid.uuid4().hex[:8]}")
    
    # Content
    title: str = ""
    description: str = ""
    proposal_type: ProposalType = ProposalType.CODE_IMPROVEMENT
    
    # Changes
    changes: List[CodeChange] = field(default_factory=list)
    
    # Rationale
    motivation: str = ""
    expected_benefit: str = ""
    risks: List[str] = field(default_factory=list)
    
    # Status
    status: ProposalStatus = ProposalStatus.DRAFT
    validation_result: Optional[ValidationResult] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"  # "system", "user", or agent name
    
    # For learning
    feedback: Optional[str] = None
    rating: Optional[int] = None  # 1-5
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)
    blocks: List[str] = field(default_factory=list)
    
    def add_change(self, change: CodeChange):
        """Add a code change to this proposal."""
        self.changes.append(change)
        self.updated_at = datetime.now()
    
    def set_validation(self, result: ValidationResult):
        """Set validation result and update status."""
        self.validation_result = result
        self.status = ProposalStatus.APPROVED if result.passed else ProposalStatus.REJECTED
        self.updated_at = datetime.now()
    
    def apply(self):
        """Mark proposal as applied."""
        if self.status != ProposalStatus.APPROVED:
            raise ValueError("Can only apply approved proposals")
        self.status = ProposalStatus.APPLIED
        self.updated_at = datetime.now()
    
    def rollback(self):
        """Mark proposal as rolled back."""
        if self.status != ProposalStatus.APPLIED:
            raise ValueError("Can only rollback applied proposals")
        self.status = ProposalStatus.ROLLED_BACK
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "proposal_type": self.proposal_type.value,
            "changes": [c.to_dict() for c in self.changes],
            "motivation": self.motivation,
            "expected_benefit": self.expected_benefit,
            "risks": self.risks,
            "status": self.status.value,
            "validation_result": self.validation_result.to_dict() if self.validation_result else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "feedback": self.feedback,
            "rating": self.rating,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvolutionProposal":
        """Create proposal from dictionary."""
        proposal = cls(
            id=data.get("id", f"prop_{uuid.uuid4().hex[:8]}"),
            title=data.get("title", ""),
            description=data.get("description", ""),
            proposal_type=ProposalType(data.get("proposal_type", "code_improvement")),
            motivation=data.get("motivation", ""),
            expected_benefit=data.get("expected_benefit", ""),
            risks=data.get("risks", []),
            status=ProposalStatus(data.get("status", "draft")),
            created_by=data.get("created_by", "system"),
        )
        
        for change_data in data.get("changes", []):
            proposal.add_change(CodeChange(**change_data))
        
        return proposal
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


# Proposal templates for common evolutions
PROPOSAL_TEMPLATES = {
    "new_equation": {
        "title": "Add {equation_name} Equation",
        "description": "Add the {equation_name} equation to the {domain} domain.",
        "motivation": "This equation is fundamental to {domain} physics.",
        "expected_benefit": "Enables calculations involving {variables}.",
    },
    "bug_fix": {
        "title": "Fix {bug_description}",
        "description": "Correct the issue where {detailed_description}.",
        "motivation": "Current behavior is incorrect because {reason}.",
        "expected_benefit": "System will now correctly {correct_behavior}.",
    },
    "performance": {
        "title": "Optimize {component}",
        "description": "Improve performance of {component} by {method}.",
        "motivation": "Current implementation is slow due to {cause}.",
        "expected_benefit": "Expected {speedup}x speedup for {operation}.",
    },
}
