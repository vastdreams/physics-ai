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

import os
import secrets

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

from api.v1 import api_v1
from api.v1.substrate import init_substrate
from api.websocket.handlers import setup_websocket_handlers
from loggers.system_logger import SystemLogger
from substrate.main import create_physics_ai

_logger = SystemLogger()

# Initialize SocketIO
socketio = SocketIO(cors_allowed_origins="*")

# Global hot reloader reference
_hot_reloader = None


def create_app(enable_hot_reload: bool = None) -> Flask:
    """
    Create and configure Flask application with WebSocket support.

    Args:
        enable_hot_reload: Enable hot reload (default: True in debug mode).

    Returns:
        Flask application instance.
    """
    global _hot_reloader

    app = Flask(__name__)

    # SECURITY: Use environment variable for secret key, with secure fallback
    app.config["SECRET_KEY"] = (
        os.getenv("FLASK_SECRET_KEY")
        or os.getenv("SECRET_KEY")
        or secrets.token_hex(32)
    )

    # Enable CORS — configurable via CORS_ORIGINS env var (comma-separated)
    _cors_origins = os.getenv("CORS_ORIGINS", "*")
    CORS(app, origins=[o.strip() for o in _cors_origins.split(",")])

    # Initialize SocketIO with app
    socketio.init_app(app)

    # Register blueprints
    app.register_blueprint(api_v1)

    from api.v1.hot_reload import hot_reload_bp, set_reloader
    app.register_blueprint(hot_reload_bp)

    # Initialize core PhysicsAI and wire substrate API
    physics_ai = create_physics_ai()
    init_substrate(physics_ai)

    # Setup WebSocket handlers
    setup_websocket_handlers(app, socketio)

    # Setup middleware
    from api.middleware.logging import LoggingMiddleware
    from api.middleware.rate_limit import RateLimitMiddleware
    from api.middleware.validation import ValidationMiddleware

    LoggingMiddleware.setup(app)
    ValidationMiddleware.setup(app)
    RateLimitMiddleware.setup(app, global_limit=120, global_window=60)

    # Health check endpoint
    @app.route("/health", methods=["GET"])
    def health() -> tuple:
        """Return application health status."""
        hot_reload_status = "enabled" if _hot_reloader and _hot_reloader._running else "disabled"
        return {
            "status": "healthy",
            "hot_reload": hot_reload_status,
            "version": os.getenv("APP_VERSION", "dev"),
            "build": os.getenv("BUILD_SHA", "local"),
        }, 200

    # System-wide stats endpoint (used by Dashboard)
    import time as _time

    _app_start_time = _time.time()

    @app.route("/api/v1/system/stats", methods=["GET"])
    def system_stats() -> tuple:
        """Aggregated platform statistics for the Dashboard."""
        from api.v1.rules import rule_engine

        stats: dict = {}

        # Rules
        try:
            stats["rules"] = len(rule_engine.list_rules())
        except Exception:
            stats["rules"] = 0

        # Knowledge
        try:
            from physics.knowledge import get_knowledge_graph

            graph = get_knowledge_graph()
            stats["knowledge_count"] = graph.get("statistics", {}).get("total_nodes", 0)
        except Exception:
            stats["knowledge_count"] = 0

        # Simulations — no persistent counter yet
        stats["simulations"] = 0

        # Evolution
        try:
            from ai.evolution.tracker import EvolutionTracker

            tracker = EvolutionTracker()
            stats["evolutions"] = len(tracker.history) if hasattr(tracker, "history") else 0
        except Exception:
            stats["evolutions"] = 0

        # Uptime
        elapsed = _time.time() - _app_start_time
        h, rem = divmod(int(elapsed), 3600)
        m, _ = divmod(rem, 60)
        stats["uptime"] = f"{h}h {m}m"

        return stats, 200

    # Initialize hot reload if enabled
    if enable_hot_reload is None:
        enable_hot_reload = os.getenv("ENABLE_HOT_RELOAD", "true").lower() == "true"

    if enable_hot_reload:
        try:
            from utilities.hot_reload import start_hot_reload

            def on_reload_callback(event: object) -> None:
                """Emit WebSocket event when a module reloads."""
                if event.success:
                    socketio.emit("module_reloaded", {
                        "module": event.module_name,
                        "timestamp": event.timestamp.isoformat(),
                        "reload_time_ms": event.reload_time_ms,
                    })
                else:
                    socketio.emit("module_reload_failed", {
                        "module": event.module_name,
                        "error": event.error[:200] if event.error else None,
                    })

            _hot_reloader = start_hot_reload(
                watch_dirs=["physics", "substrate", "api", "core", "rules", "evolution", "utilities"],
                on_reload=on_reload_callback,
            )
            set_reloader(_hot_reloader)
            _logger.log("Hot reload enabled", level="INFO")
        except Exception as e:
            _logger.log(f"Failed to enable hot reload: {e}", level="WARNING")

    _logger.log("Flask application created with WebSocket support", level="INFO")

    return app


def get_socketio() -> SocketIO:
    """Get the global SocketIO instance."""
    return socketio


if __name__ == "__main__":
    app = create_app()
    socketio.run(
        app,
        debug=True,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5002")),
        allow_unsafe_werkzeug=True,
    )
