from fastapi import WebSocket, WebSocketDisconnect, status
from typing import Dict, List, Set
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time notifications"""
    
    def __init__(self):
        # Dictionary mapping user_id to list of their active WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Set of all connected websockets for broadcast operations
        self.all_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        
        # Add to user-specific connections
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        
        # Add to all connections set
        self.all_connections.add(websocket)
        
        logger.info(f"✅ WebSocket connected for user: {user_id}")
        logger.info(f"📊 Total active connections: {len(self.all_connections)}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection",
            "status": "connected",
            "message": "Successfully connected to notification service",
            "timestamp": datetime.now().isoformat()
        }, websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection"""
        # Remove from user-specific connections
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            
            # Clean up empty user entries
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        # Remove from all connections
        self.all_connections.discard(websocket)
        
        logger.info(f"❌ WebSocket disconnected for user: {user_id}")
        logger.info(f"📊 Total active connections: {len(self.all_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"❌ Error sending personal message: {e}")
    
    async def send_to_user(self, message: dict, user_id: str):
        """Send a message to all connections of a specific user"""
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"❌ Error sending to user {user_id}: {e}")
                    disconnected.append(connection)
            
            # Clean up disconnected websockets
            for conn in disconnected:
                self.disconnect(conn, user_id)
    
    async def broadcast(self, message: dict):
        """Send a message to all connected clients"""
        disconnected = []
        for connection in self.all_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"❌ Error broadcasting message: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected websockets
        for conn in disconnected:
            # Find and remove from user connections
            for user_id, connections in list(self.active_connections.items()):
                if conn in connections:
                    self.disconnect(conn, user_id)
                    break
    
    def get_user_connection_count(self, user_id: str) -> int:
        """Get the number of active connections for a user"""
        return len(self.active_connections.get(user_id, []))
    
    def get_total_connections(self) -> int:
        """Get total number of active connections"""
        return len(self.all_connections)
    
    def is_user_connected(self, user_id: str) -> bool:
        """Check if a user has any active connections"""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0


# Global connection manager instance
manager = ConnectionManager()


async def send_notification(user_id: str, notification_data: dict):
    """
    Helper function to send a notification to a specific user
    
    Args:
        user_id: The user ID to send the notification to
        notification_data: Dictionary containing notification details
    """
    message = {
        "type": "notification",
        "data": {
            "id": notification_data.get("id", f"notif_{datetime.now().timestamp()}"),
            "type": notification_data.get("notification_type", "system"),
            "title": notification_data.get("title", "Notification"),
            "message": notification_data.get("message", ""),
            "task_id": notification_data.get("task_id"),
            "priority": notification_data.get("priority", "medium"),
            "timestamp": notification_data.get("timestamp", datetime.now().isoformat()),
        }
    }
    
    await manager.send_to_user(message, user_id)
    logger.info(f"📨 Notification sent to user {user_id}: {notification_data.get('title')}")