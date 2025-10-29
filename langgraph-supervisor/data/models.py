"""
Data Models
Pydantic models for all data structures
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Account(BaseModel):
    """Account data model"""
    account_id: str
    name: str
    status: str
    is_tna: bool = False
    created_at: str
    pricing_model: str
    address_line1: str
    address_line2: str = ""
    address_city: str
    address_state: str
    address_postal_code: str
    address_country: str = ""
    facilities: List[Dict[str, Any]] = []
    total_amount_due: float = 0.0
    total_amount_due_this_week: float = 0.0
    invoice_id: str = ""
    invoice_amount: float = 0.0
    invoice_due_date: str = ""
    current_balance: float = 0.0
    points_earned_this_quarter: int = 0
    pending_balance: int = 0
    current_tier: str = ""
    next_tier: str = ""
    points_to_next_tier: int = 0
    quarter_end_date: str = ""
    free_vials_available: int = 0
    rewards_required_for_next_free_vial: int = 0
    rewards_redeemed_towards_next_free_vial: int = 0
    rewards_status: str = ""
    rewards_updated_at: str = ""
    evolux_level: str = ""


class Facility(BaseModel):
    """Facility data model"""
    id: str
    name: str
    status: str
    has_signed_medical_liability_agreement: bool = False
    medical_license_id: str = ""
    medical_license_state: str = ""
    medical_license_number: str = ""
    medical_license_involvement: str = ""
    medical_license_expiration_date: str = ""
    medical_license_is_expired: bool = False
    medical_license_status: str = ""
    medical_license_owner_first_name: str = ""
    medical_license_owner_last_name: str = ""
    account_id: str = ""
    account_name: str = ""
    account_status: str = ""
    account_has_signed_financial_agreement: bool = False
    account_has_accepted_jet_terms: bool = False
    shipping_address_line1: str = ""
    shipping_address_line2: str = ""
    shipping_address_city: str = ""
    shipping_address_state: str = ""
    shipping_address_zip: str = ""
    shipping_address_commercial: bool = False
    sponsored: bool = False
    agreement_status: str = ""
    agreement_signed_at: str = ""
    agreement_type: str = ""


class Note(BaseModel):
    """Note data model"""
    note_id: str
    user_id: str
    content: str
    created_at: datetime
    updated_at: datetime


class Message(BaseModel):
    """Chat message model"""
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Session(BaseModel):
    """Session data model"""
    session_id: str
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[Message] = []
