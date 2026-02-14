"""
PATH: api/websocket/events.py
PURPOSE: WebSocket event types and data structures for real-time updates.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


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
    """Represents a single WebSocket event with metadata."""

    event_type: EventType
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    session_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a JSON-serializable dictionary."""
        return {
            "event_type": self.event_type.value,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
        }


class WebSocketEvents:
    """
    WebSocket event manager.

    Responsibilities:
    - Event creation
    - Session registration and tracking
    """

    def __init__(self) -> None:
        """Initialise the event manager with an empty session registry."""
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    def create_event(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        session_id: Optional[str] = None,
    ) -> WebSocketEvent:
        """
        Create a new WebSocket event.

        Args:
            event_type: The type of event.
            data: Payload for the event.
            session_id: Optional originating session ID.

        Returns:
            A populated ``WebSocketEvent`` instance.
        """
        return WebSocketEvent(
            event_type=event_type,
            data=data,
            session_id=session_id,
        )

    def register_session(self, session_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Register an active WebSocket session."""
        self.active_sessions[session_id] = metadata or {}

    def unregister_session(self, session_id: str) -> None:
        """Remove a session from the active registry."""
        self.active_sessions.pop(session_id, None)

    def get_active_sessions(self) -> List[str]:
        """Return a list of active session IDs."""
        return list(self.active_sessions.keys())
