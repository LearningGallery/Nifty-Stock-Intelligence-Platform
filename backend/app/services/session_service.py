"""
Chat Session Management Service
"""
import boto3
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from app.config import settings
from app.models.chat import MessageRole, ChatMessage, ChatSession
from app.core.logging import logger
from app.core.exceptions import DynamoDBException


class SessionService:
    """
    Manages chat sessions and messages in DynamoDB
    """
    
    def __init__(self):
        dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
        self.sessions_table = dynamodb.Table(settings.CHAT_SESSIONS_TABLE)
        self.messages_table = dynamodb.Table(settings.CHAT_MESSAGES_TABLE)
    
    async def create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Create a new chat session
        """
        try:
            timestamp = int(datetime.utcnow().timestamp())
            ttl = int((datetime.utcnow() + timedelta(days=30)).timestamp())
            
            item = {
                "session_id": session_id,
                "created_at": timestamp,
                "updated_at": timestamp,
                "user_id": user_id or "anonymous",
                "metadata": metadata or {},
                "ttl": ttl
            }
            
            self.sessions_table.put_item(Item=item)
            logger.info(f"Created session: {session_id}")
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise DynamoDBException(f"Failed to create session")
    
    async def session_exists(self, session_id: str) -> bool:
        """
        Check if session exists
        """
        try:
            response = self.sessions_table.get_item(
                Key={"session_id": session_id}
            )
            return "Item" in response
        except Exception as e:
            logger.error(f"Error checking session: {e}")
            return False
    
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """
        Get session with all messages
        """
        try:
            # Get session
            response = self.sessions_table.get_item(
                Key={"session_id": session_id}
            )
            
            if "Item" not in response:
                return None
            
            session_data = response["Item"]
            
            # Get messages
            messages = await self.get_messages(session_id)
            
            return ChatSession(
                session_id=session_id,
                user_id=session_data.get("user_id"),
                created_at=datetime.fromtimestamp(int(session_data["created_at"])),
                updated_at=datetime.fromtimestamp(int(session_data["updated_at"])),
                messages=messages,
                metadata=session_data.get("metadata", {})
            )
            
        except Exception as e:
            logger.error(f"Error getting session: {e}")
            return None
    
    async def add_message(
        self,
        session_id: str,
        message_id: str,
        role: MessageRole,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add a message to a session
        """
        try:
            timestamp = int(datetime.utcnow().timestamp())
            ttl = int((datetime.utcnow() + timedelta(days=30)).timestamp())
            
            item = {
                "session_id": session_id,
                "message_id": message_id,
                "role": role.value,
                "content": content,
                "timestamp": timestamp,
                "metadata": metadata or {},
                "ttl": ttl
            }
            
            self.messages_table.put_item(Item=item)
            
            # Update session updated_at
            self.sessions_table.update_item(
                Key={"session_id": session_id},
                UpdateExpression="SET updated_at = :updated_at",
                ExpressionAttributeValues={
                    ":updated_at": timestamp
                }
            )
            
            logger.info(f"Added message to session {session_id}")
            
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            raise DynamoDBException("Failed to add message")
    
    async def get_messages(self, session_id: str) -> List[ChatMessage]:
        """
        Get all messages for a session
        """
        try:
            response = self.messages_table.query(
                KeyConditionExpression="session_id = :session_id",
                ExpressionAttributeValues={
                    ":session_id": session_id
                },
                ScanIndexForward=True  # Ascending order by timestamp
            )
            
            messages = []
            for item in response.get("Items", []):
                messages.append(ChatMessage(
                    message_id=item["message_id"],
                    role=MessageRole(item["role"]),
                    content=item["content"],
                    timestamp=datetime.fromtimestamp(int(item["timestamp"])),
                    metadata=item.get("metadata", {})
                ))
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return []
    
    async def get_conversation_history(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history in format suitable for LLM context
        """
        messages = await self.get_messages(session_id)
        
        # Return last N messages
        recent_messages = messages[-limit:] if len(messages) > limit else messages
        
        return [
            {
                "role": msg.role.value,
                "content": msg.content
            }
            for msg in recent_messages
        ]
    
    async def delete_session(self, session_id: str):
        """
        Delete a session and all its messages
        """
        try:
            # Delete all messages
            messages = await self.get_messages(session_id)
            for msg in messages:
                self.messages_table.delete_item(
                    Key={
                        "session_id": session_id,
                        "message_id": msg.message_id
                    }
                )
            
            # Delete session
            self.sessions_table.delete_item(
                Key={"session_id": session_id}
            )
            
            logger.info(f"Deleted session: {session_id}")
            
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            raise DynamoDBException("Failed to delete session")
    
    async def list_user_sessions(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[ChatSession]:
        """
        List all sessions for a user
        """
        try:
            response = self.sessions_table.query(
                IndexName="UserIdIndex",
                KeyConditionExpression="user_id = :user_id",
                ExpressionAttributeValues={
                    ":user_id": user_id
                },
                ScanIndexForward=False,  # Descending order (newest first)
                Limit=limit
            )
            
            sessions = []
            for item in response.get("Items", []):
                sessions.append(ChatSession(
                    session_id=item["session_id"],
                    user_id=item["user_id"],
                    created_at=datetime.fromtimestamp(int(item["created_at"])),
                    updated_at=datetime.fromtimestamp(int(item["updated_at"])),
                    messages=[],  # Don't load messages for list view
                    metadata=item.get("metadata", {})
                ))
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error listing sessions: {e}")
            return []
