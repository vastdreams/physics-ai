# utilities/
"""
Synergy Expansion Engine with Interaction Terms.

Inspired by DREAM architecture - advanced synergy calculations with interaction terms.

First Principle Analysis:
- Synergy: S_net = Σ S_i + Σ w_ij S_i S_j (interaction terms)
- Log-space: log(S) = Σ log(1+δ_i) + Σ w_ij δ_i δ_j
- Regularization: Group-lasso for sparse synergy
- Mathematical foundation: Synergy matrices, interaction terms, regularization
- Architecture: Modular expansion engine with validation
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass, field
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from utilities.vector_framework import VECTORFramework, DeltaFactor


@dataclass
class SynergyExpansion:
    """Represents a synergy expansion."""
    name: str
    base_value: float
    delta_factors: List[str] = field(default_factory=list)
    interaction_terms: Dict[Tuple[str, str], float] = field(default_factory=dict)
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class SynergyExpansionEngine:
    """
    Synergy expansion engine with interaction terms.
    
    Features:
    - Base expansions: S_i
    - Interaction terms: w_ij S_i S_j
    - Log-space calculations
    - Regularization (group-lasso)
    - Validation against first-principles
    """
    
    def __init__(self):
        """Initialize synergy expansion engine."""
        self.logger = SystemLogger()
        self.vector = VECTORFramework()
        self.expansions: Dict[str, SynergyExpansion] = {}
        self.interaction_matrix: Dict[Tuple[str, str], float] = {}
        
        self.logger.log("SynergyExpansionEngine initialized", level="INFO")
    
    def add_expansion(self, expansion: SynergyExpansion) -> None:
        """Add a synergy expansion."""
        self.expansions[expansion.name] = expansion
        
        # Register interaction terms
        for (factor1, factor2), weight in expansion.interaction_terms.items():
            self.interaction_matrix[(factor1, factor2)] = weight
        
        self.logger.log(f"Synergy expansion added: {expansion.name}", level="INFO")
    
    def compute_net_synergy(self,
                            expansion_names: List[str],
                            delta_values: Dict[str, float],
                            use_log_space: bool = True) -> float:
        """
        Compute net synergy from multiple expansions.
        
        Mathematical:
        - Linear: S_net = Σ S_i + Σ w_ij S_i S_j
        - Log-space: log(S_net) = Σ log(1+δ_i) + Σ w_ij δ_i δ_j
        
        Args:
            expansion_names: List of expansion names
            delta_values: Dictionary of δ-factor values
            use_log_space: Whether to use log-space calculations
            
        Returns:
            Net synergy value
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="COMPUTE_NET_SYNERGY",
            input_data={'expansions': expansion_names, 'use_log_space': use_log_space},
            level=LogLevel.INFO
        )
        
        try:
            if use_log_space:
                # Log-space calculation
                log_synergy = 0.0
                
                # Base terms: Σ log(1+δ_i)
                for expansion_name in expansion_names:
                    if expansion_name in self.expansions:
                        expansion = self.expansions[expansion_name]
                        for delta_name in expansion.delta_factors:
                            if delta_name in delta_values:
                                delta = delta_values[delta_name]
                                log_synergy += np.log(1.0 + delta)
                
                # Interaction terms: Σ w_ij δ_i δ_j
                interaction_sum = 0.0
                delta_list = list(delta_values.items())
                for i, (name1, value1) in enumerate(delta_list):
                    for j, (name2, value2) in enumerate(delta_list):
                        if i < j:  # Avoid double counting
                            weight = self.interaction_matrix.get((name1, name2), 0.0)
                            interaction_sum += weight * value1 * value2
                
                log_synergy += interaction_sum
                
                # Convert back from log-space
                net_synergy = np.exp(log_synergy)
            else:
                # Linear calculation
                net_synergy = 0.0
                
                # Base terms: Σ S_i
                for expansion_name in expansion_names:
                    if expansion_name in self.expansions:
                        expansion = self.expansions[expansion_name]
                        net_synergy += expansion.base_value
                
                # Interaction terms: Σ w_ij S_i S_j
                for (name1, name2), weight in self.interaction_matrix.items():
                    if name1 in delta_values and name2 in delta_values:
                        value1 = delta_values[name1]
                        value2 = delta_values[name2]
                        net_synergy += weight * value1 * value2
            
            cot.end_step(
                step_id,
                output_data={'net_synergy': net_synergy},
                validation_passed=True
            )
            
            self.logger.log(f"Net synergy computed: {net_synergy:.4f}", level="DEBUG")
            
            return float(net_synergy)
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error computing net synergy: {str(e)}", level="ERROR")
            raise
    
    def apply_group_lasso_regularization(self,
                                       lambda_reg: float = 0.1) -> Dict[Tuple[str, str], float]:
        """
        Apply group-lasso regularization to interaction terms.
        
        Mathematical: Zero out small interaction terms
        - If |w_ij| < λ, set w_ij = 0
        
        Args:
            lambda_reg: Regularization parameter
            
        Returns:
            Regularized interaction matrix
        """
        regularized = {}
        
        for (name1, name2), weight in self.interaction_matrix.items():
            if abs(weight) >= lambda_reg:
                regularized[(name1, name2)] = weight
            else:
                # Zero out small terms
                self.logger.log(
                    f"Regularized out interaction: {name1}-{name2} (weight={weight:.4f} < {lambda_reg})",
                    level="DEBUG"
                )
        
        self.interaction_matrix = regularized
        
        return regularized
    
    def validate_expansion(self, expansion_name: str, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate expansion against first-principles.
        
        Args:
            expansion_name: Expansion name
            context: Validation context
            
        Returns:
            Tuple of (is_valid, violations)
        """
        if expansion_name not in self.expansions:
            return False, ["Expansion not found"]
        
        expansion = self.expansions[expansion_name]
        violations = []
        
        # Check base value is reasonable
        if expansion.base_value < -1.0 or expansion.base_value > 10.0:
            violations.append(f"Base value out of range: {expansion.base_value}")
        
        # Check interaction terms
        for (name1, name2), weight in expansion.interaction_terms.items():
            if abs(weight) > 10.0:
                violations.append(f"Large interaction term: {name1}-{name2} = {weight}")
        
        is_valid = len(violations) == 0
        
        if is_valid:
            self.logger.log(f"Expansion validated: {expansion_name}", level="DEBUG")
        else:
            self.logger.log(f"Expansion validation failed: {expansion_name} - {violations}", level="WARNING")
        
        return is_valid, violations
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get expansion statistics."""
        num_expansions = len(self.expansions)
        num_interactions = len(self.interaction_matrix)
        
        # Average interaction strength
        if num_interactions > 0:
            avg_interaction = np.mean([abs(w) for w in self.interaction_matrix.values()])
        else:
            avg_interaction = 0.0
        
        return {
            'num_expansions': num_expansions,
            'num_interactions': num_interactions,
            'avg_interaction_strength': float(avg_interaction)
        }

