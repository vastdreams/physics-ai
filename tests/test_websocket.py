# tests/
"""
WebSocket connection tests.
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestWebSocket(unittest.TestCase):
    """Test WebSocket functionality."""
    
    def test_websocket_import(self):
        """Test WebSocket module imports."""
        try:
            from api.websocket import setup_websocket_handlers, WebSocketEvents
            from api.websocket.events import EventType, WebSocketEvent
            
            self.assertTrue(True)  # If imports succeed, test passes
        except ImportError as e:
            self.fail(f"Failed to import WebSocket modules: {e}")
    
    def test_websocket_events(self):
        """Test WebSocket events."""
        try:
            from api.websocket.events import WebSocketEvents, EventType
            
            events = WebSocketEvents()
            
            # Create event
            event = events.create_event(
                EventType.SIMULATION_UPDATE,
                {"data": "test"}
            )
            
            self.assertIsNotNone(event)
            self.assertEqual(event.event_type, EventType.SIMULATION_UPDATE)
            self.assertEqual(event.data, {"data": "test"})
        except Exception as e:
            self.fail(f"Failed to create WebSocket event: {e}")
    
    def test_event_types(self):
        """Test event type enum."""
        try:
            from api.websocket.events import EventType
            
            # Test all event types exist
            event_types = [
                EventType.SIMULATION_UPDATE,
                EventType.COT_UPDATE,
                EventType.NODE_UPDATE,
                EventType.PERFORMANCE_UPDATE,
                EventType.VECTOR_UPDATE,
                EventType.EVOLUTION_UPDATE,
                EventType.CONTEXT_UPDATE
            ]
            
            for event_type in event_types:
                self.assertIsNotNone(event_type)
                self.assertIsInstance(event_type.value, str)
        except Exception as e:
            self.fail(f"Failed to test event types: {e}")
    
    def test_session_management(self):
        """Test session management."""
        try:
            from api.websocket.events import WebSocketEvents
            
            events = WebSocketEvents()
            
            # Register session
            events.register_session("session_1", {"user": "test"})
            
            # Get active sessions
            active = events.get_active_sessions()
            
            self.assertIn("session_1", active)
            
            # Unregister session
            events.unregister_session("session_1")
            
            active = events.get_active_sessions()
            self.assertNotIn("session_1", active)
        except Exception as e:
            self.fail(f"Failed to test session management: {e}")


if __name__ == '__main__':
    unittest.main()

