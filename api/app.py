# api/
"""
PATH: api/app.py
PURPOSE: Main Flask application with WebSocket support.

FLOW:
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│ create_app  │───▶│ Register     │───▶│ Setup       │
│             │    │ Blueprints   │    │ Middleware  │
└─────────────┘    └──────────────┘    └─────────────┘

DEPENDENCIES:
- Flask: Web framework
- flask_socketio: WebSocket support
- api.v1: API endpoints
"""

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from api.v1 import api_v1
from substrate.main import create_physics_ai
from api.v1.substrate import init_substrate
import sys
import os
import secrets
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loggers.system_logger import SystemLogger
from api.websocket.handlers import setup_websocket_handlers

logger = SystemLogger()

# Initialize SocketIO
socketio = SocketIO(cors_allowed_origins="*")


def create_app():
    """
    Create and configure Flask application with WebSocket support.
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # SECURITY: Use environment variable for secret key, with secure fallback
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY') or os.getenv('SECRET_KEY') or secrets.token_hex(32)
    
    # Enable CORS
    CORS(app)
    
    # Initialize SocketIO with app
    socketio.init_app(app)
    
    # Register blueprints
    app.register_blueprint(api_v1)

    # Initialize core PhysicsAI and wire substrate API
    physics_ai = create_physics_ai()
    init_substrate(physics_ai)
    
    # Setup WebSocket handlers
    setup_websocket_handlers(app, socketio)
    
    # Setup middleware
    from api.middleware.logging import LoggingMiddleware
    from api.middleware.validation import ValidationMiddleware
    from api.middleware.auth import AuthMiddleware
    
    LoggingMiddleware.setup(app)
    ValidationMiddleware.setup(app)
    AuthMiddleware.setup(app)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        return {'status': 'healthy'}, 200
    
    logger.log("Flask application created with WebSocket support", level="INFO")
    
    return app


def get_socketio():
    """Get SocketIO instance."""
    return socketio


if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True, host='0.0.0.0', port=5002, allow_unsafe_werkzeug=True)

