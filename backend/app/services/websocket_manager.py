"""WebSocket Manager for handling real-time client connections and broadcasting."""

from typing import List, Dict, Any
from fastapi import WebSocket

class WebSocketManager:
    """Manages WebSocket connections and broadcasting."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept connection and add to active list."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove connection from active list."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        """Send JSON message to all connected clients."""
        # Copy list to avoid issues if connections drop during iteration
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                # If sending fails, assume disconnected
                self.disconnect(connection)

# Global instance
websocket_manager = WebSocketManager()
