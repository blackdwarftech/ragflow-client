"""Chat Session API module for managing RagFlow chat sessions."""

import logging
from typing import Dict, Any, Optional, List

from ragflow_client.api.chat_assistant import ChatAssistantAPI
from ragflow_client.utils.api_utils import make_request, ResponseError

# Configure logging
logger = logging.getLogger(__name__)

class ChatSessionAPI(ChatAssistantAPI):
    """
    API client for managing RagFlow chat sessions.
    
    This class provides methods for creating, retrieving, and managing chat sessions.
    It inherits from ChatAssistantAPI to interact with chat assistants.
    """
    
    def create_session(self, dataset_name: str, session_name: str) -> Dict[str, Any]:
        """
        Create a new chat session for a dataset.
        
        Args:
            dataset_name (str): Name of the dataset to create session for
            session_name (str): Name of the session to create
        
        Returns:
            dict: API response containing session information
            
        Raises:
            ResponseError: If API returns an error response
            ValueError: If chat assistant is not found
        """
        logger.info(f"Creating chat session '{session_name}' for dataset '{dataset_name}'")
        
        # Get chat assistant information
        chat_assistant = self.list_chat_assistants(dataset_name)
        
        # Check if assistant exists
        if not chat_assistant.get("data") or len(chat_assistant["data"]) == 0:
            logger.error(f"No chat assistant found for dataset '{dataset_name}'")
            raise ValueError(f"No chat assistant found for dataset '{dataset_name}'")
        
        chat_assistant_id = chat_assistant['data'][0]['id']
        
        url = f"{self.config.api_base_url}/chats/{chat_assistant_id}/sessions"
        
        data = {
            "name": f"{session_name} - {dataset_name}"
        }
        
        try:
            response = make_request("POST", url, self.config.headers, data)
            logger.info(f"Chat session '{session_name}' created successfully for dataset '{dataset_name}'")
            return response
        except ResponseError as e:
            logger.error(f"Failed to create chat session '{session_name}': {e.message}")
            raise
    
    def list_sessions(self, dataset_name: str) -> Dict[str, Any]:
        """
        List all chat sessions for a dataset.
        
        Args:
            dataset_name (str): Name of the dataset to list sessions for
        
        Returns:
            dict: API response containing list of sessions
            
        Raises:
            ResponseError: If API returns an error response
            ValueError: If chat assistant is not found
        """
        logger.info(f"Listing chat sessions for dataset '{dataset_name}'")
        
        # Get chat assistant information
        chat_assistant = self.list_chat_assistants(dataset_name)
        
        # Check if assistant exists
        if not chat_assistant.get("data") or len(chat_assistant["data"]) == 0:
            logger.error(f"No chat assistant found for dataset '{dataset_name}'")
            raise ValueError(f"No chat assistant found for dataset '{dataset_name}'")
        
        chat_assistant_id = chat_assistant['data'][0]['id']
        
        url = f"{self.config.api_base_url}/chats/{chat_assistant_id}/sessions"
        
        try:
            response = make_request("GET", url, self.config.headers)
            
            # Log session count
            if response.get("data"):
                logger.info(f"Found {len(response['data'])} sessions for dataset '{dataset_name}'")
            else:
                logger.info(f"No chat sessions found for dataset '{dataset_name}'")
                
            return response
        except ResponseError as e:
            logger.error(f"Failed to list chat sessions for dataset '{dataset_name}': {e.message}")
            raise
    
    def get_session(self, dataset_name: str, session_name: str) -> Dict[str, Any]:
        """
        Get a specific chat session by name.
        
        Args:
            dataset_name (str): Name of the dataset containing the session
            session_name (str): Name of the session to retrieve
        
        Returns:
            dict: API response containing session information
            
        Raises:
            ResponseError: If API returns an error response
            ValueError: If chat assistant is not found
        """
        logger.info(f"Getting chat session '{session_name}' for dataset '{dataset_name}'")
        
        # Get chat assistant information
        chat_assistant = self.list_chat_assistants(dataset_name)
        
        # Check if assistant exists
        if not chat_assistant.get("data") or len(chat_assistant["data"]) == 0:
            logger.error(f"No chat assistant found for dataset '{dataset_name}'")
            raise ValueError(f"No chat assistant found for dataset '{dataset_name}'")
        
        chat_assistant_id = chat_assistant['data'][0]['id']
        
        # Use URL-encoded session name in the query
        full_session_name = f"{session_name} - {dataset_name}"
        url = f"{self.config.api_base_url}/chats/{chat_assistant_id}/sessions?name={full_session_name}"
        
        try:
            response = make_request("GET", url, self.config.headers)
            
            if not response.get("data") or len(response["data"]) == 0:
                logger.info(f"Chat session '{session_name}' not found for dataset '{dataset_name}'")
            else:
                logger.info(f"Found chat session '{session_name}' for dataset '{dataset_name}'")
                
            return response
        except ResponseError as e:
            logger.error(f"Failed to get chat session '{session_name}': {e.message}")
            raise
    
    def delete_session(self, dataset_name: str, session_name: str) -> Dict[str, Any]:
        """
        Delete a chat session.
        
        Args:
            dataset_name (str): Name of the dataset containing the session
            session_name (str): Name of the session to delete
        
        Returns:
            dict: API response or status information
            
        Raises:
            ResponseError: If API returns an error response
            ValueError: If chat session is not found
        """
        logger.info(f"Deleting chat session '{session_name}' for dataset '{dataset_name}'")
        
        # Get session ID first
        session = self.get_session(dataset_name, session_name)
        
        # Check if session exists
        if not session.get("data") or len(session["data"]) == 0:
            logger.warning(f"Chat session '{session_name}' not found for dataset '{dataset_name}'")
            return {"status": "success", "message": "No chat session found to delete"}
        
        session_id = session["data"][0]["id"]
        
        # Get chat assistant information
        chat_assistant = self.list_chat_assistants(dataset_name)
        chat_assistant_id = chat_assistant['data'][0]['id']
        
        url = f"{self.config.api_base_url}/chats/{chat_assistant_id}/sessions"
        
        data = {
            "ids": [session_id]
        }
        
        try:
            response = make_request("DELETE", url, self.config.headers, data)
            logger.info(f"Chat session '{session_name}' deleted successfully")
            return response
        except ResponseError as e:
            logger.error(f"Failed to delete chat session '{session_name}': {e.message}")
            raise 