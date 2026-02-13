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

import argparse
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    parser = argparse.ArgumentParser(description='Beyond Frontier Development Server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5002, help='Port to listen on (default: 5002)')
    parser.add_argument('--no-hot-reload', action='store_true', help='Disable hot reload')
    parser.add_argument('--debug', action='store_true', default=True, help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Set environment variables
    os.environ['ENABLE_HOT_RELOAD'] = 'false' if args.no_hot_reload else 'true'
    
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                    Beyond Frontier Development Server                   ║
╠═══════════════════════════════════════════════════════════════════╣
║  Hot Reload: {hot_reload:<10}                                      ║
║  Host:       {host:<15}                                      ║
║  Port:       {port:<10}                                           ║
║  Debug:      {debug:<10}                                           ║
╠═══════════════════════════════════════════════════════════════════╣
║  Hot Reload API:                                                   ║
║    GET  /api/v1/hot-reload/status   - Get reload status           ║
║    GET  /api/v1/hot-reload/modules  - List watched modules        ║
║    POST /api/v1/hot-reload/reload   - Trigger manual reload       ║
║    POST /api/v1/hot-reload/toggle   - Toggle auto-reload          ║
╚═══════════════════════════════════════════════════════════════════╝
    """.format(
        hot_reload='Enabled' if not args.no_hot_reload else 'Disabled',
        host=args.host,
        port=args.port,
        debug='Enabled' if args.debug else 'Disabled',
    ))
    
    # Import and run
    from api.app import create_app, socketio
    
    app = create_app(enable_hot_reload=not args.no_hot_reload)
    
    print(f"\n🚀 Starting server at http://{args.host}:{args.port}")
    print("   Press Ctrl+C to stop\n")
    
    socketio.run(
        app,
        debug=args.debug,
        host=args.host,
        port=args.port,
        allow_unsafe_werkzeug=True,
        use_reloader=False,  # We use our own hot reload
    )


if __name__ == '__main__':
    main()
