# api/services/
"""
Simulation Service - Business logic for physics simulations.
"""

from typing import Any, Dict, Optional, Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from physics.integration.physics_integrator import PhysicsIntegrator
from physics.permanence.retrieval import Retrieval
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel


class SimulationService:
    """
    Service for physics simulations.
    
    Encapsulates business logic for simulation operations.
    """
    
    def __init__(self):
        """Initialize simulation service."""
        self.logger = SystemLogger()
        self.integrator = PhysicsIntegrator()
        self.retrieval = Retrieval()
        
        self.logger.log("SimulationService initialized", level="INFO")
    
    def run_simulation(self,
                      scenario: Dict[str, Any],
                      initial_conditions: Dict[str, Any],
                      time_span: Tuple[float, float],
                      num_steps: int = 100,
                      use_cache: bool = True) -> Dict[str, Any]:
        """
        Run physics simulation.
        
        Args:
            scenario: Physical scenario
            initial_conditions: Initial conditions
            time_span: Time span tuple
            num_steps: Number of steps
            use_cache: Whether to use permanence cache
            
        Returns:
            Simulation results
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="SERVICE_RUN_SIMULATION",
            input_data={'scenario_keys': list(scenario.keys())},
            level=LogLevel.INFO
        )
        
        try:
            # Try retrieval first (uses cache if available)
            if use_cache:
                result = self.retrieval.get_state(
                    scenario=scenario,
                    initial_conditions=initial_conditions,
                    time_span=time_span,
                    num_steps=num_steps,
                    use_cache=True
                )
            else:
                # Direct computation
                result = self.integrator.simulate(
                    scenario=scenario,
                    initial_conditions=initial_conditions,
                    time_span=time_span,
                    num_steps=num_steps
                )
            
            cot.end_step(
                step_id,
                output_data={'result_keys': list(result.keys())},
                validation_passed=True
            )
            
            return result
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error in simulation service: {str(e)}", level="ERROR")
            raise

