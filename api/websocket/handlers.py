"""
PATH: api/websocket/handlers.py
PURPOSE: WebSocket handlers for real-time client communication.
"""

from typing import Any, Dict, Optional

from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room

from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel

from .events import EventType, WebSocketEvents

_logger = SystemLogger()
_ws_events = WebSocketEvents()

# Global SocketIO instance (initialised in setup_websocket_handlers)
socketio: Optional[SocketIO] = None


def setup_websocket_handlers(app: Any, socketio_instance: SocketIO) -> None:
    """
    Register WebSocket event handlers on the SocketIO instance.

    Args:
        app: Flask application.
        socketio_instance: SocketIO instance to attach handlers to.
    """
    global socketio
    socketio = socketio_instance

    @socketio.on("connect")
    def handle_connect(auth: Optional[Dict[str, Any]] = None) -> None:
        """Handle client connection."""
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(action="WS_CONNECT", level=LogLevel.INFO)

        try:
            session_id: str = request.sid
            _ws_events.register_session(session_id)

            cot.end_step(step_id, output_data={"session_id": session_id}, validation_passed=True)

            _logger.log(f"WebSocket client connected: {session_id}", level="INFO")
            emit("connected", {"session_id": session_id})
        except Exception as e:
            cot.end_step(step_id, output_data={"error": str(e)}, validation_passed=False)
            _logger.log(f"Error in WebSocket connect: {e}", level="ERROR")

    @socketio.on("disconnect")
    def handle_disconnect() -> None:
        """Handle client disconnection."""
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(action="WS_DISCONNECT", level=LogLevel.INFO)

        try:
            session_id: str = request.sid
            _ws_events.unregister_session(session_id)

            cot.end_step(step_id, output_data={"session_id": session_id}, validation_passed=True)

            _logger.log(f"WebSocket client disconnected: {session_id}", level="INFO")
        except Exception as e:
            cot.end_step(step_id, output_data={"error": str(e)}, validation_passed=False)
            _logger.log(f"Error in WebSocket disconnect: {e}", level="ERROR")

    @socketio.on("subscribe")
    def handle_subscribe(data: Dict[str, Any]) -> None:
        """Handle subscription to event types."""
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(action="WS_SUBSCRIBE", level=LogLevel.INFO)

        try:
            session_id: str = request.sid
            event_types = data.get("event_types", [])

            for event_type in event_types:
                join_room(event_type, sid=session_id)

            cot.end_step(step_id, output_data={"event_types": event_types}, validation_passed=True)

            _logger.log(f"Client subscribed to: {event_types}", level="DEBUG")
            emit("subscribed", {"event_types": event_types})
        except Exception as e:
            cot.end_step(step_id, output_data={"error": str(e)}, validation_passed=False)
            _logger.log(f"Error in WebSocket subscribe: {e}", level="ERROR")

    @socketio.on("unsubscribe")
    def handle_unsubscribe(data: Dict[str, Any]) -> None:
        """Handle unsubscription from event types."""
        session_id: str = request.sid
        event_types = data.get("event_types", [])

        for event_type in event_types:
            leave_room(event_type, sid=session_id)

        _logger.log(f"Client unsubscribed from: {event_types}", level="DEBUG")
        emit("unsubscribed", {"event_types": event_types})

    _logger.log("WebSocket handlers setup complete", level="INFO")


def broadcast_event(
    event_type: EventType,
    data: Dict[str, Any],
    room: Optional[str] = None,
) -> None:
    """
    Broadcast an event to connected WebSocket clients.

    Args:
        event_type: The event type to emit.
        data: Payload to include with the event.
        room: Optional room to limit the broadcast.
    """
    if not socketio:
        _logger.log("SocketIO not initialized", level="WARNING")
        return

    event = _ws_events.create_event(event_type, data)

    if room:
        socketio.emit(event_type.value, event.to_dict(), room=room)
    else:
        socketio.emit(event_type.value, event.to_dict(), broadcast=True)

    _logger.log(f"Event broadcasted: {event_type.value}", level="DEBUG")
