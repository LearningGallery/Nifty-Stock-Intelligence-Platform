"""
Chat API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional
import uuid
from datetime import datetime

from app.models.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSession,
    MessageRole
)
from app.services.orchestration import OrchestrationService
from app.services.session_service import SessionService
from app.core.security import get_current_user, get_optional_user
from app.core.logging import logger
from app.core.exceptions import ValidationException

router = APIRouter()


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    request: ChatMessageRequest,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
) -> ChatMessageResponse:
    """
    Send a chat message and get AI response
    
    This endpoint handles:
    - New chat sessions
    - Continuing existing conversations
    - Stock analysis queries
    - Follow-up questions with context
    """
    try:
        # Initialize services
        orchestration_service = OrchestrationService()
        session_service = SessionService()
        
        # Get or create session
        session_id = request.session_id
        user_id = user["user_id"] if user else None
        
        if not session_id:
            session_id = str(uuid.uuid4())
            await session_service.create_session(session_id, user_id)
            logger.info(f"Created new chat session: {session_id}")
        else:
            # Validate session exists
            session_exists = await session_service.session_exists(session_id)
            if not session_exists:
                raise ValidationException(
                    message="Invalid session_id",
                    details={"session_id": session_id}
                )
        
        # Store user message
        user_message_id = str(uuid.uuid4())
        await session_service.add_message(
            session_id=session_id,
            message_id=user_message_id,
            role=MessageRole.USER,
            content=request.message,
            metadata=request.context
        )
        
        logger.info(f"Processing message in session {session_id}: {request.message[:50]}...")
        
        # Get conversation history
        history = await session_service.get_conversation_history(session_id)
        
        # Process with orchestration layer
        response_data = await orchestration_service.process_chat_message(
            message=request.message,
            session_id=session_id,
            conversation_history=history,
            context=request.context
        )
        
        # Store assistant response
        assistant_message_id = str(uuid.uuid4())
        await session_service.add_message(
            session_id=session_id,
            message_id=assistant_message_id,
            role=MessageRole.ASSISTANT,
            content=response_data["content"],
            metadata={
                "analysis_data": response_data.get("analysis_data"),
                "sources": response_data.get("sources")
            }
        )
        
        logger.info(f"Successfully processed message in session {session_id}")
        
        # Return response
        return ChatMessageResponse(
            session_id=session_id,
            message_id=assistant_message_id,
            content=response_data["content"],
            role=MessageRole.ASSISTANT,
            timestamp=datetime.utcnow(),
            analysis_data=response_data.get("analysis_data"),
            sources=response_data.get("sources")
        )
        
    except ValidationException:
        raise
    except Exception as e:
        logger.exception(f"Error processing chat message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message. Please try again."
        )


@router.get("/sessions/{session_id}", response_model=ChatSession)
async def get_session(
    session_id: str,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
) -> ChatSession:
    """
    Retrieve chat session with message history
    """
    try:
        session_service = SessionService()
        
        # Get session
        session = await session_service.get_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Verify ownership if authenticated
        if user and session.get("user_id") != user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error retrieving session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session"
        )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete a chat session (requires authentication)
    """
    try:
        session_service = SessionService()
        
        # Get session to verify ownership
        session = await session_service.get_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        if session.get("user_id") != user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Delete session
        await session_service.delete_session(session_id)
        logger.info(f"Deleted session {session_id} for user {user['user_id']}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete session"
        )


@router.get("/sessions", response_model=list[ChatSession])
async def list_user_sessions(
    user: Dict[str, Any] = Depends(get_current_user),
    limit: int = 20
) -> list[ChatSession]:
    """
    List all chat sessions for authenticated user
    """
    try:
        session_service = SessionService()
        sessions = await session_service.list_user_sessions(
            user_id=user["user_id"],
            limit=limit
        )
        
        return sessions
        
    except Exception as e:
        logger.exception(f"Error listing sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sessions"
        )
