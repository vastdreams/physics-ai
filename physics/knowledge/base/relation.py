"""
PATH: physics/knowledge/base/relation.py
PURPOSE: Relation types for physics knowledge graph edges

DESIGN PRINCIPLES:
- Relations are typed and directional
- Each relation carries semantic meaning
- Relations can have properties (strength, conditions)
- Enables inference and reasoning over the graph
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional


class RelationType(Enum):
    """Types of relations between knowledge nodes."""
    
    # Derivation relations
    DERIVES_FROM = "derives_from"    # A is derived from B
    LEADS_TO = "leads_to"            # A implies/leads to B
    
    # Dependency relations
    USES = "uses"                    # A uses constant/equation B
    REQUIRES = "requires"            # A requires condition B
    
    # Validation relations
    VALIDATES = "validates"          # Experiment A validates theory B
    CONTRADICTS = "contradicts"      # A contradicts B
    
    # Generalization relations
    GENERALIZES = "generalizes"      # A is a generalization of B
    SPECIAL_CASE = "special_case"    # A is a special case of B
    
    # Domain relations
    BELONGS_TO = "belongs_to"        # A belongs to domain B
    CONNECTS = "connects"            # A connects domains B and C
    
    # Equivalence relations
    EQUIVALENT = "equivalent"        # A is equivalent to B (different form)
    APPROXIMATES = "approximates"    # A approximates B under conditions


@dataclass(frozen=True)
class Relation:
    """
    Base class for graph edges.
    
    Immutable to ensure graph integrity.
    """
    
    source_id: str                   # Source node ID
    target_id: str                   # Target node ID
    relation_type: RelationType
    
    # Optional properties
    strength: float = 1.0            # Relation strength (0-1)
    bidirectional: bool = False      # Is relation symmetric?
    conditions: tuple = field(default_factory=tuple)
    notes: str = ""
    
    @property
    def id(self) -> str:
        """Unique relation identifier."""
        return f"{self.source_id}--{self.relation_type.value}-->{self.target_id}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'source_id': self.source_id,
            'target_id': self.target_id,
            'relation_type': self.relation_type.value,
            'strength': self.strength,
            'bidirectional': self.bidirectional,
            'conditions': list(self.conditions),
            'notes': self.notes,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relation':
        return cls(
            source_id=data['source_id'],
            target_id=data['target_id'],
            relation_type=RelationType(data['relation_type']),
            strength=data.get('strength', 1.0),
            bidirectional=data.get('bidirectional', False),
            conditions=tuple(data.get('conditions', [])),
            notes=data.get('notes', ''),
        )
    
    def __hash__(self):
        return hash(self.id)


# Convenience factory functions for common relation types

def DerivesFrom(source: str, target: str, **kwargs) -> Relation:
    """Create a 'derives_from' relation."""
    return Relation(
        source_id=source,
        target_id=target,
        relation_type=RelationType.DERIVES_FROM,
        **kwargs
    )


def LeadsTo(source: str, target: str, **kwargs) -> Relation:
    """Create a 'leads_to' relation."""
    return Relation(
        source_id=source,
        target_id=target,
        relation_type=RelationType.LEADS_TO,
        **kwargs
    )


def Uses(source: str, target: str, **kwargs) -> Relation:
    """Create a 'uses' relation (equation uses constant)."""
    return Relation(
        source_id=source,
        target_id=target,
        relation_type=RelationType.USES,
        **kwargs
    )


def Requires(source: str, target: str, conditions: tuple = (), **kwargs) -> Relation:
    """Create a 'requires' relation with conditions."""
    return Relation(
        source_id=source,
        target_id=target,
        relation_type=RelationType.REQUIRES,
        conditions=conditions,
        **kwargs
    )


def Validates(source: str, target: str, strength: float = 1.0, **kwargs) -> Relation:
    """Create a 'validates' relation (experiment validates theory)."""
    return Relation(
        source_id=source,
        target_id=target,
        relation_type=RelationType.VALIDATES,
        strength=strength,
        **kwargs
    )


def Contradicts(source: str, target: str, **kwargs) -> Relation:
    """Create a 'contradicts' relation."""
    return Relation(
        source_id=source,
        target_id=target,
        relation_type=RelationType.CONTRADICTS,
        **kwargs
    )


def Generalizes(source: str, target: str, **kwargs) -> Relation:
    """Create a 'generalizes' relation (A generalizes B)."""
    return Relation(
        source_id=source,
        target_id=target,
        relation_type=RelationType.GENERALIZES,
        **kwargs
    )


def SpecialCase(source: str, target: str, conditions: tuple = (), **kwargs) -> Relation:
    """Create a 'special_case' relation (A is special case of B under conditions)."""
    return Relation(
        source_id=source,
        target_id=target,
        relation_type=RelationType.SPECIAL_CASE,
        conditions=conditions,
        **kwargs
    )
