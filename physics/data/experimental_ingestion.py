"""
PATH: physics/data/experimental_ingestion.py
PURPOSE: Ingest and normalize experimental physics data

Normalizes raw measurements to dimensionless deviation parameters:
    δ_E = (E - E_ref) / E_ref     (energy deviation)
    δ_g = (g - g_ref) / g_ref     (coupling constant deviation)
    δ_m = (m - m_ref) / m_ref     (mass deviation)

DEPENDENCIES:
- numpy: Numerical computation
- validators.data_validator: Input validation
- loggers.system_logger: Structured logging
"""

from typing import Any, Dict, List, Tuple

import numpy as np

from loggers.system_logger import SystemLogger
from validators.data_validator import DataValidator

# Minimum reference value to avoid division by zero
_REF_MIN_TOLERANCE: float = 1e-10


class ExperimentalDataIngestion:
    """
    Experimental data ingestion and normalization.

    Converts raw measurements to dimensionless deviation parameters
    suitable for the physics framework.
    """

    def __init__(self) -> None:
        """Initialize experimental data ingestion system."""
        self.validator = DataValidator()
        self._logger = SystemLogger()

        self.reference_values: Dict[str, float] = {
            'energy': 1.0,
            'coupling_constant': 1.0,
            'mass': 1.0,
            'length': 1.0,
        }

        self._logger.log("ExperimentalDataIngestion initialized", level="INFO")

    def normalize_energy(self,
                          energy: float,
                          reference_energy: float | None = None) -> float:
        """
        Normalize energy to dimensionless deviation.

        Equation: δ_E = (E - E_ref) / E_ref

        Args:
            energy: Energy value
            reference_energy: Reference energy (None = use default)

        Returns:
            Dimensionless energy deviation δ_E
        """
        if reference_energy is None:
            reference_energy = self.reference_values['energy']

        if abs(reference_energy) < _REF_MIN_TOLERANCE:
            self._logger.log("Reference energy too small", level="WARNING")
            return 0.0

        delta_e = (energy - reference_energy) / reference_energy

        self._logger.log(f"Energy normalized: δ_E = {delta_e}", level="DEBUG")
        return delta_e

    def normalize_coupling_constant(self,
                                     coupling: float,
                                     reference_coupling: float | None = None) -> float:
        """
        Normalize coupling constant to dimensionless deviation.

        Equation: δ_g = (g - g_ref) / g_ref

        Args:
            coupling: Coupling constant g
            reference_coupling: Reference coupling (None = use default)

        Returns:
            Dimensionless coupling deviation δ_g
        """
        if reference_coupling is None:
            reference_coupling = self.reference_values['coupling_constant']

        if abs(reference_coupling) < _REF_MIN_TOLERANCE:
            self._logger.log("Reference coupling too small", level="WARNING")
            return 0.0

        delta_g = (coupling - reference_coupling) / reference_coupling

        self._logger.log(f"Coupling normalized: δ_g = {delta_g}", level="DEBUG")
        return delta_g

    def normalize_mass(self,
                       mass: float,
                       reference_mass: float | None = None) -> float:
        """
        Normalize mass to dimensionless deviation.

        Equation: δ_m = (m - m_ref) / m_ref

        Args:
            mass: Mass value
            reference_mass: Reference mass (None = use default)

        Returns:
            Dimensionless mass deviation δ_m
        """
        if reference_mass is None:
            reference_mass = self.reference_values['mass']

        if abs(reference_mass) < _REF_MIN_TOLERANCE:
            self._logger.log("Reference mass too small", level="WARNING")
            return 0.0

        delta_m = (mass - reference_mass) / reference_mass

        self._logger.log(f"Mass normalized: δ_m = {delta_m}", level="DEBUG")
        return delta_m

    def ingest_experimental_data(self,
                                  data: Dict[str, Any],
                                  data_type: str) -> Dict[str, float]:
        """
        Ingest experimental data and normalize to dimensionless parameters.

        Args:
            data: Dictionary with experimental data
            data_type: Type of data ("energy", "coupling", "mass")

        Returns:
            Dictionary with normalized dimensionless parameters
        """
        normalized: Dict[str, float] = {}

        if data_type == "energy":
            if 'energy' in data:
                normalized['delta_energy'] = self.normalize_energy(
                    data['energy'],
                    data.get('reference_energy')
                )
        elif data_type == "coupling":
            if 'coupling' in data:
                normalized['delta_coupling'] = self.normalize_coupling_constant(
                    data['coupling'],
                    data.get('reference_coupling')
                )
        elif data_type == "mass":
            if 'mass' in data:
                normalized['delta_mass'] = self.normalize_mass(
                    data['mass'],
                    data.get('reference_mass')
                )
        else:
            self._logger.log(f"Unknown data type: {data_type}", level="WARNING")

        self._logger.log(f"Experimental data ingested: {data_type}", level="INFO")
        return normalized

    def compute_uncertainty(self,
                             value: float,
                             uncertainty: float,
                             reference: float) -> Tuple[float, float]:
        """
        Compute normalized value and uncertainty.

        Args:
            value: Measured value
            uncertainty: Measurement uncertainty
            reference: Reference value

        Returns:
            Tuple of (normalized_value, normalized_uncertainty)
        """
        normalized_value = (value - reference) / reference
        normalized_uncertainty = uncertainty / reference

        return normalized_value, normalized_uncertainty

    def set_reference_value(self,
                             parameter_name: str,
                             reference_value: float) -> None:
        """
        Set reference value for normalization.

        Args:
            parameter_name: Parameter name ("energy", "coupling", etc.)
            reference_value: Reference value
        """
        self.reference_values[parameter_name] = reference_value
        self._logger.log(
            f"Reference value set: {parameter_name} = {reference_value}",
            level="INFO"
        )

    def validate_data(self,
                       data: Dict[str, Any],
                       expected_keys: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate experimental data structure.

        Args:
            data: Data dictionary
            expected_keys: List of expected keys

        Returns:
            Tuple of (is_valid, list of missing keys)
        """
        missing_keys = [key for key in expected_keys if key not in data]

        is_valid = len(missing_keys) == 0

        if not is_valid:
            self._logger.log(f"Data validation failed: missing keys {missing_keys}", level="WARNING")
        else:
            self._logger.log("Data validation passed", level="DEBUG")

        return is_valid, missing_keys
