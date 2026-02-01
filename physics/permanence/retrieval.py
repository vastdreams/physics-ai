# physics/permanence/
"""
Retrieval - Fast lookup for pre-computed states.

Inspired by DREAM architecture - rapid retrieval of permanence states.

First Principle Analysis:
- Retrieval: Hash lookup → Return cached state or compute
- Fallback: If not cached, compute and store
- Mathematical foundation: Hash tables, caching algorithms
- Architecture: Fast retrieval with automatic fallback
"""

from typing import Any, Dict, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from .state_cache import StateCache
from physics.integration.physics_integrator import PhysicsIntegrator


class Retrieval:
    """
    Fast retrieval system for pre-computed states.
    
    Features:
    - Hash-based lookup
    - Automatic fallback to computation
    - Cache management
    """
    
    def __init__(self, state_cache: Optional[StateCache] = None):
        """
        Initialize retrieval system.
        
        Args:
            state_cache: Optional state cache instance
        """
        self.logger = SystemLogger()
        self.state_cache = state_cache or StateCache()
        self.integrator = PhysicsIntegrator()
        
        self.logger.log("Retrieval initialized", level="INFO")
    
    def get_state(self,
                  scenario: Dict[str, Any],
                  initial_conditions: Dict[str, Any],
                  time_span: tuple,
                  num_steps: int = 100,
                  use_cache: bool = True) -> Dict[str, Any]:
        """
        Get state (cached or computed).
        
        Args:
            scenario: Physical scenario
            initial_conditions: Initial conditions
            time_span: Time span tuple
            num_steps: Number of steps
            use_cache: Whether to use cache
            
        Returns:
            State dictionary
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="RETRIEVE_STATE",
            input_data={'use_cache': use_cache},
            level=LogLevel.INFO
        )
        
        try:
            # Prepare input data
            input_data = {
                'scenario': scenario,
                'initial_conditions': initial_conditions,
                'time_span': time_span,
                'num_steps': num_steps
            }
            
            # Try cache first
            if use_cache:
                cached_state = self.state_cache.retrieve(input_data)
                if cached_state:
                    cot.end_step(step_id, output_data={'source': 'cache'}, validation_passed=True)
                    self.logger.log("State retrieved from cache", level="DEBUG")
                    return cached_state
            
            # Compute if not cached
            state = self.integrator.simulate(
                scenario=scenario,
                initial_conditions=initial_conditions,
                time_span=time_span,
                num_steps=num_steps
            )
            
            # Store in cache
            if use_cache:
                self.state_cache.store(
                    input_data=input_data,
                    state=state,
                    metadata={'computed': True}
                )
            
            cot.end_step(step_id, output_data={'source': 'computed'}, validation_passed=True)
            
            self.logger.log("State computed and cached", level="DEBUG")
            
            return state
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error retrieving state: {str(e)}", level="ERROR")
            raise

