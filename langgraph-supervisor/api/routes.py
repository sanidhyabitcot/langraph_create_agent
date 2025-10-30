"""
API Routes
FastAPI endpoints for the LangChain v1 single agent
"""
import logging
from fastapi import APIRouter, HTTPException, status
from typing import Optional

from api.schemas import (
    CreateSessionRequest,
    CreateSessionResponse,
    ChatRequest,
    ChatResponse,
    SessionInfo,
    ConversationHistory,
    HealthResponse
)
from services import session_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter()


@router.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "LangGraph Single Agent API",
        "version": "1.0.0",
        "description": "LangGraph + OpenAI Multi-Tool Agentic System",
        "endpoints": {
            "health": "GET /health",
            "create_session": "POST /sessions",
            "chat": "POST /chat",
            "list_sessions": "GET /sessions",
            "get_session": "GET /sessions/{session_id}",
            "delete_session": "DELETE /sessions/{session_id}",
            "get_history": "GET /sessions/{session_id}/history"
        },
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    from agent import get_agent
    agent = get_agent()
    model_name = getattr(agent.model, "model_name", "gpt-4o-mini") if hasattr(agent, "model") else "gpt-4o-mini"
    return HealthResponse(
        status="healthy",
        agent_model=model_name,
        active_sessions=len(session_service.sessions)
    )


@router.post(
    "/sessions",
    response_model=CreateSessionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Sessions"]
)
async def create_session(request: CreateSessionRequest):
    """
    Create a new conversation session
    
    - **user_id**: User identifier for the session
    """
    session = session_service.create_session(user_id=request.user_id)
    
    return CreateSessionResponse(
        conversation_id=session.session_id,
        user_id=request.user_id,
        created_at=session.created_at.isoformat()
    )


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Send a message to the single agent
    
    - **text**: User message/query
    - **user_id**: User identifier  
    - **account_id**: Optional account ID for context
    - **facility_id**: Optional facility ID for context
    - **conversation_id**: Conversation ID for session context
    
    Returns natural language response and structured data in flat format.
    """
    try:
        logger.info(f"Chat request received for conversation: {request.conversation_id}")
        
        # Verify conversation exists
        session = session_service.get_session(request.conversation_id)
        if not session:
            logger.warning(f"Conversation not found: {request.conversation_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation '{request.conversation_id}' not found"
            )
        
        # Get conversation history
        conversation_history = session_service.get_conversation_history(request.conversation_id)
        logger.info(f"Conversation history length: {len(conversation_history)}")
        
        # Get agent and process message with context
        from agent import get_agent
        agent = get_agent()
        result = agent.process_message(
            user_message=request.text,
            conversation_history=conversation_history,
            account_id=request.account_id,
            facility_id=request.facility_id,
            user_id=request.user_id,
            conversation_id=request.conversation_id  # Pass conversation_id for memory
        )
        
        logger.info(f"Message processed. Card key: {result['card_key']}")
        
        # Add user message to session
        session_service.add_message(
            session_id=request.conversation_id,
            role="user",
            content=request.text
        )
        
        # Add assistant response to session
        session_service.add_message(
            session_id=request.conversation_id,
            role="assistant",
            content=result["final_response"]
        )
        
        return ChatResponse(
            conversation_id=request.conversation_id,
            final_response=result["final_response"],
            card_key=result["card_key"],
            account_overview=result.get("account_overview"),
            rewards_overview=result.get("rewards_overview"),
            facility_overview=result.get("facility_overview"),
            order_overview=result.get("order_overview"),
            note_overview=result.get("note_overview", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


@router.get("/sessions", response_model=list[SessionInfo], tags=["Sessions"])
async def list_sessions(user_id: Optional[str] = None):
    """
    List all sessions
    
    - **user_id**: Optional filter by user ID
    """
    sessions = session_service.list_sessions(user_id=user_id)
    return [SessionInfo(**session) for session in sessions]


@router.get("/sessions/{session_id}", response_model=SessionInfo, tags=["Sessions"])
async def get_session(session_id: str):
    """
    Get session information
    
    - **session_id**: Session identifier
    """
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found"
        )
    
    return SessionInfo(
        session_id=session.session_id,
        user_id=session.user_id,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
        message_count=len(session.messages)
    )


@router.delete("/sessions/{session_id}", tags=["Sessions"])
async def delete_session(session_id: str):
    """
    Delete a session
    
    - **session_id**: Session identifier
    """
    success = session_service.delete_session(session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found"
        )
    
    return {"message": f"Session '{session_id}' deleted successfully"}


@router.get(
    "/sessions/{session_id}/history",
    response_model=ConversationHistory,
    tags=["Sessions"]
)
async def get_conversation_history(
    session_id: str,
    include_metadata: bool = False
):
    """
    Get conversation history for a session
    
    - **session_id**: Session identifier
    - **include_metadata**: Include timestamp metadata
    """
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found"
        )
    
    if include_metadata:
        messages = [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in session.messages
        ]
    else:
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in session.messages
        ]
    
    return ConversationHistory(
        session_id=session_id,
        messages=messages
    )
