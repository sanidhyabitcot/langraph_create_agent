"""
Account Service
Business logic for account operations
"""
import logging
from typing import Dict, Any, Optional
from data import mock_store

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AccountService:
    """Service for account operations"""
    
    def __init__(self):
        """Initialize account service"""
        try:
            logger.info("Initializing AccountService")
            self.store = mock_store
            logger.info("AccountService initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing AccountService: {str(e)}", exc_info=True)
            raise
    
    def get_account_details(self, account_id: str) -> Dict[str, Any]:
        """
        Get account details by ID
        
        Args:
            account_id: Account identifier
            
        Returns:
            Account details dictionary
        """
        try:
            logger.info(f"Fetching account details for: {account_id}")
            account = self.store.get_account(account_id)
            
            if account:
                logger.info(f"Account found: {account_id}")
                return {
                    "success": True,
                    "data": account.dict()
                }
            else:
                logger.warning(f"Account not found: {account_id}")
                return {
                    "success": False,
                    "error": f"Account with ID '{account_id}' not found"
                }
                
        except Exception as e:
            logger.error(f"Error getting account details: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to get account details: {str(e)}"
            }
    
    def get_all_accounts(self) -> Dict[str, Any]:
        """
        Get all accounts
        
        Returns:
            Dictionary with all accounts
        """
        accounts = self.store.get_all_accounts()
        return {
            "success": True,
            "data": {
                "account_overview": [acc.dict() for acc in accounts]
            }
        }


# Global instance
account_service = AccountService()
