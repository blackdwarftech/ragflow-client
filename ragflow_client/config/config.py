"""Configuration management for RagFlow client."""

import os
from dotenv import load_dotenv
from typing import Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Config:
    """
    Configuration manager for RagFlow client.
    
    Handles loading credentials from environment variables or from direct parameters.
    Validates that required credentials are provided before allowing operations.
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the configuration with optional direct credentials.
        
        Args:
            api_key (str, optional): RagFlow API key. If not provided, will try to load from environment.
            base_url (str, optional): RagFlow base URL. If not provided, will try to load from environment.
        """
        # Try to load environment variables
        load_dotenv()
        
        # Use provided credentials or fall back to environment variables
        self.api_key = api_key or os.environ.get("RAGFLOW_API_KEY")
        self.base_url = base_url or os.environ.get("RAGFLOW_BASE_URL")
        
        if not self.api_key or not self.base_url:
            missing = []
            if not self.api_key:
                missing.append("RAGFLOW_API_KEY")
            if not self.base_url:
                missing.append("RAGFLOW_BASE_URL")
            
            logger.warning(f"Missing required configuration: {', '.join(missing)}")
        
        # Construct API base URL
        self.api_base_url = f"{self.base_url}/api/v1" if self.base_url else None
        
        # Prepare headers for API requests
        self.headers = None
        if self.api_key:
            self.headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
    
    def validate(self) -> bool:
        """
        Validate that all required configuration is present.
        
        Returns:
            bool: True if configuration is valid, False otherwise.
        
        Raises:
            ValueError: If required configuration is missing.
        """
        if not self.api_key or not self.base_url:
            missing = []
            if not self.api_key:
                missing.append("RAGFLOW_API_KEY")
            if not self.base_url:
                missing.append("RAGFLOW_BASE_URL")
            
            error_msg = f"Missing required configuration: {', '.join(missing)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        return True
    
    def get_headers_without_content_type(self) -> dict:
        """
        Get headers without Content-Type for file uploads.
        
        Returns:
            dict: Headers dictionary without Content-Type header.
        """
        if not self.headers:
            self.validate()  # Will raise error if missing credentials
            
        return {k: v for k, v in self.headers.items() if k.lower() != 'content-type'} 