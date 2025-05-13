"""API utility functions for RagFlow client."""

import logging
import json
from typing import Dict, Any, Optional, Union
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

# Configure logging
logger = logging.getLogger(__name__)

class ResponseError(Exception):
    """Exception raised for errors in API responses."""
    
    def __init__(self, status_code: int, message: str, response_data: Optional[Dict[str, Any]] = None):
        """
        Initialize ResponseError with status code and message.
        
        Args:
            status_code (int): HTTP status code
            message (str): Error message
            response_data (dict, optional): Full response data if available
        """
        self.status_code = status_code
        self.message = message
        self.response_data = response_data
        super().__init__(f"API Error (Status {status_code}): {message}")


def handle_response(response: requests.Response, expected_status_codes: list = None) -> Dict[str, Any]:
    """
    Handle API response, including error checking and logging.
    
    Args:
        response (requests.Response): Response object from requests library
        expected_status_codes (list, optional): List of status codes considered successful.
                                               Defaults to [200]
    
    Returns:
        dict: Parsed JSON response data
    
    Raises:
        ResponseError: If response status code is not as expected or JSON parsing fails
    """
    if expected_status_codes is None:
        expected_status_codes = [200]
    
    try:
        response_data = response.json()
    except ValueError:
        logger.error(f"Failed to parse response as JSON: {response.text[:100]}...")
        raise ResponseError(
            response.status_code,
            f"Invalid JSON response: {response.text[:100]}...",
        )
    
    # Log response info for debugging
    logger.debug(f"Response status: {response.status_code}")
    logger.debug(f"Response data: {json.dumps(response_data)[:500]}...")
    
    if response.status_code not in expected_status_codes:
        error_message = response_data.get('message', 'Unknown error')
        error_code = response_data.get('code', 'unknown')
        logger.error(f"API Error: {error_code} - {error_message}")
        
        raise ResponseError(
            response.status_code,
            error_message,
            response_data
        )
    
    return response_data


def make_request(
    method: str, 
    url: str, 
    headers: Dict[str, str], 
    data: Optional[Dict[str, Any]] = None,
    files: Optional[Any] = None,
    timeout: int = 30,
    expected_status_codes: Optional[list] = None
) -> Dict[str, Any]:
    """
    Make an HTTP request with proper error handling.
    
    Args:
        method (str): HTTP method (GET, POST, DELETE, etc.)
        url (str): URL to make request to
        headers (dict): Headers to include in request
        data (dict, optional): JSON data to send in request body
        files (list, optional): Files to upload
        timeout (int, optional): Request timeout in seconds. Defaults to 30.
        expected_status_codes (list, optional): List of status codes considered successful.
    
    Returns:
        dict: Parsed JSON response
    
    Raises:
        ResponseError: If API returns an error response
        ConnectionError: If connection to API fails
        Timeout: If request times out
        RequestException: For other request-related errors
    """
    if expected_status_codes is None:
        expected_status_codes = [200]
    
    logger.debug(f"Making {method} request to: {url}")
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=timeout)
        elif method.upper() == 'POST':
            if files:
                # For file uploads, don't include data as JSON
                response = requests.post(url, headers=headers, files=files, timeout=timeout)
            else:
                response = requests.post(url, headers=headers, json=data, timeout=timeout)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers, json=data, timeout=timeout)
        else:
            logger.error(f"Unsupported HTTP method: {method}")
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        return handle_response(response, expected_status_codes)
    
    except Timeout:
        logger.error(f"Request timeout: {url}")
        raise
    except ConnectionError:
        logger.error(f"Connection error: {url}")
        raise
    except RequestException as e:
        logger.error(f"Request error: {str(e)}")
        raise 