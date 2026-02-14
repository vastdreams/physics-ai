"""
PATH: api/middleware/logging.py
PURPOSE: Logging middleware that records API requests and responses.
"""

from flask import Flask, Response, g, request

from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel

_logger = SystemLogger()


class LoggingMiddleware:
    """Logging middleware for API requests."""

    @staticmethod
    def log_request() -> None:
        """Log the incoming request and start a chain-of-thought step."""
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="API_REQUEST",
            input_data={
                "method": request.method,
                "path": request.path,
                "endpoint": request.endpoint,
            },
            level=LogLevel.INFO,
        )

        # Store step_id in Flask g for potential downstream use
        g.cot_step_id = step_id

        _logger.log(f"API Request: {request.method} {request.path}", level="INFO")

    @staticmethod
    def log_response(response: Response) -> Response:
        """Log the outgoing response status."""
        _logger.log(f"API Response: {response.status_code}", level="DEBUG")
        return response

    @staticmethod
    def setup(app: Flask) -> None:
        """Register request/response logging hooks on *app*."""

        @app.before_request
        def before_request() -> None:
            LoggingMiddleware.log_request()

        @app.after_request
        def after_request(response: Response) -> Response:
            return LoggingMiddleware.log_response(response)
