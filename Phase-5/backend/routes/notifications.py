from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlmodel import Session
from typing import Optional
import logging
import asyncio
from datetime import datetime

from ws_manager import manager, send_notification
from database import get_session
from models.user import User
# from routes.auth import get_current_user_ws  # Not needed - auth disabled for development

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/notifications/{user_id}")
async def websocket_notifications_endpoint(
    websocket: WebSocket,
    user_id: str,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time notifications
    
    Accepts connections at: ws://localhost:8000/ws/notifications/{user_id}?token={jwt_token}
    
    Messages from server:
    - Connection confirmation
    - Task notifications (created, updated, deleted, completed)
    - System notifications
    - Ping/pong for keepalive
    
    Messages to server:
    - pong (response to ping)
    - Any custom messages
    """
    
    # For development: Accept connection without authentication
    # TODO: Enable authentication in production
    # if not token:
    #     await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    #     return
    
    try:
        # Connect the websocket
        await manager.connect(websocket, user_id)
        
        # Send initial connection success message
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "user_id": user_id,
            "message": "WebSocket connection established successfully",
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection alive and handle incoming messages
        try:
            while True:
                # Wait for messages from client
                data = await websocket.receive_text()
                
                try:
                    message = eval(data) if isinstance(data, str) else data
                    
                    # Handle different message types from client
                    if isinstance(message, dict):
                        msg_type = message.get("type")
                        
                        if msg_type == "pong":
                            # Client responded to ping
                            logger.debug(f"Received pong from user {user_id}")
                        
                        elif msg_type == "subscribe":
                            # Client wants to subscribe to specific notification types
                            logger.info(f"User {user_id} subscribed to: {message.get('topics', [])}")
                        
                        else:
                            # Echo back any other message (for testing)
                            await websocket.send_json({
                                "type": "echo",
                                "original": message,
                                "timestamp": datetime.now().isoformat()
                            })
                    
                except Exception as parse_error:
                    logger.error(f"Error parsing message: {parse_error}")
                
        except WebSocketDisconnect:
            logger.info(f"User {user_id} disconnected normally")
        except Exception as e:
            logger.error(f"Error in WebSocket connection for user {user_id}: {e}")
        finally:
            # Clean up connection
            manager.disconnect(websocket, user_id)
    
    except Exception as e:
        logger.error(f"Failed to establish WebSocket connection: {e}")
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except:
            pass


@router.get("/ws/status")
async def websocket_status():
    """Get WebSocket server status and statistics"""
    return {
        "status": "operational",
        "total_connections": manager.get_total_connections(),
        "timestamp": datetime.now().isoformat()
    }


@router.get("/ws/users/{user_id}/status")
async def user_websocket_status(user_id: str):
    """Check if a specific user has active WebSocket connections"""
    return {
        "user_id": user_id,
        "connected": manager.is_user_connected(user_id),
        "connection_count": manager.get_user_connection_count(user_id),
        "timestamp": datetime.now().isoformat()
    }


@router.post("/ws/test-notification/{user_id}")
async def send_test_notification(user_id: str):
    """
    Send a test notification to a specific user (for testing)
    
    This endpoint allows you to test the notification system
    """
    test_notification = {
        "id": f"test_{datetime.now().timestamp()}",
        "notification_type": "system",
        "title": "Test Notification",
        "message": "This is a test notification from the server",
        "priority": "medium",
        "timestamp": datetime.now().isoformat()
    }
    
    await send_notification(user_id, test_notification)
    
    return {
        "success": True,
        "message": f"Test notification sent to user {user_id}",
        "notification": test_notification
    }


# Background task to send periodic pings (keepalive)
async def ping_connections():
    """Send periodic ping to all connections to keep them alive"""
    while True:
        await asyncio.sleep(30)  # Ping every 30 seconds
        
        if manager.get_total_connections() > 0:
            await manager.broadcast({
                "type": "ping",
                "timestamp": datetime.now().isoformat()
            })
            logger.debug(f"Sent ping to {manager.get_total_connections()} connections")


# Start the ping task when the app starts
@router.on_event("startup")
async def startup_event():
    """Start background tasks"""
    logger.info("Starting WebSocket background tasks")
    # Note: In production, use proper background task management
    # asyncio.create_task(ping_connections())