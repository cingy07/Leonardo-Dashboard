"""
Congressional data service handling representative and committee information.
This service manages interactions with the Google Civic API and committee data.
"""

import httpx
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import ExternalServiceError, ValidationError

# Import the class instead of the instance
from app.services.cache import CacheService
from app.services.metrics import MetricsService

logger = logging.getLogger(__name__)

class CongressionalService:
    """
    Service for managing congressional representative and committee data.
    Handles external API calls, data processing, and caching for congressional information.
    """
    
    def __init__(self):
        """Initialize the congressional service with necessary configurations."""
        self.api_key = settings.GOOGLE_CIVIC_API_KEY
        self.api_url = settings.GOOGLE_CIVIC_API_URL
        self.committee_data: Dict[str, List[str]] = {}
        self.last_committee_update: Optional[datetime] = None
        self.cache_service = None
        self.metrics_service = None
        
    def initialize(self):
        """Initialize services and load data."""
        # Importing here to avoid circular imports
        from app.services import cache_service, metrics_service
        self.cache_service = cache_service
        self.metrics_service = metrics_service
        
        # Load committee data on initialization
        self.load_committee_data()
    
    async def load_committee_data(self) -> None:
        """
        Load committee data from JSON files.
        Updates the in-memory cache of committee assignments.
        """
        try:
            committee_file = Path(settings.DATA_DIR) / "committees.json"
            if not committee_file.exists():
                logger.warning("Committee data file not found")
                return
            
            with open(committee_file, 'r') as f:
                self.committee_data = json.load(f)
                
            self.last_committee_update = datetime.utcnow()
            logger.info("Successfully loaded committee data")
            
        except Exception as e:
            logger.error(f"Error loading committee data: {str(e)}")
            raise ExternalServiceError(
                "Committee Data",
                "Failed to load committee information"
            )
    
    async def get_representative_info(self, zip_code: str) -> Dict[str, Any]:
        """
        Retrieve representative information for a given ZIP code.
        
        Args:
            zip_code: The ZIP code to look up
            
        Returns:
            Dictionary containing representative information
            
        Raises:
            ExternalServiceError: If the API call fails
            ValidationError: If the ZIP code is invalid
        """
        # Ensure cache service is initialized
        if self.cache_service is None:
            from app.services import cache_service
            self.cache_service = cache_service
            
        # Check cache first
        cache_key = f"rep_info:{zip_code}"
        cached_data = await self.cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.api_url}/representatives"
                params = {
                    "address": zip_code,
                    "roles": "legislatorLowerBody",
                    "key": self.api_key
                }
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Process the response
                representative_info = self._process_civic_api_response(data)
                
                # Cache the result
                await self.cache_service.set(cache_key, representative_info)
                
                # Update metrics
                if self.metrics_service:
                    await self.metrics_service.record_api_call("civic_api", response.status_code)
                
                return representative_info
                
        except httpx.HTTPError as e:
            logger.error(f"Error calling Civic API: {str(e)}")
            raise ExternalServiceError(
                "Google Civic API",
                f"Failed to retrieve representative data: {str(e)}"
            )
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise ExternalServiceError(
                "Congressional Service",
                "An unexpected error occurred"
            )
    
    def _process_civic_api_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the raw API response into a standardized format.
        
        Args:
            data: Raw API response data
            
        Returns:
            Processed representative information
        """
        try:
            divisions = data.get("divisions", {})
            officials = data.get("officials", [])
            
            if not officials:
                return {"error": "No representative found"}
            
            # Extract district information
            district_info = None
            for key, value in divisions.items():
                if "cd:" in key:
                    district_number = key.split("cd:")[-1]
                    state = key.split("/state:")[-1].split("/")[0].upper()
                    district_info = {"state": state, "number": district_number}
                    break
            
            if not district_info:
                return {"error": "District information not found"}
            
            # Get representative information
            representative = officials[0]
            return {
                "name": representative.get("name"),
                "party": representative.get("party"),
                "state": district_info["state"],
                "district": district_info["number"],
                "photo_url": representative.get("photoUrl"),
                "channels": representative.get("channels", []),
                "urls": representative.get("urls", [])
            }
            
        except Exception as e:
            logger.error(f"Error processing API response: {str(e)}")
            raise ValidationError("Failed to process representative data")
    
    async def get_committees(self, representative_name: str) -> List[str]:
        """
        Get committee assignments for a representative.
        
        Args:
            representative_name: Name of the representative
            
        Returns:
            List of committee names
        """
        # Ensure committee data is loaded
        if not self.committee_data:
            await self.load_committee_data()
        
        committees = []
        for committee, members in self.committee_data.items():
            if representative_name in members:
                committees.append(committee)
        
        return committees
    
    async def is_healthy(self) -> bool:
        """
        Check the health of the congressional service.
        
        Returns:
            True if the service is healthy, False otherwise
        """
        try:
            # Check API accessibility
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/divisions",
                    params={"key": self.api_key}
                )
                response.raise_for_status()
            
            # Check committee data
            if not self.committee_data:
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False