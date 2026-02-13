"""
PATH: ai/rubric/evaluator.py
PURPOSE: Scores AI responses against rubrics using programmatic checks + LLM evaluation

WHY: Combining programmatic checks (reliable, fast) with LLM evaluation
(nuanced, contextual) gives calibrated scores that match human judgment.
This follows the LLM-Rubric (ACL 2024) approach of using multiple
evaluation signals and combining them.

FLOW:
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  Response +  │───▶│ Programmatic │───▶│  Combine    │
│  Rubric      │    │ Checks       │    │  Scores     │
│              │    └──────────────┘    │             │
│              │    ┌──────────────┐    │             │
│              │───▶│ LLM-based    │───▶│  → Report   │
│              │    │ Evaluation   │    │             │
└─────────────┘    └──────────────┘    └─────────────┘

DEPENDENCIES:
- ai.rubric.definitions: Rubric structures
- validators.code_validator: For programmatic code checks
- re, ast: For programmatic content analysis
"""

import re
import ast
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from ai.rubric.definitions import (
    Rubric,
    RubricDimension,
    RubricQuestion,
    PHYSICS_RUBRIC,
)


@dataclass
class RubricScore:
    """Score for a single rubric question."""
    question_id: str
    question_text: str
    dimension: RubricDimension
    score: float  # 0.0 - 1.0 (normalized)
    raw_score: int  # 0 - max_score
    max_score: int
    level_label: str
    explanation: str
    # Whether this was scored programmatically or by LLM
    evaluation_method: str  # "programmatic" or "llm" or "heuristic"
    confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_id": self.question_id,
            "question": self.question_text,
            "dimension": self.dimension.value,
            "score": round(self.score, 3),
            "raw_score": self.raw_score,
            "max_score": self.max_score,
            "level": self.level_label,
            "explanation": self.explanation,
            "method": self.evaluation_method,
            "confidence": round(self.confidence, 3),
        }


@dataclass
class DimensionSummary:
    """Aggregated score for an entire dimension."""
    dimension: RubricDimension
    score: float  # 0.0 - 1.0 weighted average
    question_scores: List[RubricScore]
    passed_gate: bool
    gate_threshold: float
    grade: str  # A/B/C/D/F
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimension": self.dimension.value,
            "score": round(self.score, 3),
            "grade": self.grade,
            "passed": self.passed_gate,
            "threshold": self.gate_threshold,
            "questions": [q.to_dict() for q in self.question_scores],
        }


@dataclass
class RubricReport:
    """Complete evaluation report for a response."""
    rubric_name: str
    overall_score: float  # 0.0 - 1.0
    overall_grade: str  # A/B/C/D/F
    dimensions: Dict[str, DimensionSummary]
    all_gates_passed: bool
    failed_gates: List[str]  # Dimensions that failed
    evaluation_time_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    # For the frontend
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rubric": self.rubric_name,
            "overall_score": round(self.overall_score, 3),
            "overall_grade": self.overall_grade,
            "all_gates_passed": self.all_gates_passed,
            "failed_gates": self.failed_gates,
            "dimensions": {k: v.to_dict() for k, v in self.dimensions.items()},
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "suggestions": self.suggestions,
            "evaluation_time_ms": round(self.evaluation_time_ms, 1),
        }


def _score_to_grade(score: float) -> str:
    """Convert a 0-1 score to a letter grade."""
    if score >= 0.9:
        return "A"
    elif score >= 0.75:
        return "B"
    elif score >= 0.6:
        return "C"
    elif score >= 0.4:
        return "D"
    else:
        return "F"


class RubricEvaluator:
    """
    Evaluates AI responses against rubrics.
    
    Uses a hybrid approach:
    1. Programmatic checks for measurable criteria (units, code safety, formatting)
    2. Heuristic analysis for structural criteria (has derivation, has references)
    3. LLM-based evaluation for nuanced criteria (insight, clarity, rigor)
    
    The combination follows the LLM-Rubric insight that calibrated
    multi-signal scoring outperforms single-method evaluation.
    """
    
    def __init__(self, rubric: Optional[Rubric] = None):
        """
        Initialize evaluator.
        
        Args:
            rubric: Rubric to evaluate against (defaults to PHYSICS_RUBRIC)
        """
        self.rubric = rubric or PHYSICS_RUBRIC
        
        # Registry of programmatic evaluators
        self._programmatic_evaluators = {
            "pa_units_dimensions": self._check_units_dimensions,
            "pa_conservation": self._check_conservation_mentions,
            "ec_visual_math": self._check_math_formatting,
            "pv_sources": self._check_source_references,
            "pv_artefact_coverage": self._check_artefact_coverage,
            "cq_safety": self._check_code_safety,
        }
    
    def evaluate(
        self,
        content: str,
        query: str = "",
        code: Optional[str] = None,
        artefacts: Optional[List[Dict]] = None,
        reasoning: Optional[Any] = None,
    ) -> RubricReport:
        """
        Evaluate a response against the rubric.
        
        Args:
            content: The response text
            query: The original user query
            code: Any code in the response
            artefacts: Artefact references
            reasoning: Chain of thought / reasoning data
        
        Returns:
            RubricReport with scores and analysis
        """
        start_time = time.time()
        
        context = {
            "content": content or "",
            "query": query or "",
            "code": code,
            "artefacts": artefacts or [],
            "reasoning": reasoning,
            "has_code": bool(code) or self._detect_code_blocks(content or ""),
        }
        
        # Score each question
        question_scores: List[RubricScore] = []
        for question in self.rubric.questions:
            # Skip code questions if no code present
            if question.dimension == RubricDimension.CODE_QUALITY and not context["has_code"]:
                continue
            
            score = self._evaluate_question(question, context)
            question_scores.append(score)
        
        # Aggregate by dimension
        dimensions = self._aggregate_dimensions(question_scores)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(dimensions)
        overall_grade = _score_to_grade(overall_score)
        
        # Check gates
        failed_gates = []
        for dim_name, summary in dimensions.items():
            if not summary.passed_gate:
                failed_gates.append(dim_name)
        
        all_passed = len(failed_gates) == 0 and overall_score >= self.rubric.overall_threshold
        
        # Generate insights
        strengths, weaknesses, suggestions = self._generate_insights(dimensions, question_scores)
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        return RubricReport(
            rubric_name=self.rubric.name,
            overall_score=overall_score,
            overall_grade=overall_grade,
            dimensions=dimensions,
            all_gates_passed=all_passed,
            failed_gates=failed_gates,
            evaluation_time_ms=elapsed_ms,
            strengths=strengths,
            weaknesses=weaknesses,
            suggestions=suggestions,
        )
    
    def _evaluate_question(
        self, question: RubricQuestion, context: Dict[str, Any]
    ) -> RubricScore:
        """Evaluate a single rubric question."""
        
        # Try programmatic evaluation first
        if question.id in self._programmatic_evaluators:
            return self._programmatic_evaluators[question.id](question, context)
        
        # Fall back to heuristic evaluation
        return self._heuristic_evaluate(question, context)
    
    # ================================================================
    # HEURISTIC EVALUATORS (fast, no LLM needed)
    # ================================================================
    
    def _heuristic_evaluate(
        self, question: RubricQuestion, context: Dict[str, Any]
    ) -> RubricScore:
        """
        Heuristic evaluation based on content analysis.
        
        Uses keyword matching, structural analysis, and pattern
        detection to approximate quality scores.
        """
        content = context["content"]
        question_id = question.id
        max_score = question.max_score
        
        # Physics accuracy heuristics
        if question_id == "pa_fundamental_laws":
            score = self._heur_fundamental_laws(content)
        elif question_id == "pa_assumptions":
            score = self._heur_assumptions(content)
        # Math rigor heuristics
        elif question_id == "mr_derivation_validity":
            score = self._heur_derivation(content)
        elif question_id == "mr_notation_consistency":
            score = self._heur_notation(content)
        elif question_id == "mr_boundary_conditions":
            score = self._heur_boundaries(content)
        # Explanation clarity heuristics
        elif question_id == "ec_first_principles":
            score = self._heur_first_principles(content)
        elif question_id == "ec_plain_language":
            score = self._heur_plain_language(content)
        elif question_id == "ec_structure":
            score = self._heur_structure(content)
        # Code quality heuristics
        elif question_id == "cq_correctness":
            score = self._heur_code_correctness(context.get("code", ""), content)
        elif question_id == "cq_readability":
            score = self._heur_code_readability(context.get("code", ""), content)
        # Pedagogical heuristics
        elif question_id == "pv_insight":
            score = self._heur_insight(content)
        elif question_id == "pv_connections":
            score = self._heur_connections(content)
        elif question_id == "pv_verification":
            score = self._heur_verification(content)
        else:
            # Default: moderate score with low confidence
            score = 2
        
        # Clamp to valid range
        score = max(0, min(max_score, score))
        normalized = score / max_score if max_score > 0 else 0.0
        
        # Find matching level
        level_label = "Unknown"
        explanation = "Heuristic evaluation"
        for level in question.levels:
            if level.score == score:
                level_label = level.label
                explanation = level.description
                break
        
        return RubricScore(
            question_id=question.id,
            question_text=question.question,
            dimension=question.dimension,
            score=normalized,
            raw_score=score,
            max_score=max_score,
            level_label=level_label,
            explanation=explanation,
            evaluation_method="heuristic",
            confidence=0.6,
        )
    
    # ================================================================
    # PROGRAMMATIC EVALUATORS (reliable, measurable)
    # ================================================================
    
    def _check_units_dimensions(
        self, question: RubricQuestion, context: Dict[str, Any]
    ) -> RubricScore:
        """Check for proper units and dimensional analysis."""
        content = context["content"]
        
        # Look for unit patterns
        unit_patterns = [
            r'\b(?:m|kg|s|A|K|mol|cd|N|J|W|Pa|Hz|V|F|C|T|H|lm|lx|Bq|Gy|Sv)\b',
            r'\b(?:meter|kilogram|second|ampere|kelvin|joule|watt|newton)\b',
            r'\b(?:eV|MeV|GeV|TeV)\b',
            r'(?:m/s|kg\*m|N\*m|J/s)',
            r'\b(?:ergs?|dynes?|gauss)\b',
        ]
        
        unit_count = sum(
            len(re.findall(p, content, re.IGNORECASE))
            for p in unit_patterns
        )
        
        # Check for dimensional analysis keywords
        has_dimensional = bool(re.search(
            r'dimension|unit[s]?\s+(?:of|are|is)|SI\s+unit|CGS|natural\s+units',
            content, re.IGNORECASE
        ))
        
        # Numbers present without units?
        numbers = re.findall(r'(?<!\[art_)(?<!\w)\d+\.?\d*(?!\w)', content)
        numbers_count = len(numbers)
        
        if unit_count >= 5 and has_dimensional:
            raw_score = 4
        elif unit_count >= 3:
            raw_score = 3
        elif unit_count >= 1:
            raw_score = 2
        elif numbers_count > 3:
            raw_score = 1  # Numbers without units
        else:
            raw_score = 2  # No numbers needed (qualitative)
        
        return self._make_score(question, raw_score, "programmatic", 0.85)
    
    def _check_conservation_mentions(
        self, question: RubricQuestion, context: Dict[str, Any]
    ) -> RubricScore:
        """Check for conservation law awareness."""
        content = context["content"]
        
        conservation_patterns = [
            r'conserv\w+\s+(?:of\s+)?(?:energy|momentum|charge|mass|angular|baryon|lepton)',
            r'(?:energy|momentum|charge)\s+(?:is\s+)?conserv',
            r'total\s+(?:energy|momentum)\s+(?:remains|unchanged|constant)',
            r'Noether|symmetry.*conserv|conserv.*symmetry',
        ]
        
        matches = sum(
            len(re.findall(p, content, re.IGNORECASE))
            for p in conservation_patterns
        )
        
        # Also check for explicit verification
        has_verification = bool(re.search(
            r'verify|check|confirm|validated|conservation\s+(?:holds|satisfied|respected)',
            content, re.IGNORECASE
        ))
        
        if matches >= 3 and has_verification:
            raw_score = 4
        elif matches >= 2:
            raw_score = 3
        elif matches >= 1:
            raw_score = 2
        else:
            # Not all problems need conservation checks
            raw_score = 2
        
        return self._make_score(question, raw_score, "programmatic", 0.8)
    
    def _check_math_formatting(
        self, question: RubricQuestion, context: Dict[str, Any]
    ) -> RubricScore:
        """Check for proper LaTeX/math formatting."""
        content = context["content"]
        
        # LaTeX patterns
        latex_inline = len(re.findall(r'\$[^$]+\$', content))
        latex_display = len(re.findall(r'\$\$[^$]+\$\$', content))
        latex_commands = len(re.findall(r'\\(?:frac|sqrt|int|sum|partial|nabla|vec|hat|dot|ddot)', content))
        # Escaped LaTeX
        escaped_inline = len(re.findall(r'\\\([^)]+\\\)', content))
        escaped_display = len(re.findall(r'\\\[[^\]]+\\\]', content))
        
        total_math = latex_inline + latex_display + latex_commands + escaped_inline + escaped_display
        
        # Markdown formatting
        has_headers = bool(re.search(r'^#{1,6}\s', content, re.MULTILINE))
        has_bold = bool(re.search(r'\*\*[^*]+\*\*', content))
        has_lists = bool(re.search(r'^[\s]*[-*]\s', content, re.MULTILINE))
        
        format_features = sum([has_headers, has_bold, has_lists])
        
        if total_math >= 5 and format_features >= 2:
            raw_score = 4
        elif total_math >= 3 or (total_math >= 1 and format_features >= 2):
            raw_score = 3
        elif total_math >= 1 or format_features >= 1:
            raw_score = 2
        elif len(content) > 200:
            raw_score = 1  # Long content with no formatting
        else:
            raw_score = 2  # Short content may not need formatting
        
        return self._make_score(question, raw_score, "programmatic", 0.9)
    
    def _check_source_references(
        self, question: RubricQuestion, context: Dict[str, Any]
    ) -> RubricScore:
        """Check for source references and citations."""
        content = context["content"]
        
        # Artefact references
        artefact_refs = len(re.findall(r'\[art_[a-f0-9]+\]', content))
        
        # Equation references
        equation_refs = len(re.findall(
            r'(?:equation|eq\.|Eq\.|formula|law|theorem|principle|lemma)\s*(?:\(?\d+\)?|\[[\w.]+\])',
            content, re.IGNORECASE
        ))
        
        # Named physics references
        named_refs = len(re.findall(
            r"(?:Newton|Einstein|Maxwell|Schr[oö]dinger|Dirac|Boltzmann|Lagrange|Hamilton|Euler|Gauss|Faraday|Ampere|Coulomb|Planck|Heisenberg|Bohr|Feynman)'s?\s+(?:law|equation|principle|theorem|constant|formula)",
            content, re.IGNORECASE
        ))
        
        total_refs = artefact_refs + equation_refs + named_refs
        
        if total_refs >= 5:
            raw_score = 4
        elif total_refs >= 3:
            raw_score = 3
        elif total_refs >= 1:
            raw_score = 2
        elif len(content) > 300:
            raw_score = 1  # Long answer with no references
        else:
            raw_score = 2
        
        return self._make_score(question, raw_score, "programmatic", 0.85)
    
    def _check_artefact_coverage(
        self, question: RubricQuestion, context: Dict[str, Any]
    ) -> RubricScore:
        """Check artefact ID coverage for numeric values."""
        content = context["content"]
        artefacts = context.get("artefacts", [])
        
        artefact_refs = re.findall(r'\[art_[a-f0-9]+\]', content)
        numbers = re.findall(r'(?<!\[art_)\b\d+\.?\d*\b', content)
        
        ref_count = len(artefact_refs)
        num_count = len(numbers)
        
        # Filter trivial numbers (1, 2, 3 which are often step numbers)
        significant_numbers = [n for n in numbers if float(n) not in range(0, 10) or '.' in n]
        sig_count = len(significant_numbers)
        
        if ref_count > 0 and sig_count == 0:
            raw_score = 4  # All numbers backed
        elif ref_count > 0 and ref_count >= sig_count:
            raw_score = 4
        elif ref_count > 0:
            raw_score = 3
        elif sig_count == 0:
            raw_score = 3  # No significant numbers, no refs needed
        elif len(artefacts) > 0:
            raw_score = 2  # Artefacts exist but not referenced
        else:
            raw_score = 1
        
        return self._make_score(question, raw_score, "programmatic", 0.9)
    
    def _check_code_safety(
        self, question: RubricQuestion, context: Dict[str, Any]
    ) -> RubricScore:
        """Check code safety using AST analysis."""
        code = context.get("code") or ""
        content = context["content"]
        
        # Extract code blocks from content if no separate code
        if not code:
            code_blocks = re.findall(r'```(?:python)?\n(.*?)```', content, re.DOTALL)
            code = '\n'.join(code_blocks)
        
        if not code.strip():
            return self._make_score(question, 3, "programmatic", 0.9)
        
        # Basic safety checks
        dangerous_patterns = [
            r'\beval\b', r'\bexec\b', r'\bos\.',
            r'\bsubprocess\b', r'\b__import__\b',
            r'\bopen\s*\(', r'\bsystem\s*\(',
        ]
        
        danger_count = sum(
            len(re.findall(p, code))
            for p in dangerous_patterns
        )
        
        # Try AST parse
        try:
            ast.parse(code)
            has_syntax_error = False
        except SyntaxError:
            has_syntax_error = True
        
        if has_syntax_error:
            raw_score = 1
        elif danger_count >= 2:
            raw_score = 0
        elif danger_count == 1:
            raw_score = 1
        else:
            # Check for input validation
            has_validation = bool(re.search(
                r'(?:isinstance|assert|raise|ValueError|TypeError|if\s+not)',
                code
            ))
            raw_score = 4 if has_validation else 3
        
        return self._make_score(question, raw_score, "programmatic", 0.95)
    
    # ================================================================
    # HEURISTIC HELPERS
    # ================================================================
    
    def _heur_fundamental_laws(self, content: str) -> int:
        """Heuristic: Are fundamental laws correctly cited?"""
        law_patterns = [
            r"Newton's\s+(?:first|second|third|law)",
            r"conservation\s+of\s+(?:energy|momentum|angular|charge|mass)",
            r"Maxwell's\s+equations?",
            r"Schr[oö]dinger\s+equation",
            r"Einstein\s+field\s+equations?",
            r"E\s*=\s*mc\^?2",
            r"F\s*=\s*ma",
            r"Lagrangian|Hamiltonian|action\s+principle",
            r"Boltzmann|partition\s+function|entropy",
            r"Coulomb|Gauss|Faraday|Ampere",
        ]
        matches = sum(1 for p in law_patterns if re.search(p, content, re.IGNORECASE))
        
        has_applicability = bool(re.search(
            r'valid\s+(?:when|for|in)|regime|approximation|limit',
            content, re.IGNORECASE
        ))
        
        if matches >= 3 and has_applicability:
            return 4
        elif matches >= 2:
            return 3
        elif matches >= 1:
            return 2
        elif len(content) > 200:
            return 1
        return 2
    
    def _heur_assumptions(self, content: str) -> int:
        """Heuristic: Are assumptions stated?"""
        assumption_patterns = [
            r'assum\w+',
            r'(?:we|let\s+us)\s+(?:assume|consider|suppose)',
            r'neglect\w*|ignor\w*|approximat\w*',
            r'ideal\w*|perfect\w*|frictionless|massless',
            r'small\s+angle|linear\w*\s+regime',
            r'valid\s+(?:when|for|if)',
        ]
        matches = sum(1 for p in assumption_patterns if re.search(p, content, re.IGNORECASE))
        
        has_justification = bool(re.search(
            r'because|since|(?:this|which)\s+is\s+valid|justified',
            content, re.IGNORECASE
        ))
        
        if matches >= 3 and has_justification:
            return 4
        elif matches >= 2:
            return 3
        elif matches >= 1:
            return 2
        elif len(content) > 300:
            return 1
        return 2
    
    def _heur_derivation(self, content: str) -> int:
        """Heuristic: Does the derivation have logical steps?"""
        step_markers = len(re.findall(
            r'(?:^|\n)\s*(?:\d+[\.):]|step\s+\d|therefore|thus|hence|it follows|substitut|rearrang)',
            content, re.IGNORECASE | re.MULTILINE
        ))
        
        math_expressions = len(re.findall(r'\$[^$]+\$|\\\([^)]+\\\)', content))
        has_equals = len(re.findall(r'=', content))
        
        if step_markers >= 4 and math_expressions >= 3:
            return 4
        elif step_markers >= 3 or (step_markers >= 2 and math_expressions >= 2):
            return 3
        elif step_markers >= 1 or has_equals >= 3:
            return 2
        elif len(content) > 200:
            return 1
        return 2
    
    def _heur_notation(self, content: str) -> int:
        """Heuristic: Is notation consistent?"""
        has_latex = bool(re.search(r'\$|\\[a-zA-Z]+', content))
        has_defined = bool(re.search(r'(?:where|let|define)\s+\$?\\?\w+', content, re.IGNORECASE))
        
        if has_latex and has_defined:
            return 3
        elif has_latex:
            return 2
        return 2
    
    def _heur_boundaries(self, content: str) -> int:
        """Heuristic: Are boundary/special cases handled?"""
        boundary_terms = len(re.findall(
            r'boundary|initial\s+condition|limit(?:ing)?|special\s+case|edge\s+case|(?:as|when)\s+\w+\s*(?:→|->|approaches)',
            content, re.IGNORECASE
        ))
        
        if boundary_terms >= 3:
            return 4
        elif boundary_terms >= 2:
            return 3
        elif boundary_terms >= 1:
            return 2
        return 1
    
    def _heur_first_principles(self, content: str) -> int:
        """Heuristic: Does it build from first principles?"""
        fp_markers = len(re.findall(
            r'first\s+principle|fundament\w+|axiom|postulat|start(?:ing)?\s+from|begin(?:ning)?\s+with|deriv(?:e|ation)',
            content, re.IGNORECASE
        ))
        
        has_chain = bool(re.search(
            r'(?:therefore|thus|hence|it follows|this gives|this leads|which means|combining|substituting)',
            content, re.IGNORECASE
        ))
        
        step_count = len(re.findall(r'(?:^|\n)\s*\d+[\.):]', content, re.MULTILINE))
        
        if fp_markers >= 2 and has_chain and step_count >= 3:
            return 4
        elif fp_markers >= 1 and has_chain:
            return 3
        elif has_chain or fp_markers >= 1:
            return 2
        elif len(content) > 200:
            return 1
        return 2
    
    def _heur_plain_language(self, content: str) -> int:
        """Heuristic: Is there plain language alongside math?"""
        has_math = bool(re.search(r'\$|\\[a-zA-Z]+', content))
        
        explanation_markers = len(re.findall(
            r'(?:in other words|this means|intuitively|physically|think of|imagine|like|analogy|simply put|basically)',
            content, re.IGNORECASE
        ))
        
        # Check for reasonable sentence-to-math ratio
        sentences = len(re.findall(r'[.!?]\s', content))
        math_blocks = len(re.findall(r'\$\$[^$]+\$\$', content))
        
        if explanation_markers >= 3 and has_math:
            return 4
        elif explanation_markers >= 1 and has_math:
            return 3
        elif sentences > 3 or explanation_markers >= 1:
            return 2
        elif has_math and sentences < 2:
            return 1
        return 2
    
    def _heur_structure(self, content: str) -> int:
        """Heuristic: Is the response well-structured?"""
        has_headers = len(re.findall(r'^#{1,6}\s', content, re.MULTILINE))
        has_bold = len(re.findall(r'\*\*[^*]+\*\*', content))
        has_lists = len(re.findall(r'^[\s]*[-*\d.]+\s', content, re.MULTILINE))
        has_sections = has_headers >= 2
        
        total_structure = has_headers + has_bold + has_lists
        
        if has_sections and total_structure >= 5:
            return 4
        elif total_structure >= 3:
            return 3
        elif total_structure >= 1:
            return 2
        elif len(content) > 500:
            return 1  # Long unstructured content
        return 2
    
    def _heur_code_correctness(self, code: str, content: str) -> int:
        """Heuristic: Code correctness check."""
        if not code:
            code_blocks = re.findall(r'```(?:python)?\n(.*?)```', content, re.DOTALL)
            code = '\n'.join(code_blocks)
        
        if not code.strip():
            return 3
        
        try:
            ast.parse(code)
        except SyntaxError:
            return 1
        
        has_physics_lib = bool(re.search(r'numpy|scipy|sympy|matplotlib', code))
        has_docstring = bool(re.search(r'""".*?"""|\'\'\'.*?\'\'\'', code, re.DOTALL))
        
        if has_physics_lib and has_docstring:
            return 3
        elif has_physics_lib:
            return 3
        return 2
    
    def _heur_code_readability(self, code: str, content: str) -> int:
        """Heuristic: Code readability check."""
        if not code:
            code_blocks = re.findall(r'```(?:python)?\n(.*?)```', content, re.DOTALL)
            code = '\n'.join(code_blocks)
        
        if not code.strip():
            return 3
        
        has_comments = len(re.findall(r'#\s+\S', code))
        has_docstring = bool(re.search(r'"""', code))
        has_type_hints = bool(re.search(r':\s*(?:int|float|str|List|Dict|Optional)', code))
        
        score = 2
        if has_comments >= 3:
            score += 1
        if has_docstring:
            score += 1
        if has_type_hints:
            score = min(score + 1, 4)
        
        return min(score, 4)
    
    def _heur_insight(self, content: str) -> int:
        """Heuristic: Physical insight quality."""
        insight_markers = len(re.findall(
            r'physic\w+\s+(?:meaning|interpretation|significance|insight|intuition)|'
            r'what\s+this\s+(?:means|tells|shows)|'
            r'the\s+key\s+(?:insight|idea|concept)|'
            r'notice\s+that|importantly|remarkably|interestingly',
            content, re.IGNORECASE
        ))
        
        if insight_markers >= 3:
            return 4
        elif insight_markers >= 2:
            return 3
        elif insight_markers >= 1:
            return 2
        elif len(content) > 300:
            return 1
        return 2
    
    def _heur_connections(self, content: str) -> int:
        """Heuristic: Connections to broader physics."""
        connection_patterns = [
            r'relat(?:ed|ion|es)\s+to',
            r'connect\w+\s+(?:to|with)',
            r'(?:special|limiting)\s+case',
            r'general(?:iz\w+)?',
            r'(?:quantum|classical|relativistic)\s+limit',
            r'analogous|similar\s+to|just\s+like',
            r'broader|wider|deeper\s+(?:context|implications|significance)',
        ]
        matches = sum(1 for p in connection_patterns if re.search(p, content, re.IGNORECASE))
        
        if matches >= 3:
            return 4
        elif matches >= 2:
            return 3
        elif matches >= 1:
            return 2
        return 1
    
    def _heur_verification(self, content: str) -> int:
        """Heuristic: Verification methods present."""
        verification_patterns = [
            r'dimensional\s+analysis|dimensions?\s+check',
            r'(?:limiting|special)\s+case|(?:as|when)\s+\w+\s*(?:→|->|approaches)\s*(?:0|infinity|∞)',
            r'sanity\s+check|cross.?check|verif\w+|validat\w+',
            r'order\s+of\s+magnitude',
            r'consistent\s+with|agrees?\s+with|matches',
            r'known\s+result|expected|recover',
        ]
        matches = sum(1 for p in verification_patterns if re.search(p, content, re.IGNORECASE))
        
        if matches >= 3:
            return 4
        elif matches >= 2:
            return 3
        elif matches >= 1:
            return 2
        elif len(content) > 300:
            return 1
        return 1
    
    # ================================================================
    # AGGREGATION
    # ================================================================
    
    def _make_score(
        self, question: RubricQuestion, raw_score: int, method: str, confidence: float
    ) -> RubricScore:
        """Create a RubricScore from a raw score."""
        raw_score = max(0, min(question.max_score, raw_score))
        normalized = raw_score / question.max_score if question.max_score > 0 else 0.0
        
        level_label = "Unknown"
        explanation = ""
        for level in question.levels:
            if level.score == raw_score:
                level_label = level.label
                explanation = level.description
                break
        
        return RubricScore(
            question_id=question.id,
            question_text=question.question,
            dimension=question.dimension,
            score=normalized,
            raw_score=raw_score,
            max_score=question.max_score,
            level_label=level_label,
            explanation=explanation,
            evaluation_method=method,
            confidence=confidence,
        )
    
    def _aggregate_dimensions(
        self, scores: List[RubricScore]
    ) -> Dict[str, DimensionSummary]:
        """Aggregate question scores into dimension summaries."""
        dims: Dict[RubricDimension, List[RubricScore]] = {}
        for score in scores:
            dims.setdefault(score.dimension, []).append(score)
        
        summaries = {}
        for dim, dim_scores in dims.items():
            # Weighted average within dimension
            total_weight = sum(
                q.weight for q in self.rubric.questions
                if q.id in [s.question_id for s in dim_scores]
            )
            
            if total_weight == 0:
                dim_score = 0.0
            else:
                weighted_sum = 0.0
                for s in dim_scores:
                    q = next((q for q in self.rubric.questions if q.id == s.question_id), None)
                    weight = q.weight if q else 1.0
                    weighted_sum += s.score * weight
                dim_score = weighted_sum / total_weight
            
            threshold = self.rubric.get_gate_threshold(dim)
            
            summaries[dim.value] = DimensionSummary(
                dimension=dim,
                score=dim_score,
                question_scores=dim_scores,
                passed_gate=dim_score >= threshold,
                gate_threshold=threshold,
                grade=_score_to_grade(dim_score),
            )
        
        return summaries
    
    def _calculate_overall_score(
        self, dimensions: Dict[str, DimensionSummary]
    ) -> float:
        """Calculate overall weighted score across dimensions."""
        total_weight = 0.0
        weighted_sum = 0.0
        
        for dim_name, summary in dimensions.items():
            dim_enum = summary.dimension
            weight = self.rubric.get_dimension_weight(dim_enum)
            weighted_sum += summary.score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _generate_insights(
        self,
        dimensions: Dict[str, DimensionSummary],
        scores: List[RubricScore],
    ) -> Tuple[List[str], List[str], List[str]]:
        """Generate human-readable strengths, weaknesses, and suggestions."""
        strengths = []
        weaknesses = []
        suggestions = []
        
        for dim_name, summary in dimensions.items():
            if summary.score >= 0.75:
                strengths.append(
                    f"Strong {dim_name.replace('_', ' ')}: {summary.grade} grade"
                )
            elif summary.score < 0.5:
                weaknesses.append(
                    f"Weak {dim_name.replace('_', ' ')}: {summary.grade} grade"
                )
        
        # Find lowest-scoring questions for suggestions
        sorted_scores = sorted(scores, key=lambda s: s.score)
        for s in sorted_scores[:3]:
            if s.score < 0.5:
                suggestions.append(
                    f"Improve '{s.question_text[:60]}...' (currently: {s.level_label})"
                )
        
        return strengths, weaknesses, suggestions
    
    def _detect_code_blocks(self, content: str) -> bool:
        """Detect if content contains code blocks."""
        return bool(re.search(r'```\w*\n', content))
