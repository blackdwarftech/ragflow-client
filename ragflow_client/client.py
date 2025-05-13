"""Main RagFlow client that provides a simplified interface to the RagFlow API."""

import logging
from typing import Dict, Any, List, Optional, Union

from ragflow_client.config.config import Config
from ragflow_client.api.chat import ChatAPI

# Configure logging
logger = logging.getLogger(__name__)

class RagFlowClient:
    """
    Main client for interacting with the RagFlow API.
    
    This class provides a simplified interface to all RagFlow functionality,
    including dataset management, document handling, and chat capabilities.
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the RagFlow client.
        
        Args:
            api_key (str, optional): RagFlow API key. If not provided, will try to load from environment.
            base_url (str, optional): RagFlow base URL. If not provided, will try to load from environment.
            
        Raises:
            ValueError: If required credentials cannot be found in environment variables.
        """
        # Initialize configuration
        self.config = Config(api_key=api_key, base_url=base_url)
        
        # Log initialization without exposing credentials
        if self.config.api_key and self.config.base_url:
            logger.info(f"Initialized RagFlow client with provided credentials")
        elif self.config.api_key:
            logger.info(f"Initialized RagFlow client with provided API key and environment URL")
        elif self.config.base_url:
            logger.info(f"Initialized RagFlow client with environment API key and provided URL")
        else:
            logger.info(f"Initialized RagFlow client with environment credentials")
        
        # Initialize API client
        self.api = ChatAPI(self.config)
    
    def create_dataset(self, dataset_name: str) -> Dict[str, Any]:
        """
        Create a new dataset.
        
        Args:
            dataset_name (str): Name of the dataset to create
        
        Returns:
            dict: API response containing dataset information
            
        Raises:
            ValueError: If required credentials are missing
            ResponseError: If API returns an error response
        """
        self.config.validate()
        return self.api.create_dataset(dataset_name)
    
    def get_dataset(self, dataset_name: str) -> Dict[str, Any]:
        """
        Get dataset information by name.
        
        Args:
            dataset_name (str): Name of the dataset to retrieve
        
        Returns:
            dict: Dataset information
            
        Raises:
            ValueError: If required credentials are missing or dataset is not found
        """
        self.config.validate()
        return self.api.get_dataset(dataset_name)
    
    def delete_dataset(self, dataset_name: str) -> bool:
        """
        Delete a dataset by name.
        
        Args:
            dataset_name (str): Name of the dataset to delete
        
        Returns:
            bool: True if deletion was successful, False otherwise
            
        Raises:
            ValueError: If required credentials are missing
        """
        self.config.validate()
        return self.api.delete_dataset(dataset_name)
    
    def upload_document(self, 
                        dataset_name: str, 
                        file_paths: Union[str, List[str]], 
                        show_progress: bool = True) -> Dict[str, Any]:
        """
        Upload documents to a dataset.
        
        Args:
            dataset_name (str): Name of the dataset to upload documents to
            file_paths (str or list): Path to file or list of file paths to upload
            show_progress (bool, optional): Whether to show progress bar. Defaults to True.
        
        Returns:
            dict: Upload status and list of uploaded documents
            
        Raises:
            ValueError: If required credentials are missing or dataset is not found
            FileNotFoundError: If any of the files don't exist
        """
        self.config.validate()
        
        # Convert single file path to list
        if isinstance(file_paths, str):
            file_paths = [file_paths]
            
        return self.api.upload_document(dataset_name, file_paths, show_progress)
    
    def list_documents(self, dataset_name: str) -> List[Dict[str, Any]]:
        """
        List all documents in a dataset.
        
        Args:
            dataset_name (str): Name of the dataset to list documents from
        
        Returns:
            list: List of document information dictionaries
            
        Raises:
            ValueError: If required credentials are missing or dataset is not found
        """
        self.config.validate()
        return self.api.list_documents(dataset_name)
    
    def delete_documents(self, dataset_name: str, document_ids: Optional[List[str]] = None) -> bool:
        """
        Delete documents from a dataset.
        
        Args:
            dataset_name (str): Name of the dataset containing documents to delete
            document_ids (list, optional): List of document IDs to delete. 
                                          If None, deletes all documents. Defaults to None.
        
        Returns:
            bool: True if deletion was successful, False otherwise
            
        Raises:
            ValueError: If required credentials are missing
        """
        self.config.validate()
        return self.api.delete_documents(dataset_name, document_ids)
    
    def create_chat_assistant(self, 
                              dataset_name: str, 
                              temperature: float = 0.3, 
                              top_p: float = 1.0, 
                              presence_penalty: float = 0.4) -> Dict[str, Any]:
        """
        Create a new chat assistant for a dataset.
        
        Args:
            dataset_name (str): Name of the dataset to create assistant for
            temperature (float, optional): LLM temperature parameter. Defaults to 0.3.
            top_p (float, optional): LLM top_p parameter. Defaults to 1.0.
            presence_penalty (float, optional): LLM presence penalty. Defaults to 0.4.
        
        Returns:
            dict: API response containing chat assistant information
            
        Raises:
            ValueError: If required credentials are missing or dataset is not found
            ResponseError: If API returns an error response
        """
        self.config.validate()
        return self.api.create_chat_assistant(
            dataset_name=dataset_name,
            temperature=temperature,
            top_p=top_p,
            presence_penalty=presence_penalty
        )
    
    def create_session(self, dataset_name: str, session_name: str) -> Dict[str, Any]:
        """
        Create a new chat session for a dataset.
        
        Args:
            dataset_name (str): Name of the dataset to create session for
            session_name (str): Name of the session to create
        
        Returns:
            dict: API response containing session information
            
        Raises:
            ValueError: If required credentials are missing or chat assistant is not found
            ResponseError: If API returns an error response
        """
        self.config.validate()
        return self.api.create_session(dataset_name, session_name)
    
    def chat(self, 
             dataset_name: str, 
             session_name: str, 
             user_message: str,
             stream: bool = False) -> Union[Dict[str, Any], str]:
        """
        Send a chat message and get a response.
        
        Args:
            dataset_name (str): Name of the dataset to chat with
            session_name (str): Name of the chat session to use
            user_message (str): User's message to send
            stream (bool, optional): Whether to stream the response. Defaults to False.
        
        Returns:
            Union[dict, str]: Either the full response dict or just the answer string
                              depending on return_full_response
            
        Raises:
            ValueError: If required credentials are missing or chat assistant/session not found
            ResponseError: If API returns an error response
        """
        self.config.validate()
        response = self.api.chat(dataset_name, session_name, user_message, stream)
        
        # For convenience, return just the answer string if successful
        if response.get("status") == "success" and response.get("answer"):
            return response["answer"]
        
        return response
    
    def list_sessions(self, dataset_name: str) -> Dict[str, Any]:
        """
        List all chat sessions for a dataset.
        
        Args:
            dataset_name (str): Name of the dataset to list sessions for
        
        Returns:
            dict: API response containing list of sessions
            
        Raises:
            ValueError: If required credentials are missing or chat assistant not found
            ResponseError: If API returns an error response
        """
        self.config.validate()
        return self.api.list_sessions(dataset_name)
    
    def delete_session(self, dataset_name: str, session_name: str) -> Dict[str, Any]:
        """
        Delete a chat session.
        
        Args:
            dataset_name (str): Name of the dataset containing the session
            session_name (str): Name of the session to delete
        
        Returns:
            dict: API response or status information
            
        Raises:
            ValueError: If required credentials are missing or chat session not found
            ResponseError: If API returns an error response
        """
        self.config.validate()
        return self.api.delete_session(dataset_name, session_name) 