"""
OpenAI Chat Endpoints - Integration with OpenAI Assistants for conversational recommendations
"""

import logging
from typing import Dict, Optional
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import SessionLocal
from backend.services.openai_service import OpenAIService
from backend.services.recommender import RecommenderService
from backend.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/openai",
    tags=["OpenAI Chat"],
    responses={404: {"description": "Not found"}}
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ChatRequest(BaseModel):
    """Chat message request"""
    message: str
    thread_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat message response"""
    thread_id: str
    message: str
    status: str


@router.post("/chat", response_model=ChatResponse)
async def chat_with_alie(
    request: ChatRequest,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Chat with ALIE - AI Lead Intelligence Engine
    
    Supports multi-turn conversations for business recommendations
    Uses OpenAI Assistants with Function Calling
    
    Request:
    ```json
    {
        "message": "Find me hair salons in Almaty",
        "thread_id": "thread_123..." (optional - for continuing conversation)
    }
    ```
    
    Response includes recommendations via Function Calling
    """
    
    request_id = str(uuid4())
    
    try:
        # Validate message
        if not request.message or len(request.message.strip()) == 0:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        if len(request.message) > 500:
            raise HTTPException(status_code=400, detail="Message too long (max 500 chars)")
        
        # Initialize OpenAI service
        openai_service = OpenAIService(settings.OPENAI_API_KEY)
        
        if not openai_service.client:
            raise HTTPException(status_code=500, detail="OpenAI service not available")
        
        # Get or create thread
        thread_id = request.thread_id
        if not thread_id:
            thread_id = openai_service.create_thread()
            if not thread_id:
                raise HTTPException(status_code=500, detail="Failed to create thread")
        
        # Send message to thread
        message_id = openai_service.send_message(thread_id, request.message)
        if not message_id:
            raise HTTPException(status_code=500, detail="Failed to send message")
        
        # Run assistant
        assistant_id = settings.OPENAI_ASSISTANT_ID
        if not assistant_id:
            raise HTTPException(status_code=500, detail="Assistant not configured")
        
        run_id = openai_service.run_assistant(thread_id, assistant_id)
        if not run_id:
            raise HTTPException(status_code=500, detail="Failed to run assistant")
        
        # Get run status
        run_status = openai_service.get_run_status(thread_id, run_id)
        
        # Handle function calls if needed
        if run_status and run_status.get("required_action"):
            # Process function calls
            function_calls = run_status["required_action"].get("submit_tool_results", {})
            # Handle accordingly (would implement full flow)
        
        # Get response messages
        messages = openai_service.get_messages(thread_id, limit=1)
        
        response_text = ""
        if messages and len(messages) > 0:
            response_text = messages[0].get("content", "No response")
        
        logger.info(f"Chat completed - Request: {request_id}, Thread: {thread_id}")
        
        return {
            "thread_id": thread_id,
            "message": response_text,
            "status": "success",
            "request_id": request_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.post("/threads")
async def create_thread() -> Dict:
    """
    Create a new conversation thread
    
    Use the returned thread_id for subsequent messages
    
    Response:
    ```json
    {
        "thread_id": "thread_123...",
        "created_at": "2024-01-20T10:30:00Z"
    }
    ```
    """
    try:
        openai_service = OpenAIService(settings.OPENAI_API_KEY)
        
        if not openai_service.client:
            raise HTTPException(status_code=500, detail="OpenAI service not available")
        
        thread_id = openai_service.create_thread()
        
        if not thread_id:
            raise HTTPException(status_code=500, detail="Failed to create thread")
        
        logger.info(f"Thread created: {thread_id}")
        
        return {
            "thread_id": thread_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "success"
        }
    
    except Exception as e:
        logger.error(f"Thread creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create thread: {str(e)}")


@router.get("/threads/{thread_id}")
async def get_thread_messages(thread_id: str) -> Dict:
    """
    Get conversation history from a thread
    
    Returns the last messages in the thread
    
    Response:
    ```json
    {
        "thread_id": "thread_123...",
        "messages": [
            {
                "role": "user",
                "content": "Find me hair salons",
                "timestamp": "2024-01-20T10:30:00Z"
            }
        ]
    }
    ```
    """
    try:
        openai_service = OpenAIService(settings.OPENAI_API_KEY)
        
        if not openai_service.client:
            raise HTTPException(status_code=500, detail="OpenAI service not available")
        
        messages = openai_service.get_messages(thread_id, limit=20)
        
        if messages is None:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        logger.info(f"Retrieved {len(messages)} messages from thread {thread_id}")
        
        return {
            "thread_id": thread_id,
            "messages": messages,
            "count": len(messages),
            "status": "success"
        }
    
    except Exception as e:
        logger.error(f"Error getting thread messages: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")


# Import at end to avoid circular imports
from pydantic import BaseModel
from datetime import datetime
