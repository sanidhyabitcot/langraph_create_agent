"""
Facility Service
Business logic for facility operations
"""
import logging
from typing import Dict, Any, Optional
from data import mock_store

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FacilityService:
    """Service for facility operations"""
    
    def __init__(self):
        """Initialize facility service"""
        try:
            logger.info("Initializing FacilityService")
            self.store = mock_store
            logger.info("FacilityService initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing FacilityService: {str(e)}", exc_info=True)
            raise
    
    def get_facility_details(self, facility_id: str) -> Dict[str, Any]:
        """
        Get facility details by ID
        
        Args:
            facility_id: Facility identifier
            
        Returns:
            Facility details dictionary
        """
        try:
            logger.info(f"Fetching facility details for: {facility_id}")
            facility = self.store.get_facility(facility_id)
            
            if facility:
                logger.info(f"Facility found: {facility_id}")
                return {
                    "success": True,
                    "data": facility.dict()
                }
            else:
                logger.warning(f"Facility not found: {facility_id}")
                return {
                    "success": False,
                    "error": f"Facility with ID '{facility_id}' not found"
                }
                
        except Exception as e:
            logger.error(f"Error getting facility details: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to get facility details: {str(e)}"
            }
    
    def get_all_facilities(self) -> Dict[str, Any]:
        """
        Get all facilities
        
        Returns:
            Dictionary with all facilities
        """
        facilities = self.store.get_all_facilities()
        return {
            "success": True,
            "data": {
                "facility_overview": [fac.dict() for fac in facilities]
            }
        }


# Global instance
facility_service = FacilityService()
