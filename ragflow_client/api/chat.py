"""Chat API module for interacting with RagFlow chat completions."""

import logging
from typing import Dict, Any, Optional, List

from ragflow_client.api.chat_session import ChatSessionAPI
from ragflow_client.utils.api_utils import make_request, ResponseError

# Configure logging
logger = logging.getLogger(__name__)

class ChatAPI(ChatSessionAPI):
    """
    API client for interacting with RagFlow chat functionality.
    
    This class provides methods for sending chat messages and getting responses.
    It inherits from ChatSessionAPI to interact with chat sessions.
    """
    
    def chat(self, 
             dataset_name: str, 
             session_name: str, 
             user_message: str, 
             stream: bool = False) -> Dict[str, Any]:
        """
        Send a chat message and get a response.
        
        Args:
            dataset_name (str): Name of the dataset to chat with
            session_name (str): Name of the chat session to use
            user_message (str): User's message to send
            stream (bool, optional): Whether to stream the response. Defaults to False.
        
        Returns:
            dict: API response containing the chat assistant's answer
            
        Raises:
            ResponseError: If API returns an error response
            ValueError: If chat assistant or session is not found
        """
        logger.info(f"Sending chat message to '{dataset_name}' in session '{session_name}'")
        
        # Check the chat assistant and create if needed
        try:
            chat_assistant = self.list_chat_assistants(dataset_name)
            
            # Create chat assistant if it doesn't exist
            if not chat_assistant.get("data") or len(chat_assistant["data"]) == 0 or chat_assistant.get("code") == 102:
                logger.info(f"Creating chat assistant for dataset '{dataset_name}'")
                self.create_chat_assistant(dataset_name=dataset_name)
                chat_assistant = self.list_chat_assistants(dataset_name)
                
                if not chat_assistant.get("data") or len(chat_assistant["data"]) == 0:
                    logger.error(f"Failed to create chat assistant for dataset '{dataset_name}'")
                    raise ValueError(f"Failed to create chat assistant for dataset '{dataset_name}'")
            
            chat_assistant_id = chat_assistant['data'][0]['id']
            
            # Check chat session and create if needed
            session = self.get_session(dataset_name, session_name)
            
            # Create session if it doesn't exist
            if not session.get("data") or len(session["data"]) == 0:
                logger.info(f"Creating chat session '{session_name}' for dataset '{dataset_name}'")
                self.create_session(dataset_name, session_name)
                session = self.get_session(dataset_name, session_name)
                
                if not session.get("data") or len(session["data"]) == 0:
                    logger.error(f"Failed to create chat session '{session_name}'")
                    raise ValueError(f"Failed to create chat session '{session_name}'")
            
            session_id = session['data'][0]['id']
            
            # Send chat request
            url = f"{self.config.api_base_url}/chats/{chat_assistant_id}/completions"
            
            data = {
                "question": user_message,
                "stream": stream,
                "session_id": session_id
            }
            
            try:
                logger.debug(f"Sending chat request: {data}")
                response = make_request("POST", url, self.config.headers, data)
                
                # Extract answer from response
                if response.get("data") and response["data"].get("answer"):
                    answer = response["data"]["answer"]
                    logger.info(f"Received chat response ({len(answer)} chars)")
                    return {
                        "status": "success",
                        "answer": answer,
                        "session_id": session_id,
                        "chat_assistant_id": chat_assistant_id
                    }
                else:
                    logger.warning("Received empty or invalid response from chat API")
                    return {
                        "status": "error",
                        "message": "Empty or invalid response from chat API",
                        "raw_response": response
                    }
                    
            except ResponseError as e:
                logger.error(f"Chat API error: {e.message}")
                raise
                
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            raise 