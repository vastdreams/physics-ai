# core/
"""
PATH: core/reasoning.py
PURPOSE: Implements multiple reasoning paradigms for the neurosymbolic engine.

FLOW:
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  Premises   │───▶│  Reasoning   │───▶│  Conclusion │
│             │    │   Strategy   │    │             │
└─────────────┘    └──────────────┘    └─────────────┘

First Principle Analysis:
- Deductive: If P→Q and P, then Q (modus ponens) - certainty preserving
- Inductive: Generalize from specific cases - probability increasing
- Abductive: Infer best explanation - hypothesis generation
- Analogical: Transfer knowledge from similar domains - structure mapping

Mathematical Foundation:
- Deductive: Propositional/First-order logic
- Inductive: Bayesian inference, statistical learning
- Abductive: Minimum description length, Occam's razor
- Analogical: Structure mapping theory, similarity metrics

DEPENDENCIES:
- numpy: Numerical operations
- validators: Input validation
- loggers: System logging
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Set, Callable
from enum import Enum
from dataclasses import dataclass, field
import numpy as np
from collections import defaultdict
import re

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from validators.data_validator import DataValidator
from loggers.system_logger import SystemLogger
from .engine import ReasoningEngine


class ReasoningType(Enum):
    """Types of reasoning strategies."""
    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"
    ANALOGICAL = "analogical"


@dataclass
class Proposition:
    """Represents a logical proposition."""
    statement: str
    truth_value: Optional[bool] = None
    confidence: float = 1.0
    source: str = "assertion"
    
    def __hash__(self):
        return hash(self.statement)
    
    def __eq__(self, other):
        if isinstance(other, Proposition):
            return self.statement == other.statement
        return False


@dataclass
class Implication:
    """Represents a logical implication P → Q."""
    antecedent: str  # P
    consequent: str  # Q
    confidence: float = 1.0
    
    def __hash__(self):
        return hash((self.antecedent, self.consequent))


@dataclass
class ReasoningResult:
    """Result from a reasoning operation."""
    conclusion: Any
    confidence: float
    reasoning_type: ReasoningType
    proof_steps: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'conclusion': self.conclusion,
            'confidence': self.confidence,
            'reasoning_type': self.reasoning_type.value,
            'proof_steps': self.proof_steps,
            'metadata': self.metadata
        }


class DeductiveReasoner:
    """
    Deductive reasoning: derives conclusions that are logically certain 
    given the premises.
    
    Implements:
    - Modus ponens: P, P→Q ⊢ Q
    - Modus tollens: ¬Q, P→Q ⊢ ¬P
    - Hypothetical syllogism: P→Q, Q→R ⊢ P→R
    - Disjunctive syllogism: P∨Q, ¬P ⊢ Q
    """
    
    def __init__(self):
        self.logger = SystemLogger()
        self.implications: Set[Implication] = set()
        self.facts: Dict[str, bool] = {}
    
    def add_implication(self, antecedent: str, consequent: str, confidence: float = 1.0) -> None:
        """Add an implication rule."""
        self.implications.add(Implication(antecedent, consequent, confidence))
    
    def add_fact(self, proposition: str, value: bool) -> None:
        """Add a known fact."""
        self.facts[proposition] = value
    
    def modus_ponens(self, p: str, implications: Set[Implication]) -> List[Tuple[str, float, str]]:
        """
        Apply modus ponens: P, P→Q ⊢ Q
        
        Args:
            p: The proposition P that is known to be true
            implications: Set of implications to check
            
        Returns:
            List of (conclusion, confidence, proof_step)
        """
        conclusions = []
        for impl in implications:
            if impl.antecedent == p:
                confidence = impl.confidence
                proof = f"By modus ponens: {p} and ({p} → {impl.consequent}) ⊢ {impl.consequent}"
                conclusions.append((impl.consequent, confidence, proof))
        return conclusions
    
    def modus_tollens(self, not_q: str, implications: Set[Implication]) -> List[Tuple[str, float, str]]:
        """
        Apply modus tollens: ¬Q, P→Q ⊢ ¬P
        
        Args:
            not_q: The negation ¬Q
            implications: Set of implications to check
            
        Returns:
            List of (conclusion, confidence, proof_step)
        """
        conclusions = []
        # Extract the positive form of Q
        if not_q.startswith('¬') or not_q.startswith('not '):
            q = not_q[1:] if not_q.startswith('¬') else not_q[4:]
            q = q.strip()
            
            for impl in implications:
                if impl.consequent == q:
                    not_p = f"¬{impl.antecedent}"
                    confidence = impl.confidence
                    proof = f"By modus tollens: {not_q} and ({impl.antecedent} → {q}) ⊢ {not_p}"
                    conclusions.append((not_p, confidence, proof))
        
        return conclusions
    
    def hypothetical_syllogism(self, implications: Set[Implication]) -> List[Implication]:
        """
        Apply hypothetical syllogism: P→Q, Q→R ⊢ P→R
        
        Args:
            implications: Set of implications
            
        Returns:
            List of new derived implications
        """
        new_implications = []
        impl_list = list(implications)
        
        for impl1 in impl_list:
            for impl2 in impl_list:
                if impl1.consequent == impl2.antecedent and impl1 != impl2:
                    new_impl = Implication(
                        impl1.antecedent,
                        impl2.consequent,
                        impl1.confidence * impl2.confidence
                    )
                    if new_impl not in implications:
                        new_implications.append(new_impl)
        
        return new_implications
    
    def reason(self, premises: List[str]) -> ReasoningResult:
        """
        Perform deductive reasoning on premises.
        
        Args:
            premises: List of premise strings
            
        Returns:
            ReasoningResult with conclusions
        """
        proof_steps = []
        conclusions = []
        current_confidence = 1.0
        
        # Parse premises into facts and implications
        for premise in premises:
            if '→' in premise or '->' in premise:
                # Parse implication
                parts = re.split(r'→|->',premise)
                if len(parts) == 2:
                    ant = parts[0].strip()
                    cons = parts[1].strip()
                    self.add_implication(ant, cons)
                    proof_steps.append(f"Added implication: {ant} → {cons}")
            else:
                # Parse fact
                premise = premise.strip()
                if premise.startswith('¬') or premise.startswith('not '):
                    prop = premise[1:] if premise.startswith('¬') else premise[4:]
                    self.facts[prop.strip()] = False
                else:
                    self.facts[premise] = True
                proof_steps.append(f"Added fact: {premise}")
        
        # Apply forward chaining
        changed = True
        iterations = 0
        max_iterations = 100
        
        while changed and iterations < max_iterations:
            changed = False
            iterations += 1
            
            # Apply modus ponens for all known true facts
            for fact, value in list(self.facts.items()):
                if value:
                    new_conclusions = self.modus_ponens(fact, self.implications)
                    for conc, conf, proof in new_conclusions:
                        if conc not in self.facts:
                            self.facts[conc] = True
                            conclusions.append(conc)
                            proof_steps.append(proof)
                            current_confidence = min(current_confidence, conf)
                            changed = True
                else:
                    # Apply modus tollens
                    not_fact = f"¬{fact}"
                    new_conclusions = self.modus_tollens(not_fact, self.implications)
                    for conc, conf, proof in new_conclusions:
                        # Extract the proposition from ¬P
                        prop = conc[1:] if conc.startswith('¬') else conc
                        if prop not in self.facts:
                            self.facts[prop] = False
                            conclusions.append(conc)
                            proof_steps.append(proof)
                            current_confidence = min(current_confidence, conf)
                            changed = True
            
            # Apply hypothetical syllogism to derive new implications
            new_impls = self.hypothetical_syllogism(self.implications)
            for impl in new_impls:
                self.implications.add(impl)
                proof_steps.append(f"By hypothetical syllogism: {impl.antecedent} → {impl.consequent}")
                changed = True
        
        return ReasoningResult(
            conclusion=conclusions if conclusions else list(self.facts.items()),
            confidence=current_confidence,
            reasoning_type=ReasoningType.DEDUCTIVE,
            proof_steps=proof_steps,
            metadata={
                'iterations': iterations,
                'facts_derived': len(conclusions),
                'total_facts': len(self.facts)
            }
        )


class InductiveReasoner:
    """
    Inductive reasoning: generalizes patterns from specific observations.
    
    Implements:
    - Pattern generalization
    - Statistical inference
    - Hypothesis formation
    """
    
    def __init__(self):
        self.logger = SystemLogger()
        self.observations: List[Dict[str, Any]] = []
    
    def add_observation(self, observation: Dict[str, Any]) -> None:
        """Add an observation to the dataset."""
        self.observations.append(observation)
    
    def find_patterns(self, observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Find common patterns in observations.
        
        Args:
            observations: List of observation dictionaries
            
        Returns:
            List of identified patterns
        """
        if not observations:
            return []
        
        patterns = []
        
        # Find common keys
        all_keys = set()
        for obs in observations:
            if isinstance(obs, dict):
                all_keys.update(obs.keys())
        
        # For each key, find if there's a consistent pattern
        for key in all_keys:
            values = [obs.get(key) for obs in observations if isinstance(obs, dict) and key in obs]
            
            if not values:
                continue
            
            # Check for constant value
            if len(set(str(v) for v in values)) == 1:
                patterns.append({
                    'type': 'constant',
                    'key': key,
                    'value': values[0],
                    'confidence': 1.0
                })
            
            # Check for numeric trends
            elif all(isinstance(v, (int, float)) for v in values):
                # Check monotonic increase
                if all(values[i] <= values[i+1] for i in range(len(values)-1)):
                    patterns.append({
                        'type': 'monotonic_increase',
                        'key': key,
                        'confidence': 0.8
                    })
                # Check monotonic decrease
                elif all(values[i] >= values[i+1] for i in range(len(values)-1)):
                    patterns.append({
                        'type': 'monotonic_decrease',
                        'key': key,
                        'confidence': 0.8
                    })
                # Check for linear relationship
                else:
                    # Simple linear fit
                    x = np.arange(len(values))
                    y = np.array(values)
                    if len(x) > 1:
                        # Calculate correlation
                        correlation = np.corrcoef(x, y)[0, 1] if len(x) > 2 else 0
                        if abs(correlation) > 0.8:
                            slope = (y[-1] - y[0]) / (len(y) - 1) if len(y) > 1 else 0
                            patterns.append({
                                'type': 'linear_trend',
                                'key': key,
                                'slope': slope,
                                'correlation': correlation,
                                'confidence': abs(correlation)
                            })
            
            # Check for categorical patterns
            else:
                value_counts = defaultdict(int)
                for v in values:
                    value_counts[str(v)] += 1
                
                most_common = max(value_counts.items(), key=lambda x: x[1])
                frequency = most_common[1] / len(values)
                
                if frequency > 0.7:
                    patterns.append({
                        'type': 'dominant_value',
                        'key': key,
                        'value': most_common[0],
                        'frequency': frequency,
                        'confidence': frequency
                    })
        
        return patterns
    
    def generalize(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generalize patterns into rules/hypotheses.
        
        Args:
            patterns: List of identified patterns
            
        Returns:
            Generalized hypothesis
        """
        hypothesis = {
            'rules': [],
            'confidence': 1.0
        }
        
        for pattern in patterns:
            if pattern['type'] == 'constant':
                hypothesis['rules'].append({
                    'rule': f"For all X: X.{pattern['key']} = {pattern['value']}",
                    'confidence': pattern['confidence']
                })
            elif pattern['type'] == 'monotonic_increase':
                hypothesis['rules'].append({
                    'rule': f"For all X, Y where X precedes Y: X.{pattern['key']} <= Y.{pattern['key']}",
                    'confidence': pattern['confidence']
                })
            elif pattern['type'] == 'linear_trend':
                hypothesis['rules'].append({
                    'rule': f"{pattern['key']} changes approximately linearly with slope {pattern['slope']:.4f}",
                    'confidence': pattern['confidence']
                })
            elif pattern['type'] == 'dominant_value':
                hypothesis['rules'].append({
                    'rule': f"Most likely: {pattern['key']} = {pattern['value']} (frequency: {pattern['frequency']:.2f})",
                    'confidence': pattern['confidence']
                })
            
            hypothesis['confidence'] = min(hypothesis['confidence'], pattern['confidence'])
        
        return hypothesis
    
    def reason(self, premises: List[Any]) -> ReasoningResult:
        """
        Perform inductive reasoning on observations.
        
        Args:
            premises: List of observations (dictionaries or values)
            
        Returns:
            ReasoningResult with generalized hypothesis
        """
        proof_steps = []
        
        # Convert premises to observations
        observations = []
        for i, premise in enumerate(premises):
            if isinstance(premise, dict):
                observations.append(premise)
                proof_steps.append(f"Observation {i+1}: {premise}")
            else:
                observations.append({'value': premise, 'index': i})
                proof_steps.append(f"Observation {i+1}: {premise}")
        
        # Find patterns
        patterns = self.find_patterns(observations)
        proof_steps.append(f"Found {len(patterns)} patterns")
        
        for pattern in patterns:
            proof_steps.append(f"Pattern: {pattern['type']} in '{pattern.get('key', 'data')}' "
                            f"(confidence: {pattern['confidence']:.2f})")
        
        # Generalize
        hypothesis = self.generalize(patterns)
        
        for rule in hypothesis['rules']:
            proof_steps.append(f"Generalized rule: {rule['rule']}")
        
        return ReasoningResult(
            conclusion=hypothesis,
            confidence=hypothesis['confidence'],
            reasoning_type=ReasoningType.INDUCTIVE,
            proof_steps=proof_steps,
            metadata={
                'observations_count': len(observations),
                'patterns_found': len(patterns)
            }
        )


class AbductiveReasoner:
    """
    Abductive reasoning: infers the best explanation for observations.
    
    Implements:
    - Hypothesis generation
    - Explanation ranking by simplicity and coverage
    - Bayesian hypothesis scoring
    """
    
    def __init__(self):
        self.logger = SystemLogger()
        self.hypotheses: List[Dict[str, Any]] = []
        self.priors: Dict[str, float] = {}  # Prior probabilities for hypotheses
    
    def add_hypothesis(self, name: str, explains: List[str], complexity: int = 1, prior: float = 0.5) -> None:
        """
        Add a potential explanation hypothesis.
        
        Args:
            name: Hypothesis name
            explains: List of observations this hypothesis explains
            complexity: Complexity score (lower is simpler, preferred by Occam's razor)
            prior: Prior probability of hypothesis
        """
        self.hypotheses.append({
            'name': name,
            'explains': set(explains),
            'complexity': complexity,
            'prior': prior
        })
        self.priors[name] = prior
    
    def score_hypothesis(self, hypothesis: Dict[str, Any], observations: Set[str]) -> float:
        """
        Score a hypothesis based on coverage and simplicity.
        
        Score = (coverage * prior) / complexity
        
        Args:
            hypothesis: Hypothesis to score
            observations: Set of observations to explain
            
        Returns:
            Score (higher is better)
        """
        if not observations:
            return 0.0
        
        # Coverage: what fraction of observations does this explain?
        explained = hypothesis['explains'] & observations
        coverage = len(explained) / len(observations) if observations else 0
        
        # Apply Occam's razor: prefer simpler explanations
        simplicity = 1.0 / hypothesis['complexity']
        
        # Incorporate prior probability
        prior = hypothesis['prior']
        
        # Combined score
        score = coverage * simplicity * prior
        
        return score
    
    def generate_hypotheses(self, observations: List[str]) -> List[Dict[str, Any]]:
        """
        Generate candidate hypotheses for observations.
        
        Args:
            observations: List of observation strings
            
        Returns:
            List of generated hypotheses
        """
        generated = []
        
        # Generate single-cause hypotheses
        for obs in observations:
            generated.append({
                'name': f"Cause of {obs}",
                'explains': {obs},
                'complexity': 1,
                'prior': 0.3
            })
        
        # Generate combined hypotheses (common cause)
        if len(observations) > 1:
            generated.append({
                'name': f"Common cause of all observations",
                'explains': set(observations),
                'complexity': 1,
                'prior': 0.5
            })
        
        return generated
    
    def reason(self, premises: List[Any]) -> ReasoningResult:
        """
        Perform abductive reasoning to find best explanation.
        
        Args:
            premises: List of observations to explain
            
        Returns:
            ReasoningResult with best explanation
        """
        proof_steps = []
        
        # Convert premises to observation strings
        observations = set()
        for premise in premises:
            obs_str = str(premise) if not isinstance(premise, str) else premise
            observations.add(obs_str)
            proof_steps.append(f"Observation to explain: {obs_str}")
        
        # Combine existing and generated hypotheses
        all_hypotheses = self.hypotheses + self.generate_hypotheses(list(observations))
        
        if not all_hypotheses:
            return ReasoningResult(
                conclusion={"error": "No hypotheses available"},
                confidence=0.0,
                reasoning_type=ReasoningType.ABDUCTIVE,
                proof_steps=proof_steps,
                metadata={'hypotheses_evaluated': 0}
            )
        
        # Score all hypotheses
        scored = []
        for hyp in all_hypotheses:
            score = self.score_hypothesis(hyp, observations)
            scored.append((hyp, score))
            proof_steps.append(
                f"Hypothesis '{hyp['name']}': score={score:.4f} "
                f"(coverage={len(hyp['explains'] & observations)}/{len(observations)}, "
                f"complexity={hyp['complexity']}, prior={hyp['prior']:.2f})"
            )
        
        # Sort by score
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Best explanation
        best = scored[0]
        best_hypothesis = best[0]
        best_score = best[1]
        
        proof_steps.append(f"Best explanation: '{best_hypothesis['name']}' with score {best_score:.4f}")
        
        # Calculate confidence based on score margin
        if len(scored) > 1:
            second_best = scored[1][1]
            margin = best_score - second_best
            confidence = min(0.9, 0.5 + margin)
        else:
            confidence = best_score
        
        return ReasoningResult(
            conclusion={
                'best_explanation': best_hypothesis['name'],
                'explains': list(best_hypothesis['explains']),
                'unexplained': list(observations - best_hypothesis['explains']),
                'score': best_score,
                'alternatives': [(h['name'], s) for h, s in scored[1:4]]  # Top 3 alternatives
            },
            confidence=confidence,
            reasoning_type=ReasoningType.ABDUCTIVE,
            proof_steps=proof_steps,
            metadata={
                'hypotheses_evaluated': len(scored),
                'observations_count': len(observations)
            }
        )


class AnalogicalReasoner:
    """
    Analogical reasoning: transfers knowledge from similar domains.
    
    Implements:
    - Structure mapping
    - Similarity computation
    - Knowledge transfer
    """
    
    def __init__(self):
        self.logger = SystemLogger()
        self.analogies: List[Dict[str, Any]] = []  # Known analogies/cases
    
    def add_analogy(self, source_domain: Dict[str, Any], target_domain: Dict[str, Any], 
                   mapping: Dict[str, str]) -> None:
        """
        Add a known analogy between domains.
        
        Args:
            source_domain: Source domain description
            target_domain: Target domain description
            mapping: Mapping from source to target elements
        """
        self.analogies.append({
            'source': source_domain,
            'target': target_domain,
            'mapping': mapping
        })
    
    def compute_structural_similarity(self, domain1: Dict[str, Any], domain2: Dict[str, Any]) -> float:
        """
        Compute structural similarity between two domains.
        
        Based on shared structure (keys) rather than values.
        
        Args:
            domain1: First domain
            domain2: Second domain
            
        Returns:
            Similarity score [0, 1]
        """
        if not isinstance(domain1, dict) or not isinstance(domain2, dict):
            return 0.0
        
        keys1 = set(domain1.keys())
        keys2 = set(domain2.keys())
        
        if not keys1 or not keys2:
            return 0.0
        
        # Jaccard similarity of keys
        intersection = len(keys1 & keys2)
        union = len(keys1 | keys2)
        
        key_similarity = intersection / union if union > 0 else 0
        
        # Check for similar nested structures
        nested_similarity = 0.0
        common_keys = keys1 & keys2
        
        for key in common_keys:
            v1, v2 = domain1[key], domain2[key]
            if isinstance(v1, dict) and isinstance(v2, dict):
                nested_similarity += self.compute_structural_similarity(v1, v2)
            elif type(v1) == type(v2):
                nested_similarity += 0.5
        
        if common_keys:
            nested_similarity /= len(common_keys)
        
        return 0.7 * key_similarity + 0.3 * nested_similarity
    
    def find_mapping(self, source: Dict[str, Any], target: Dict[str, Any]) -> Dict[str, str]:
        """
        Find mapping between source and target domains.
        
        Args:
            source: Source domain
            target: Target domain
            
        Returns:
            Mapping from source keys to target keys
        """
        mapping = {}
        
        source_keys = set(source.keys()) if isinstance(source, dict) else set()
        target_keys = set(target.keys()) if isinstance(target, dict) else set()
        
        # Direct matches
        for key in source_keys & target_keys:
            mapping[key] = key
        
        # Try to match remaining keys by type
        unmatched_source = source_keys - set(mapping.keys())
        unmatched_target = target_keys - set(mapping.values())
        
        for s_key in unmatched_source:
            for t_key in unmatched_target:
                if isinstance(source, dict) and isinstance(target, dict):
                    s_val = source.get(s_key)
                    t_val = target.get(t_key)
                    if type(s_val) == type(t_val):
                        mapping[s_key] = t_key
                        unmatched_target.discard(t_key)
                        break
        
        return mapping
    
    def transfer_knowledge(self, source: Dict[str, Any], mapping: Dict[str, str], 
                          known_values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transfer knowledge from source to target using mapping.
        
        Args:
            source: Source domain with known values
            mapping: Mapping from source to target
            known_values: Known values in target domain
            
        Returns:
            Transferred knowledge for target domain
        """
        transferred = dict(known_values)
        
        for source_key, target_key in mapping.items():
            if target_key not in transferred and source_key in source:
                # Transfer the value (possibly transforming)
                source_val = source[source_key]
                
                if isinstance(source_val, (int, float)):
                    # Keep numerical values with a note
                    transferred[target_key] = {
                        'value': source_val,
                        'transferred_from': source_key,
                        'confidence': 0.7
                    }
                else:
                    transferred[target_key] = {
                        'analogous_to': source_val,
                        'transferred_from': source_key,
                        'confidence': 0.6
                    }
        
        return transferred
    
    def reason(self, premises: List[Any]) -> ReasoningResult:
        """
        Perform analogical reasoning.
        
        Expects premises to contain:
        - source_domain: Known domain to reason from
        - target_domain: Domain to reason about
        - query: What to infer about target domain
        
        Args:
            premises: List containing source, target, and query
            
        Returns:
            ReasoningResult with transferred knowledge
        """
        proof_steps = []
        
        # Parse premises
        source_domain = {}
        target_domain = {}
        query = None
        
        for premise in premises:
            if isinstance(premise, dict):
                if 'source' in premise:
                    source_domain = premise['source']
                elif 'target' in premise:
                    target_domain = premise['target']
                elif 'query' in premise:
                    query = premise['query']
                else:
                    # Assume it's additional domain info
                    target_domain.update(premise)
            elif isinstance(premise, str):
                query = premise
        
        proof_steps.append(f"Source domain: {source_domain}")
        proof_steps.append(f"Target domain: {target_domain}")
        proof_steps.append(f"Query: {query}")
        
        # Compute similarity
        similarity = self.compute_structural_similarity(source_domain, target_domain)
        proof_steps.append(f"Structural similarity: {similarity:.4f}")
        
        if similarity < 0.1:
            return ReasoningResult(
                conclusion={"error": "Domains too dissimilar for analogical reasoning"},
                confidence=0.0,
                reasoning_type=ReasoningType.ANALOGICAL,
                proof_steps=proof_steps,
                metadata={'similarity': similarity}
            )
        
        # Find mapping
        mapping = self.find_mapping(source_domain, target_domain)
        proof_steps.append(f"Found mapping: {mapping}")
        
        # Transfer knowledge
        transferred = self.transfer_knowledge(source_domain, mapping, target_domain)
        proof_steps.append(f"Transferred knowledge: {transferred}")
        
        # Calculate confidence based on similarity and mapping coverage
        mapping_coverage = len(mapping) / max(len(source_domain), 1) if source_domain else 0
        confidence = 0.5 * similarity + 0.5 * mapping_coverage
        
        return ReasoningResult(
            conclusion={
                'transferred_knowledge': transferred,
                'mapping': mapping,
                'similarity': similarity,
                'query_answer': transferred.get(query) if query else None
            },
            confidence=confidence,
            reasoning_type=ReasoningType.ANALOGICAL,
            proof_steps=proof_steps,
            metadata={
                'similarity': similarity,
                'mapping_coverage': mapping_coverage
            }
        )


class ReasoningEngineImpl(ReasoningEngine):
    """
    Implementation of reasoning engine supporting multiple reasoning strategies.
    
    Supports multiple reasoning strategies and can combine them.
    """
    
    def __init__(self, reasoning_type: ReasoningType = ReasoningType.DEDUCTIVE):
        """
        Initialize reasoning engine.
        
        Args:
            reasoning_type: Default type of reasoning to use
        """
        self.reasoning_type = reasoning_type
        self.validator = DataValidator()
        self.logger = SystemLogger()
        
        # Initialize all reasoners
        self.deductive = DeductiveReasoner()
        self.inductive = InductiveReasoner()
        self.abductive = AbductiveReasoner()
        self.analogical = AnalogicalReasoner()
        
        self.logger.log(f"ReasoningEngine initialized with type: {reasoning_type.value}", level="INFO")
    
    def reason(self, premises: List[Any]) -> Any:
        """
        Perform reasoning on given premises.
        
        Mathematical approach:
        - Deductive: If P→Q and P, then Q (modus ponens)
        - Inductive: Generalize from specific cases
        - Abductive: Infer best explanation
        - Analogical: Reasoning by analogy
        
        Args:
            premises: List of premises to reason from
            
        Returns:
            Reasoning result
        """
        if not self.validator.validate_list(premises):
            self.logger.log("Invalid premises provided", level="ERROR")
            raise ValueError("Invalid premises")
        
        self.logger.log(f"Reasoning with {len(premises)} premises", level="DEBUG")
        
        try:
            if self.reasoning_type == ReasoningType.DEDUCTIVE:
                result = self._deductive_reasoning(premises)
            elif self.reasoning_type == ReasoningType.INDUCTIVE:
                result = self._inductive_reasoning(premises)
            elif self.reasoning_type == ReasoningType.ABDUCTIVE:
                result = self._abductive_reasoning(premises)
            else:
                result = self._analogical_reasoning(premises)
            
            self.logger.log("Reasoning completed", level="INFO")
            return result.to_dict()
            
        except Exception as e:
            self.logger.log(f"Error in reasoning: {str(e)}", level="ERROR")
            raise
    
    def _deductive_reasoning(self, premises: List[Any]) -> ReasoningResult:
        """Deductive reasoning: logical inference from general to specific."""
        self.logger.log("Deductive reasoning", level="DEBUG")
        # Convert premises to strings for the deductive reasoner
        string_premises = [str(p) if not isinstance(p, str) else p for p in premises]
        return self.deductive.reason(string_premises)
    
    def _inductive_reasoning(self, premises: List[Any]) -> ReasoningResult:
        """Inductive reasoning: generalization from specific cases."""
        self.logger.log("Inductive reasoning", level="DEBUG")
        return self.inductive.reason(premises)
    
    def _abductive_reasoning(self, premises: List[Any]) -> ReasoningResult:
        """Abductive reasoning: inference to best explanation."""
        self.logger.log("Abductive reasoning", level="DEBUG")
        return self.abductive.reason(premises)
    
    def _analogical_reasoning(self, premises: List[Any]) -> ReasoningResult:
        """Analogical reasoning: reasoning by analogy."""
        self.logger.log("Analogical reasoning", level="DEBUG")
        return self.analogical.reason(premises)
    
    def reason_all(self, premises: List[Any]) -> Dict[str, ReasoningResult]:
        """
        Apply all reasoning types and return combined results.
        
        Args:
            premises: List of premises
            
        Returns:
            Dictionary with results from all reasoning types
        """
        results = {}
        
        for reasoning_type in ReasoningType:
            try:
                self.reasoning_type = reasoning_type
                result = self.reason(premises)
                results[reasoning_type.value] = result
            except Exception as e:
                results[reasoning_type.value] = {
                    'error': str(e),
                    'reasoning_type': reasoning_type.value
                }
        
        return results
    
    def add_deductive_rule(self, antecedent: str, consequent: str) -> None:
        """Add a deductive implication rule."""
        self.deductive.add_implication(antecedent, consequent)
    
    def add_abductive_hypothesis(self, name: str, explains: List[str], 
                                 complexity: int = 1, prior: float = 0.5) -> None:
        """Add an abductive hypothesis."""
        self.abductive.add_hypothesis(name, explains, complexity, prior)
    
    def add_analogy(self, source: Dict[str, Any], target: Dict[str, Any], 
                   mapping: Dict[str, str]) -> None:
        """Add a known analogy."""
        self.analogical.add_analogy(source, target, mapping)
