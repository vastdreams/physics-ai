# PATH: substrate/graph/formula.py
# PURPOSE:
#   - Defines the Formula class - the atomic unit of physical knowledge
#   - Each formula represents a law, equation, principle, or model
#
# ROLE IN ARCHITECTURE:
#   - First-class node type in the FormulaGraph
#   - Everything the system "knows" about physics lives here
#
# MAIN EXPORTS:
#   - Formula: Core dataclass
#   - FormulaStatus: Enum for formula lifecycle
#   - FormulaLayer: Enum for formula abstraction level
#
# NON-RESPONSIBILITIES:
#   - Does NOT handle graph operations (that's FormulaGraph)
#   - Does NOT handle derivation planning (that's FormulaPlanner)
#
# NOTES FOR FUTURE AI:
#   - When adding new physics, create Formula objects
#   - regime_of_validity is critical - don't ignore it
#   - uncertainty should propagate through derivations

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Tuple
from enum import Enum, auto
from datetime import datetime
import hashlib
import json


class FormulaStatus(Enum):
    """Lifecycle status of a formula in the graph."""
    CANDIDATE = auto()      # Newly proposed, not yet validated
    ACCEPTED = auto()       # Validated and integrated
    DEPRECATED = auto()     # Superseded or found to be limited
    CONTESTED = auto()      # Conflicting evidence exists
    FUNDAMENTAL = auto()    # Core axiom, not derived


class FormulaLayer(Enum):
    """Abstraction level of the formula."""
    AXIOM = auto()          # Foundational principle (e.g., conservation laws)
    FUNDAMENTAL = auto()    # Fundamental theory (e.g., Standard Model, GR)
    EFFECTIVE = auto()      # Effective theory (e.g., Fermi theory)
    PHENOMENOLOGICAL = auto()  # Empirical fit (e.g., Hubble's law before expansion theory)
    APPROXIMATION = auto()  # Simplified form (e.g., small-angle approximation)
    NUMERICAL = auto()      # Numerical result or fit


@dataclass
class Variable:
    """A variable in a formula with its properties."""
    name: str
    symbol: str
    units: Optional[str] = None
    constraints: Optional[str] = None  # e.g., "> 0", "integer", "0 <= x <= 1"
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "symbol": self.symbol,
            "units": self.units,
            "constraints": self.constraints,
            "description": self.description,
        }
    
    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> Variable:
        return cls(**d)


@dataclass
class RegimeOfValidity:
    """Defines where a formula is valid."""
    
    # Quantitative bounds
    variable_bounds: Dict[str, Tuple[Optional[float], Optional[float]]] = field(default_factory=dict)
    # e.g., {"v": (None, 0.1 * c), "r": (r_s, None)}
    
    # Qualitative conditions
    conditions: List[str] = field(default_factory=list)
    # e.g., ["weak field", "non-relativistic", "thermal equilibrium"]
    
    # Scale indicators
    length_scale: Optional[Tuple[float, float]] = None  # (min, max) in meters
    energy_scale: Optional[Tuple[float, float]] = None  # (min, max) in eV
    time_scale: Optional[Tuple[float, float]] = None    # (min, max) in seconds
    
    # Domain tags
    domains: Set[str] = field(default_factory=set)
    # e.g., {"classical", "macroscopic", "low-energy"}
    
    def is_compatible(self, other: RegimeOfValidity) -> bool:
        """Check if two regimes overlap (could both apply)."""
        # Check domain compatibility
        if self.domains and other.domains:
            if not self.domains.intersection(other.domains):
                return False
        
        # Check variable bound overlaps
        for var, (lo, hi) in self.variable_bounds.items():
            if var in other.variable_bounds:
                o_lo, o_hi = other.variable_bounds[var]
                # Check for overlap
                if hi is not None and o_lo is not None and hi < o_lo:
                    return False
                if lo is not None and o_hi is not None and lo > o_hi:
                    return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "variable_bounds": self.variable_bounds,
            "conditions": self.conditions,
            "length_scale": self.length_scale,
            "energy_scale": self.energy_scale,
            "time_scale": self.time_scale,
            "domains": list(self.domains),
        }
    
    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> RegimeOfValidity:
        d = d.copy()
        d["domains"] = set(d.get("domains", []))
        return cls(**d)


@dataclass
class Evidence:
    """Evidence supporting or challenging a formula."""
    source_type: str  # "experiment", "derivation", "simulation", "observation"
    source_id: str    # Paper DOI, experiment ID, etc.
    description: str
    confidence: float  # 0 to 1
    date: Optional[datetime] = None
    supports: bool = True  # True = supports, False = challenges
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_type": self.source_type,
            "source_id": self.source_id,
            "description": self.description,
            "confidence": self.confidence,
            "date": self.date.isoformat() if self.date else None,
            "supports": self.supports,
        }
    
    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> Evidence:
        d = d.copy()
        if d.get("date"):
            d["date"] = datetime.fromisoformat(d["date"])
        return cls(**d)


@dataclass
class Formula:
    """
    A physical law, equation, principle, or model.
    
    This is the atomic unit of the reality substrate. Everything the
    Physics AI "knows" about the universe is encoded as Formula objects
    and their relationships in the FormulaGraph.
    """
    
    # Identity
    id: str
    name: str
    
    # Mathematical content
    symbolic_form: str  # LaTeX or SymPy-parseable string
    # e.g., "F = m * a" or "\\nabla \\cdot E = \\rho / \\epsilon_0"
    
    # Alternative representations
    sympy_expr: Optional[str] = None  # SymPy expression string
    latex: Optional[str] = None       # Pretty LaTeX
    code_impl: Optional[str] = None   # Python implementation reference
    
    # Variables
    inputs: List[Variable] = field(default_factory=list)
    outputs: List[Variable] = field(default_factory=list)
    parameters: List[Variable] = field(default_factory=list)  # Constants in the formula
    
    # Domain and validity
    domain: str = "general"  # classical, quantum, relativistic, statistical, etc.
    regime: RegimeOfValidity = field(default_factory=RegimeOfValidity)
    
    # Assumptions (things that must be true for formula to apply)
    assumptions: List[str] = field(default_factory=list)
    # e.g., ["point mass", "no friction", "isolated system"]
    
    # Metadata
    layer: FormulaLayer = FormulaLayer.FUNDAMENTAL
    status: FormulaStatus = FormulaStatus.CANDIDATE
    
    # Uncertainty and confidence
    uncertainty: float = 0.0  # Relative uncertainty in the formula itself
    confidence: float = 1.0   # Confidence in the formula's correctness (0-1)
    
    # Evidence
    evidence: List[Evidence] = field(default_factory=list)
    
    # Provenance
    source: Optional[str] = None  # Where this formula came from
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"  # "system", "evolution", "user", "paper:arxiv:..."
    
    # Description
    description: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        """Generate ID if not provided."""
        if not self.id:
            self.id = self._generate_id()
        if isinstance(self.tags, list):
            self.tags = set(self.tags)
    
    def _generate_id(self) -> str:
        """Generate a unique ID based on content."""
        content = f"{self.name}:{self.symbolic_form}:{self.domain}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def compute_confidence(self) -> float:
        """Compute confidence based on evidence and status."""
        if not self.evidence:
            return 0.5 if self.status == FormulaStatus.CANDIDATE else self.confidence
        
        supporting = [e for e in self.evidence if e.supports]
        challenging = [e for e in self.evidence if not e.supports]
        
        if not supporting and not challenging:
            return 0.5
        
        support_score = sum(e.confidence for e in supporting)
        challenge_score = sum(e.confidence for e in challenging)
        
        total = support_score + challenge_score
        if total == 0:
            return 0.5
        
        return support_score / total
    
    def is_applicable(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Check if this formula is applicable in a given context.
        
        Args:
            context: Dict with variable values and domain tags
            
        Returns:
            (is_applicable, list_of_reasons_if_not)
        """
        reasons = []
        
        # Check domain
        if "domain" in context:
            ctx_domains = set(context["domain"]) if isinstance(context["domain"], list) else {context["domain"]}
            if self.regime.domains and not self.regime.domains.intersection(ctx_domains):
                reasons.append(f"Domain mismatch: formula is for {self.regime.domains}, context is {ctx_domains}")
        
        # Check variable bounds
        for var, (lo, hi) in self.regime.variable_bounds.items():
            if var in context:
                val = context[var]
                if lo is not None and val < lo:
                    reasons.append(f"Variable {var}={val} below minimum {lo}")
                if hi is not None and val > hi:
                    reasons.append(f"Variable {var}={val} above maximum {hi}")
        
        # Check qualitative conditions (simplified - would need NLP in practice)
        for condition in self.regime.conditions:
            condition_key = condition.lower().replace(" ", "_")
            if condition_key in context and not context[condition_key]:
                reasons.append(f"Condition not met: {condition}")
        
        return (len(reasons) == 0, reasons)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "symbolic_form": self.symbolic_form,
            "sympy_expr": self.sympy_expr,
            "latex": self.latex,
            "code_impl": self.code_impl,
            "inputs": [v.to_dict() for v in self.inputs],
            "outputs": [v.to_dict() for v in self.outputs],
            "parameters": [v.to_dict() for v in self.parameters],
            "domain": self.domain,
            "regime": self.regime.to_dict(),
            "assumptions": self.assumptions,
            "layer": self.layer.name,
            "status": self.status.name,
            "uncertainty": self.uncertainty,
            "confidence": self.confidence,
            "evidence": [e.to_dict() for e in self.evidence],
            "source": self.source,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "created_by": self.created_by,
            "description": self.description,
            "tags": list(self.tags),
        }
    
    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> Formula:
        """Deserialize from dictionary."""
        d = d.copy()
        d["inputs"] = [Variable.from_dict(v) for v in d.get("inputs", [])]
        d["outputs"] = [Variable.from_dict(v) for v in d.get("outputs", [])]
        d["parameters"] = [Variable.from_dict(v) for v in d.get("parameters", [])]
        d["regime"] = RegimeOfValidity.from_dict(d.get("regime", {}))
        d["layer"] = FormulaLayer[d.get("layer", "FUNDAMENTAL")]
        d["status"] = FormulaStatus[d.get("status", "CANDIDATE")]
        d["evidence"] = [Evidence.from_dict(e) for e in d.get("evidence", [])]
        d["created_at"] = datetime.fromisoformat(d["created_at"]) if d.get("created_at") else datetime.now()
        d["modified_at"] = datetime.fromisoformat(d["modified_at"]) if d.get("modified_at") else datetime.now()
        d["tags"] = set(d.get("tags", []))
        return cls(**d)
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if not isinstance(other, Formula):
            return False
        return self.id == other.id
    
    def __repr__(self):
        return f"Formula(id={self.id}, name={self.name}, symbolic_form={self.symbolic_form})"


# =============================================================================
# Factory functions for common formula types
# =============================================================================

def create_conservation_law(
    name: str,
    conserved_quantity: str,
    symbolic_form: str,
    domain: str = "general",
    **kwargs
) -> Formula:
    """Factory for conservation laws."""
    return Formula(
        id=kwargs.get("id", ""),
        name=name,
        symbolic_form=symbolic_form,
        domain=domain,
        layer=FormulaLayer.AXIOM,
        status=FormulaStatus.FUNDAMENTAL,
        confidence=1.0,
        tags={"conservation", conserved_quantity, domain},
        description=f"Conservation of {conserved_quantity}",
        **{k: v for k, v in kwargs.items() if k not in ["id"]}
    )


def create_equation_of_motion(
    name: str,
    symbolic_form: str,
    domain: str,
    inputs: List[Variable],
    outputs: List[Variable],
    **kwargs
) -> Formula:
    """Factory for equations of motion."""
    return Formula(
        id=kwargs.get("id", ""),
        name=name,
        symbolic_form=symbolic_form,
        domain=domain,
        inputs=inputs,
        outputs=outputs,
        layer=FormulaLayer.FUNDAMENTAL,
        status=FormulaStatus.ACCEPTED,
        tags={"equation_of_motion", domain},
        **{k: v for k, v in kwargs.items() if k not in ["id"]}
    )


def create_approximation(
    name: str,
    symbolic_form: str,
    parent_formula_id: str,
    conditions: List[str],
    **kwargs
) -> Formula:
    """Factory for approximations of other formulas."""
    regime = RegimeOfValidity(conditions=conditions)
    return Formula(
        id=kwargs.get("id", ""),
        name=name,
        symbolic_form=symbolic_form,
        layer=FormulaLayer.APPROXIMATION,
        status=FormulaStatus.ACCEPTED,
        regime=regime,
        source=f"approximation_of:{parent_formula_id}",
        tags={"approximation"},
        **{k: v for k, v in kwargs.items() if k not in ["id"]}
    )

