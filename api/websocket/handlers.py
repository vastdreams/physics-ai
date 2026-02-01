# api/websocket/
"""
WebSocket Handlers for Real-Time Updates.

Inspired by DREAM architecture - real-time data streaming to dashboards.
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from typing import Any, Dict, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from .events import WebSocketEvents, EventType

logger = SystemLogger()
ws_events = WebSocketEvents()

# Global SocketIO instance (will be initialized in app)
socketio: Optional[SocketIO] = None


def setup_websocket_handlers(app, socketio_instance: SocketIO):
    """
    Setup WebSocket handlers.
    
    Args:
        app: Flask application
        socketio_instance: SocketIO instance
    """
    global socketio
    socketio = socketio_instance
    
    @socketio.on('connect')
    def handle_connect(auth):
        """Handle client connection."""
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(action="WS_CONNECT", level=LogLevel.INFO)
        
        try:
            session_id = request.sid
            ws_events.register_session(session_id)
            
            cot.end_step(step_id, output_data={'session_id': session_id}, validation_passed=True)
            
            logger.log(f"WebSocket client connected: {session_id}", level="INFO")
            emit('connected', {'session_id': session_id})
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            logger.log(f"Error in WebSocket connect: {str(e)}", level="ERROR")
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(action="WS_DISCONNECT", level=LogLevel.INFO)
        
        try:
            session_id = request.sid
            ws_events.unregister_session(session_id)
            
            cot.end_step(step_id, output_data={'session_id': session_id}, validation_passed=True)
            
            logger.log(f"WebSocket client disconnected: {session_id}", level="INFO")
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            logger.log(f"Error in WebSocket disconnect: {str(e)}", level="ERROR")
    
    @socketio.on('subscribe')
    def handle_subscribe(data):
        """Handle subscription to event types."""
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(action="WS_SUBSCRIBE", level=LogLevel.INFO)
        
        try:
            session_id = request.sid
            event_types = data.get('event_types', [])
            
            # Join rooms for each event type
            for event_type in event_types:
                join_room(event_type, sid=session_id)
            
            cot.end_step(step_id, output_data={'event_types': event_types}, validation_passed=True)
            
            logger.log(f"Client subscribed to: {event_types}", level="DEBUG")
            emit('subscribed', {'event_types': event_types})
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            logger.log(f"Error in WebSocket subscribe: {str(e)}", level="ERROR")
    
    @socketio.on('unsubscribe')
    def handle_unsubscribe(data):
        """Handle unsubscription from event types."""
        session_id = request.sid
        event_types = data.get('event_types', [])
        
        for event_type in event_types:
            leave_room(event_type, sid=session_id)
        
        logger.log(f"Client unsubscribed from: {event_types}", level="DEBUG")
        emit('unsubscribed', {'event_types': event_types})
    
    logger.log("WebSocket handlers setup complete", level="INFO")


def broadcast_event(event_type: EventType, data: Dict[str, Any], room: Optional[str] = None) -> None:
    """
    Broadcast event to connected clients.
    
    Args:
        event_type: Event type
        data: Event data
        room: Optional room to broadcast to
    """
    if not socketio:
        logger.log("SocketIO not initialized", level="WARNING")
        return
    
    event = ws_events.create_event(event_type, data)
    
    if room:
        socketio.emit(event_type.value, event.to_dict(), room=room)
    else:
        socketio.emit(event_type.value, event.to_dict(), broadcast=True)
    
    logger.log(f"Event broadcasted: {event_type.value}", level="DEBUG")


# Import request here to avoid circular imports
from flask import request

