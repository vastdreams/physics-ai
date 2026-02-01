# api/middleware/
"""
Validation Middleware.

Validates request data.
"""

from flask import request, jsonify
from functools import wraps
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from validators.data_validator import DataValidator
from loggers.system_logger import SystemLogger

logger = SystemLogger()
validator = DataValidator()


class ValidationMiddleware:
    """Validation middleware for API requests."""
    
    @staticmethod
    def validate_json():
        """Validate JSON request body."""
        if request.method in ['POST', 'PUT', 'PATCH']:
            if request.is_json:
                data = request.get_json()
                if not validator.validate_dict(data):
                    return jsonify({'error': 'Invalid JSON data'}), 400
        return None
    
    @staticmethod
    def setup(app):
        """Setup middleware on Flask app."""
        @app.before_request
        def before_request():
            error = ValidationMiddleware.validate_json()
            if error:
                return error

