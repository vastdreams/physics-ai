# api/middleware/
"""
Logging Middleware.

Logs all API requests and responses.
"""

from flask import request, g
from functools import wraps
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel

logger = SystemLogger()


class LoggingMiddleware:
    """Logging middleware for API requests."""
    
    @staticmethod
    def log_request():
        """Log incoming request."""
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="API_REQUEST",
            input_data={
                'method': request.method,
                'path': request.path,
                'endpoint': request.endpoint
            },
            level=LogLevel.INFO
        )
        
        # Store step_id in Flask g for later use
        g.cot_step_id = step_id
        
        logger.log(
            f"API Request: {request.method} {request.path}",
            level="INFO"
        )
    
    @staticmethod
    def log_response(response):
        """Log outgoing response."""
        if hasattr(g, 'cot_step_id'):
            # Would end CoT step here
            pass
        
        logger.log(
            f"API Response: {response.status_code}",
            level="DEBUG"
        )
        
        return response
    
    @staticmethod
    def setup(app):
        """Setup middleware on Flask app."""
        @app.before_request
        def before_request():
            LoggingMiddleware.log_request()
        
        @app.after_request
        def after_request(response):
            return LoggingMiddleware.log_response(response)

