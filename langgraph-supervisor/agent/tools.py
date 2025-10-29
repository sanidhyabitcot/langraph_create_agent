"""
Agent Tools
Tool definitions for the LangChain v1 single agent
"""
from typing import Dict, Any, Optional
from langchain_core.tools import tool

from services import account_service, facility_service, notes_service


@tool
def fetch_account_details(account_id: str) -> Dict[str, Any]:
    """
    Retrieve account related information including status, facilities, balance, and rewards.
    
    Args:
        account_id: The account ID to fetch details for (e.g., 'A-011977763')
        
    Returns:
        Dictionary with account details or error message
    """
    return account_service.get_account_details(account_id)


@tool
def fetch_facility_details(facility_id: str) -> Dict[str, Any]:
    """
    Retrieve facility related information including medical licenses, agreements, and status.
    
    Args:
        facility_id: The facility ID to fetch details for (e.g., 'F-015766066')
        
    Returns:
        Dictionary with facility details or error message
    """
    return facility_service.get_facility_details(facility_id)


@tool
def save_note(user_id: str, content: str) -> Dict[str, Any]:
    """
    Save notes or meeting minutes for a user.
    
    Args:
        user_id: The user ID to save the note for
        content: The note content or meeting minutes to save
        
    Returns:
        Dictionary with saved note details
    """
    return notes_service.save_note(user_id, content)


@tool
def fetch_notes(
    user_id: Optional[str] = None,
    date: Optional[str] = None,
    last_n: int = 5,
    order: str = "desc"
) -> Dict[str, Any]:
    """
    Retrieve notes based on filters (user_id, date, or last N notes).
    
    Args:
        user_id: Optional user ID to filter notes
        date: Optional date in YYYY-MM-DD format to filter notes
        last_n: Number of recent notes to return (default: 5)
        
    Returns:
        Dictionary with list of notes matching criteria
    """
    return notes_service.fetch_notes(
        user_id=user_id,
        date=date,
        last_n=last_n,
        order=order
    )


# List of all available tools
ALL_TOOLS = [
    fetch_account_details,
    fetch_facility_details,
    save_note,
    fetch_notes
]
