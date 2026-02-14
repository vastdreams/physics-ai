"""
Data validation module.

Validates data for type, format, and constraints.
Provides comprehensive validation to ensure system reliability
and enable future AI self-validation.
"""

from __future__ import annotations

from typing import Any, Dict, List

from loggers.system_logger import SystemLogger

_VALID_PRIMITIVE_TYPES = (str, int, float, list, dict, bool)


class DataValidator:
    """Validates data for type, format, and constraints."""

    def __init__(self) -> None:
        """Initialize data validator."""
        self._logger = SystemLogger()
        self._logger.log("DataValidator initialized", level="INFO")

    def validate_input(self, data: Any) -> bool:
        """Validate input data.

        Args:
            data: Data to validate.

        Returns:
            True if valid, False otherwise.
        """
        if data is None:
            self._logger.log("Input data is None", level="WARNING")
            return False

        if not isinstance(data, _VALID_PRIMITIVE_TYPES):
            self._logger.log(f"Invalid input type: {type(data)}", level="WARNING")
            return False

        self._logger.log("Input validation passed", level="DEBUG")
        return True

    def validate_output(self, data: Any) -> bool:
        """Validate output data.

        Args:
            data: Data to validate.

        Returns:
            True if valid, False otherwise.
        """
        if data is None:
            self._logger.log("Output data is None", level="WARNING")
            return False

        if not isinstance(data, _VALID_PRIMITIVE_TYPES):
            self._logger.log(f"Invalid output type: {type(data)}", level="WARNING")
            return False

        self._logger.log("Output validation passed", level="DEBUG")
        return True

    def validate_dict(self, data: Dict[str, Any]) -> bool:
        """Validate dictionary structure.

        Args:
            data: Dictionary to validate.

        Returns:
            True if valid (non-empty dict), False otherwise.
        """
        if not isinstance(data, dict):
            self._logger.log("Data is not a dictionary", level="WARNING")
            return False

        if len(data) == 0:
            self._logger.log("Dictionary is empty", level="WARNING")
            return False

        self._logger.log("Dictionary validation passed", level="DEBUG")
        return True

    def validate_list(self, data: List[Any]) -> bool:
        """Validate list structure.

        Args:
            data: List to validate.

        Returns:
            True if valid, False otherwise.
        """
        if not isinstance(data, list):
            self._logger.log("Data is not a list", level="WARNING")
            return False

        self._logger.log("List validation passed", level="DEBUG")
        return True

    def validate_type(self, data: Any, expected_type: type) -> bool:
        """Validate data type.

        Args:
            data: Data to validate.
            expected_type: Expected type.

        Returns:
            True if valid, False otherwise.
        """
        if not isinstance(data, expected_type):
            self._logger.log(
                f"Type mismatch: expected {expected_type}, got {type(data)}", level="WARNING"
            )
            return False

        self._logger.log("Type validation passed", level="DEBUG")
        return True
