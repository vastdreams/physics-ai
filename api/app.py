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
    
    # Enable CORS — configurable via CORS_ORIGINS env var (comma-separated)
    _cors_origins = os.getenv("CORS_ORIGINS", "*")
    CORS(app, origins=[o.strip() for o in _cors_origins.split(",")])
    
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
    from api.middleware.rate_limit import RateLimitMiddleware
    
    LoggingMiddleware.setup(app)
    ValidationMiddleware.setup(app)
    RateLimitMiddleware.setup(app, global_limit=120, global_window=60)
    # Note: Auth is now handled via decorators (@require_auth) in api/v1/auth.py
    # Note: Per-route rate limits available via @rate_limit() and @rate_limit_auth decorators
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        hot_reload_status = "enabled" if _hot_reloader and _hot_reloader._running else "disabled"
        return {
            'status': 'healthy',
            'hot_reload': hot_reload_status,
            'version': os.getenv('APP_VERSION', 'dev'),
            'build': os.getenv('BUILD_SHA', 'local'),
        }, 200

    # ── System-wide stats endpoint (used by Dashboard) ──────────
    import time as _time
    _app_start_time = _time.time()

    @app.route('/api/v1/system/stats', methods=['GET'])
    def system_stats():
        """Aggregated platform statistics for the Dashboard."""
        from api.v1.rules import rule_engine
        stats = {}
        # Rules
        try:
            rules_list = rule_engine.list_rules()
            stats['rules'] = len(rules_list)
        except Exception:
            stats['rules'] = 0
        # Knowledge
        try:
            from physics.knowledge import get_knowledge_graph
            graph = get_knowledge_graph()
            stats['knowledge_count'] = graph.get('statistics', {}).get('total_nodes', 0)
        except Exception:
            stats['knowledge_count'] = 0
        # Simulations — no persistent counter yet, return 0
        stats['simulations'] = 0
        # Evolution
        try:
            from ai.evolution.tracker import EvolutionTracker
            tracker = EvolutionTracker()
            stats['evolutions'] = len(tracker.history) if hasattr(tracker, 'history') else 0
        except Exception:
            stats['evolutions'] = 0
        # Uptime
        elapsed = _time.time() - _app_start_time
        h, rem = divmod(int(elapsed), 3600)
        m, _ = divmod(rem, 60)
        stats['uptime'] = f"{h}h {m}m"
        return stats, 200
    
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
    socketio.run(app, debug=True, host='0.0.0.0', port=int(os.getenv('PORT', '5002')), allow_unsafe_werkzeug=True)

