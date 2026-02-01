# core/
"""
PATH: core/knowledge_synthesis.py
PURPOSE: Knowledge synthesis from multiple sources with conflict resolution.

FLOW:
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│   Extract   │───▶│   Resolve    │───▶│    Build    │───▶│   Validate   │
│  Entities   │    │  Conflicts   │    │    Graph    │    │   Output     │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘

First Principle Analysis:
- Knowledge synthesis combines information from multiple sources
- Must handle conflicting information and resolve contradictions
- Mathematical foundation: information theory, graph theory, set theory
- Architecture: modular synthesis strategies

DEPENDENCIES:
- validators: Data validation
- loggers: System logging
- networkx: Graph operations (optional)
"""

import logging
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import hashlib
import json
import re

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from validators.data_validator import DataValidator
from loggers.system_logger import SystemLogger


@dataclass
class Entity:
    """Represents an extracted entity."""
    id: str
    name: str
    entity_type: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    sources: List[str] = field(default_factory=list)
    confidence: float = 1.0
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if isinstance(other, Entity):
            return self.id == other.id
        return False


@dataclass
class Relationship:
    """Represents a relationship between entities."""
    id: str
    source_entity: str
    target_entity: str
    relation_type: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    sources: List[str] = field(default_factory=list)
    
    def __hash__(self):
        return hash(self.id)


@dataclass
class KnowledgeGraph:
    """Represents a knowledge graph."""
    entities: Dict[str, Entity]
    relationships: Dict[str, Relationship]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'entities': {k: {
                'id': v.id,
                'name': v.name,
                'type': v.entity_type,
                'attributes': v.attributes,
                'confidence': v.confidence
            } for k, v in self.entities.items()},
            'relationships': {k: {
                'id': v.id,
                'source': v.source_entity,
                'target': v.target_entity,
                'type': v.relation_type,
                'confidence': v.confidence
            } for k, v in self.relationships.items()},
            'metadata': self.metadata
        }


class ConflictResolver:
    """
    Resolves conflicts between knowledge from different sources.
    
    Strategies:
    - Majority voting
    - Confidence-weighted voting
    - Recency-based resolution
    - Source credibility weighting
    """
    
    def __init__(self, strategy: str = 'confidence'):
        """
        Initialize conflict resolver.
        
        Args:
            strategy: Resolution strategy ('majority', 'confidence', 'recency')
        """
        self.strategy = strategy
        self.source_weights: Dict[str, float] = defaultdict(lambda: 1.0)
        self.logger = SystemLogger()
    
    def set_source_weight(self, source: str, weight: float) -> None:
        """Set credibility weight for a source."""
        self.source_weights[source] = weight
    
    def resolve(self, conflicting_values: List[Tuple[Any, float, str]]) -> Tuple[Any, float]:
        """
        Resolve conflict between values.
        
        Args:
            conflicting_values: List of (value, confidence, source) tuples
            
        Returns:
            Tuple of (resolved_value, final_confidence)
        """
        if not conflicting_values:
            return None, 0.0
        
        if len(conflicting_values) == 1:
            return conflicting_values[0][0], conflicting_values[0][1]
        
        if self.strategy == 'majority':
            return self._majority_voting(conflicting_values)
        elif self.strategy == 'confidence':
            return self._confidence_weighted(conflicting_values)
        else:
            return self._confidence_weighted(conflicting_values)
    
    def _majority_voting(self, values: List[Tuple[Any, float, str]]) -> Tuple[Any, float]:
        """Resolve by majority voting."""
        vote_counts = defaultdict(int)
        
        for value, _, _ in values:
            # Convert to string for hashability
            key = json.dumps(value, sort_keys=True, default=str) if isinstance(value, (dict, list)) else str(value)
            vote_counts[key] += 1
        
        # Find majority
        max_votes = max(vote_counts.values())
        winners = [k for k, v in vote_counts.items() if v == max_votes]
        
        # Calculate confidence based on agreement
        confidence = max_votes / len(values)
        
        # Return first winner (could be enhanced to handle ties better)
        winning_key = winners[0]
        
        # Find original value
        for value, conf, _ in values:
            key = json.dumps(value, sort_keys=True, default=str) if isinstance(value, (dict, list)) else str(value)
            if key == winning_key:
                return value, confidence
        
        return values[0][0], confidence
    
    def _confidence_weighted(self, values: List[Tuple[Any, float, str]]) -> Tuple[Any, float]:
        """Resolve by confidence-weighted voting."""
        weighted_votes = defaultdict(float)
        
        for value, confidence, source in values:
            key = json.dumps(value, sort_keys=True, default=str) if isinstance(value, (dict, list)) else str(value)
            source_weight = self.source_weights[source]
            weighted_votes[key] += confidence * source_weight
        
        # Find highest weighted
        winning_key = max(weighted_votes.keys(), key=lambda k: weighted_votes[k])
        
        # Normalize confidence
        total_weight = sum(weighted_votes.values())
        final_confidence = weighted_votes[winning_key] / total_weight if total_weight > 0 else 0
        
        # Find original value
        for value, conf, _ in values:
            key = json.dumps(value, sort_keys=True, default=str) if isinstance(value, (dict, list)) else str(value)
            if key == winning_key:
                return value, final_confidence
        
        return values[0][0], final_confidence


class EntityExtractor:
    """
    Extracts entities from knowledge sources.
    
    Supports extraction from:
    - Dictionaries with known schema
    - Natural language text (basic)
    - Structured documents
    """
    
    # Common physics entity patterns
    PHYSICS_PATTERNS = {
        'quantity': r'\b(\d+(?:\.\d+)?)\s*(kg|m|s|J|N|W|V|A|Hz|Pa|K)\b',
        'equation': r'([a-zA-Z]+)\s*=\s*([^,.\n]+)',
        'constant': r'(speed of light|gravitational constant|planck constant|c|G|h|ℏ)',
        'theory': r'\b(quantum|classical|relativistic|statistical)\s+(mechanics|physics|theory)\b',
    }
    
    def __init__(self):
        self.logger = SystemLogger()
        self.entity_counter = 0
    
    def _generate_id(self, prefix: str = 'entity') -> str:
        """Generate unique entity ID."""
        self.entity_counter += 1
        return f"{prefix}_{self.entity_counter}"
    
    def extract_from_dict(self, data: Dict[str, Any], source: str = 'dict') -> List[Entity]:
        """
        Extract entities from a dictionary.
        
        Args:
            data: Dictionary containing knowledge
            source: Source identifier
            
        Returns:
            List of extracted entities
        """
        entities = []
        
        def extract_recursive(obj: Any, path: str = '') -> None:
            if isinstance(obj, dict):
                # The dict itself might be an entity
                if 'name' in obj or 'id' in obj or 'type' in obj:
                    entity = Entity(
                        id=self._generate_id(),
                        name=str(obj.get('name', obj.get('id', path))),
                        entity_type=obj.get('type', 'object'),
                        attributes={k: v for k, v in obj.items() if k not in ['name', 'id', 'type']},
                        sources=[source]
                    )
                    entities.append(entity)
                
                # Recurse into nested dicts
                for key, value in obj.items():
                    extract_recursive(value, f"{path}.{key}" if path else key)
            
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    extract_recursive(item, f"{path}[{i}]")
            
            elif isinstance(obj, (str, int, float, bool)):
                # Check if it's a physics quantity or constant
                if isinstance(obj, str):
                    for pattern_name, pattern in self.PHYSICS_PATTERNS.items():
                        matches = re.findall(pattern, obj, re.IGNORECASE)
                        for match in matches:
                            if isinstance(match, tuple):
                                match = ' '.join(match)
                            entity = Entity(
                                id=self._generate_id(pattern_name),
                                name=match,
                                entity_type=pattern_name,
                                attributes={'raw_value': obj, 'path': path},
                                sources=[source]
                            )
                            entities.append(entity)
        
        extract_recursive(data)
        return entities
    
    def extract_from_text(self, text: str, source: str = 'text') -> List[Entity]:
        """
        Extract entities from natural language text (basic extraction).
        
        Args:
            text: Text to extract from
            source: Source identifier
            
        Returns:
            List of extracted entities
        """
        entities = []
        
        for pattern_name, pattern in self.PHYSICS_PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match_str = ' '.join(match)
                else:
                    match_str = match
                
                entity = Entity(
                    id=self._generate_id(pattern_name),
                    name=match_str,
                    entity_type=pattern_name,
                    attributes={'context': text[:100]},
                    sources=[source]
                )
                entities.append(entity)
        
        return entities


class RelationshipExtractor:
    """
    Extracts relationships between entities.
    """
    
    # Common physics relationships
    RELATION_PATTERNS = [
        (r'(\w+)\s+equals?\s+(\w+)', 'equals'),
        (r'(\w+)\s+is\s+proportional\s+to\s+(\w+)', 'proportional_to'),
        (r'(\w+)\s+depends?\s+on\s+(\w+)', 'depends_on'),
        (r'(\w+)\s+causes?\s+(\w+)', 'causes'),
        (r'(\w+)\s+derives?\s+from\s+(\w+)', 'derived_from'),
    ]
    
    def __init__(self):
        self.logger = SystemLogger()
        self.relation_counter = 0
    
    def _generate_id(self) -> str:
        """Generate unique relationship ID."""
        self.relation_counter += 1
        return f"rel_{self.relation_counter}"
    
    def extract_from_entities(self, entities: List[Entity]) -> List[Relationship]:
        """
        Extract relationships based on entity attributes.
        
        Args:
            entities: List of entities
            
        Returns:
            List of relationships
        """
        relationships = []
        entity_map = {e.id: e for e in entities}
        
        # Look for shared attributes that might indicate relationships
        for i, e1 in enumerate(entities):
            for e2 in entities[i+1:]:
                # Check for common sources
                common_sources = set(e1.sources) & set(e2.sources)
                if common_sources:
                    # Entities from same source might be related
                    relationship = Relationship(
                        id=self._generate_id(),
                        source_entity=e1.id,
                        target_entity=e2.id,
                        relation_type='co_occurs',
                        attributes={'common_sources': list(common_sources)},
                        confidence=0.5,
                        sources=list(common_sources)
                    )
                    relationships.append(relationship)
                
                # Check for type relationships
                if e1.entity_type == e2.entity_type:
                    relationship = Relationship(
                        id=self._generate_id(),
                        source_entity=e1.id,
                        target_entity=e2.id,
                        relation_type='same_type',
                        attributes={'type': e1.entity_type},
                        confidence=0.7
                    )
                    relationships.append(relationship)
        
        return relationships


class KnowledgeSynthesizer:
    """
    Synthesizes knowledge from multiple sources.
    
    Combines information, resolves conflicts, and creates
    integrated knowledge representations.
    """
    
    def __init__(self, conflict_strategy: str = 'confidence'):
        """
        Initialize knowledge synthesizer.
        
        Args:
            conflict_strategy: Strategy for conflict resolution
        """
        self.validator = DataValidator()
        self.logger = SystemLogger()
        self.knowledge_graph = KnowledgeGraph(entities={}, relationships={})
        
        self.entity_extractor = EntityExtractor()
        self.relationship_extractor = RelationshipExtractor()
        self.conflict_resolver = ConflictResolver(strategy=conflict_strategy)
        
        self.logger.log("KnowledgeSynthesizer initialized", level="INFO")
    
    def synthesize(self, knowledge_sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Synthesize knowledge from multiple sources.
        
        Mathematical approach:
        - Information fusion: weighted combination of sources
        - Conflict resolution: majority voting or confidence-based
        - Graph construction: knowledge represented as graph
        
        Args:
            knowledge_sources: List of knowledge dictionaries
            
        Returns:
            Synthesized knowledge
        """
        if not self.validator.validate_list(knowledge_sources):
            self.logger.log("Invalid knowledge sources", level="ERROR")
            raise ValueError("Invalid knowledge sources")
        
        self.logger.log(f"Synthesizing from {len(knowledge_sources)} sources", level="DEBUG")
        
        try:
            # Extract entities and relationships
            entities = self._extract_entities(knowledge_sources)
            relationships = self._extract_relationships(knowledge_sources)
            
            # Resolve conflicts
            resolved_entities = self._resolve_entity_conflicts(entities)
            resolved_relationships = self._resolve_relationship_conflicts(relationships)
            
            # Build knowledge graph
            self.knowledge_graph = self._build_graph(resolved_entities, resolved_relationships)
            
            synthesized = {
                "entities": [e.__dict__ for e in resolved_entities],
                "relationships": [r.__dict__ for r in resolved_relationships],
                "graph": self.knowledge_graph.to_dict(),
                "statistics": {
                    "source_count": len(knowledge_sources),
                    "entity_count": len(resolved_entities),
                    "relationship_count": len(resolved_relationships)
                }
            }
            
            if not self.validator.validate_dict(synthesized):
                self.logger.log("Invalid synthesized knowledge", level="ERROR")
                raise ValueError("Invalid synthesized knowledge")
            
            self.logger.log("Knowledge synthesis completed", level="INFO")
            return synthesized
            
        except Exception as e:
            self.logger.log(f"Error in synthesis: {str(e)}", level="ERROR")
            raise
    
    def _extract_entities(self, sources: List[Dict[str, Any]]) -> List[Entity]:
        """Extract entities from knowledge sources."""
        all_entities = []
        
        for i, source in enumerate(sources):
            source_id = source.get('source_id', f'source_{i}')
            entities = self.entity_extractor.extract_from_dict(source, source_id)
            all_entities.extend(entities)
        
        self.logger.log(f"Extracted {len(all_entities)} entities", level="DEBUG")
        return all_entities
    
    def _extract_relationships(self, sources: List[Dict[str, Any]]) -> List[Relationship]:
        """Extract relationships from knowledge sources."""
        # First get all entities
        all_entities = self._extract_entities(sources)
        
        # Then extract relationships
        relationships = self.relationship_extractor.extract_from_entities(all_entities)
        
        self.logger.log(f"Extracted {len(relationships)} relationships", level="DEBUG")
        return relationships
    
    def _resolve_entity_conflicts(self, entities: List[Entity]) -> List[Entity]:
        """Resolve conflicts in extracted entities."""
        # Group entities by name (potential duplicates)
        entity_groups = defaultdict(list)
        for entity in entities:
            entity_groups[entity.name.lower()].append(entity)
        
        resolved = []
        for name, group in entity_groups.items():
            if len(group) == 1:
                resolved.append(group[0])
            else:
                # Merge entities with same name
                merged = self._merge_entities(group)
                resolved.append(merged)
        
        self.logger.log(f"Resolved to {len(resolved)} unique entities", level="DEBUG")
        return resolved
    
    def _merge_entities(self, entities: List[Entity]) -> Entity:
        """Merge multiple entities into one."""
        if not entities:
            return None
        
        # Use first entity as base
        merged = Entity(
            id=entities[0].id,
            name=entities[0].name,
            entity_type=entities[0].entity_type,
            attributes={},
            sources=[],
            confidence=0.0
        )
        
        # Merge attributes
        for entity in entities:
            merged.sources.extend(entity.sources)
            merged.confidence = max(merged.confidence, entity.confidence)
            
            for key, value in entity.attributes.items():
                if key not in merged.attributes:
                    merged.attributes[key] = value
                else:
                    # Resolve attribute conflict
                    existing = merged.attributes[key]
                    if existing != value:
                        resolved, _ = self.conflict_resolver.resolve([
                            (existing, merged.confidence, merged.sources[0] if merged.sources else ''),
                            (value, entity.confidence, entity.sources[0] if entity.sources else '')
                        ])
                        merged.attributes[key] = resolved
        
        # Remove duplicate sources
        merged.sources = list(set(merged.sources))
        
        return merged
    
    def _resolve_relationship_conflicts(self, relationships: List[Relationship]) -> List[Relationship]:
        """Resolve conflicts in extracted relationships."""
        # Group by (source, target, type)
        rel_groups = defaultdict(list)
        for rel in relationships:
            key = (rel.source_entity, rel.target_entity, rel.relation_type)
            rel_groups[key].append(rel)
        
        resolved = []
        for key, group in rel_groups.items():
            if len(group) == 1:
                resolved.append(group[0])
            else:
                # Merge relationships
                merged = Relationship(
                    id=group[0].id,
                    source_entity=group[0].source_entity,
                    target_entity=group[0].target_entity,
                    relation_type=group[0].relation_type,
                    attributes={},
                    confidence=max(r.confidence for r in group),
                    sources=list(set(s for r in group for s in r.sources))
                )
                resolved.append(merged)
        
        self.logger.log(f"Resolved to {len(resolved)} unique relationships", level="DEBUG")
        return resolved
    
    def _build_graph(self, entities: List[Entity], relationships: List[Relationship]) -> KnowledgeGraph:
        """Build knowledge graph from entities and relationships."""
        entity_dict = {e.id: e for e in entities}
        rel_dict = {r.id: r for r in relationships}
        
        return KnowledgeGraph(
            entities=entity_dict,
            relationships=rel_dict,
            metadata={
                'entity_count': len(entities),
                'relationship_count': len(relationships),
                'entity_types': list(set(e.entity_type for e in entities)),
                'relationship_types': list(set(r.relation_type for r in relationships))
            }
        )
    
    def query_graph(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Query the knowledge graph.
        
        Args:
            query: Query specification
            
        Returns:
            List of matching results
        """
        results = []
        
        # Query entities
        if 'entity_type' in query:
            for entity in self.knowledge_graph.entities.values():
                if entity.entity_type == query['entity_type']:
                    results.append({
                        'type': 'entity',
                        'data': entity.__dict__
                    })
        
        # Query relationships
        if 'relation_type' in query:
            for rel in self.knowledge_graph.relationships.values():
                if rel.relation_type == query['relation_type']:
                    results.append({
                        'type': 'relationship',
                        'data': rel.__dict__
                    })
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get synthesis statistics."""
        return {
            'entity_count': len(self.knowledge_graph.entities),
            'relationship_count': len(self.knowledge_graph.relationships),
            'entity_types': self.knowledge_graph.metadata.get('entity_types', []),
            'relationship_types': self.knowledge_graph.metadata.get('relationship_types', [])
        }
