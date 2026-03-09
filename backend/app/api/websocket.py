from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import asyncio
from ..services.websocket_manager import websocket_manager
from ..utils.logger import logger

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time call status updates.

    Usage:
        ws://localhost:8000/ws
        ws://localhost:8000/ws?client_id=unique-client-id

    Message Types Received:
        - ping: Heartbeat to keep connection alive

    Message Types Sent:
        - connection.established: Sent when connection is established
        - pong: Response to ping
        - call.initiated: Call has been initiated
        - call.ringing: Phone is ringing
        - call.answered: Call was answered
        - call.in_progress: Call is in progress
        - call.completed: Call completed successfully
        - call.busy: Recipient was busy
        - call.failed: Call failed
        - call.no_answer: No one answered
        - incoming.call: Incoming call notification
    """
    await websocket_manager.connect(websocket, client_id)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            message_type = data.get("type")

            if message_type == "ping":
                # Handle ping/heartbeat
                await websocket_manager.handle_ping(websocket)

            elif message_type == "subscribe":
                # Client wants to subscribe to updates
                logger.info(f"Client {client_id} subscribed to updates")
                await websocket_manager.send_personal_message(
                    websocket,
                    {
                        "type": "subscribed",
                        "timestamp": "",
                        "data": {"message": "Subscribed to call updates"}
                    }
                )

            elif message_type == "unsubscribe":
                # Client wants to unsubscribe
                logger.info(f"Client {client_id} unsubscribed from updates")
                await websocket_manager.send_personal_message(
                    websocket,
                    {
                        "type": "unsubscribed",
                        "timestamp": "",
                        "data": {"message": "Unsubscribed from call updates"}
                    }
                )

            else:
                # Unknown message type
                logger.warning(f"Unknown WebSocket message type: {message_type}")
                await websocket_manager.send_personal_message(
                    websocket,
                    {
                        "type": "error",
                        "timestamp": "",
                        "data": {"message": f"Unknown message type: {message_type}"}
                    }
                )

    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        logger.info(f"Client {client_id} disconnected normally")

    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {str(e)}")
        websocket_manager.disconnect(websocket)


@router.get("/ws/connections")
async def get_websocket_connections():
    """
    Get information about active WebSocket connections.
    Useful for monitoring and debugging.
    """
    return {
        "active_connections": websocket_manager.get_connection_count(),
        "connections": websocket_manager.get_connection_info()
    }
