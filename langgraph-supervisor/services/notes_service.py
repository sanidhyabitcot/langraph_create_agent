"""
Notes Service
Business logic for notes operations
"""
import logging
from typing import Dict, Any, Optional, List
from data import mock_store

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotesService:
    """Service for notes operations"""
    
    def __init__(self):
        """Initialize notes service"""
        try:
            logger.info("Initializing NotesService")
            self.store = mock_store
            logger.info("NotesService initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing NotesService: {str(e)}", exc_info=True)
            raise
    
    def save_note(self, account_id: str, content: str) -> Dict[str, Any]:
        """
        Save a note for an account
        
        Args:
            account_id: Account identifier
            content: Note content
            
        Returns:
            Saved note details
        """
        try:
            logger.info(f"Saving note for account: {account_id}")
            note = self.store.save_note(account_id, content)
            logger.info(f"Note saved successfully for account: {account_id}")
            return {
                "success": True,
                "data": note.dict(),
                "message": "Note saved successfully"
            }
        except Exception as e:
            logger.error(f"Error saving note: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to save note: {str(e)}"
            }
    
    def fetch_notes(
        self,
        account_id: Optional[str] = None,
        date: Optional[str] = None,
        last_n: int = 5,
        order: str = "desc"
    ) -> Dict[str, Any]:
        """
        Fetch notes with optional filters
        
        Args:
            account_id: Optional account ID filter
            date: Optional date filter (YYYY-MM-DD)
            last_n: Number of recent notes to return
            
        Returns:
            Dictionary with notes list
        """
        try:
            logger.info(f"Fetching notes for account: {account_id}, date: {date}, last_n: {last_n}")
            # Normalize date formats like DD/MM/YYYY to YYYY-MM-DD
            if date and "/" in date:
                try:
                    dd, mm, yyyy = date.split("/")
                    date = f"{yyyy}-{mm.zfill(2)}-{dd.zfill(2)}"
                except Exception:
                    pass
            notes = self.store.get_notes(
                account_id=account_id,
                date=date,
                last_n=last_n,
                order=order
            )
            logger.info(f"Fetched {len(notes)} notes")
            return {
                "success": True,
                "data": [note.dict() for note in notes],
                "count": len(notes)
            }
        except Exception as e:
            logger.error(f"Error fetching notes: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to fetch notes: {str(e)}"
            }


# Global instance
notes_service = NotesService()
