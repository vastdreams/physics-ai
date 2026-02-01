# physics/domains/statistical/
"""
Statistical mechanics module.

Implements thermodynamics, ensemble theory, and phase transitions
with synergy factors for quantum corrections.
"""

from .thermodynamics import Thermodynamics
from .ensemble_theory import EnsembleTheory
from .phase_transitions import PhaseTransitions

__all__ = [
    'Thermodynamics',
    'EnsembleTheory',
    'PhaseTransitions'
]

