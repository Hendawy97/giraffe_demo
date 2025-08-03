"""
WebSocket API endpoints for real-time collaboration.
"""

import json
import uuid
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.api.deps import get_db
from app.core.security import verify_token
from app.models.user import User
from app.models.project import Project, EditHistory


router = APIRouter()
logger = structlog.get_logger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time collaboration."""
    
    def __init__(self):
        # Dict[project_id, Dict[user_id, WebSocket]]
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        # Track user sessions
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def connect(
        self, 
        websocket: WebSocket, 
        project_id: str, 
        user_id: str,
        user_info: Dict[str, Any]
    ):
        """
        Connect a user to a project room.
        
        Args:
            websocket: WebSocket connection
            project_id: Project ID
            user_id: User ID
            user_info: User information for presence
        """
        await websocket.accept()
        
        if project_id not in self.active_connections:
            self.active_connections[project_id] = {}
        
        self.active_connections[project_id][user_id] = websocket
        
        # Track user session
        if project_id not in self.user_sessions:
            self.user_sessions[project_id] = {}
        
        self.user_sessions[project_id][user_id] = {
            "user_info": user_info,
            "connected_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
        }
        
        # Notify others about user joining
        await self.broadcast_to_project(
            project_id,
            {
                "type": "user_joined",
                "user_id": user_id,
                "user_info": user_info,
                "timestamp": datetime.utcnow().isoformat(),
            },
            exclude_user_id=user_id
        )
        
        # Send current active users to the new connection
        active_users = [
            {
                "user_id": uid,
                "user_info": session["user_info"],
                "connected_at": session["connected_at"],
            }
            for uid, session in self.user_sessions.get(project_id, {}).items()
            if uid != user_id
        ]
        
        await self.send_personal_message(
            websocket,
            {
                "type": "active_users",
                "users": active_users,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        
        logger.info(
            "User connected to project",
            project_id=project_id,
            user_id=user_id,
            total_connections=len(self.active_connections.get(project_id, {}))
        )
    
    def disconnect(self, project_id: str, user_id: str):
        """
        Disconnect a user from a project room.
        
        Args:
            project_id: Project ID
            user_id: User ID
        """
        if project_id in self.active_connections:
            self.active_connections[project_id].pop(user_id, None)
            
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
        
        if project_id in self.user_sessions:
            user_info = self.user_sessions[project_id].pop(user_id, {}).get("user_info")
            
            if not self.user_sessions[project_id]:
                del self.user_sessions[project_id]
            
            # Notify others about user leaving
            if user_info:
                asyncio.create_task(
                    self.broadcast_to_project(
                        project_id,
                        {
                            "type": "user_left",
                            "user_id": user_id,
                            "user_info": user_info,
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                        exclude_user_id=user_id
                    )
                )
        
        logger.info(
            "User disconnected from project",
            project_id=project_id,
            user_id=user_id,
            remaining_connections=len(self.active_connections.get(project_id, {}))
        )
    
    async def send_personal_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """
        Send a message to a specific WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            message: Message to send
        """
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error("Failed to send personal message", error=str(e))
    
    async def broadcast_to_project(
        self, 
        project_id: str, 
        message: Dict[str, Any],
        exclude_user_id: Optional[str] = None
    ):
        """
        Broadcast a message to all users in a project room.
        
        Args:
            project_id: Project ID
            message: Message to broadcast
            exclude_user_id: User ID to exclude from broadcast
        """
        if project_id not in self.active_connections:
            return
        
        message_text = json.dumps(message)
        failed_connections = []
        
        for user_id, websocket in self.active_connections[project_id].items():
            if exclude_user_id and user_id == exclude_user_id:
                continue
                
            try:
                await websocket.send_text(message_text)
            except Exception as e:
                logger.error(
                    "Failed to send message to user",
                    project_id=project_id,
                    user_id=user_id,
                    error=str(e)
                )
                failed_connections.append(user_id)
        
        # Clean up failed connections
        for user_id in failed_connections:
            self.disconnect(project_id, user_id)
    
    def get_project_users(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Get list of active users in a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List[Dict[str, Any]]: List of active users
        """
        if project_id not in self.user_sessions:
            return []
        
        return [
            {
                "user_id": user_id,
                "user_info": session["user_info"],
                "connected_at": session["connected_at"],
                "last_activity": session["last_activity"],
            }
            for user_id, session in self.user_sessions[project_id].items()
        ]


# Global connection manager instance
manager = ConnectionManager()


async def get_websocket_user(
    token: str = Query(..., description="JWT access token"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Authenticate user for WebSocket connection.
    
    Args:
        token: JWT access token
        db: Database session
        
    Returns:
        User: Authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        user_id_str = verify_token(token, token_type="access")
        user_id = uuid.UUID(user_id_str)
        
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or inactive user"
            )
        
        return user
        
    except Exception as e:
        logger.error("WebSocket authentication failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


@router.websocket("/projects/{project_id}")
async def project_websocket(
    websocket: WebSocket,
    project_id: uuid.UUID,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """
    WebSocket endpoint for real-time project collaboration.
    
    Args:
        websocket: WebSocket connection
        project_id: Project ID
        token: JWT access token
        db: Database session
    """
    try:
        # Authenticate user
        user = await get_websocket_user(token, db)
        
        # Check project access
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        
        if not project:
            await websocket.close(code=4404, reason="Project not found")
            return
        
        if not project.is_public and project.owner_id != user.id:
            await websocket.close(code=4403, reason="Project access denied")
            return
        
        # Connect user to project room
        user_info = {
            "id": str(user.id),
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
        }
        
        await manager.connect(
            websocket=websocket,
            project_id=str(project_id),
            user_id=str(user.id),
            user_info=user_info
        )
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                
                try:
                    message = json.loads(data)
                    message_type = message.get("type")
                    
                    # Update user activity
                    if str(project_id) in manager.user_sessions:
                        if str(user.id) in manager.user_sessions[str(project_id)]:
                            manager.user_sessions[str(project_id)][str(user.id)]["last_activity"] = datetime.utcnow().isoformat()
                    
                    if message_type == "edit":
                        # Handle edit operations
                        await handle_edit_message(
                            project_id=project_id,
                            user_id=user.id,
                            message=message,
                            db=db
                        )
                        
                        # Broadcast edit to other users
                        await manager.broadcast_to_project(
                            str(project_id),
                            {
                                **message,
                                "user_id": str(user.id),
                                "user_info": user_info,
                                "timestamp": datetime.utcnow().isoformat(),
                            },
                            exclude_user_id=str(user.id)
                        )
                    
                    elif message_type == "cursor":
                        # Handle cursor movement
                        await manager.broadcast_to_project(
                            str(project_id),
                            {
                                **message,
                                "user_id": str(user.id),
                                "user_info": user_info,
                                "timestamp": datetime.utcnow().isoformat(),
                            },
                            exclude_user_id=str(user.id)
                        )
                    
                    elif message_type == "ping":
                        # Handle ping/heartbeat
                        await manager.send_personal_message(
                            websocket,
                            {
                                "type": "pong",
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        )
                    
                    else:
                        logger.warning(
                            "Unknown message type",
                            message_type=message_type,
                            user_id=str(user.id),
                            project_id=str(project_id)
                        )
                
                except json.JSONDecodeError:
                    logger.error("Invalid JSON received", user_id=str(user.id))
                    await manager.send_personal_message(
                        websocket,
                        {
                            "type": "error",
                            "message": "Invalid JSON format",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )
                
        except WebSocketDisconnect:
            logger.info("WebSocket disconnected", user_id=str(user.id), project_id=str(project_id))
        
        finally:
            manager.disconnect(str(project_id), str(user.id))
    
    except Exception as e:
        logger.error("WebSocket connection error", error=str(e))
        try:
            await websocket.close(code=4500, reason="Internal server error")
        except:
            pass


async def handle_edit_message(
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    message: Dict[str, Any],
    db: AsyncSession,
):
    """
    Handle edit messages and save to edit history.
    
    Args:
        project_id: Project ID
        user_id: User ID who made the edit
        message: Edit message data
        db: Database session
    """
    try:
        edit_history = EditHistory(
            project_id=project_id,
            user_id=user_id,
            action=message.get("action", "unknown"),
            object_type=message.get("object_type", "unknown"),
            object_id=message.get("object_id"),
            changes=message.get("changes"),
            previous_data=message.get("previous_data"),
            new_data=message.get("new_data"),
            session_id=message.get("session_id"),
        )
        
        db.add(edit_history)
        await db.commit()
        
        logger.info(
            "Edit saved to history",
            project_id=str(project_id),
            user_id=str(user_id),
            action=edit_history.action,
            object_type=edit_history.object_type
        )
        
    except Exception as e:
        logger.error(
            "Failed to save edit history",
            project_id=str(project_id),
            user_id=str(user_id),
            error=str(e)
        )
        await db.rollback()


@router.get("/projects/{project_id}/users")
async def get_project_active_users(project_id: uuid.UUID) -> Dict[str, Any]:
    """
    Get list of currently active users in a project.
    
    Args:
        project_id: Project ID
        
    Returns:
        Dict[str, Any]: List of active users
    """
    users = manager.get_project_users(str(project_id))
    
    return {
        "project_id": str(project_id),
        "active_users": users,
        "total": len(users),
        "timestamp": datetime.utcnow().isoformat(),
    }