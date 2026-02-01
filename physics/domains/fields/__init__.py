# physics/domains/fields/
"""
Field theory module.

Implements electromagnetic fields, gauge theories, and general relativity
with synergy factors for quantum corrections.
"""

from .electromagnetic import ElectromagneticField
from .gauge_theory import GaugeTheory
from .general_relativity import GeneralRelativity

__all__ = [
    'ElectromagneticField',
    'GaugeTheory',
    'GeneralRelativity'
]

