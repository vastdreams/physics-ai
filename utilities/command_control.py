# utilities/
"""
Command & Control (C2) Center for Algorithm Orchestration.

Inspired by DREAM architecture Section 4.3.3.6.2.1 - C2 Center.

First Principle Analysis:
- C2 Center: Central orchestrator for all algorithms
- Decision: Choose MCMC vs Particle Filter based on problem
- Triggers: MHA, variance checks, overlay validation
- Mathematical foundation: Decision theory, algorithm selection
- Architecture: Centralized control with pluggable algorithms
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from utilities.vector_framework import VECTORFramework
from utilities.particle_filters import ParticleFilter
from utilities.performance_monitoring import PerformanceMonitor


class AlgorithmType(Enum):
    """Types of algorithms."""
    MCMC = "mcmc"
    PARTICLE_FILTER = "particle_filter"
    BAYESIAN_UPDATE = "bayesian_update"
    MHA = "multi_head_attention"
    OVERLAY_VALIDATION = "overlay_validation"


@dataclass
class AlgorithmDecision:
    """Represents an algorithm selection decision."""
    algorithm: AlgorithmType
    reasoning: str
    parameters: Dict[str, Any]
    confidence: float = 1.0


class CommandControlCenter:
    """
    Command & Control Center for algorithm orchestration.
    
    Features:
    - Algorithm selection (MCMC vs Particle Filter)
    - Variance checks
    - MHA triggering
    - Overlay validation
    - Performance monitoring
    """
    
    def __init__(self):
        """Initialize C2 Center."""
        self.logger = SystemLogger()
        self.vector = VECTORFramework()
        self.performance_monitor = PerformanceMonitor()
        self.algorithm_registry: Dict[AlgorithmType, Callable] = {}
        self.decision_history: List[AlgorithmDecision] = []
        
        self.logger.log("CommandControlCenter initialized", level="INFO")
    
    def select_algorithm(self,
                        problem_type: str,
                        data_dimension: int,
                        is_real_time: bool = False,
                        context: Optional[Dict[str, Any]] = None) -> AlgorithmDecision:
        """
        Select appropriate algorithm based on problem characteristics.
        
        Decision logic:
        - Real-time streaming + many factors → Particle Filters
        - Smaller dimension or offline → MCMC
        - High uncertainty → MHA for weighting
        
        Args:
            problem_type: Type of problem
            data_dimension: Dimension of data
            is_real_time: Whether real-time processing needed
            context: Additional context
            
        Returns:
            Algorithm decision
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="C2_SELECT_ALGORITHM",
            input_data={
                'problem_type': problem_type,
                'data_dimension': data_dimension,
                'is_real_time': is_real_time
            },
            level=LogLevel.DECISION
        )
        
        try:
            # Decision logic
            if is_real_time and data_dimension > 10:
                algorithm = AlgorithmType.PARTICLE_FILTER
                reasoning = "Real-time streaming with many factors requires particle filters"
                parameters = {'num_particles': 100}
            elif data_dimension < 5:
                algorithm = AlgorithmType.BAYESIAN_UPDATE
                reasoning = "Small dimension suitable for direct Bayesian update"
                parameters = {}
            else:
                algorithm = AlgorithmType.MCMC
                reasoning = "Medium dimension, offline processing - use MCMC"
                parameters = {'num_samples': 1000}
            
            decision = AlgorithmDecision(
                algorithm=algorithm,
                reasoning=reasoning,
                parameters=parameters,
                confidence=0.8
            )
            
            self.decision_history.append(decision)
            
            cot.log_decision(
                decision=f"Algorithm selection: {algorithm.value}",
                options=[a.value for a in AlgorithmType],
                chosen_option=algorithm.value,
                reasoning=reasoning
            )
            
            cot.end_step(step_id, output_data={'algorithm': algorithm.value}, validation_passed=True)
            
            self.logger.log(f"Algorithm selected: {algorithm.value} - {reasoning}", level="INFO")
            
            return decision
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error in algorithm selection: {str(e)}", level="ERROR")
            raise
    
    def check_variance(self, v_max: Optional[float] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Check variance and throttle if needed.
        
        Args:
            v_max: Maximum variance (uses framework default if None)
            
        Returns:
            Tuple of (throttled, statistics)
        """
        if v_max:
            self.vector.v_max = v_max
        
        v_obs = self.vector.compute_observed_variance()
        is_throttled = v_obs > self.vector.v_max
        
        if is_throttled:
            throttled = self.vector.throttle_variance()
            self.logger.log(f"Variance throttled: v_obs={v_obs:.4f} > v_max={self.vector.v_max}", level="WARNING")
        else:
            throttled = {}
        
        stats = self.vector.get_statistics()
        
        return is_throttled, stats
    
    def trigger_mha(self,
                   queries: List[Any],
                   keys: List[Any],
                   values: List[Any],
                   variances: List[float],
                   num_heads: int = 4) -> Tuple[Any, List[float]]:
        """
        Trigger Multi-Head Attention.
        
        Args:
            queries: Query vectors
            keys: Key vectors
            values: Value vectors
            variances: Variance for each input
            num_heads: Number of attention heads
            
        Returns:
            Tuple of (attention_output, attention_weights)
        """
        import numpy as np
        
        # Convert to numpy arrays if needed
        queries = [np.array(q) if not isinstance(q, np.ndarray) else q for q in queries]
        keys = [np.array(k) if not isinstance(k, np.ndarray) else k for k in keys]
        values = [np.array(v) if not isinstance(v, np.ndarray) else v for v in values]
        
        output, weights = self.vector.multi_head_attention(
            queries=queries,
            keys=keys,
            values=values,
            variances=variances,
            num_heads=num_heads
        )
        
        self.logger.log(f"MHA triggered: {len(queries)} inputs, {num_heads} heads", level="DEBUG")
        
        return output, weights
    
    def trigger_overlay_validation(self,
                                  simple_output: Dict[str, Any],
                                  complex_output: Dict[str, Any],
                                  epsilon_limit: float = 0.1) -> Tuple[bool, float]:
        """
        Trigger overlay validation.
        
        Args:
            simple_output: Simple model output
            complex_output: Complex model output
            epsilon_limit: Maximum allowed deviation
            
        Returns:
            Tuple of (is_valid, deviation)
        """
        is_valid, deviation = self.vector.overlay_validation(
            simple_output,
            complex_output,
            epsilon_limit
        )
        
        # Log to performance monitor
        self.performance_monitor.record_metric(
            "overlay_deviation",
            deviation,
            variance=0.0
        )
        
        return is_valid, deviation
    
    def orchestrate_workflow(self,
                            workflow_steps: List[Dict[str, Any]],
                            context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate a complete workflow.
        
        Args:
            workflow_steps: List of workflow steps
            context: Workflow context
            
        Returns:
            Final context after workflow
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="C2_ORCHESTRATE_WORKFLOW",
            input_data={'num_steps': len(workflow_steps)},
            level=LogLevel.INFO
        )
        
        try:
            current_context = context.copy()
            
            for i, step in enumerate(workflow_steps):
                step_type = step.get('type')
                step_data = step.get('data', {})
                
                if step_type == 'variance_check':
                    throttled, stats = self.check_variance(step_data.get('v_max'))
                    current_context['variance_stats'] = stats
                
                elif step_type == 'mha':
                    output, weights = self.trigger_mha(
                        queries=step_data.get('queries', []),
                        keys=step_data.get('keys', []),
                        values=step_data.get('values', []),
                        variances=step_data.get('variances', []),
                        num_heads=step_data.get('num_heads', 4)
                    )
                    current_context['mha_output'] = output
                    current_context['mha_weights'] = weights
                
                elif step_type == 'overlay_validation':
                    is_valid, deviation = self.trigger_overlay_validation(
                        simple_output=step_data.get('simple_output', {}),
                        complex_output=step_data.get('complex_output', {}),
                        epsilon_limit=step_data.get('epsilon_limit', 0.1)
                    )
                    current_context['validation_passed'] = is_valid
                    current_context['validation_deviation'] = deviation
                
                elif step_type == 'algorithm_selection':
                    decision = self.select_algorithm(
                        problem_type=step_data.get('problem_type', 'unknown'),
                        data_dimension=step_data.get('data_dimension', 1),
                        is_real_time=step_data.get('is_real_time', False)
                    )
                    current_context['selected_algorithm'] = decision.algorithm.value
            
            cot.end_step(step_id, output_data={'workflow_completed': True}, validation_passed=True)
            
            self.logger.log(f"Workflow orchestrated: {len(workflow_steps)} steps", level="INFO")
            
            return current_context
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error orchestrating workflow: {str(e)}", level="ERROR")
            raise
    
    def register_algorithm(self, algorithm_type: AlgorithmType, implementation: Callable) -> None:
        """Register an algorithm implementation."""
        self.algorithm_registry[algorithm_type] = implementation
        self.logger.log(f"Algorithm registered: {algorithm_type.value}", level="INFO")
    
    def get_decision_history(self) -> List[Dict[str, Any]]:
        """Get decision history."""
        return [
            {
                'algorithm': d.algorithm.value,
                'reasoning': d.reasoning,
                'parameters': d.parameters,
                'confidence': d.confidence
            }
            for d in self.decision_history
        ]

