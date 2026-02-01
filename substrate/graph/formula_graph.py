# PATH: substrate/graph/formula_graph.py
# PURPOSE:
#   - The Formula Graph - the reality substrate of Physics AI
#   - Stores formulas and their relationships (derivations, limits, etc.)
#
# ROLE IN ARCHITECTURE:
#   - Central knowledge store for all physics knowledge
#   - Everything else queries and modifies this graph
#
# MAIN EXPORTS:
#   - FormulaGraph: The main graph class
#   - EdgeType: Types of relationships between formulas
#
# NON-RESPONSIBILITIES:
#   - Does NOT plan derivation paths (that's FormulaPlanner)
#   - Does NOT handle persistence (uses simple JSON for now)
#
# NOTES FOR FUTURE AI:
#   - This is the "fabric of reality" - treat it with respect
#   - Edges encode physics knowledge (derivations, limits, etc.)
#   - Evolution modifies this graph - changes propagate everywhere

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Tuple, Iterator, Callable
from enum import Enum, auto
from datetime import datetime
import json
import os
from pathlib import Path
from collections import defaultdict

from substrate.graph.formula import (
    Formula, FormulaStatus, FormulaLayer, 
    Variable, RegimeOfValidity, Evidence
)


class EdgeType(Enum):
    """Types of relationships between formulas."""
    
    # Derivation relationships
    DERIVES_FROM = auto()           # F1 can be derived from F2
    SPECIAL_CASE_OF = auto()        # F1 is a special case of F2
    GENERALIZES = auto()            # F1 generalizes F2
    
    # Limit relationships
    LOW_ENERGY_LIMIT_OF = auto()    # F1 is the low-energy limit of F2
    HIGH_ENERGY_LIMIT_OF = auto()   # F1 is the high-energy limit of F2
    NON_RELATIVISTIC_LIMIT_OF = auto()  # F1 is v << c limit of F2
    CLASSICAL_LIMIT_OF = auto()     # F1 is ℏ → 0 limit of F2
    CONTINUUM_LIMIT_OF = auto()     # F1 is large-N limit of F2
    WEAK_FIELD_LIMIT_OF = auto()    # F1 is weak-field limit of F2
    
    # Phenomenological relationships
    PHENOMENOLOGICAL_FIT_TO = auto()  # F1 is an empirical fit to F2's predictions
    EFFECTIVE_THEORY_OF = auto()      # F1 is an effective theory derived from F2
    
    # Conflict relationships
    CONTRADICTS = auto()            # F1 and F2 make incompatible predictions
    SUPERSEDES = auto()             # F1 replaces F2 (F2 is now deprecated)
    
    # Dependency relationships
    DEPENDS_ON = auto()             # F1 requires F2 to be true
    USES_PARAMETER_FROM = auto()    # F1 uses a parameter defined in F2
    
    # Validation relationships
    CALIBRATED_BY = auto()          # F1's parameters are calibrated by experiment/F2
    VALIDATED_BY = auto()           # F1 is experimentally validated by F2
    
    # Composition relationships
    COMBINES_WITH = auto()          # F1 and F2 can be combined
    EQUIVALENT_TO = auto()          # F1 and F2 are mathematically equivalent


@dataclass
class Edge:
    """An edge in the formula graph."""
    source_id: str
    target_id: str
    edge_type: EdgeType
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.edge_type.name,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
        }
    
    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> Edge:
        d = d.copy()
        d["edge_type"] = EdgeType[d["edge_type"]]
        d["created_at"] = datetime.fromisoformat(d["created_at"]) if d.get("created_at") else datetime.now()
        return cls(**d)


class FormulaGraph:
    """
    The Formula Graph - the reality substrate of Physics AI.
    
    This is the central knowledge store. All physics knowledge is encoded
    as Formula nodes and Edge relationships. The system reasons by walking
    this graph, and evolves by modifying it.
    
    Key operations:
    - add_formula / remove_formula: Modify nodes
    - add_edge / remove_edge: Modify relationships
    - find_paths: Find derivation chains between formulas
    - query: Find formulas matching criteria
    - check_consistency: Validate graph invariants
    """
    
    def __init__(self, persist_path: Optional[str] = None):
        """
        Initialize the formula graph.
        
        Args:
            persist_path: Path to JSON file for persistence (optional)
        """
        self._formulas: Dict[str, Formula] = {}
        self._edges: List[Edge] = []
        
        # Indices for fast lookup
        self._by_domain: Dict[str, Set[str]] = defaultdict(set)
        self._by_tag: Dict[str, Set[str]] = defaultdict(set)
        self._by_status: Dict[FormulaStatus, Set[str]] = defaultdict(set)
        self._by_layer: Dict[FormulaLayer, Set[str]] = defaultdict(set)
        
        # Edge indices
        self._outgoing: Dict[str, List[Edge]] = defaultdict(list)
        self._incoming: Dict[str, List[Edge]] = defaultdict(list)
        self._by_edge_type: Dict[EdgeType, List[Edge]] = defaultdict(list)
        
        # Persistence
        self._persist_path = persist_path
        if persist_path and os.path.exists(persist_path):
            self.load(persist_path)
    
    # =========================================================================
    # Node operations
    # =========================================================================
    
    def add_formula(self, formula: Formula, overwrite: bool = False) -> bool:
        """
        Add a formula to the graph.
        
        Args:
            formula: The formula to add
            overwrite: If True, overwrite existing formula with same ID
            
        Returns:
            True if added, False if already exists and overwrite=False
        """
        if formula.id in self._formulas and not overwrite:
            return False
        
        # Remove from indices if overwriting
        if formula.id in self._formulas:
            self._remove_from_indices(self._formulas[formula.id])
        
        # Add formula
        self._formulas[formula.id] = formula
        
        # Update indices
        self._add_to_indices(formula)
        
        return True
    
    def remove_formula(self, formula_id: str) -> Optional[Formula]:
        """
        Remove a formula from the graph.
        
        Args:
            formula_id: ID of formula to remove
            
        Returns:
            The removed formula, or None if not found
        """
        if formula_id not in self._formulas:
            return None
        
        formula = self._formulas.pop(formula_id)
        self._remove_from_indices(formula)
        
        # Remove associated edges
        self._edges = [e for e in self._edges 
                       if e.source_id != formula_id and e.target_id != formula_id]
        self._rebuild_edge_indices()
        
        return formula
    
    def get_formula(self, formula_id: str) -> Optional[Formula]:
        """Get a formula by ID."""
        return self._formulas.get(formula_id)
    
    def get_all_formulas(self) -> List[Formula]:
        """Get all formulas in the graph."""
        return list(self._formulas.values())
    
    def _add_to_indices(self, formula: Formula):
        """Add formula to lookup indices."""
        self._by_domain[formula.domain].add(formula.id)
        for tag in formula.tags:
            self._by_tag[tag].add(formula.id)
        self._by_status[formula.status].add(formula.id)
        self._by_layer[formula.layer].add(formula.id)
    
    def _remove_from_indices(self, formula: Formula):
        """Remove formula from lookup indices."""
        self._by_domain[formula.domain].discard(formula.id)
        for tag in formula.tags:
            self._by_tag[tag].discard(formula.id)
        self._by_status[formula.status].discard(formula.id)
        self._by_layer[formula.layer].discard(formula.id)
    
    # =========================================================================
    # Edge operations
    # =========================================================================
    
    def add_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: EdgeType,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
        created_by: str = "system"
    ) -> bool:
        """
        Add an edge between two formulas.
        
        Args:
            source_id: Source formula ID
            target_id: Target formula ID
            edge_type: Type of relationship
            confidence: Confidence in this relationship
            metadata: Additional metadata
            created_by: Who created this edge
            
        Returns:
            True if added, False if formulas don't exist
        """
        if source_id not in self._formulas or target_id not in self._formulas:
            return False
        
        edge = Edge(
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            confidence=confidence,
            metadata=metadata or {},
            created_by=created_by,
        )
        
        self._edges.append(edge)
        self._outgoing[source_id].append(edge)
        self._incoming[target_id].append(edge)
        self._by_edge_type[edge_type].append(edge)
        
        return True
    
    def remove_edge(self, source_id: str, target_id: str, edge_type: EdgeType) -> bool:
        """Remove a specific edge."""
        for i, edge in enumerate(self._edges):
            if (edge.source_id == source_id and 
                edge.target_id == target_id and 
                edge.edge_type == edge_type):
                self._edges.pop(i)
                self._rebuild_edge_indices()
                return True
        return False
    
    def get_edges_from(self, formula_id: str, edge_type: Optional[EdgeType] = None) -> List[Edge]:
        """Get all edges originating from a formula."""
        edges = self._outgoing.get(formula_id, [])
        if edge_type:
            edges = [e for e in edges if e.edge_type == edge_type]
        return edges
    
    def get_edges_to(self, formula_id: str, edge_type: Optional[EdgeType] = None) -> List[Edge]:
        """Get all edges pointing to a formula."""
        edges = self._incoming.get(formula_id, [])
        if edge_type:
            edges = [e for e in edges if e.edge_type == edge_type]
        return edges
    
    def _rebuild_edge_indices(self):
        """Rebuild edge indices from scratch."""
        self._outgoing = defaultdict(list)
        self._incoming = defaultdict(list)
        self._by_edge_type = defaultdict(list)
        
        for edge in self._edges:
            self._outgoing[edge.source_id].append(edge)
            self._incoming[edge.target_id].append(edge)
            self._by_edge_type[edge.edge_type].append(edge)
    
    # =========================================================================
    # Query operations
    # =========================================================================
    
    def query(
        self,
        domain: Optional[str] = None,
        tags: Optional[Set[str]] = None,
        status: Optional[FormulaStatus] = None,
        layer: Optional[FormulaLayer] = None,
        min_confidence: float = 0.0,
        custom_filter: Optional[Callable[[Formula], bool]] = None
    ) -> List[Formula]:
        """
        Query formulas matching criteria.
        
        Args:
            domain: Filter by domain
            tags: Filter by tags (formula must have ALL tags)
            status: Filter by status
            layer: Filter by layer
            min_confidence: Minimum confidence
            custom_filter: Custom filter function
            
        Returns:
            List of matching formulas
        """
        # Start with all formula IDs
        candidate_ids: Optional[Set[str]] = None
        
        # Apply index-based filters
        if domain:
            candidate_ids = self._by_domain.get(domain, set()).copy()
        
        if tags:
            for tag in tags:
                tag_ids = self._by_tag.get(tag, set())
                if candidate_ids is None:
                    candidate_ids = tag_ids.copy()
                else:
                    candidate_ids &= tag_ids
        
        if status:
            status_ids = self._by_status.get(status, set())
            if candidate_ids is None:
                candidate_ids = status_ids.copy()
            else:
                candidate_ids &= status_ids
        
        if layer:
            layer_ids = self._by_layer.get(layer, set())
            if candidate_ids is None:
                candidate_ids = layer_ids.copy()
            else:
                candidate_ids &= layer_ids
        
        # If no filters applied, use all formulas
        if candidate_ids is None:
            candidate_ids = set(self._formulas.keys())
        
        # Apply remaining filters
        results = []
        for fid in candidate_ids:
            formula = self._formulas[fid]
            if formula.confidence < min_confidence:
                continue
            if custom_filter and not custom_filter(formula):
                continue
            results.append(formula)
        
        return results
    
    def find_by_input_output(
        self,
        inputs: Optional[List[str]] = None,
        outputs: Optional[List[str]] = None
    ) -> List[Formula]:
        """
        Find formulas that can transform given inputs to outputs.
        
        Args:
            inputs: Variable names available as input
            outputs: Variable names needed as output
            
        Returns:
            List of formulas that could apply
        """
        results = []
        input_set = set(inputs) if inputs else None
        output_set = set(outputs) if outputs else None
        
        for formula in self._formulas.values():
            # Check if formula's inputs are subset of available inputs
            if input_set:
                formula_inputs = {v.symbol for v in formula.inputs}
                if not formula_inputs.issubset(input_set):
                    continue
            
            # Check if formula provides needed outputs
            if output_set:
                formula_outputs = {v.symbol for v in formula.outputs}
                if not formula_outputs.intersection(output_set):
                    continue
            
            results.append(formula)
        
        return results
    
    # =========================================================================
    # Path finding
    # =========================================================================
    
    def find_paths(
        self,
        start_id: str,
        end_id: str,
        max_depth: int = 10,
        allowed_edge_types: Optional[Set[EdgeType]] = None
    ) -> List[List[Tuple[str, EdgeType]]]:
        """
        Find all paths from start formula to end formula.
        
        Args:
            start_id: Starting formula ID
            end_id: Target formula ID
            max_depth: Maximum path length
            allowed_edge_types: Edge types to traverse (None = all)
            
        Returns:
            List of paths, where each path is list of (formula_id, edge_type) tuples
        """
        if start_id not in self._formulas or end_id not in self._formulas:
            return []
        
        paths = []
        visited = set()
        
        def dfs(current_id: str, path: List[Tuple[str, EdgeType]], depth: int):
            if depth > max_depth:
                return
            
            if current_id == end_id:
                paths.append(path.copy())
                return
            
            if current_id in visited:
                return
            
            visited.add(current_id)
            
            for edge in self._outgoing.get(current_id, []):
                if allowed_edge_types and edge.edge_type not in allowed_edge_types:
                    continue
                path.append((edge.target_id, edge.edge_type))
                dfs(edge.target_id, path, depth + 1)
                path.pop()
            
            visited.remove(current_id)
        
        dfs(start_id, [(start_id, None)], 0)
        return paths
    
    def find_derivation_chain(
        self,
        inputs: Set[str],
        outputs: Set[str],
        context: Dict[str, Any],
        max_chain_length: int = 10
    ) -> List[List[str]]:
        """
        Find chains of formulas that derive outputs from inputs.
        
        This is the core operation for the FormulaPlanner.
        
        Args:
            inputs: Available input variable symbols
            outputs: Required output variable symbols
            context: Context for applicability checking
            max_chain_length: Maximum number of formulas in chain
            
        Returns:
            List of formula ID chains, each chain derives outputs from inputs
        """
        chains = []
        
        # Find formulas that provide each output
        output_providers: Dict[str, List[Formula]] = {}
        for out_var in outputs:
            providers = self.find_by_input_output(outputs=[out_var])
            # Filter by applicability
            providers = [f for f in providers if f.is_applicable(context)[0]]
            output_providers[out_var] = providers
        
        # Simple approach: for each output, try to build a chain
        def build_chain(
            needed_outputs: Set[str],
            available_inputs: Set[str],
            current_chain: List[str],
            depth: int
        ):
            if depth > max_chain_length:
                return
            
            if not needed_outputs:
                chains.append(current_chain.copy())
                return
            
            # Pick an output to resolve
            output = next(iter(needed_outputs))
            
            for formula in output_providers.get(output, []):
                if formula.id in current_chain:
                    continue
                
                # What does this formula need?
                formula_inputs = {v.symbol for v in formula.inputs}
                formula_outputs = {v.symbol for v in formula.outputs}
                
                # New available after using this formula
                new_available = available_inputs | formula_outputs
                
                # New needed: remove what this formula provides, add what it needs
                new_needed = (needed_outputs - formula_outputs) | (formula_inputs - available_inputs)
                
                # Recurse
                current_chain.append(formula.id)
                build_chain(new_needed, new_available, current_chain, depth + 1)
                current_chain.pop()
        
        build_chain(outputs, inputs, [], 0)
        return chains
    
    # =========================================================================
    # Consistency checking
    # =========================================================================
    
    def check_consistency(self) -> List[Dict[str, Any]]:
        """
        Check the graph for consistency issues.
        
        Returns:
            List of issues found
        """
        issues = []
        
        # Check for contradictions
        for edge in self._by_edge_type.get(EdgeType.CONTRADICTS, []):
            source = self._formulas.get(edge.source_id)
            target = self._formulas.get(edge.target_id)
            if source and target:
                if source.status == FormulaStatus.ACCEPTED and target.status == FormulaStatus.ACCEPTED:
                    issues.append({
                        "type": "contradiction",
                        "severity": "high",
                        "message": f"Contradiction between accepted formulas: {source.name} and {target.name}",
                        "formula_ids": [source.id, target.id],
                    })
        
        # Check for cycles in derivation edges
        derivation_types = {
            EdgeType.DERIVES_FROM, EdgeType.SPECIAL_CASE_OF,
            EdgeType.GENERALIZES, EdgeType.DEPENDS_ON
        }
        cycles = self._find_cycles(derivation_types)
        for cycle in cycles:
            issues.append({
                "type": "derivation_cycle",
                "severity": "medium",
                "message": f"Cycle in derivation graph: {' -> '.join(cycle)}",
                "formula_ids": cycle,
            })
        
        # Check for orphan formulas (no edges)
        for fid, formula in self._formulas.items():
            if not self._outgoing.get(fid) and not self._incoming.get(fid):
                if formula.layer not in {FormulaLayer.AXIOM, FormulaLayer.FUNDAMENTAL}:
                    issues.append({
                        "type": "orphan",
                        "severity": "low",
                        "message": f"Formula {formula.name} has no connections",
                        "formula_ids": [fid],
                    })
        
        # Check for low-confidence chains
        for formula in self._formulas.values():
            if formula.status == FormulaStatus.ACCEPTED and formula.confidence < 0.5:
                issues.append({
                    "type": "low_confidence_accepted",
                    "severity": "medium",
                    "message": f"Accepted formula {formula.name} has low confidence: {formula.confidence}",
                    "formula_ids": [formula.id],
                })
        
        return issues
    
    def _find_cycles(self, edge_types: Set[EdgeType]) -> List[List[str]]:
        """Find cycles in the graph considering only specified edge types."""
        cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node_id: str):
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)
            
            for edge in self._outgoing.get(node_id, []):
                if edge.edge_type not in edge_types:
                    continue
                
                neighbor = edge.target_id
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
            
            path.pop()
            rec_stack.remove(node_id)
        
        for node_id in self._formulas:
            if node_id not in visited:
                dfs(node_id)
        
        return cycles
    
    # =========================================================================
    # Persistence
    # =========================================================================
    
    def save(self, path: Optional[str] = None):
        """Save graph to JSON file."""
        path = path or self._persist_path
        if not path:
            raise ValueError("No path specified for saving")
        
        data = {
            "formulas": [f.to_dict() for f in self._formulas.values()],
            "edges": [e.to_dict() for e in self._edges],
            "metadata": {
                "saved_at": datetime.now().isoformat(),
                "version": "1.0",
            }
        }
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    
    def load(self, path: str):
        """Load graph from JSON file."""
        with open(path) as f:
            data = json.load(f)
        
        # Clear current state
        self._formulas.clear()
        self._edges.clear()
        
        # Load formulas
        for f_dict in data.get("formulas", []):
            formula = Formula.from_dict(f_dict)
            self._formulas[formula.id] = formula
            self._add_to_indices(formula)
        
        # Load edges
        for e_dict in data.get("edges", []):
            edge = Edge.from_dict(e_dict)
            self._edges.append(edge)
        
        self._rebuild_edge_indices()
    
    # =========================================================================
    # Statistics
    # =========================================================================
    
    def stats(self) -> Dict[str, Any]:
        """Get statistics about the graph."""
        return {
            "total_formulas": len(self._formulas),
            "total_edges": len(self._edges),
            "by_domain": {k: len(v) for k, v in self._by_domain.items()},
            "by_status": {k.name: len(v) for k, v in self._by_status.items()},
            "by_layer": {k.name: len(v) for k, v in self._by_layer.items()},
            "by_edge_type": {k.name: len(v) for k, v in self._by_edge_type.items()},
        }
    
    def __len__(self) -> int:
        return len(self._formulas)
    
    def __iter__(self) -> Iterator[Formula]:
        return iter(self._formulas.values())
    
    def __contains__(self, formula_id: str) -> bool:
        return formula_id in self._formulas


# =============================================================================
# Factory for pre-populated graphs
# =============================================================================

def create_classical_mechanics_graph() -> FormulaGraph:
    """Create a graph pre-populated with classical mechanics formulas."""
    graph = FormulaGraph()
    
    # Newton's Second Law
    f_ma = Formula(
        id="newton_2",
        name="Newton's Second Law",
        symbolic_form="F = m * a",
        sympy_expr="Eq(F, m * a)",
        domain="classical",
        layer=FormulaLayer.FUNDAMENTAL,
        status=FormulaStatus.FUNDAMENTAL,
        confidence=1.0,
        inputs=[
            Variable("mass", "m", "kg", "> 0"),
            Variable("acceleration", "a", "m/s^2"),
        ],
        outputs=[
            Variable("force", "F", "N"),
        ],
        assumptions=["point mass", "inertial frame"],
        regime=RegimeOfValidity(
            conditions=["non-relativistic"],
            domains={"classical", "macroscopic"},
        ),
        tags={"mechanics", "force", "fundamental"},
        description="Force equals mass times acceleration",
    )
    graph.add_formula(f_ma)
    
    # Conservation of Energy
    f_energy = Formula(
        id="energy_conservation",
        name="Conservation of Energy",
        symbolic_form="dE/dt = 0",
        domain="classical",
        layer=FormulaLayer.AXIOM,
        status=FormulaStatus.FUNDAMENTAL,
        confidence=1.0,
        assumptions=["isolated system"],
        regime=RegimeOfValidity(domains={"classical", "quantum", "relativistic"}),
        tags={"conservation", "energy", "fundamental"},
        description="Energy is conserved in isolated systems",
    )
    graph.add_formula(f_energy)
    
    # Conservation of Momentum
    f_momentum = Formula(
        id="momentum_conservation",
        name="Conservation of Momentum",
        symbolic_form="dp/dt = 0",
        domain="classical",
        layer=FormulaLayer.AXIOM,
        status=FormulaStatus.FUNDAMENTAL,
        confidence=1.0,
        assumptions=["isolated system", "no external forces"],
        regime=RegimeOfValidity(domains={"classical", "quantum", "relativistic"}),
        tags={"conservation", "momentum", "fundamental"},
        description="Momentum is conserved when no external forces act",
    )
    graph.add_formula(f_momentum)
    
    # Kinetic Energy
    f_ke = Formula(
        id="kinetic_energy",
        name="Kinetic Energy",
        symbolic_form="KE = (1/2) * m * v^2",
        sympy_expr="Eq(KE, Rational(1, 2) * m * v**2)",
        domain="classical",
        layer=FormulaLayer.FUNDAMENTAL,
        status=FormulaStatus.ACCEPTED,
        confidence=1.0,
        inputs=[
            Variable("mass", "m", "kg", "> 0"),
            Variable("velocity", "v", "m/s"),
        ],
        outputs=[
            Variable("kinetic_energy", "KE", "J", ">= 0"),
        ],
        assumptions=["non-relativistic"],
        regime=RegimeOfValidity(
            conditions=["v << c"],
            domains={"classical"},
        ),
        tags={"energy", "mechanics"},
        description="Kinetic energy of a moving object",
    )
    graph.add_formula(f_ke)
    
    # Gravitational Force
    f_grav = Formula(
        id="gravitational_force",
        name="Newton's Law of Gravitation",
        symbolic_form="F = G * m1 * m2 / r^2",
        sympy_expr="Eq(F, G * m1 * m2 / r**2)",
        domain="classical",
        layer=FormulaLayer.FUNDAMENTAL,
        status=FormulaStatus.ACCEPTED,
        confidence=1.0,
        inputs=[
            Variable("mass_1", "m1", "kg", "> 0"),
            Variable("mass_2", "m2", "kg", "> 0"),
            Variable("distance", "r", "m", "> 0"),
        ],
        outputs=[
            Variable("force", "F", "N"),
        ],
        parameters=[
            Variable("gravitational_constant", "G", "N*m^2/kg^2"),
        ],
        assumptions=["point masses", "weak field"],
        regime=RegimeOfValidity(
            conditions=["weak field", "non-relativistic"],
            domains={"classical"},
        ),
        tags={"gravity", "force", "fundamental"},
        description="Gravitational attraction between two masses",
    )
    graph.add_formula(f_grav)
    
    # Add relationships
    graph.add_edge("kinetic_energy", "energy_conservation", EdgeType.DEPENDS_ON)
    graph.add_edge("newton_2", "momentum_conservation", EdgeType.DERIVES_FROM)
    graph.add_edge("gravitational_force", "newton_2", EdgeType.COMBINES_WITH)
    
    return graph

