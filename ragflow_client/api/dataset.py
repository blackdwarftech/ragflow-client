"""Dataset API module for interacting with RagFlow datasets."""

import json
import logging
from typing import Dict, Any, Optional, List

from ragflow_sdk import RAGFlow

from ragflow_client.config.config import Config
from ragflow_client.utils.api_utils import make_request, ResponseError

# Configure logging
logger = logging.getLogger(__name__)

class DatasetAPI:
    """
    API client for managing RagFlow datasets.
    
    This class provides methods for creating, retrieving, and deleting datasets.
    It requires valid RagFlow credentials to function.
    """
    
    def __init__(self, config: Config, rag_object: Optional[RAGFlow] = None):
        """
        Initialize the Dataset API client.
        
        Args:
            config (Config): Configuration object with API credentials
            rag_object (RAGFlow, optional): Existing RAGFlow object to use
        """
        self.config = config
        self.config.validate()  # Ensure we have valid credentials
        
        # Initialize RAGFlow SDK object if not provided
        if rag_object:
            self.rag_object = rag_object
        else:
            self.rag_object = RAGFlow(
                api_key=self.config.api_key,
                base_url=self.config.base_url
            )
    
    def create_dataset(self, dataset_name: str) -> Dict[str, Any]:
        """
        Create a new dataset.
        
        Args:
            dataset_name (str): Name of the dataset to create
        
        Returns:
            dict: API response containing dataset information
        
        Raises:
            ResponseError: If API returns an error response
        """
        logger.info(f"Creating dataset: {dataset_name}")
        
        url = f"{self.config.api_base_url}/datasets"
        
        data = {
            "name": dataset_name,
            "permission": "me",
            "chunk_method": "naive",
            "pagerank": 50,
            "parser_config": {
                "chunk_token_num": 1024,
                "html4excel": True,
                "delimiter": "\n",
                "raptor": {
                    "use_raptor": False
                },
                "graphrag": {
                    "use_graphrag": True,
                    "entity_types": [
                        "person", "geo", "event", "category", "services", "product",
                        "company", "organization/corporation", "account", "transcation",
                        "place/location", "role", "skill", "document/article", "project",
                        "law", "asset", "contact numbers", "email address"
                    ],
                    "method": "Light"
                }
            }
        }
        
        try:
            response = make_request("POST", url, self.config.headers, data)
            logger.info(f"Dataset '{dataset_name}' created successfully")
            return response
        except ResponseError as e:
            logger.error(f"Failed to create dataset '{dataset_name}': {e.message}")
            raise
    
    def get_dataset(self, dataset_name: str) -> Dict[str, Any]:
        """
        Get dataset information by name.
        
        Args:
            dataset_name (str): Name of the dataset to retrieve
        
        Returns:
            dict: Dataset information
        
        Raises:
            ValueError: If dataset is not found
        """
        logger.info(f"Getting dataset: {dataset_name}")
        
        try:
            datasets = self.rag_object.list_datasets(name=dataset_name)
            
            if not datasets:
                logger.warning(f"Dataset '{dataset_name}' not found")
                return {"id": None, "name": dataset_name, "error": "Dataset not found"}
            
            # Get the first matching dataset
            dataset = datasets[0]
            
            # Extract attributes from dataset object
            dataset_dict = dataset.__dict__ if hasattr(dataset, '__dict__') else {}
            clean_dict = {k: v for k, v in dataset_dict.items() if not k.startswith('_')}
            
            logger.debug(f"Retrieved dataset: {json.dumps(clean_dict, default=str)[:100]}...")
            return clean_dict
            
        except Exception as e:
            logger.error(f"Error retrieving dataset '{dataset_name}': {str(e)}")
            raise
    
    def delete_dataset(self, dataset_name: str) -> bool:
        """
        Delete a dataset by name.
        
        Args:
            dataset_name (str): Name of the dataset to delete
        
        Returns:
            bool: True if deletion was successful, False otherwise
        
        Raises:
            ResponseError: If API returns an error response
        """
        logger.info(f"Deleting dataset: {dataset_name}")
        
        try:
            # Get dataset ID first
            dataset = self.get_dataset(dataset_name=dataset_name)
            
            if not dataset.get("id"):
                logger.warning(f"Cannot delete dataset '{dataset_name}': Not found")
                return False
            
            dataset_id = dataset["id"]
            
            # Import here to avoid circular imports
            from ragflow_client.api.chat_assistant import ChatAssistantAPI
            
            # Try to delete associated chat assistant first
            try:
                chat_api = ChatAssistantAPI(self.config, self.rag_object)
                chat_api.delete_chat_assistant(dataset_name)
                logger.info(f"Deleted chat assistant for dataset '{dataset_name}'")
            except Exception as e:
                logger.warning(f"Could not delete chat assistant: {str(e)}")
            
            # Delete the dataset
            self.rag_object.delete_datasets(ids=[dataset_id])
            logger.info(f"Dataset '{dataset_name}' deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting dataset '{dataset_name}': {str(e)}")
            return False 