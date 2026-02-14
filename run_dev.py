#!/usr/bin/env python3
"""
PATH: run_dev.py
PURPOSE: Development server runner with hot reload enabled

WHY: Provides a simple way to start the Beyond Frontier server with auto-reload
     functionality for rapid development.

USAGE:
    python run_dev.py                    # Start with default settings
    python run_dev.py --port 5002        # Custom port
    python run_dev.py --no-hot-reload    # Disable hot reload
    python run_dev.py --host 0.0.0.0     # Bind to all interfaces
"""

from __future__ import annotations

import argparse
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_DEFAULT_HOST = "127.0.0.1"
_DEFAULT_PORT = 5002


def main() -> None:
    """Parse arguments and start the development server."""
    parser = argparse.ArgumentParser(description="Beyond Frontier Development Server")
    parser.add_argument(
        "--host", default=_DEFAULT_HOST, help=f"Host to bind to (default: {_DEFAULT_HOST})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=_DEFAULT_PORT,
        help=f"Port to listen on (default: {_DEFAULT_PORT})",
    )
    parser.add_argument("--no-hot-reload", action="store_true", help="Disable hot reload")
    parser.add_argument("--debug", action="store_true", default=True, help="Enable debug mode")

    args = parser.parse_args()

    os.environ["ENABLE_HOT_RELOAD"] = "false" if args.no_hot_reload else "true"

    hot_reload = "Enabled" if not args.no_hot_reload else "Disabled"
    debug = "Enabled" if args.debug else "Disabled"

    print(
        f"\n"
        f"{'=' * 67}\n"
        f"  Beyond Frontier Development Server\n"
        f"{'=' * 67}\n"
        f"  Hot Reload: {hot_reload:<10}\n"
        f"  Host:       {args.host:<15}\n"
        f"  Port:       {args.port:<10}\n"
        f"  Debug:      {debug:<10}\n"
        f"{'-' * 67}\n"
        f"  Hot Reload API:\n"
        f"    GET  /api/v1/hot-reload/status   - Get reload status\n"
        f"    GET  /api/v1/hot-reload/modules  - List watched modules\n"
        f"    POST /api/v1/hot-reload/reload   - Trigger manual reload\n"
        f"    POST /api/v1/hot-reload/toggle   - Toggle auto-reload\n"
        f"{'=' * 67}\n"
    )

    from api.app import create_app, socketio

    app = create_app(enable_hot_reload=not args.no_hot_reload)

    print(f"\nStarting server at http://{args.host}:{args.port}")
    print("   Press Ctrl+C to stop\n")

    socketio.run(
        app,
        debug=args.debug,
        host=args.host,
        port=args.port,
        allow_unsafe_werkzeug=True,
        use_reloader=False,  # We use our own hot reload
    )


if __name__ == "__main__":
    main()
