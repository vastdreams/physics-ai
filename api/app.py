# api/
"""
PATH: api/app.py
PURPOSE: Main Flask application with WebSocket support and hot reload.

FLOW:
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│ create_app  │───▶│ Register     │───▶│ Setup       │
│             │    │ Blueprints   │    │ Middleware  │
└─────────────┘    └──────────────┘    └─────────────┘
                                              │
                                              ▼
                                       ┌─────────────┐
                                       │ Hot Reload  │
                                       │ (optional)  │
                                       └─────────────┘

DEPENDENCIES:
- Flask: Web framework
- flask_socketio: WebSocket support
- api.v1: API endpoints
- utilities.hot_reload: Auto-update system
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

# Global hot reloader reference
_hot_reloader = None


def create_app(enable_hot_reload: bool = None):
    """
    Create and configure Flask application with WebSocket support.
    
    Args:
        enable_hot_reload: Enable hot reload (default: True in debug mode)
    
    Returns:
        Flask application instance
    """
    global _hot_reloader
    
    app = Flask(__name__)
    
    # SECURITY: Use environment variable for secret key, with secure fallback
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY') or os.getenv('SECRET_KEY') or secrets.token_hex(32)
    
    # Enable CORS
    CORS(app)
    
    # Initialize SocketIO with app
    socketio.init_app(app)
    
    # Register blueprints
    app.register_blueprint(api_v1)
    
    # Register hot reload API
    from api.v1.hot_reload import hot_reload_bp, set_reloader
    app.register_blueprint(hot_reload_bp)

    # Initialize core PhysicsAI and wire substrate API
    physics_ai = create_physics_ai()
    init_substrate(physics_ai)
    
    # Setup WebSocket handlers
    setup_websocket_handlers(app, socketio)
    
    # Setup middleware
    from api.middleware.logging import LoggingMiddleware
    from api.middleware.validation import ValidationMiddleware
    
    LoggingMiddleware.setup(app)
    ValidationMiddleware.setup(app)
    # Note: Auth is now handled via decorators (@require_auth) in api/v1/auth.py
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        hot_reload_status = "enabled" if _hot_reloader and _hot_reloader._running else "disabled"
        return {
            'status': 'healthy',
            'hot_reload': hot_reload_status,
        }, 200
    
    # Initialize hot reload if enabled
    if enable_hot_reload is None:
        enable_hot_reload = os.getenv('ENABLE_HOT_RELOAD', 'true').lower() == 'true'
    
    if enable_hot_reload:
        try:
            from utilities.hot_reload import start_hot_reload
            
            def on_reload_callback(event):
                # Emit WebSocket event when module reloads
                if event.success:
                    socketio.emit('module_reloaded', {
                        'module': event.module_name,
                        'timestamp': event.timestamp.isoformat(),
                        'reload_time_ms': event.reload_time_ms,
                    })
                else:
                    socketio.emit('module_reload_failed', {
                        'module': event.module_name,
                        'error': event.error[:200] if event.error else None,
                    })
            
            _hot_reloader = start_hot_reload(
                watch_dirs=['physics', 'substrate', 'api', 'core', 'rules', 'evolution', 'utilities'],
                on_reload=on_reload_callback,
            )
            set_reloader(_hot_reloader)
            logger.log("Hot reload enabled", level="INFO")
        except Exception as e:
            logger.log(f"Failed to enable hot reload: {e}", level="WARNING")
    
    logger.log("Flask application created with WebSocket support", level="INFO")
    
    return app


def get_socketio():
    """Get SocketIO instance."""
    return socketio


if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True, host='0.0.0.0', port=5002, allow_unsafe_werkzeug=True)

