"""
PATH: ai/rubric/__init__.py
PURPOSE: Rubric Quality Gates system for Beyond Frontier

Implements rubric-based multidimensional evaluation
inspired by RubricHub, LLM-Rubric (Microsoft/ACL 2024),
and PEARL frameworks.
"""

from ai.rubric.definitions import (
    RubricDimension,
    RubricLevel,
    RubricQuestion,
    Rubric,
    PHYSICS_RUBRIC,
    get_rubric_for_domain,
)
from ai.rubric.evaluator import RubricEvaluator, RubricScore, RubricReport
from ai.rubric.quality_gate import QualityGate, GateDecision, GateVerdict

__all__ = [
    "RubricDimension",
    "RubricLevel",
    "RubricQuestion",
    "Rubric",
    "PHYSICS_RUBRIC",
    "get_rubric_for_domain",
    "RubricEvaluator",
    "RubricScore",
    "RubricReport",
    "QualityGate",
    "GateDecision",
    "GateVerdict",
]
