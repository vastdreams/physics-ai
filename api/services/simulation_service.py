"""
PATH: api/services/simulation_service.py
PURPOSE: Business logic for physics simulation operations.
"""

from typing import Any, Dict, Tuple

from loggers.system_logger import SystemLogger
from physics.integration.physics_integrator import PhysicsIntegrator
from physics.permanence.retrieval import Retrieval
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel


class SimulationService:
    """Service layer for physics simulations."""

    def __init__(self) -> None:
        """Initialise the physics integrator and retrieval cache."""
        self._logger = SystemLogger()
        self.integrator = PhysicsIntegrator()
        self.retrieval = Retrieval()
        self._logger.log("SimulationService initialized", level="INFO")

    def run_simulation(
        self,
        scenario: Dict[str, Any],
        initial_conditions: Dict[str, Any],
        time_span: Tuple[float, float],
        num_steps: int = 100,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Run a physics simulation.

        Args:
            scenario: Description of the physical scenario.
            initial_conditions: Starting state for the simulation.
            time_span: ``(t_start, t_end)`` time boundaries.
            num_steps: Number of integration steps.
            use_cache: Whether to attempt retrieval from cache first.

        Returns:
            A dictionary of simulation results.
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="SERVICE_RUN_SIMULATION",
            input_data={"scenario_keys": list(scenario.keys())},
            level=LogLevel.INFO,
        )

        try:
            if use_cache:
                result = self.retrieval.get_state(
                    scenario=scenario,
                    initial_conditions=initial_conditions,
                    time_span=time_span,
                    num_steps=num_steps,
                    use_cache=True,
                )
            else:
                result = self.integrator.simulate(
                    scenario=scenario,
                    initial_conditions=initial_conditions,
                    time_span=time_span,
                    num_steps=num_steps,
                )

            cot.end_step(
                step_id,
                output_data={"result_keys": list(result.keys())},
                validation_passed=True,
            )
            return result
        except Exception as e:
            cot.end_step(step_id, output_data={"error": str(e)}, validation_passed=False)
            self._logger.log(f"Error in simulation service: {e}", level="ERROR")
            raise
