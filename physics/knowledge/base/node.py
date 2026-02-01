"""
PATH: physics/knowledge/base/node.py
PURPOSE: Base node classes for micro-modular physics knowledge representation

DESIGN PRINCIPLES:
- Each node is a self-contained unit of knowledge
- Nodes are immutable after creation (for AI safety)
- Nodes declare their own relations (incoming/outgoing)
- Serializable to JSON for persistence and AI evolution
- Hashable for graph operations
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from abc import ABC, abstractmethod
import hashlib
import json


class NodeType(Enum):
    """Types of knowledge nodes."""
    CONSTANT = "constant"
    EQUATION = "equation"
    THEOREM = "theorem"
    PRINCIPLE = "principle"
    LAW = "law"
    DEFINITION = "definition"
    APPROXIMATION = "approximation"
    EXPERIMENTAL = "experimental"


class NodeStatus(Enum):
    """Verification status of knowledge."""
    FUNDAMENTAL = "fundamental"      # Axiom or postulate
    PROVEN = "proven"                # Mathematically derived
    EXPERIMENTAL = "experimental"    # Experimentally verified
    EMPIRICAL = "empirical"          # Fitted to data
    THEORETICAL = "theoretical"      # Predicted, not yet verified
    APPROXIMATE = "approximate"      # Valid under conditions
    DEPRECATED = "deprecated"        # Superseded


@dataclass(frozen=True)
class KnowledgeNode(ABC):
    """
    Base class for all physics knowledge nodes.
    
    Immutable by design - AI can create new nodes but not modify existing ones.
    This ensures knowledge integrity and allows safe self-evolution.
    """
    
    # Core identity
    id: str                          # Unique identifier (e.g., "newton_second_law")
    name: str                        # Human-readable name
    domain: str                      # Physics domain (e.g., "classical_mechanics")
    
    # Classification
    node_type: NodeType = field(default=NodeType.EQUATION)
    status: NodeStatus = field(default=NodeStatus.PROVEN)
    
    # Metadata
    description: str = ""
    discoverer: str = ""
    year: Optional[int] = None
    tags: tuple = field(default_factory=tuple)  # Immutable tuple instead of list
    
    # Relations (declared by node, resolved by graph)
    derives_from: tuple = field(default_factory=tuple)   # Node IDs this derives from
    leads_to: tuple = field(default_factory=tuple)       # Node IDs this leads to
    uses: tuple = field(default_factory=tuple)           # Constants/equations used
    conditions: tuple = field(default_factory=tuple)     # Validity conditions
    
    @property
    def hash(self) -> str:
        """Content-addressable hash for integrity verification."""
        content = f"{self.id}:{self.name}:{self.domain}:{self.node_type.value}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Serialize node to dictionary."""
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeNode':
        """Deserialize node from dictionary."""
        pass
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if not isinstance(other, KnowledgeNode):
            return False
        return self.id == other.id


@dataclass(frozen=True)
class ConstantNode(KnowledgeNode):
    """
    Physical constant node.
    
    Examples: Speed of light (c), Planck constant (h), Gravitational constant (G)
    """
    
    symbol: str = ""                 # LaTeX symbol (e.g., "c", "\\hbar")
    value: float = 0.0               # Numerical value in SI units
    uncertainty: float = 0.0         # Measurement uncertainty
    unit: str = ""                   # SI unit string
    dimension: str = ""              # Dimensional formula (e.g., "L T^-1")
    
    node_type: NodeType = field(default=NodeType.CONSTANT)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'domain': self.domain,
            'node_type': self.node_type.value,
            'status': self.status.value,
            'symbol': self.symbol,
            'value': self.value,
            'uncertainty': self.uncertainty,
            'unit': self.unit,
            'dimension': self.dimension,
            'description': self.description,
            'discoverer': self.discoverer,
            'year': self.year,
            'tags': list(self.tags),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConstantNode':
        return cls(
            id=data['id'],
            name=data['name'],
            domain=data['domain'],
            node_type=NodeType(data.get('node_type', 'constant')),
            status=NodeStatus(data.get('status', 'experimental')),
            symbol=data.get('symbol', ''),
            value=data.get('value', 0.0),
            uncertainty=data.get('uncertainty', 0.0),
            unit=data.get('unit', ''),
            dimension=data.get('dimension', ''),
            description=data.get('description', ''),
            discoverer=data.get('discoverer', ''),
            year=data.get('year'),
            tags=tuple(data.get('tags', [])),
        )


@dataclass(frozen=True)
class EquationNode(KnowledgeNode):
    """
    Physics equation node.
    
    Examples: F = ma, E = mc², Schrödinger equation
    """
    
    latex: str = ""                  # LaTeX representation
    sympy: str = ""                  # SymPy-parseable expression
    variables: tuple = field(default_factory=tuple)  # Variable definitions
    
    # First principles derivation
    derivation_steps: tuple = field(default_factory=tuple)
    assumptions: tuple = field(default_factory=tuple)
    
    node_type: NodeType = field(default=NodeType.EQUATION)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'domain': self.domain,
            'node_type': self.node_type.value,
            'status': self.status.value,
            'latex': self.latex,
            'sympy': self.sympy,
            'variables': list(self.variables),
            'derivation_steps': list(self.derivation_steps),
            'assumptions': list(self.assumptions),
            'derives_from': list(self.derives_from),
            'leads_to': list(self.leads_to),
            'uses': list(self.uses),
            'conditions': list(self.conditions),
            'description': self.description,
            'discoverer': self.discoverer,
            'year': self.year,
            'tags': list(self.tags),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EquationNode':
        return cls(
            id=data['id'],
            name=data['name'],
            domain=data['domain'],
            node_type=NodeType(data.get('node_type', 'equation')),
            status=NodeStatus(data.get('status', 'proven')),
            latex=data.get('latex', ''),
            sympy=data.get('sympy', ''),
            variables=tuple(data.get('variables', [])),
            derivation_steps=tuple(data.get('derivation_steps', [])),
            assumptions=tuple(data.get('assumptions', [])),
            derives_from=tuple(data.get('derives_from', [])),
            leads_to=tuple(data.get('leads_to', [])),
            uses=tuple(data.get('uses', [])),
            conditions=tuple(data.get('conditions', [])),
            description=data.get('description', ''),
            discoverer=data.get('discoverer', ''),
            year=data.get('year'),
            tags=tuple(data.get('tags', [])),
        )


@dataclass(frozen=True)
class TheoremNode(KnowledgeNode):
    """
    Mathematical theorem in physics.
    
    Examples: Noether's theorem, Liouville's theorem
    """
    
    statement: str = ""              # Formal statement
    proof_outline: tuple = field(default_factory=tuple)
    
    node_type: NodeType = field(default=NodeType.THEOREM)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'domain': self.domain,
            'node_type': self.node_type.value,
            'status': self.status.value,
            'statement': self.statement,
            'proof_outline': list(self.proof_outline),
            'derives_from': list(self.derives_from),
            'leads_to': list(self.leads_to),
            'uses': list(self.uses),
            'description': self.description,
            'discoverer': self.discoverer,
            'year': self.year,
            'tags': list(self.tags),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TheoremNode':
        return cls(
            id=data['id'],
            name=data['name'],
            domain=data['domain'],
            node_type=NodeType(data.get('node_type', 'theorem')),
            status=NodeStatus(data.get('status', 'proven')),
            statement=data.get('statement', ''),
            proof_outline=tuple(data.get('proof_outline', [])),
            derives_from=tuple(data.get('derives_from', [])),
            leads_to=tuple(data.get('leads_to', [])),
            uses=tuple(data.get('uses', [])),
            description=data.get('description', ''),
            discoverer=data.get('discoverer', ''),
            year=data.get('year'),
            tags=tuple(data.get('tags', [])),
        )


@dataclass(frozen=True)
class PrincipleNode(KnowledgeNode):
    """
    Fundamental physics principle (axiom/postulate).
    
    Examples: Principle of least action, Equivalence principle
    """
    
    statement: str = ""              # Formal statement
    mathematical_form: str = ""      # Mathematical expression if applicable
    
    node_type: NodeType = field(default=NodeType.PRINCIPLE)
    status: NodeStatus = field(default=NodeStatus.FUNDAMENTAL)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'domain': self.domain,
            'node_type': self.node_type.value,
            'status': self.status.value,
            'statement': self.statement,
            'mathematical_form': self.mathematical_form,
            'leads_to': list(self.leads_to),
            'description': self.description,
            'discoverer': self.discoverer,
            'year': self.year,
            'tags': list(self.tags),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PrincipleNode':
        return cls(
            id=data['id'],
            name=data['name'],
            domain=data['domain'],
            node_type=NodeType(data.get('node_type', 'principle')),
            status=NodeStatus(data.get('status', 'fundamental')),
            statement=data.get('statement', ''),
            mathematical_form=data.get('mathematical_form', ''),
            leads_to=tuple(data.get('leads_to', [])),
            description=data.get('description', ''),
            discoverer=data.get('discoverer', ''),
            year=data.get('year'),
            tags=tuple(data.get('tags', [])),
        )
