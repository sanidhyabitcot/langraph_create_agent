"""
Agent Tools
Tool definitions for the LangChain v1 single agent
Tools accept RunnableConfig to receive account_id, facility_id, and user_id
"""
from typing import Dict, Any, Optional
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

from services import account_service, facility_service, notes_service


@tool
def fetch_account_details(config: RunnableConfig, account_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve account related information including status, facilities, balance, and rewards.
    
    Args:
        config: Configuration object containing account_id and facility_id
        account_id: Optional account ID. If not provided, will be extracted from config.
        
    Returns:
        Dictionary with account details or error message
        
    Use this tool when user requests:
    - Account information, account details, account overview
    - Account balance, rewards, loyalty information
    - Any query about account data
    """
    # Extract account_id from config if not provided as parameter
    if not account_id:
        account_id = config.get("configurable", {}).get("account_id")
    
    if not account_id:
        return {
            "success": False,
            "error": "account_id is required. Please provide it in the request or config."
        }
    
    return account_service.get_account_details(account_id)


@tool
def fetch_facility_details(config: RunnableConfig, facility_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve facility related information including medical licenses, agreements, and status.
    
    Args:
        config: Configuration object containing account_id and facility_id
        facility_id: Optional facility ID. If not provided, will be extracted from config.
        
    Returns:
        Dictionary with facility details or error message
        
    Use this tool when user requests:
    - Facility information, facility details, facility overview
    - Facility licenses, agreements, status
    - Any query about facility data
    """
    # Extract facility_id from config if not provided as parameter
    if not facility_id:
        facility_id = config.get("configurable", {}).get("facility_id")
    
    if not facility_id:
        return {
            "success": False,
            "error": "facility_id is required. Please provide it in the request or config."
        }
    
    return facility_service.get_facility_details(facility_id)


@tool
def save_note(
    config: RunnableConfig,
    content: str,
    account_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Save notes or meeting minutes for a user.
    
    Args:
        config: Configuration object containing account_id (preferred) or user_id
        content: The note content or meeting minutes to save
        account_id: Optional account ID. If not provided, will be extracted from config.
        user_id: Optional user ID. Deprecated pathway; retained for backward compatibility.
        
    Returns:
        Dictionary with saved note details
        
    Use this tool when user wants to:
    - Save a note
    - Store meeting minutes
    - Record information
    """
    # Prefer account_id for scoping notes; fallback to legacy user_id if needed
    if not account_id:
        account_id = config.get("configurable", {}).get("account_id")
    
    if account_id:
        return notes_service.save_note(account_id=account_id, content=content)
    
    # Legacy fallback (not recommended)
    if not user_id:
        user_id = config.get("configurable", {}).get("user_id")
    if user_id:
        # Maintain backward compatibility in case older callers still pass user_id
        return notes_service.save_note(account_id=user_id, content=content)
    
    return {
        "success": False,
        "error": "account_id is required. Provide it in the request or config."
    }


@tool
def fetch_notes(
    config: RunnableConfig,
    account_id: Optional[str] = None,
    date: Optional[str] = None,
    last_n: Optional[int] = None,
    order: Optional[str] = None,
    first_limit: Optional[int] = None,
    to_date: Optional[str] = None,
    from_date: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve notes based on filters (user_id, date, or last N notes).
    
    Args:
        config: Configuration object containing account_id (preferred)
        account_id: Optional account ID. If not provided, will be extracted from config.
        date: Optional date in YYYY-MM-DD format to filter notes
        last_n: Number of recent notes to return (default: 5)
        order: Order of results - "desc" (newest first) or "asc" (oldest first)
        first_limit: Number of first notes to return (alternative to last_n)
        to_date: End date for date range filter (YYYY-MM-DD or DD/MM/YYYY)
        from_date: Start date for date range filter (YYYY-MM-DD or DD/MM/YYYY)
        
    Returns:
        Dictionary with list of notes matching criteria
        
    Use this tool when user requests:
    - "Fetch notes", "Show notes", "Display notes", "List notes"
    - "Fetch last N notes", "Fetch first N notes"
    - "Fetch notes from date", "Show notes from 2024-01-01"
    """
    # Extract account_id from config if not provided as parameter
    if not account_id:
        account_id = config.get("configurable", {}).get("account_id")
    
    # Set defaults if not provided
    if last_n is None and first_limit is None:
        last_n = 5
    if order is None:
        order = "desc"
    
    return notes_service.fetch_notes(
        account_id=account_id,
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
