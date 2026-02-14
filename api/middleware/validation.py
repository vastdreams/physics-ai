"""
PATH: api/middleware/validation.py
PURPOSE: Validation middleware that checks incoming request payloads.
"""

from typing import Optional, Tuple

from flask import Flask, jsonify, request

from loggers.system_logger import SystemLogger
from validators.data_validator import DataValidator

_logger = SystemLogger()
_validator = DataValidator()


class ValidationMiddleware:
    """Validation middleware for API requests."""

    @staticmethod
    def validate_json() -> Optional[Tuple]:
        """Return an error tuple if the JSON body is invalid, else ``None``."""
        if request.method in ("POST", "PUT", "PATCH"):
            if request.is_json:
                data = request.get_json()
                if not _validator.validate_dict(data):
                    return jsonify({"error": "Invalid JSON data"}), 400
        return None

    @staticmethod
    def setup(app: Flask) -> None:
        """Register the validation before-request hook on *app*."""

        @app.before_request
        def before_request() -> Optional[Tuple]:
            error = ValidationMiddleware.validate_json()
            if error:
                return error
            return None
