"""
PATH: ai/evolution/engine.py
PURPOSE: Self-evolution engine that coordinates the evolution process

The engine:
1. Generates evolution proposals using LLM
2. Validates proposals
3. Applies approved changes (with human approval gate)
4. Tracks and learns from history
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
import json
import os

from .proposal import (
    EvolutionProposal, 
    ProposalType, 
    ProposalStatus, 
    CodeChange,
    ValidationResult,
)
from .validator import ProposalValidator
from .tracker import EvolutionTracker


@dataclass
class EvolutionConfig:
    """Configuration for the evolution engine."""
    require_human_approval: bool = True
    auto_apply_threshold: float = 0.95  # Confidence needed for auto-apply
    max_pending_proposals: int = 10
    enable_rollback: bool = True
    storage_path: str = "/tmp/physics_ai_evolution"


class SelfEvolutionEngine:
    """
    Main engine for self-evolution.
    
    Coordinates the full evolution lifecycle:
    - Proposal generation
    - Validation
    - Human approval gates
    - Application
    - Rollback if needed
    - Learning from outcomes
    """
    
    def __init__(self, config: Optional[EvolutionConfig] = None):
        """
        Initialize the evolution engine.
        
        Args:
            config: Evolution configuration
        """
        self.config = config or EvolutionConfig()
        self.validator = ProposalValidator()
        self.tracker = EvolutionTracker(self.config.storage_path)
        
        # Approval gates (human-in-the-loop)
        self._approval_callbacks: List[Callable] = []
        
        # Applied changes for rollback
        self._applied_changes: Dict[str, List[Dict]] = {}
    
    def register_approval_callback(self, callback: Callable):
        """Register a callback for human approval."""
        self._approval_callbacks.append(callback)
    
    async def generate_proposal(
        self,
        trigger: str,
        context: Dict[str, Any] = None,
        proposal_type: ProposalType = ProposalType.CODE_IMPROVEMENT,
    ) -> EvolutionProposal:
        """
        Generate an evolution proposal.
        
        Args:
            trigger: What triggered this proposal (error, user request, etc.)
            context: Additional context
            proposal_type: Type of proposal to generate
        
        Returns:
            Generated EvolutionProposal
        """
        # For now, create a structured proposal
        # In full implementation, this would use the LLM to generate
        proposal = EvolutionProposal(
            proposal_type=proposal_type,
            title=f"Evolution triggered by: {trigger}",
            description=f"Auto-generated proposal based on: {trigger}",
            motivation=trigger,
            created_by="evolution_engine",
        )
        
        # Add to tracker
        self.tracker.add_proposal(proposal)
        
        return proposal
    
    def create_equation_proposal(
        self,
        equation_name: str,
        latex: str,
        sympy: str,
        variables: List[tuple],
        domain: str,
        description: str = "",
        motivation: str = "",
    ) -> EvolutionProposal:
        """
        Create a proposal for a new equation.
        
        Args:
            equation_name: Name of the equation
            latex: LaTeX representation
            sympy: SymPy representation
            variables: List of (symbol, name, unit) tuples
            domain: Physics domain
            description: Equation description
            motivation: Why add this equation
        
        Returns:
            EvolutionProposal for the new equation
        """
        # Generate equation ID
        eq_id = equation_name.lower().replace(" ", "_").replace("'", "")
        
        # Generate Python code for the equation
        vars_str = ",\n            ".join([
            f'("{v[0]}", "{v[1]}", "{v[2]}")' for v in variables
        ])
        
        code = f'''EquationNode(
    id="{eq_id}",
    name="{equation_name}",
    description="{description}",
    latex=r"{latex}",
    sympy="{sympy}",
    variables=[
        {vars_str}
    ],
    domain="{domain}",
    tags=["{domain}", "auto_generated"],
)'''
        
        # Create proposal
        proposal = EvolutionProposal(
            proposal_type=ProposalType.NEW_EQUATION,
            title=f"Add {equation_name}",
            description=f"Add the {equation_name} equation to the {domain} domain.",
            motivation=motivation or f"Expand {domain} equation coverage",
            expected_benefit=f"Enable calculations involving {', '.join(v[0] for v in variables)}",
        )
        
        # Add the code change
        # Determine target file based on domain
        domain_file = f"physics/knowledge/equations/{domain.lower()}/equations.py"
        
        proposal.add_change(CodeChange(
            file_path=domain_file,
            change_type="add",
            new_content=code,
            description=f"Add {equation_name} to {domain} equations",
        ))
        
        # Add to tracker
        self.tracker.add_proposal(proposal)
        
        return proposal
    
    def validate_proposal(self, proposal: EvolutionProposal) -> ValidationResult:
        """
        Validate a proposal.
        
        Args:
            proposal: Proposal to validate
        
        Returns:
            ValidationResult with pass/fail and details
        """
        proposal.status = ProposalStatus.VALIDATING
        self.tracker.update_proposal(proposal)
        
        result = self.validator.validate(proposal)
        proposal.set_validation(result)
        self.tracker.update_proposal(proposal)
        
        return result
    
    async def request_approval(self, proposal: EvolutionProposal) -> bool:
        """
        Request human approval for a proposal.
        
        Args:
            proposal: Proposal needing approval
        
        Returns:
            True if approved, False if rejected
        """
        if not self.config.require_human_approval:
            # Auto-approve if high confidence
            if proposal.validation_result and \
               proposal.validation_result.confidence >= self.config.auto_apply_threshold:
                return True
        
        # Call approval callbacks
        for callback in self._approval_callbacks:
            try:
                approved = await callback(proposal)
                if not approved:
                    return False
            except Exception:
                pass
        
        return True
    
    def apply_proposal(self, proposal: EvolutionProposal) -> bool:
        """
        Apply an approved proposal.
        
        Args:
            proposal: Approved proposal to apply
        
        Returns:
            True if successfully applied
        """
        if proposal.status != ProposalStatus.APPROVED:
            raise ValueError("Can only apply approved proposals")
        
        applied_changes = []
        
        try:
            for change in proposal.changes:
                # Store original for rollback
                original = None
                if os.path.exists(change.file_path):
                    with open(change.file_path, "r") as f:
                        original = f.read()
                
                applied_changes.append({
                    "file_path": change.file_path,
                    "original": original,
                    "change_type": change.change_type,
                })
                
                # Apply change
                if change.change_type == "add":
                    # Append to file or create new
                    mode = "a" if os.path.exists(change.file_path) else "w"
                    with open(change.file_path, mode) as f:
                        f.write("\n" + change.new_content + "\n")
                
                elif change.change_type == "modify":
                    if original and change.old_content:
                        new_content = original.replace(change.old_content, change.new_content)
                        with open(change.file_path, "w") as f:
                            f.write(new_content)
                
                elif change.change_type == "delete":
                    if os.path.exists(change.file_path):
                        os.remove(change.file_path)
            
            # Store for potential rollback
            self._applied_changes[proposal.id] = applied_changes
            
            proposal.apply()
            self.tracker.update_proposal(proposal)
            
            return True
            
        except Exception as e:
            # Rollback on failure
            self._rollback_changes(applied_changes)
            proposal.status = ProposalStatus.REJECTED
            if proposal.validation_result:
                proposal.validation_result.errors.append(f"Apply failed: {str(e)}")
            self.tracker.update_proposal(proposal)
            return False
    
    def _rollback_changes(self, changes: List[Dict]):
        """Rollback a list of changes."""
        for change in reversed(changes):
            try:
                if change["original"] is not None:
                    with open(change["file_path"], "w") as f:
                        f.write(change["original"])
                elif change["change_type"] == "add":
                    # Remove the file if it was added
                    if os.path.exists(change["file_path"]):
                        os.remove(change["file_path"])
            except Exception:
                pass
    
    def rollback_proposal(self, proposal_id: str) -> bool:
        """
        Rollback an applied proposal.
        
        Args:
            proposal_id: ID of proposal to rollback
        
        Returns:
            True if successfully rolled back
        """
        proposal = self.tracker.get_proposal(proposal_id)
        if not proposal:
            return False
        
        if proposal.status != ProposalStatus.APPLIED:
            return False
        
        if proposal_id not in self._applied_changes:
            return False
        
        self._rollback_changes(self._applied_changes[proposal_id])
        proposal.rollback()
        self.tracker.update_proposal(proposal)
        
        del self._applied_changes[proposal_id]
        
        return True
    
    def rate_proposal(self, proposal_id: str, rating: int, feedback: str = ""):
        """
        Rate a proposal for learning.
        
        Args:
            proposal_id: ID of proposal to rate
            rating: 1-5 rating
            feedback: Optional feedback text
        """
        proposal = self.tracker.get_proposal(proposal_id)
        if proposal:
            proposal.rating = max(1, min(5, rating))
            proposal.feedback = feedback
            self.tracker.update_proposal(proposal)
    
    def get_evolution_status(self) -> Dict[str, Any]:
        """Get current evolution system status."""
        metrics = self.tracker.get_metrics()
        pending = self.tracker.get_pending_proposals()
        
        return {
            "metrics": metrics.to_dict(),
            "pending_count": len(pending),
            "pending_proposals": [p.to_dict() for p in pending[:5]],
            "recent_patterns": {
                "success": self.tracker.get_successful_patterns(),
                "failure": self.tracker.get_failure_patterns(),
            },
            "config": {
                "require_human_approval": self.config.require_human_approval,
                "auto_apply_threshold": self.config.auto_apply_threshold,
            }
        }
    
    def get_proposal_history(
        self,
        limit: int = 50,
        status: Optional[ProposalStatus] = None,
    ) -> List[Dict[str, Any]]:
        """Get proposal history."""
        proposals = self.tracker.get_all_proposals(status=status, limit=limit)
        return [p.to_dict() for p in proposals]


# Global engine instance
_engine: Optional[SelfEvolutionEngine] = None


def get_evolution_engine() -> SelfEvolutionEngine:
    """Get or create the global evolution engine."""
    global _engine
    if _engine is None:
        _engine = SelfEvolutionEngine()
    return _engine
