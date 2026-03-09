from fastapi import WebSocket
from typing import List, Dict, Any
from datetime import datetime
import json
import asyncio
from ..utils.logger import logger


class ConnectionManager:
    """
    Manages WebSocket connections and broadcasts messages to connected clients.
    """

    def __init__(self):
        """Initialize the connection manager with an empty connection pool."""
        self.active_connections: List[WebSocket] = []
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, client_id: str = None):
        """
        Accept and register a new WebSocket connection.

        Args:
            websocket: The WebSocket connection to accept
            client_id: Optional client identifier
        """
        await websocket.accept()
        self.active_connections.append(websocket)

        # Store metadata about the connection
        self.connection_metadata[websocket] = {
            "client_id": client_id,
            "connected_at": datetime.utcnow().isoformat(),
            "last_ping": datetime.utcnow().isoformat()
        }

        logger.info(f"WebSocket client connected. Total connections: {len(self.active_connections)}")

        # Send connection confirmation
        await self.send_personal_message(
            websocket,
            {
                "type": "connection.established",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "message": "Connected to Twilio Call Server",
                    "client_id": client_id
                }
            }
        )

    def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection from the pool.

        Args:
            websocket: The WebSocket connection to remove
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            client_info = self.connection_metadata.pop(websocket, {})
            logger.info(
                f"WebSocket client disconnected. "
                f"Client ID: {client_info.get('client_id', 'unknown')}. "
                f"Remaining connections: {len(self.active_connections)}"
            )

    async def send_personal_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """
        Send a message to a specific WebSocket connection.

        Args:
            websocket: The WebSocket connection to send to
            message: Dictionary to send as JSON
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {str(e)}")
            self.disconnect(websocket)

    async def broadcast(self, message: Dict[str, Any], exclude: WebSocket = None):
        """
        Broadcast a message to all connected clients.

        Args:
            message: Dictionary to send as JSON
            exclude: Optional WebSocket connection to exclude from broadcast
        """
        if not self.active_connections:
            logger.debug("No active connections to broadcast to")
            return

        # Track disconnected clients
        disconnected = []

        for connection in self.active_connections:
            if connection == exclude:
                continue

            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {str(e)}")
                disconnected.append(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

        if message.get("type") != "ping":  # Don't log ping messages
            logger.debug(
                f"Broadcasted message type '{message.get('type')}' to "
                f"{len(self.active_connections)} clients"
            )

    async def handle_ping(self, websocket: WebSocket):
        """
        Handle ping message from client.

        Args:
            websocket: The WebSocket connection that sent the ping
        """
        if websocket in self.connection_metadata:
            self.connection_metadata[websocket]["last_ping"] = datetime.utcnow().isoformat()

        await self.send_personal_message(
            websocket,
            {
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {}
            }
        )

    async def broadcast_call_event(
        self,
        event_type: str,
        call_sid: str,
        status: str,
        direction: str,
        from_number: str,
        to_number: str,
        duration: int = None,
        error: str = None
    ):
        """
        Broadcast a call event to all connected clients.

        Args:
            event_type: Type of event (e.g., 'call.initiated', 'call.completed')
            call_sid: Twilio call SID
            status: Call status
            direction: Call direction (inbound/outbound)
            from_number: Caller number
            to_number: Recipient number
            duration: Call duration in seconds (optional)
            error: Error message if any (optional)
        """
        message = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "callSid": call_sid,
                "status": status,
                "direction": direction,
                "from": from_number,
                "to": to_number
            }
        }

        if duration is not None:
            message["data"]["duration"] = duration

        if error:
            message["data"]["error"] = error

        await self.broadcast(message)

    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self.active_connections)

    def get_connection_info(self) -> List[Dict[str, Any]]:
        """Get information about all active connections."""
        return [
            {
                "client_id": metadata.get("client_id"),
                "connected_at": metadata.get("connected_at"),
                "last_ping": metadata.get("last_ping")
            }
            for metadata in self.connection_metadata.values()
        ]


# Global instance
websocket_manager = ConnectionManager()
