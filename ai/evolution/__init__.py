"""
PATH: ai/evolution/__init__.py
PURPOSE: Self-evolution system for Physics AI

The AI can:
1. Propose improvements to its own codebase
2. Validate proposals through tests and checks
3. Track evolution history
4. Learn from feedback
"""

from .proposal import EvolutionProposal, ProposalType, ProposalStatus
from .validator import ProposalValidator
from .tracker import EvolutionTracker
from .engine import SelfEvolutionEngine

__all__ = [
    'EvolutionProposal',
    'ProposalType',
    'ProposalStatus',
    'ProposalValidator',
    'EvolutionTracker',
    'SelfEvolutionEngine',
]
