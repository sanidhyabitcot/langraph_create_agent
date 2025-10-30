"""
Response Models for Structured Output
Pydantic models for structured agent responses
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AccountOverview(BaseModel):
    """Account overview model for structured output"""
    account_id: str
    name: Optional[str] = None
    status: Optional[str] = None
    balance: Optional[float] = None
    current_tier: Optional[str] = None
    points_earned_this_quarter: Optional[int] = None
    free_vials_available: Optional[int] = None
    rewards_status: Optional[str] = None
    # Add other account fields as needed
    # We'll populate from the actual account data returned by tools


class FacilityOverview(BaseModel):
    """Facility overview model for structured output"""
    id: str
    name: Optional[str] = None
    status: Optional[str] = None
    medical_license_number: Optional[str] = None
    medical_license_state: Optional[str] = None
    agreement_status: Optional[str] = None
    account_id: Optional[str] = None
    account_name: Optional[str] = None
    # Add other facility fields as needed


class RewardOverview(BaseModel):
    """Reward overview model"""
    current_tier: Optional[str] = None
    next_tier: Optional[str] = None
    points_to_next_tier: Optional[int] = None
    points_earned_this_quarter: Optional[int] = None
    pending_balance: Optional[int] = None
    free_vials_available: Optional[int] = None
    rewards_status: Optional[str] = None


class OrderOverview(BaseModel):
    """Order overview model"""
    order_id: Optional[str] = None
    status: Optional[str] = None
    amount: Optional[float] = None


class NoteOverview(BaseModel):
    """Note overview model"""
    note_id: Optional[str] = None
    content: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AgentOutput(BaseModel):
    """Structured output from the agent - AgentOutput determines card_key and data"""
    
    final_response: str = Field(..., description="Natural language response to the user")
    
    account_overview: Optional[List[AccountOverview]] = Field(
        None, 
        description="Pick the exact account details from the account overview card. Include this ONLY when user requests COMPLETE/FULL account information."
    )
    
    facility_overview: Optional[List[FacilityOverview]] = Field(
        None, 
        description="List of facility overviews for the account. Include this ONLY when user requests COMPLETE/FULL facility information."
    )
    
    rewards_overview: Optional[List[RewardOverview]] = Field(
        None, 
        description="List of reward overviews for the account. Include this ONLY when user requests COMPLETE/FULL rewards information."
    )
    
    order_overview: Optional[List[OrderOverview]] = Field(
        None, 
        description="List of order overviews for the account. Include this ONLY when user requests COMPLETE/FULL order information."
    )
    
    note_overview: List[NoteOverview] = Field(
        default_factory=list, 
        description="List of note overviews. Include this when user requests to FETCH/LIST/DISPLAY/SHOW notes."
    )
    
    card_key: str = Field(
        default="other",
        description="""Select the appropriate card key based on user's query. CRITICAL: Read all rules carefully.

VALID VALUES:
- "account_overview"
- "facility_overview"
- "rewards_overview"
- "order_overview"
- "note_overview"
- "other"

SELECTION RULES:

1. "account_overview":
   Use ONLY when user explicitly requests COMPLETE/FULL account information:
   ✓ Valid queries: "show account overview", "account details", "account summary", "full account info"
   ✗ Invalid: "what is the account balance?", "show invoices", "account name", "how many points?"
   Rule: If query asks about ONE specific account field → use "other"

2. "facility_overview":
   Use ONLY when user explicitly requests COMPLETE/FULL facility information:
   ✓ Valid queries: "show facility overview", "facility details", "facility summary", "full facility info"
   ✗ Invalid: "what is the facility name?", "facility address", "who is the sales rep?"
   Rule: If query asks about ONE specific facility field → use "other"

3. "rewards_overview":
   Use ONLY when user explicitly requests COMPLETE/FULL rewards information:
   ✓ Valid queries: "show rewards overview", "rewards details", "rewards summary", "all rewards info"
   ✗ Invalid: "how many points?", "current tier", "what's my loyalty status?"
   Rule: If query asks about ONE specific rewards field → use "other"

4. "order_overview":
   Use ONLY when user explicitly requests COMPLETE/FULL order information:
   ✓ Valid queries: "show order overview", "order details", "order summary", "all orders"
   ✗ Invalid: "order status", "last order date", "pending orders count"
   Rule: If query asks about ONE specific order field → use "other"

5. "note_overview":
   Use ONLY when user explicitly requests to FETCH/LIST/DISPLAY/SHOW notes:
   ✓ Valid queries: "fetch notes", "show notes", "display notes", "list notes", "fetch notes from 2024-01-01", "show last 5 notes"
   ✗ Invalid: "summarize notes", "analyze notes", "what did I note about X?"
   SPECIAL RULE: Set as "note_overview" even if no notes available (user asked to fetch)
   Rule: If user wants to ANALYZE/PROCESS notes → use "other"

6. "other":
   Use for:
   - Specific questions about one field ("what is the balance?", "current tier?")
   - Greetings and general conversation
   - Follow-up questions
   - Analysis or processing requests
   - Any query that doesn't explicitly request a FULL/COMPLETE overview"""
    )

    class Config:
        extra = "forbid"
