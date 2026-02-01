# ai/brain_modal/
"""
Brain Modal System for Expert Feedback and Recursive Audit.

Inspired by DREAM architecture - Brain LLM trained on expert thought processes.

First Principle Analysis:
- Brain modal: B = {feedback_loop, audit_system, recursive_review}
- Expert feedback: Review CoT logs → Provide expert-level feedback
- Recursive brain: Self-audit and continuous refinement
- Mathematical foundation: Feedback loops, audit trails, recursive algorithms
- Architecture: Modular brain system with expert feedback integration
"""

from .expert_feedback import ExpertFeedback, ExpertFeedbackSystem
from .audit_system import AuditSystem
from .recursive_brain import RecursiveBrain
from .feedback_processor import FeedbackProcessor

__all__ = [
    'ExpertFeedback',
    'ExpertFeedbackSystem',
    'AuditSystem',
    'RecursiveBrain',
    'FeedbackProcessor'
]

