"""Chat Assistant API module for managing RagFlow chat assistants."""

import logging
from typing import Dict, Any, Optional

from ragflow_client.api.document import DocumentAPI
from ragflow_client.utils.api_utils import make_request, ResponseError
from ragflow_client.api.prompt.chat_prompt import ChatPrompt

# Configure logging
logger = logging.getLogger(__name__)

class ChatAssistantAPI(DocumentAPI):
    """
    API client for managing RagFlow chat assistants.
    
    This class provides methods for creating, retrieving, and deleting chat assistants.
    It inherits from DocumentAPI to interact with documents and datasets.
    """
    
    def create_chat_assistant(self, dataset_name: str, 
                              temperature: float = 0.50, 
                              top_p: float = 0.50, 
                              presence_penalty: float = 0.40,
                              top_n: int = 10,
                              enable_knowledge_graph: bool = True) -> Dict[str, Any]:
        """
        Create a new chat assistant for a dataset.
        
        Args:
            dataset_name (str): Name of the dataset to create assistant for
            temperature (float, optional): LLM temperature parameter. Defaults to 0.3.
            top_p (float, optional): LLM top_p parameter. Defaults to 1.0.
            presence_penalty (float, optional): LLM presence penalty. Defaults to 0.4.
            top_n (int, optional): Top N documents to consider. Defaults to 10.
            enable_knowledge_graph (bool, optional): Whether to enable knowledge graph. Defaults to True.
        
        Returns:
            dict: API response containing chat assistant information
            
        Raises:
            ResponseError: If API returns an error response
            ValueError: If dataset is not found
        """
        logger.info(f"Creating chat assistant for dataset '{dataset_name}'")
        
        # Get dataset information first
        dataset = self.get_dataset(dataset_name=dataset_name)
        if not dataset.get("id"):
            logger.error(f"Dataset '{dataset_name}' not found")
            raise ValueError(f"Dataset '{dataset_name}' not found")
        
        dataset_id = dataset['id']
        
        url = f"{self.config.api_base_url}/chats"
        
        data = {
            "name": dataset_name,
            "description": f"This is a Rag assistant for the dataset {dataset_name}",
            "dataset_ids": [dataset_id],
            "llm": {
                "temperature": temperature,
                "top_p": top_p,
                "presence_penalty": presence_penalty
            },
            "prompt": {
                "top_n": top_n,
                "knowledge_graph": enable_knowledge_graph,
                "prompt": ChatPrompt
            }
        }
        
        try:
            response = make_request("POST", url, self.config.headers, data)
            logger.info(f"Chat assistant created successfully for dataset '{dataset_name}'")
            return response
        except ResponseError as e:
            logger.error(f"Failed to create chat assistant for dataset '{dataset_name}': {e.message}")
            raise
    
    def list_chat_assistants(self, dataset_name: str) -> Dict[str, Any]:
        """
        List chat assistants for a dataset.
        
        Args:
            dataset_name (str): Name of the dataset to list assistants for
        
        Returns:
            dict: API response containing list of chat assistants
            
        Raises:
            ResponseError: If API returns an error response
        """
        logger.info(f"Listing chat assistants for dataset '{dataset_name}'")
        
        url = f"{self.config.api_base_url}/chats?name={dataset_name}"
        
        try:
            response = make_request("GET", url, self.config.headers)
            
            # Check if any assistants found
            if not response.get("data") or len(response["data"]) == 0:
                logger.info(f"No chat assistants found for dataset '{dataset_name}'")
            else:
                logger.info(f"Found {len(response['data'])} chat assistants for dataset '{dataset_name}'")
            
            return response
        except ResponseError as e:
            logger.error(f"Failed to list chat assistants for dataset '{dataset_name}': {e.message}")
            raise
    
    def delete_chat_assistant(self, dataset_name: str) -> Dict[str, Any]:
        """
        Delete a chat assistant for a dataset.
        
        Args:
            dataset_name (str): Name of the dataset to delete assistant for
        
        Returns:
            dict: API response or status information
            
        Raises:
            ResponseError: If API returns an error response
        """
        logger.info(f"Deleting chat assistant for dataset '{dataset_name}'")
        
        try:
            # Get assistant ID first
            chat_assistant = self.list_chat_assistants(dataset_name)
            
            # Check if assistant exists
            if not chat_assistant.get("data") or len(chat_assistant["data"]) == 0:
                logger.info(f"No chat assistant found for dataset '{dataset_name}'")
                return {"status": "success", "message": "No chat assistant found to delete"}
            
            chat_assistant_id = chat_assistant['data'][0]['id']
            
            url = f"{self.config.api_base_url}/chats"
            
            data = {
                "ids": [chat_assistant_id]
            }
            
            response = make_request("DELETE", url, self.config.headers, data)
            logger.info(f"Chat assistant deleted successfully for dataset '{dataset_name}'")
            return response
            
        except ResponseError as e:
            logger.error(f"Failed to delete chat assistant for dataset '{dataset_name}': {e.message}")
            raise
        except Exception as e:
            logger.warning(f"Error during chat assistant deletion: {str(e)}")
            return {"status": "failed", "message": str(e)} 