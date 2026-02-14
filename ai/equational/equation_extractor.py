"""
PATH: ai/equational/equation_extractor.py
PURPOSE: Extract equations from research papers.

Inspired by DREAM architecture — extract mathematical relationships.

FLOW:
┌────────────────┐    ┌─────────────────┐    ┌───────────────────┐
│ Research Paper │ →  │ Pattern Matching │ →  │ ExtractedEquation │
└────────────────┘    └─────────────────┘    └───────────────────┘

DEPENDENCIES:
- loggers.system_logger: structured logging
- utilities.cot_logging: chain-of-thought audit trail
- research_ingestion: paper data structures
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel

from .research_ingestion import ResearchPaper

_CONTEXT_WINDOW_SIZE = 200

# Domain keyword mapping for equation classification
_DOMAIN_KEYWORDS: Dict[str, List[str]] = {
    "quantum": ["\\hbar", "\\psi", "hamiltonian", "schrodinger"],
    "classical": ["F=ma", "\\vec{F}", "newton"],
    "electromagnetic": ["\\vec{E}", "\\vec{B}", "maxwell"],
    "statistical": ["\\beta", "partition", "ensemble"],
    "relativistic": ["\\gamma", "lorentz", "einstein"],
}

# Common non-variable single letters (excluded from variable extraction)
_NON_VARIABLE_LETTERS = frozenset({"e", "i", "d", "t"})


@dataclass
class ExtractedEquation:
    """Represents an extracted equation."""

    equation_id: str
    equation: str
    equation_type: str  # 'inline', 'display', 'numbered', 'align'
    context: str = ""
    variables: List[str] = field(default_factory=list)
    domain: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    extracted_at: datetime = field(default_factory=datetime.now)


class EquationExtractor:
    """Equation extractor from research papers.

    Features:
    - LaTeX equation extraction
    - Inline math extraction
    - Display math extraction
    - Variable identification
    - Context extraction
    """

    def __init__(self) -> None:
        """Initialise equation extractor."""
        self._logger = SystemLogger()
        self.equations: Dict[str, ExtractedEquation] = {}

        self.patterns = {
            "display_math": re.compile(r"\$\$([^$]+)\$\$", re.DOTALL),
            "inline_math": re.compile(r"\$([^$]+)\$"),
            "equation_env": re.compile(r"\\begin\{equation\}(.*?)\\end\{equation\}", re.DOTALL),
            "align_env": re.compile(r"\\begin\{align\}(.*?)\\end\{align\}", re.DOTALL),
        }

        self._logger.log("EquationExtractor initialized", level="INFO")

    def extract_from_paper(self, paper: ResearchPaper) -> List[ExtractedEquation]:
        """Extract equations from a research paper.

        Args:
            paper: ResearchPaper instance.

        Returns:
            List of extracted equations.
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="EXTRACT_EQUATIONS",
            input_data={"paper_id": paper.paper_id},
            level=LogLevel.INFO,
        )

        try:
            equations: List[ExtractedEquation] = []
            content = paper.content

            extraction_specs = [
                ("display_math", "display"),
                ("inline_math", "inline"),
                ("equation_env", "numbered"),
                ("align_env", "align"),
            ]

            for pattern_key, eq_type in extraction_specs:
                for match in self.patterns[pattern_key].finditer(content):
                    eq_text = match.group(1).strip()
                    context = self._extract_context(content, match.start(), match.end())
                    equation = self._create_equation(eq_text, eq_type, context, paper.paper_id)
                    equations.append(equation)

            for eq in equations:
                self.equations[eq.equation_id] = eq

            paper.equations = [eq.equation for eq in equations]

            cot.end_step(
                step_id,
                output_data={"num_equations": len(equations)},
                validation_passed=True,
            )

            self._logger.log(
                f"Extracted {len(equations)} equations from {paper.paper_id}", level="INFO"
            )

            return equations

        except Exception as e:
            cot.end_step(step_id, output_data={"error": str(e)}, validation_passed=False)
            self._logger.log(f"Error extracting equations: {e}", level="ERROR")
            return []

    def _create_equation(
        self,
        eq_text: str,
        eq_type: str,
        context: str,
        paper_id: str,
    ) -> ExtractedEquation:
        """Create an ExtractedEquation instance."""
        equation_id = f"eq_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        variables = self._extract_variables(eq_text)
        domain = self._identify_domain(eq_text, context)

        return ExtractedEquation(
            equation_id=equation_id,
            equation=eq_text,
            equation_type=eq_type,
            context=context,
            variables=variables,
            domain=domain,
            metadata={"paper_id": paper_id},
        )

    @staticmethod
    def _extract_context(content: str, start: int, end: int) -> str:
        """Extract context window around an equation.

        Args:
            content: Full document content.
            start: Match start index.
            end: Match end index.

        Returns:
            Surrounding text.
        """
        context_start = max(0, start - _CONTEXT_WINDOW_SIZE)
        context_end = min(len(content), end + _CONTEXT_WINDOW_SIZE)
        return content[context_start:context_end]

    @staticmethod
    def _extract_variables(eq_text: str) -> List[str]:
        """Extract variable names from an equation string."""
        variables: set[str] = set()

        var_pattern = re.compile(r"\b([a-z])\b", re.IGNORECASE)
        for match in var_pattern.finditer(eq_text):
            var = match.group(1).lower()
            if var not in _NON_VARIABLE_LETTERS:
                variables.add(var)

        greek_pattern = re.compile(r"\\[a-z]+|[\u0391-\u03C9]")
        for match in greek_pattern.finditer(eq_text):
            variables.add(match.group(0))

        return sorted(variables)

    @staticmethod
    def _identify_domain(eq_text: str, context: str) -> Optional[str]:
        """Identify physics domain from equation text and surrounding context."""
        combined = f"{eq_text} {context}".lower()

        for domain, keywords in _DOMAIN_KEYWORDS.items():
            if any(keyword in combined for keyword in keywords):
                return domain

        return None

    def get_equation(self, equation_id: str) -> Optional[ExtractedEquation]:
        """Get equation by ID."""
        return self.equations.get(equation_id)

    def list_equations(self) -> List[Dict[str, Any]]:
        """List all extracted equations."""
        return [
            {
                "equation_id": eq.equation_id,
                "equation": eq.equation,
                "equation_type": eq.equation_type,
                "domain": eq.domain,
                "variables": eq.variables,
            }
            for eq in self.equations.values()
        ]
