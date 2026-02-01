# api/websocket/
"""
WebSocket Events Definition.

Event types and data structures for real-time updates.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class EventType(Enum):
    """WebSocket event types."""
    SIMULATION_UPDATE = "simulation_update"
    COT_UPDATE = "cot_update"
    NODE_UPDATE = "node_update"
    PERFORMANCE_UPDATE = "performance_update"
    VECTOR_UPDATE = "vector_update"
    EVOLUTION_UPDATE = "evolution_update"
    CONTEXT_UPDATE = "context_update"


@dataclass
class WebSocketEvent:
    """Represents a WebSocket event."""
    event_type: EventType
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'event_type': self.event_type.value,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'session_id': self.session_id
        }


class WebSocketEvents:
    """
    WebSocket event manager.
    
    Features:
    - Event creation
    - Event broadcasting
    - Session management
    """
    
    def __init__(self):
        """Initialize WebSocket events manager."""
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_event(self,
                    event_type: EventType,
                    data: Dict[str, Any],
                    session_id: Optional[str] = None) -> WebSocketEvent:
        """
        Create WebSocket event.
        
        Args:
            event_type: Event type
            data: Event data
            session_id: Optional session ID
            
        Returns:
            WebSocketEvent instance
        """
        return WebSocketEvent(
            event_type=event_type,
            data=data,
            session_id=session_id
        )
    
    def register_session(self, session_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Register active session."""
        self.active_sessions[session_id] = metadata or {}
    
    def unregister_session(self, session_id: str) -> None:
        """Unregister session."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs."""
        return list(self.active_sessions.keys())

