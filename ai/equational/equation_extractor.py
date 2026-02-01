# ai/equational/
"""
Equation Extractor - Extract equations from research papers.

Inspired by DREAM architecture - extract mathematical relationships.

First Principle Analysis:
- Extraction: Parse text → Identify equation patterns → Extract equations
- Patterns: LaTeX equations, inline math, display math
- Mathematical foundation: Regular expressions, pattern matching, parsing
- Architecture: Modular extractor with multiple pattern support
"""

from typing import Any, Dict, List, Optional, Tuple
import re
from dataclasses import dataclass, field
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from .research_ingestion import ResearchPaper


@dataclass
class ExtractedEquation:
    """Represents an extracted equation."""
    equation_id: str
    equation: str
    equation_type: str  # 'inline', 'display', 'numbered'
    context: str = ""  # Surrounding text
    variables: List[str] = field(default_factory=list)
    domain: Optional[str] = None  # Physics domain
    metadata: Dict[str, Any] = field(default_factory=dict)
    extracted_at: datetime = field(default_factory=datetime.now)


class EquationExtractor:
    """
    Equation extractor from research papers.
    
    Features:
    - LaTeX equation extraction
    - Inline math extraction
    - Display math extraction
    - Variable identification
    - Context extraction
    """
    
    def __init__(self):
        """Initialize equation extractor."""
        self.logger = SystemLogger()
        self.equations: Dict[str, ExtractedEquation] = {}
        
        # LaTeX equation patterns
        self.patterns = {
            'display_math': re.compile(r'\$\$([^$]+)\$\$', re.DOTALL),
            'inline_math': re.compile(r'\$([^$]+)\$'),
            'equation_env': re.compile(r'\\begin\{equation\}(.*?)\\end\{equation\}', re.DOTALL),
            'align_env': re.compile(r'\\begin\{align\}(.*?)\\end\{align\}', re.DOTALL),
        }
        
        self.logger.log("EquationExtractor initialized", level="INFO")
    
    def extract_from_paper(self, paper: ResearchPaper) -> List[ExtractedEquation]:
        """
        Extract equations from research paper.
        
        Args:
            paper: ResearchPaper instance
            
        Returns:
            List of extracted equations
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="EXTRACT_EQUATIONS",
            input_data={'paper_id': paper.paper_id},
            level=LogLevel.INFO
        )
        
        try:
            equations = []
            content = paper.content
            
            # Extract display math ($$...$$)
            for match in self.patterns['display_math'].finditer(content):
                eq_text = match.group(1).strip()
                context = self._extract_context(content, match.start(), match.end())
                equation = self._create_equation(eq_text, 'display', context, paper.paper_id)
                equations.append(equation)
            
            # Extract inline math ($...$)
            for match in self.patterns['inline_math'].finditer(content):
                eq_text = match.group(1).strip()
                context = self._extract_context(content, match.start(), match.end())
                equation = self._create_equation(eq_text, 'inline', context, paper.paper_id)
                equations.append(equation)
            
            # Extract equation environment
            for match in self.patterns['equation_env'].finditer(content):
                eq_text = match.group(1).strip()
                context = self._extract_context(content, match.start(), match.end())
                equation = self._create_equation(eq_text, 'numbered', context, paper.paper_id)
                equations.append(equation)
            
            # Extract align environment
            for match in self.patterns['align_env'].finditer(content):
                eq_text = match.group(1).strip()
                context = self._extract_context(content, match.start(), match.end())
                equation = self._create_equation(eq_text, 'align', context, paper.paper_id)
                equations.append(equation)
            
            # Store equations
            for eq in equations:
                self.equations[eq.equation_id] = eq
            
            # Update paper
            paper.equations = [eq.equation for eq in equations]
            
            cot.end_step(
                step_id,
                output_data={'num_equations': len(equations)},
                validation_passed=True
            )
            
            self.logger.log(f"Extracted {len(equations)} equations from {paper.paper_id}", level="INFO")
            
            return equations
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error extracting equations: {str(e)}", level="ERROR")
            return []
    
    def _create_equation(self,
                        eq_text: str,
                        eq_type: str,
                        context: str,
                        paper_id: str) -> ExtractedEquation:
        """Create ExtractedEquation instance."""
        equation_id = f"eq_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Extract variables (simple pattern matching)
        variables = self._extract_variables(eq_text)
        
        # Identify domain (simple keyword matching)
        domain = self._identify_domain(eq_text, context)
        
        return ExtractedEquation(
            equation_id=equation_id,
            equation=eq_text,
            equation_type=eq_type,
            context=context,
            variables=variables,
            domain=domain,
            metadata={'paper_id': paper_id}
        )
    
    def _extract_context(self, content: str, start: int, end: int, window: int = 200) -> str:
        """Extract context around equation."""
        context_start = max(0, start - window)
        context_end = min(len(content), end + window)
        return content[context_start:context_end]
    
    def _extract_variables(self, eq_text: str) -> List[str]:
        """Extract variable names from equation."""
        # Simple pattern: single letters, greek letters, subscripts
        variables = set()
        
        # Single letter variables
        var_pattern = re.compile(r'\b([a-z])\b', re.IGNORECASE)
        for match in var_pattern.finditer(eq_text):
            var = match.group(1).lower()
            if var not in ['e', 'i', 'd', 't']:  # Common non-variables
                variables.add(var)
        
        # Greek letters
        greek_pattern = re.compile(r'\\[a-z]+|[\u0391-\u03C9]')
        for match in greek_pattern.finditer(eq_text):
            variables.add(match.group(0))
        
        return sorted(list(variables))
    
    def _identify_domain(self, eq_text: str, context: str) -> Optional[str]:
        """Identify physics domain from equation and context."""
        domains = {
            'quantum': ['\\hbar', '\\psi', 'hamiltonian', 'schrodinger'],
            'classical': ['F=ma', '\\vec{F}', 'newton'],
            'electromagnetic': ['\\vec{E}', '\\vec{B}', 'maxwell'],
            'statistical': ['\\beta', 'partition', 'ensemble'],
            'relativistic': ['\\gamma', 'lorentz', 'einstein']
        }
        
        combined = (eq_text + ' ' + context).lower()
        
        for domain, keywords in domains.items():
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
                'equation_id': eq.equation_id,
                'equation': eq.equation,
                'equation_type': eq.equation_type,
                'domain': eq.domain,
                'variables': eq.variables
            }
            for eq in self.equations.values()
        ]

