"""
PATH: physics/permanence/retrieval.py
PURPOSE: Fast lookup for pre-computed states with automatic fallback

Inspired by DREAM architecture — attempts cache retrieval first,
falls back to full simulation when cache misses occur.

FLOW:
┌───────┐   ┌───────────┐   hit   ┌────────────┐
│ Input │ → │ Cache     │ ──────→ │ Return     │
└───────┘   │ lookup    │         │ cached     │
            └─────┬─────┘         └────────────┘
                  │ miss
                  ▼
            ┌───────────┐   ┌────────────┐
            │ Compute   │ → │ Store +    │
            │ via sim   │   │ return     │
            └───────────┘   └────────────┘

DEPENDENCIES:
- loggers.system_logger: Structured logging
- utilities.cot_logging: Chain-of-thought logging
- .state_cache: Hash-based state cache
- physics.integration.physics_integrator: Simulation fallback
"""

from typing import Any, Dict, Optional

from loggers.system_logger import SystemLogger
from physics.integration.physics_integrator import PhysicsIntegrator
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel

from .state_cache import StateCache


class Retrieval:
    """
    Fast retrieval system for pre-computed states.

    Provides hash-based cache lookup with automatic fallback
    to full physics simulation on cache miss.
    """

    def __init__(self, state_cache: Optional[StateCache] = None) -> None:
        """
        Initialize retrieval system.

        Args:
            state_cache: Optional state cache instance (creates default if None)
        """
        self._logger = SystemLogger()
        self.state_cache = state_cache or StateCache()
        self.integrator = PhysicsIntegrator()

        self._logger.log("Retrieval initialized", level="INFO")

    def get_state(self,
                  scenario: Dict[str, Any],
                  initial_conditions: Dict[str, Any],
                  time_span: tuple,
                  num_steps: int = 100,
                  use_cache: bool = True) -> Dict[str, Any]:
        """
        Get state from cache or compute via simulation.

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
            input_data = {
                'scenario': scenario,
                'initial_conditions': initial_conditions,
                'time_span': time_span,
                'num_steps': num_steps
            }

            if use_cache:
                cached_state = self.state_cache.retrieve(input_data)
                if cached_state:
                    cot.end_step(step_id, output_data={'source': 'cache'}, validation_passed=True)
                    self._logger.log("State retrieved from cache", level="DEBUG")
                    return cached_state

            state = self.integrator.simulate(
                scenario=scenario,
                initial_conditions=initial_conditions,
                time_span=time_span,
                num_steps=num_steps
            )

            if use_cache:
                self.state_cache.store(
                    input_data=input_data,
                    state=state,
                    metadata={'computed': True}
                )

            cot.end_step(step_id, output_data={'source': 'computed'}, validation_passed=True)
            self._logger.log("State computed and cached", level="DEBUG")

            return state

        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self._logger.log(f"Error retrieving state: {e}", level="ERROR")
            raise
