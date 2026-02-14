"""
PATH: api/services/evolution_service.py
PURPOSE: Business logic for code evolution operations.
"""

from typing import Any, Dict, List, Optional, Tuple

from ai.nodal_vectorization.graph_builder import GraphBuilder
from evolution.self_evolution import SelfEvolutionEngine
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel


class EvolutionService:
    """Service layer for code evolution operations."""

    def __init__(self) -> None:
        """Initialise the evolution engine and supporting services."""
        self._logger = SystemLogger()
        graph_builder = GraphBuilder()
        self.evolution_engine = SelfEvolutionEngine(graph_builder)
        self._logger.log("EvolutionService initialized", level="INFO")

    def analyze_codebase(self, directory_path: str) -> Dict[str, Any]:
        """
        Analyse a codebase for evolution opportunities.

        Args:
            directory_path: Filesystem path to the directory to analyse.

        Returns:
            A dictionary of analysis results.
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="SERVICE_ANALYZE_CODEBASE",
            input_data={"directory": directory_path},
            level=LogLevel.INFO,
        )

        try:
            analysis = self.evolution_engine.analyze_codebase(directory_path)
            cot.end_step(
                step_id,
                output_data={"analysis_keys": list(analysis.keys())},
                validation_passed=True,
            )
            return analysis
        except Exception as e:
            cot.end_step(step_id, output_data={"error": str(e)}, validation_passed=False)
            self._logger.log(f"Error in evolution service: {e}", level="ERROR")
            raise

    def evolve_function(
        self,
        file_path: str,
        function_name: str,
        improvement_spec: Dict[str, Any],
    ) -> Tuple[bool, Optional[str]]:
        """
        Apply an evolutionary improvement to a single function.

        Args:
            file_path: Path to the source file.
            function_name: Name of the target function.
            improvement_spec: Specification describing the desired improvement.

        Returns:
            A tuple of ``(success, new_code)``.
        """
        return self.evolution_engine.evolve_function(
            file_path=file_path,
            function_name=function_name,
            improvement_spec=improvement_spec,
        )

    def get_evolution_history(self) -> List[Dict[str, Any]]:
        """Return the full evolution history."""
        return self.evolution_engine.get_evolution_history()
