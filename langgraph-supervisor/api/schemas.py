"""
API Schemas
Request and response models for the API
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# Request Models

class CreateSessionRequest(BaseModel):
    """Request model for creating a session"""
    user_id: str = Field(..., description="User identifier")


class ChatRequest(BaseModel):
    """Request model for chat endpoint - matches expected format"""
    text: str = Field(..., description="User message/query")
    user_id: str = Field(..., description="User identifier")
    account_id: Optional[str] = Field(None, description="Optional account ID for context")
    facility_id: Optional[str] = Field(None, description="Optional facility ID for context")
    conversation_id: str = Field(..., description="Conversation ID for session context")


# Response Models

class CreateSessionResponse(BaseModel):
    """Response model for session creation"""
    conversation_id: str
    user_id: str
    created_at: str
    message: str = "Conversation created successfully"


class ChatResponse(BaseModel):
    """Response model for chat endpoint - matches expected format"""
    conversation_id: str = Field(..., description="Conversation ID")
    final_response: str = Field(..., description="Natural language response")
    card_key: str = Field(..., description="Card key to determine UI display")
    account_overview: Optional[List[Dict[str, Any]]] = Field(None, description="Account data if requested")
    rewards_overview: Optional[Dict[str, Any]] = Field(None, description="Rewards data if requested")
    facility_overview: Optional[List[Dict[str, Any]]] = Field(None, description="Facility data if requested")
    order_overview: Optional[List[Dict[str, Any]]] = Field(None, description="Order data if requested")
    note_overview: Optional[List[Dict[str, Any]]] = Field(None, description="Notes data if requested")


class SessionInfo(BaseModel):
    """Session information model"""
    session_id: str
    user_id: Optional[str]
    created_at: str
    updated_at: str
    message_count: int


class ConversationHistory(BaseModel):
    """Conversation history model"""
    session_id: str
    messages: List[Dict[str, Any]]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    agent_model: str
    active_sessions: int
