# ai/brain_modal/
"""
Recursive Brain - Self-audit and continuous refinement.

Inspired by DREAM architecture - recursive brain for continuous feedback.

First Principle Analysis:
- Recursion: Review → Feedback → Refine → Review (iterative loop)
- Self-audit: System reviews its own decisions
- Mathematical foundation: Recursive algorithms, feedback loops
- Architecture: Recursive system with depth limits and termination conditions
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from .expert_feedback import ExpertFeedbackSystem
from .audit_system import AuditSystem


@dataclass
class RecursiveReview:
    """Represents a recursive review cycle."""
    review_id: str
    target: str  # What is being reviewed
    depth: int = 0
    feedback: List[Dict[str, Any]] = field(default_factory=list)
    refinements: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class RecursiveBrain:
    """
    Recursive brain for self-audit and continuous refinement.
    
    Features:
    - Recursive review cycles
    - Self-audit mechanisms
    - Continuous refinement
    - Depth-limited recursion
    """
    
    def __init__(self,
                 expert_feedback: Optional[ExpertFeedbackSystem] = None,
                 audit_system: Optional[AuditSystem] = None,
                 max_depth: int = 3):
        """
        Initialize recursive brain.
        
        Args:
            expert_feedback: Optional expert feedback system
            audit_system: Optional audit system
            max_depth: Maximum recursion depth
        """
        self.logger = SystemLogger()
        self.expert_feedback = expert_feedback or ExpertFeedbackSystem()
        self.audit_system = audit_system or AuditSystem()
        self.max_depth = max_depth
        self.review_history: List[RecursiveReview] = []
        
        self.logger.log(f"RecursiveBrain initialized (max_depth={max_depth})", level="INFO")
    
    def recursive_review(self,
                       target: str,
                       target_data: Dict[str, Any],
                       depth: int = 0) -> RecursiveReview:
        """
        Perform recursive review.
        
        Mathematical: R(target, depth) = Review(target) + R(Refine(target), depth+1) if depth < max_depth
        
        Args:
            target: Target identifier
            target_data: Target data
            depth: Current recursion depth
            
        Returns:
            RecursiveReview instance
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="RECURSIVE_REVIEW",
            input_data={'target': target, 'depth': depth},
            level=LogLevel.DECISION
        )
        
        try:
            review_id = f"review_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            review = RecursiveReview(
                review_id=review_id,
                target=target,
                depth=depth
            )
            
            # Perform expert feedback review
            if 'cot_log' in target_data:
                feedback_list = self.expert_feedback.review_cot_log(target_data['cot_log'])
                review.feedback = [
                    {
                        'feedback_id': fb.feedback_id,
                        'type': fb.feedback_type,
                        'message': fb.message,
                        'severity': fb.severity
                    }
                    for fb in feedback_list
                ]
            
            # Perform audit
            audit_result = self.audit_system.perform_audit('consistency', target_data)
            review.feedback.append({
                'type': 'audit',
                'findings': audit_result.findings,
                'recommendations': audit_result.recommendations
            })
            
            # Recursive refinement if depth allows
            if depth < self.max_depth and review.feedback:
                # Check if refinement is needed
                critical_feedback = [f for f in review.feedback if f.get('severity') in ['high', 'critical']]
                
                if critical_feedback:
                    # Recursively review refined version
                    refined_data = self._apply_refinements(target_data, review.feedback)
                    refined_review = self.recursive_review(
                        target=f"{target}_refined",
                        target_data=refined_data,
                        depth=depth + 1
                    )
                    review.refinements.append({
                        'review_id': refined_review.review_id,
                        'depth': refined_review.depth,
                        'feedback_count': len(refined_review.feedback)
                    })
            
            self.review_history.append(review)
            
            cot.end_step(
                step_id,
                output_data={'review_id': review_id, 'depth': depth, 'feedback_count': len(review.feedback)},
                validation_passed=len(review.feedback) == 0
            )
            
            self.logger.log(f"Recursive review completed: {review_id} (depth={depth})", level="INFO")
            
            return review
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error in recursive review: {str(e)}", level="ERROR")
            raise
    
    def _apply_refinements(self,
                          target_data: Dict[str, Any],
                          feedback: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Apply refinements based on feedback.
        
        Args:
            target_data: Original target data
            feedback: Feedback list
            
        Returns:
            Refined target data
        """
        refined = target_data.copy()
        
        # Apply refinements based on feedback
        for fb in feedback:
            if fb.get('type') == 'gap' and 'suggestions' in fb:
                # Add missing elements
                for suggestion in fb['suggestions']:
                    if 'validation' in suggestion.lower():
                        refined['has_validation'] = True
        
        return refined
    
    def get_review_history(self) -> List[Dict[str, Any]]:
        """Get review history."""
        return [
            {
                'review_id': review.review_id,
                'target': review.target,
                'depth': review.depth,
                'feedback_count': len(review.feedback),
                'refinements_count': len(review.refinements),
                'created_at': review.created_at.isoformat()
            }
            for review in self.review_history
        ]

