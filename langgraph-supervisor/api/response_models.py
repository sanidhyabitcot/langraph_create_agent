"""
Response Models for Structured Output
Pydantic models for structured agent responses
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class StructuredResponse(BaseModel):
    """Structured response from the agent"""
    intent: str = Field(..., description="Intent of the response: account_query, facility_query, note_operation, general")
    card_key: str = Field(..., description="Key to determine which UI card to display")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Extracted entities")
    data: Dict[str, Any] = Field(default_factory=dict, description="Structured data for display")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    tools_used: List[str] = Field(default_factory=list, description="Tools that were used")


