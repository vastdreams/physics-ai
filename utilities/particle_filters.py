# utilities/
"""
Particle Filters for Sequential Bayesian Updates.

Inspired by DREAM architecture - sequential importance resampling.

First Principle Analysis:
- Particles: P = {p_1, p_2, ..., p_N} where p_i = (state, weight)
- Sequential update: w_i^(k) = p(data | p_i^(k))
- Resampling: Resample based on weights
- Mathematical foundation: Sequential Monte Carlo, Bayesian filtering
- Architecture: Modular particle filter with customizable dynamics
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel


@dataclass
class Particle:
    """Represents a particle in the filter."""
    state: Dict[str, float]
    weight: float = 1.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ParticleFilter:
    """
    Particle filter for sequential Bayesian updates.
    
    Features:
    - Sequential state estimation
    - Importance resampling
    - Custom dynamics and observation models
    - Variance tracking
    """
    
    def __init__(self,
                 num_particles: int = 100,
                 resample_threshold: float = 0.5):
        """
        Initialize particle filter.
        
        Args:
            num_particles: Number of particles
            resample_threshold: Effective sample size threshold for resampling
        """
        self.logger = SystemLogger()
        self.num_particles = num_particles
        self.resample_threshold = resample_threshold
        self.particles: List[Particle] = []
        self.iteration = 0
        
        self.logger.log(f"ParticleFilter initialized (N={num_particles})", level="INFO")
    
    def initialize(self,
                   initial_states: Optional[List[Dict[str, float]]] = None,
                   initial_distribution: Optional[Callable] = None) -> None:
        """
        Initialize particles.
        
        Args:
            initial_states: Optional list of initial states
            initial_distribution: Optional function to sample initial states
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="PARTICLE_FILTER_INITIALIZE",
            level=LogLevel.INFO
        )
        
        try:
            if initial_states:
                # Use provided states
                self.particles = [
                    Particle(state=state, weight=1.0 / len(initial_states))
                    for state in initial_states[:self.num_particles]
                ]
            elif initial_distribution:
                # Sample from distribution
                self.particles = [
                    Particle(state=initial_distribution(), weight=1.0 / self.num_particles)
                    for _ in range(self.num_particles)
                ]
            else:
                # Default: uniform initialization
                self.particles = [
                    Particle(state={}, weight=1.0 / self.num_particles)
                    for _ in range(self.num_particles)
                ]
            
            cot.end_step(step_id, output_data={'num_particles': len(self.particles)}, validation_passed=True)
            self.logger.log(f"Particles initialized: {len(self.particles)}", level="INFO")
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error initializing particles: {str(e)}", level="ERROR")
            raise
    
    def predict(self, dynamics: Callable[[Dict[str, float]], Dict[str, float]], noise: Optional[Dict[str, float]] = None) -> None:
        """
        Prediction step: propagate particles through dynamics.
        
        Args:
            dynamics: Function f(state) -> new_state
            noise: Optional noise to add (variance for each state variable)
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="PARTICLE_FILTER_PREDICT",
            level=LogLevel.INFO
        )
        
        try:
            for particle in self.particles:
                # Apply dynamics
                new_state = dynamics(particle.state)
                
                # Add noise if provided
                if noise:
                    for key, variance in noise.items():
                        if key in new_state:
                            new_state[key] += np.random.normal(0, np.sqrt(variance))
                
                particle.state = new_state
            
            self.iteration += 1
            
            cot.end_step(step_id, output_data={'iteration': self.iteration}, validation_passed=True)
            self.logger.log(f"Prediction step completed: iteration {self.iteration}", level="DEBUG")
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error in prediction: {str(e)}", level="ERROR")
            raise
    
    def update(self,
               observation: Dict[str, float],
               likelihood: Callable[[Dict[str, float], Dict[str, float]], float]) -> None:
        """
        Update step: weight particles by observation likelihood.
        
        Args:
            observation: Observed data
            likelihood: Function likelihood(particle_state, observation) -> probability
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="PARTICLE_FILTER_UPDATE",
            level=LogLevel.INFO
        )
        
        try:
            # Compute weights
            weights = []
            for particle in self.particles:
                weight = likelihood(particle.state, observation)
                weights.append(weight)
            
            # Normalize weights
            total_weight = sum(weights)
            if total_weight > 0:
                weights = [w / total_weight for w in weights]
            else:
                # Uniform weights if all zero
                weights = [1.0 / len(self.particles)] * len(self.particles)
            
            # Update particle weights
            for particle, weight in zip(self.particles, weights):
                particle.weight = weight
            
            cot.end_step(
                step_id,
                output_data={
                    'max_weight': max(weights),
                    'min_weight': min(weights),
                    'effective_sample_size': self._effective_sample_size()
                },
                validation_passed=True
            )
            
            self.logger.log(f"Update step completed: max_weight={max(weights):.4f}", level="DEBUG")
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error in update: {str(e)}", level="ERROR")
            raise
    
    def resample(self) -> None:
        """
        Resample particles based on weights.
        
        Uses systematic resampling.
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="PARTICLE_FILTER_RESAMPLE",
            level=LogLevel.INFO
        )
        
        try:
            # Check if resampling needed
            ess = self._effective_sample_size()
            if ess > self.resample_threshold * self.num_particles:
                cot.end_step(step_id, output_data={'ess': ess, 'resampled': False}, validation_passed=True)
                return
            
            # Systematic resampling
            weights = [p.weight for p in self.particles]
            cumulative_weights = np.cumsum(weights)
            
            new_particles = []
            step = 1.0 / self.num_particles
            u = np.random.uniform(0, step)
            
            j = 0
            for i in range(self.num_particles):
                while u > cumulative_weights[j]:
                    j += 1
                
                # Copy particle (in practice would deep copy)
                new_particle = Particle(
                    state=dict(self.particles[j].state),
                    weight=1.0 / self.num_particles,
                    metadata=dict(self.particles[j].metadata) if self.particles[j].metadata else {}
                )
                new_particles.append(new_particle)
                u += step
            
            self.particles = new_particles
            
            cot.end_step(step_id, output_data={'ess': ess, 'resampled': True}, validation_passed=True)
            self.logger.log(f"Resampling completed: {len(self.particles)} particles", level="DEBUG")
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error in resampling: {str(e)}", level="ERROR")
            raise
    
    def _effective_sample_size(self) -> float:
        """
        Compute effective sample size.
        
        Mathematical: ESS = 1 / Σ w_i²
        
        Returns:
            Effective sample size
        """
        weights = [p.weight for p in self.particles]
        if not weights:
            return 0.0
        
        weights_array = np.array(weights)
        ess = 1.0 / np.sum(weights_array**2)
        return float(ess)
    
    def get_estimate(self) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Get state estimate (mean and variance).
        
        Returns:
            Tuple of (mean_state, variance_state)
        """
        if not self.particles:
            return {}, {}
        
        # Get all state keys
        all_keys = set()
        for particle in self.particles:
            all_keys.update(particle.state.keys())
        
        mean_state = {}
        variance_state = {}
        
        for key in all_keys:
            values = [p.state.get(key, 0.0) for p in self.particles]
            weights = [p.weight for p in self.particles]
            
            # Weighted mean
            mean = np.average(values, weights=weights)
            
            # Weighted variance
            variance = np.average([(v - mean)**2 for v in values], weights=weights)
            
            mean_state[key] = float(mean)
            variance_state[key] = float(variance)
        
        return mean_state, variance_state
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get filter statistics."""
        ess = self._effective_sample_size()
        mean_state, variance_state = self.get_estimate()
        
        return {
            'num_particles': len(self.particles),
            'effective_sample_size': ess,
            'iteration': self.iteration,
            'mean_state': mean_state,
            'variance_state': variance_state
        }

