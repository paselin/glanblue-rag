"""
Chat API endpoint.
"""
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse

from app.models.schemas import ChatRequest, ChatResponse, Source
from app.agents.agent import get_agent
from app.core.logging import setup_logging

logger = setup_logging()
router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat with the Granblue Fantasy AI assistant.
    
    Args:
        request: Chat request with message and optional context
        
    Returns:
        Chat response with answer and sources
    """
    try:
        logger.info(f"Received chat request: {request.message[:50]}...")
        
        # Get or create conversation ID
        conversation_id = request.conversation_id or str(uuid4())
        
        # Get agent
        agent = get_agent()
        
        # Prepare context
        context = None
        if request.context:
            context = request.context.model_dump(exclude_none=True)
        
        # Invoke agent
        result = agent.invoke(
            message=request.message,
            context=context,
        )
        
        # Build response
        response = ChatResponse(
            response=result["response"],
            sources=result.get("sources", []),
            suggested_actions=[
                "他のキャラクターを検索",
                "編成例を見る",
                "武器編成について聞く",
            ],
            conversation_id=conversation_id,
        )
        
        logger.info(f"Chat response generated for conversation {conversation_id}")
        
        return response
        
    except Exception as e:
        logger.error(f"Chat request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/history/{conversation_id}")
async def get_chat_history(conversation_id: str):
    """
    Get chat history for a conversation.
    
    Note: This is a placeholder. In production, you'd store and retrieve
    conversation history from a database.
    """
    # TODO: Implement conversation history storage
    return {
        "conversation_id": conversation_id,
        "messages": [],
        "created_at": None,
        "updated_at": None,
    }
