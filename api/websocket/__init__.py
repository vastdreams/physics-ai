# api/websocket/
"""
WebSocket Support for Real-Time Updates.

Inspired by DREAM architecture - real-time data streaming.

First Principle Analysis:
- WebSocket: Bidirectional communication channel
- Events: {simulation_update, cot_update, node_update, performance_update}
- Mathematical foundation: Event-driven architecture, pub/sub patterns
- Architecture: Flask-SocketIO integration with event handlers
"""

from .handlers import setup_websocket_handlers
from .events import WebSocketEvents

__all__ = [
    'setup_websocket_handlers',
    'WebSocketEvents'
]

