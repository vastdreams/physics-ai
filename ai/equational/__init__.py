# ai/equational/
"""
Equational AI System for Research Ingestion and Equation Generation.

Inspired by DREAM architecture - equational memory through research ingestion.

First Principle Analysis:
- Research ingestion: Parse papers → Extract equations → Validate → Store
- Equation store: Knowledge base of physics equations
- Permanence: Pre-computed equational states
- Mathematical foundation: Equation parsing, validation, knowledge graphs
- Architecture: Modular system for research → equations → physics integration
"""

from .research_ingestion import ResearchIngestion
from .equation_extractor import EquationExtractor
from .equation_store import EquationStore
from .equation_validator import EquationValidator

__all__ = [
    'ResearchIngestion',
    'EquationExtractor',
    'EquationStore',
    'EquationValidator'
]

