"""
Chat Data Models
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class MessageRole(str, Enum):
    """Message role enum"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessageRequest(BaseModel):
    """Chat message request"""
    session_id: Optional[str] = Field(None, description="Chat session ID")
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Additional context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "message": "Analyze TCS stock for short-term trading",
                "context": {}
            }
        }


class ChatMessage(BaseModel):
    """Individual chat message"""
    message_id: str
    role: MessageRole
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = {}


class ChatSession(BaseModel):
    """Chat session model"""
    session_id: str
    user_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessage] = []
    metadata: Dict[str, Any] = {}


class ChatMessageResponse(BaseModel):
    """Chat message response"""
    session_id: str
    message_id: str
    content: str
    role: MessageRole
    timestamp: datetime
    analysis_data: Optional[Dict[str, Any]] = None
    sources: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "message_id": "msg_123456",
                "content": "Based on analysis, TCS shows...",
                "role": "assistant",
                "timestamp": "2024-01-15T10:30:00Z",
                "analysis_data": {
                    "stock_symbol": "TCS",
                    "recommendation": "BUY",
                    "confidence": "HIGH"
                },
                "sources": [
                    {
                        "type": "news",
                        "title": "TCS Q3 Results",
                        "url": "https://example.com"
                    }
                ]
            }
        }
