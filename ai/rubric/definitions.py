"""
PATH: ai/rubric/definitions.py
PURPOSE: Rubric definitions for Beyond Frontier quality evaluation

WHY: Inspired by RubricHub (coarse-to-fine rubric generation) and
PEARL (multi-metric framework), this module defines structured
evaluation rubrics for physics AI responses. Fine-grained rubrics
reveal specific weaknesses that coarse rubrics miss.

FLOW:
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Dimension   │───▶│   Questions  │───▶│   Levels     │
│  (what area) │    │ (what to ask)│    │ (score 0-4)  │
└──────────────┘    └──────────────┘    └──────────────┘

RESEARCH BASIS:
- RubricHub: Coarse-to-fine rubric design
- LLM-Rubric (ACL 2024): Multidimensional calibrated scoring
- PEARL: 7-metric framework (Technical, Argumentative, Explanation)
- ResearchRubrics: Domain-specific expert rubrics

DEPENDENCIES:
- None (pure data definitions)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class RubricDimension(Enum):
    """
    Evaluation dimensions for physics AI responses.
    
    Each dimension targets a specific quality aspect.
    The combination provides a comprehensive quality profile.
    """
    PHYSICS_ACCURACY = "physics_accuracy"
    MATHEMATICAL_RIGOR = "mathematical_rigor"
    EXPLANATION_CLARITY = "explanation_clarity"
    PROVENANCE_COMPLETENESS = "provenance_completeness"
    CODE_QUALITY = "code_quality"
    PEDAGOGICAL_VALUE = "pedagogical_value"


@dataclass
class RubricLevel:
    """
    A single level in a rubric scale (0-4).
    
    Each level has a numeric score and a description
    of what quality looks like at that level.
    """
    score: int
    label: str
    description: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": self.score,
            "label": self.label,
            "description": self.description,
        }


@dataclass
class RubricQuestion:
    """
    A specific evaluation question within a dimension.
    
    Fine-grained questions capture nuances that a single
    coarse question would miss. This is the key insight
    from RubricHub: fine-grained rubrics provide richer
    discriminative signals.
    """
    id: str
    question: str
    dimension: RubricDimension
    levels: List[RubricLevel]
    weight: float = 1.0
    # Whether this question requires domain expertise
    is_expert: bool = False
    # Whether this can be evaluated programmatically (not just LLM)
    is_programmatic: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "question": self.question,
            "dimension": self.dimension.value,
            "levels": [l.to_dict() for l in self.levels],
            "weight": self.weight,
            "is_expert": self.is_expert,
            "is_programmatic": self.is_programmatic,
        }
    
    @property
    def max_score(self) -> int:
        """Maximum achievable score for this question."""
        return max(l.score for l in self.levels)


@dataclass
class Rubric:
    """
    Complete rubric for evaluating a physics AI response.
    
    Contains multiple questions across multiple dimensions,
    with configurable weights for domain-specific emphasis.
    """
    name: str
    description: str
    questions: List[RubricQuestion]
    # Per-dimension weight overrides
    dimension_weights: Dict[RubricDimension, float] = field(default_factory=dict)
    # Minimum scores to pass quality gate per dimension
    gate_thresholds: Dict[RubricDimension, float] = field(default_factory=dict)
    # Overall minimum to pass
    overall_threshold: float = 0.6
    
    def get_questions_for_dimension(self, dimension: RubricDimension) -> List[RubricQuestion]:
        """Get all questions for a specific dimension."""
        return [q for q in self.questions if q.dimension == dimension]
    
    def get_dimension_weight(self, dimension: RubricDimension) -> float:
        """Get weight for a dimension, defaulting to 1.0."""
        return self.dimension_weights.get(dimension, 1.0)
    
    def get_gate_threshold(self, dimension: RubricDimension) -> float:
        """Get pass threshold for a dimension, defaulting to overall."""
        return self.gate_thresholds.get(dimension, self.overall_threshold)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "questions": [q.to_dict() for q in self.questions],
            "dimension_weights": {k.value: v for k, v in self.dimension_weights.items()},
            "gate_thresholds": {k.value: v for k, v in self.gate_thresholds.items()},
            "overall_threshold": self.overall_threshold,
        }


# ============================================================
# STANDARD RUBRIC LEVELS (reusable across questions)
# ============================================================

STANDARD_LEVELS = [
    RubricLevel(0, "Absent", "Not present or completely incorrect"),
    RubricLevel(1, "Poor", "Major errors or significant gaps"),
    RubricLevel(2, "Adequate", "Partially correct with notable issues"),
    RubricLevel(3, "Good", "Mostly correct with minor issues"),
    RubricLevel(4, "Excellent", "Thorough, accurate, and well-presented"),
]


# ============================================================
# PHYSICS ACCURACY QUESTIONS (Fine-grained)
# ============================================================

PHYSICS_ACCURACY_QUESTIONS = [
    RubricQuestion(
        id="pa_fundamental_laws",
        question="Are the fundamental physics laws cited correctly (e.g., Newton's laws, conservation laws, Maxwell's equations)?",
        dimension=RubricDimension.PHYSICS_ACCURACY,
        weight=2.0,
        is_expert=True,
        levels=[
            RubricLevel(0, "Wrong", "Fundamental laws are stated incorrectly or misapplied"),
            RubricLevel(1, "Confused", "Laws cited but applied in wrong context or with wrong form"),
            RubricLevel(2, "Partial", "Some laws correct, others missing or imprecise"),
            RubricLevel(3, "Correct", "Laws correctly stated and applied to the problem"),
            RubricLevel(4, "Expert", "Laws precisely stated with correct domain of applicability and limitations noted"),
        ],
    ),
    RubricQuestion(
        id="pa_units_dimensions",
        question="Are all physical quantities expressed with correct units and dimensions?",
        dimension=RubricDimension.PHYSICS_ACCURACY,
        weight=1.5,
        is_programmatic=True,
        levels=[
            RubricLevel(0, "Wrong", "Units missing or dimensionally inconsistent"),
            RubricLevel(1, "Inconsistent", "Some units present but dimensional analysis fails"),
            RubricLevel(2, "Partial", "Most units correct, minor dimensional issues"),
            RubricLevel(3, "Correct", "All units present and dimensionally consistent"),
            RubricLevel(4, "Rigorous", "Units, dimensions, and significant figures all handled properly"),
        ],
    ),
    RubricQuestion(
        id="pa_assumptions",
        question="Are physical assumptions explicitly stated and valid for the problem regime?",
        dimension=RubricDimension.PHYSICS_ACCURACY,
        weight=1.5,
        levels=[
            RubricLevel(0, "Hidden", "No assumptions stated, implicit assumptions may be wrong"),
            RubricLevel(1, "Incomplete", "Some assumptions stated but key ones missing"),
            RubricLevel(2, "Listed", "Assumptions listed but validity not discussed"),
            RubricLevel(3, "Justified", "Assumptions stated with justification for the regime"),
            RubricLevel(4, "Comprehensive", "All assumptions explicit, justified, and limitations of each noted"),
        ],
    ),
    RubricQuestion(
        id="pa_conservation",
        question="Does the solution respect conservation laws (energy, momentum, charge, etc.)?",
        dimension=RubricDimension.PHYSICS_ACCURACY,
        weight=2.0,
        is_programmatic=True,
        levels=[
            RubricLevel(0, "Violated", "Conservation laws clearly violated in the solution"),
            RubricLevel(1, "Unclear", "Cannot determine if conservation laws hold"),
            RubricLevel(2, "Implicit", "Conservation appears respected but not checked"),
            RubricLevel(3, "Respected", "Conservation laws explicitly satisfied"),
            RubricLevel(4, "Verified", "Conservation laws checked, verified, and used as validation"),
        ],
    ),
]

# ============================================================
# MATHEMATICAL RIGOR QUESTIONS
# ============================================================

MATHEMATICAL_RIGOR_QUESTIONS = [
    RubricQuestion(
        id="mr_derivation_validity",
        question="Is the mathematical derivation logically valid (each step follows from the previous)?",
        dimension=RubricDimension.MATHEMATICAL_RIGOR,
        weight=2.0,
        levels=[
            RubricLevel(0, "Invalid", "Logical gaps or non-sequiturs in derivation"),
            RubricLevel(1, "Flawed", "Some steps valid but critical gaps exist"),
            RubricLevel(2, "Rough", "General approach correct but steps skipped or hand-waved"),
            RubricLevel(3, "Sound", "Each step logically follows with minor omissions"),
            RubricLevel(4, "Rigorous", "Every step justified, no gaps, could serve as a proof"),
        ],
    ),
    RubricQuestion(
        id="mr_notation_consistency",
        question="Is mathematical notation used consistently and correctly throughout?",
        dimension=RubricDimension.MATHEMATICAL_RIGOR,
        weight=1.0,
        levels=[
            RubricLevel(0, "Chaotic", "Notation inconsistent, symbols undefined or reused"),
            RubricLevel(1, "Sloppy", "Notation mostly readable but inconsistencies exist"),
            RubricLevel(2, "Adequate", "Standard notation used but some variables undefined"),
            RubricLevel(3, "Clean", "Consistent notation, variables defined"),
            RubricLevel(4, "Publication", "Publication-quality notation with all terms defined at first use"),
        ],
    ),
    RubricQuestion(
        id="mr_boundary_conditions",
        question="Are boundary conditions and special cases handled correctly?",
        dimension=RubricDimension.MATHEMATICAL_RIGOR,
        weight=1.5,
        levels=[
            RubricLevel(0, "Ignored", "No boundary conditions or special cases considered"),
            RubricLevel(1, "Mentioned", "Boundary conditions acknowledged but not applied"),
            RubricLevel(2, "Partial", "Some boundary conditions applied, others missed"),
            RubricLevel(3, "Applied", "Boundary conditions properly applied and verified"),
            RubricLevel(4, "Exhaustive", "All boundary conditions, edge cases, and limits thoroughly analyzed"),
        ],
    ),
]

# ============================================================
# EXPLANATION CLARITY QUESTIONS
# ============================================================

EXPLANATION_CLARITY_QUESTIONS = [
    RubricQuestion(
        id="ec_first_principles",
        question="Does the explanation build from first principles rather than asserting results?",
        dimension=RubricDimension.EXPLANATION_CLARITY,
        weight=2.0,
        levels=[
            RubricLevel(0, "Assertion", "Results stated without derivation or reasoning"),
            RubricLevel(1, "Shallow", "Some reasoning but starts from advanced results"),
            RubricLevel(2, "Partial", "Builds from known principles but skips foundational steps"),
            RubricLevel(3, "Grounded", "Builds from fundamental principles with clear chain"),
            RubricLevel(4, "Foundational", "Traces back to axioms/fundamental laws with complete logical chain"),
        ],
    ),
    RubricQuestion(
        id="ec_plain_language",
        question="Are complex concepts explained in plain, accessible language alongside formal notation?",
        dimension=RubricDimension.EXPLANATION_CLARITY,
        weight=1.5,
        levels=[
            RubricLevel(0, "Opaque", "Only formal notation, no plain language explanation"),
            RubricLevel(1, "Jargon-heavy", "Attempted explanation but requires expert knowledge"),
            RubricLevel(2, "Mixed", "Some plain language but key concepts still opaque"),
            RubricLevel(3, "Clear", "Most concepts explained clearly alongside math"),
            RubricLevel(4, "Intuitive", "Every concept has both formal and intuitive explanation, analogies used"),
        ],
    ),
    RubricQuestion(
        id="ec_structure",
        question="Is the response well-structured with logical flow (problem → analysis → solution → interpretation)?",
        dimension=RubricDimension.EXPLANATION_CLARITY,
        weight=1.0,
        levels=[
            RubricLevel(0, "Disorganized", "No clear structure, information scattered"),
            RubricLevel(1, "Loose", "Some structure but hard to follow the thread"),
            RubricLevel(2, "Basic", "Has sections but transitions are weak"),
            RubricLevel(3, "Organized", "Clear structure with logical progression"),
            RubricLevel(4, "Exemplary", "Professional structure with clear headers, transitions, and summary"),
        ],
    ),
    RubricQuestion(
        id="ec_visual_math",
        question="Is mathematical content properly formatted and readable (LaTeX, equations, diagrams)?",
        dimension=RubricDimension.EXPLANATION_CLARITY,
        weight=1.0,
        is_programmatic=True,
        levels=[
            RubricLevel(0, "Raw", "Math as plain text, unformatted, unreadable"),
            RubricLevel(1, "Partial", "Some formatting but inconsistent or broken"),
            RubricLevel(2, "Readable", "Math formatted but could be cleaner"),
            RubricLevel(3, "Well-formatted", "Proper LaTeX/math rendering throughout"),
            RubricLevel(4, "Publication", "Beautiful typography, numbered equations, proper display/inline usage"),
        ],
    ),
]

# ============================================================
# PROVENANCE COMPLETENESS QUESTIONS
# ============================================================

PROVENANCE_COMPLETENESS_QUESTIONS = [
    RubricQuestion(
        id="pv_sources",
        question="Are claims supported by references to computations, equations, or known results?",
        dimension=RubricDimension.PROVENANCE_COMPLETENESS,
        weight=2.0,
        is_programmatic=True,
        levels=[
            RubricLevel(0, "Unsourced", "Claims made without any supporting reference"),
            RubricLevel(1, "Sparse", "Few references, most claims unsupported"),
            RubricLevel(2, "Partial", "Key claims referenced but minor ones floating"),
            RubricLevel(3, "Referenced", "Most claims tied to computations or known results"),
            RubricLevel(4, "Full provenance", "Every claim traceable to artefact, equation, or citation"),
        ],
    ),
    RubricQuestion(
        id="pv_artefact_coverage",
        question="Are numeric values backed by artefact IDs from deterministic computation?",
        dimension=RubricDimension.PROVENANCE_COMPLETENESS,
        weight=2.0,
        is_programmatic=True,
        levels=[
            RubricLevel(0, "None", "Numeric values stated without artefact references"),
            RubricLevel(1, "Few", "Some artefact references but most numbers untraced"),
            RubricLevel(2, "Mixed", "About half of numeric values have artefact backing"),
            RubricLevel(3, "Good", "Most numeric values reference artefacts"),
            RubricLevel(4, "Complete", "All numeric values have artefact IDs, provenance chain complete"),
        ],
    ),
]

# ============================================================
# CODE QUALITY QUESTIONS
# ============================================================

CODE_QUALITY_QUESTIONS = [
    RubricQuestion(
        id="cq_correctness",
        question="Does the generated code correctly implement the physics described?",
        dimension=RubricDimension.CODE_QUALITY,
        weight=2.0,
        levels=[
            RubricLevel(0, "Broken", "Code has syntax errors or does not run"),
            RubricLevel(1, "Buggy", "Code runs but produces incorrect results"),
            RubricLevel(2, "Approximate", "Code roughly correct but edge cases fail"),
            RubricLevel(3, "Correct", "Code produces correct results for stated domain"),
            RubricLevel(4, "Verified", "Code correct, tested, and handles edge cases"),
        ],
    ),
    RubricQuestion(
        id="cq_safety",
        question="Is the code free of dangerous operations (no eval, exec, file access, etc.)?",
        dimension=RubricDimension.CODE_QUALITY,
        weight=1.5,
        is_programmatic=True,
        levels=[
            RubricLevel(0, "Dangerous", "Contains dangerous operations that could harm the system"),
            RubricLevel(1, "Risky", "Contains operations that could be exploited"),
            RubricLevel(2, "Cautious", "No dangerous ops but some imports could be problematic"),
            RubricLevel(3, "Safe", "Clean, safe code with no dangerous patterns"),
            RubricLevel(4, "Sandboxed", "Safe code with explicit sandboxing and input validation"),
        ],
    ),
    RubricQuestion(
        id="cq_readability",
        question="Is the code well-documented, readable, and follows good practices?",
        dimension=RubricDimension.CODE_QUALITY,
        weight=1.0,
        levels=[
            RubricLevel(0, "Unreadable", "No comments, poor naming, spaghetti logic"),
            RubricLevel(1, "Minimal", "Some structure but poorly documented"),
            RubricLevel(2, "Adequate", "Readable but could use more documentation"),
            RubricLevel(3, "Clean", "Well-structured with docstrings and clear naming"),
            RubricLevel(4, "Exemplary", "Publication-quality code with full documentation and type hints"),
        ],
    ),
]

# ============================================================
# PEDAGOGICAL VALUE QUESTIONS
# ============================================================

PEDAGOGICAL_VALUE_QUESTIONS = [
    RubricQuestion(
        id="pv_insight",
        question="Does the response provide genuine physical insight beyond just solving the math?",
        dimension=RubricDimension.PEDAGOGICAL_VALUE,
        weight=1.5,
        levels=[
            RubricLevel(0, "Mechanical", "Pure computation with no physical interpretation"),
            RubricLevel(1, "Minimal", "Brief mention of physical meaning"),
            RubricLevel(2, "Some", "Physical interpretation provided for key results"),
            RubricLevel(3, "Insightful", "Rich physical interpretation connecting math to reality"),
            RubricLevel(4, "Illuminating", "Deep insight, connects to broader physics, reveals 'why' not just 'what'"),
        ],
    ),
    RubricQuestion(
        id="pv_connections",
        question="Does the response connect to related concepts, limits, or broader physics?",
        dimension=RubricDimension.PEDAGOGICAL_VALUE,
        weight=1.0,
        levels=[
            RubricLevel(0, "Isolated", "Treats problem in complete isolation"),
            RubricLevel(1, "Tangential", "Mentions related concepts without connecting them"),
            RubricLevel(2, "Some links", "A few connections to related physics"),
            RubricLevel(3, "Connected", "Links to limiting cases, related theorems, or applications"),
            RubricLevel(4, "Unified", "Shows how this fits into the broader tapestry of physics"),
        ],
    ),
    RubricQuestion(
        id="pv_verification",
        question="Does the response include ways to verify or validate the result (limiting cases, dimensional analysis, sanity checks)?",
        dimension=RubricDimension.PEDAGOGICAL_VALUE,
        weight=1.5,
        levels=[
            RubricLevel(0, "None", "No verification or validation offered"),
            RubricLevel(1, "Minimal", "One quick check mentioned"),
            RubricLevel(2, "Some", "A couple of verification methods mentioned"),
            RubricLevel(3, "Thorough", "Multiple verification methods applied (limits, dimensions, sanity)"),
            RubricLevel(4, "Exhaustive", "Comprehensive validation with independent cross-checks and error analysis"),
        ],
    ),
]


# ============================================================
# ASSEMBLED RUBRICS
# ============================================================

PHYSICS_RUBRIC = Rubric(
    name="Beyond Frontier Standard Rubric",
    description="Comprehensive evaluation rubric for Beyond Frontier responses, combining fine-grained questions across 6 dimensions. Inspired by RubricHub coarse-to-fine methodology.",
    questions=(
        PHYSICS_ACCURACY_QUESTIONS +
        MATHEMATICAL_RIGOR_QUESTIONS +
        EXPLANATION_CLARITY_QUESTIONS +
        PROVENANCE_COMPLETENESS_QUESTIONS +
        CODE_QUALITY_QUESTIONS +
        PEDAGOGICAL_VALUE_QUESTIONS
    ),
    dimension_weights={
        RubricDimension.PHYSICS_ACCURACY: 2.0,
        RubricDimension.MATHEMATICAL_RIGOR: 1.5,
        RubricDimension.EXPLANATION_CLARITY: 1.2,
        RubricDimension.PROVENANCE_COMPLETENESS: 1.5,
        RubricDimension.CODE_QUALITY: 1.0,
        RubricDimension.PEDAGOGICAL_VALUE: 1.0,
    },
    gate_thresholds={
        RubricDimension.PHYSICS_ACCURACY: 0.6,
        RubricDimension.MATHEMATICAL_RIGOR: 0.5,
        RubricDimension.EXPLANATION_CLARITY: 0.5,
        RubricDimension.PROVENANCE_COMPLETENESS: 0.4,
        RubricDimension.CODE_QUALITY: 0.5,
        RubricDimension.PEDAGOGICAL_VALUE: 0.3,
    },
    overall_threshold=0.55,
)

# Lightweight rubric for quick Gatekeeper checks
QUICK_RUBRIC = Rubric(
    name="Quick Quality Check",
    description="Lightweight rubric for fast quality assessment (Gatekeeper tier).",
    questions=[
        PHYSICS_ACCURACY_QUESTIONS[0],   # Fundamental laws
        EXPLANATION_CLARITY_QUESTIONS[0], # First principles
        PROVENANCE_COMPLETENESS_QUESTIONS[0], # Sources
    ],
    overall_threshold=0.5,
)

# Code-focused rubric for code generation responses
CODE_RUBRIC = Rubric(
    name="Code Quality Rubric",
    description="Focused rubric for evaluating generated physics code.",
    questions=(
        CODE_QUALITY_QUESTIONS +
        [PHYSICS_ACCURACY_QUESTIONS[1]] +  # Units/dimensions
        [EXPLANATION_CLARITY_QUESTIONS[3]]  # Visual/math formatting
    ),
    dimension_weights={
        RubricDimension.CODE_QUALITY: 2.0,
        RubricDimension.PHYSICS_ACCURACY: 1.5,
    },
    overall_threshold=0.6,
)


def get_rubric_for_domain(domain: str, has_code: bool = False) -> Rubric:
    """
    Select appropriate rubric based on response domain.
    
    Args:
        domain: Physics domain (e.g., 'quantum', 'classical', 'general')
        has_code: Whether the response includes code
    
    Returns:
        Appropriate Rubric instance
    """
    if has_code:
        return CODE_RUBRIC
    
    # For now, use the standard rubric for all physics domains
    # Future: domain-specific rubrics with adjusted weights
    return PHYSICS_RUBRIC
