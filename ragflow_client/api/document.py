"""Document API module for interacting with RagFlow documents."""

import json
import time
import logging
from typing import Dict, Any, List, Optional
import os
from tqdm import tqdm

from ragflow_client.config.config import Config
from ragflow_client.api.dataset import DatasetAPI
from ragflow_client.utils.api_utils import make_request, ResponseError

# Configure logging
logger = logging.getLogger(__name__)

class DocumentAPI(DatasetAPI):
    """
    API client for managing RagFlow documents.
    
    This class provides methods for uploading, listing, and deleting documents.
    It inherits from DatasetAPI to interact with datasets.
    """
    
    def upload_document(self, 
                        dataset_name: str, 
                        file_paths: List[str], 
                        show_progress: bool = True, 
                        polling_interval: float = 0.5) -> Dict[str, Any]:
        """
        Upload documents to a dataset and wait for processing to complete.
        
        Args:
            dataset_name (str): Name of the dataset to upload documents to
            file_paths (list): List of file paths to upload
            show_progress (bool, optional): Whether to show progress bar. Defaults to True.
            polling_interval (float, optional): Time between polling for status. Defaults to 0.5.
        
        Returns:
            dict: Upload status and list of uploaded documents
            
        Raises:
            FileNotFoundError: If any of the files don't exist
            ResponseError: If API returns an error response
            ValueError: If dataset is not found
        """
        # First verify all files exist
        for file_path in file_paths:
            if not os.path.isfile(file_path):
                logger.error(f"File not found: {file_path}")
                raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get the dataset
        dataset = self.get_dataset(dataset_name=dataset_name)
        if not dataset.get("id"):
            logger.error(f"Dataset '{dataset_name}' not found")
            raise ValueError(f"Dataset '{dataset_name}' not found")
        
        dataset_id = dataset['id']
        
        logger.info(f"Uploading {len(file_paths)} document(s) to dataset '{dataset_name}'")
        
        # Display file names being uploaded
        for i, file_path in enumerate(file_paths):
            file_name = os.path.basename(file_path)
            logger.info(f"[{i+1}/{len(file_paths)}] Uploading: {file_name}")
        
        url = f"{self.config.api_base_url}/datasets/{dataset_id}/documents"
        
        # Create file objects for upload
        files = []
        try:
            for file_path in file_paths:
                file_name = os.path.basename(file_path)
                files.append(('file', (file_name, open(file_path, 'rb'), 'application/octet-stream')))
            
            # Upload files
            headers_without_content_type = self.config.get_headers_without_content_type()
            make_request("POST", url, headers_without_content_type, files=files)
            
            logger.info(f"All documents uploaded successfully, starting processing...")
        finally:
            # Close file handles
            for _, (_, file_obj, _) in files:
                file_obj.close()
        
        # List documents and parse any that aren't already done
        documents = self.list_documents(dataset_name=dataset_name)
        docs_to_parse = [doc for doc in documents if doc.get("run") != "DONE"]
        
        if docs_to_parse:
            doc_ids = [doc["id"] for doc in docs_to_parse]
            logger.info(f"Processing {len(doc_ids)} documents...")
            self.parse_documents(dataset_name=dataset_name, document_ids=doc_ids)
        
        # Wait for documents to be processed
        if show_progress:
            with tqdm(total=100, desc="Processing documents", unit="%") as pbar:
                prev_remaining = len(docs_to_parse)
                while True:
                    unparsed_docs = self.parsed_document_checker(dataset_name=dataset_name)
                    
                    if unparsed_docs == 0:
                        pbar.update(100 - pbar.n)  # Complete the progress bar
                        break
                    
                    # Calculate progress based on remaining docs
                    if prev_remaining > 0:
                        progress = int((prev_remaining - unparsed_docs) / prev_remaining * (100 - pbar.n))
                        if progress > 0:
                            pbar.update(progress)
                            prev_remaining = unparsed_docs
                    
                    time.sleep(polling_interval)
        else:
            # Wait without progress bar
            while self.parsed_document_checker(dataset_name=dataset_name) > 0:
                time.sleep(polling_interval)
        
        logger.info(f"Document processing completed")
        
        # Get final documents list
        final_documents = self.list_documents(dataset_name=dataset_name)
        
        return {
            "documents": final_documents,
            "status": "success",
            "count": len(final_documents)
        }
    
    def list_documents(self, dataset_name: str) -> List[Dict[str, Any]]:
        """
        List all documents in a dataset.
        
        Args:
            dataset_name (str): Name of the dataset to list documents from
        
        Returns:
            list: List of document information dictionaries
            
        Raises:
            ValueError: If dataset is not found
        """
        logger.info(f"Listing documents in dataset '{dataset_name}'")
        
        try:
            datasets = self.rag_object.list_datasets(name=dataset_name)
            
            if not datasets:
                logger.warning(f"Dataset '{dataset_name}' not found")
                return []
            
            documents = []
            for dataset in datasets:
                doc_list = dataset.list_documents()
                for doc in doc_list:
                    documents.append(doc)
            
            # Convert document objects to dictionaries
            docs = []
            for doc in documents:
                doc_dict = {k: v for k, v in (doc.__dict__ if hasattr(doc, '__dict__') else {}).items() 
                        if not k.startswith('_')}
                docs.append(doc_dict)
            
            logger.debug(f"Found {len(docs)} documents in dataset '{dataset_name}'")
            return docs
            
        except Exception as e:
            logger.error(f"Error listing documents for dataset '{dataset_name}': {str(e)}")
            raise
    
    def get_document(self, dataset_name: str, document_id: str) -> Dict[str, Any]:
        """
        Get information about a specific document.
        
        Args:
            dataset_name (str): Name of the dataset containing the document
            document_id (str): ID of the document to retrieve
        
        Returns:
            dict: Document information
            
        Raises:
            ResponseError: If API returns an error response
            ValueError: If dataset is not found
        """
        logger.info(f"Getting document {document_id} from dataset '{dataset_name}'")
        
        dataset = self.get_dataset(dataset_name=dataset_name)
        if not dataset.get("id"):
            logger.error(f"Dataset '{dataset_name}' not found")
            raise ValueError(f"Dataset '{dataset_name}' not found")
        
        dataset_id = dataset['id']
        
        url = f"{self.config.api_base_url}/datasets/{dataset_id}/documents?id={document_id}"
        
        try:
            response = make_request("GET", url, self.config.headers)
            return response
        except ResponseError as e:
            logger.error(f"Failed to get document {document_id}: {e.message}")
            raise
    
    def parse_documents(self, dataset_name: str, document_ids: List[str]) -> Dict[str, Any]:
        """
        Start document parsing process for specified documents.
        
        Args:
            dataset_name (str): Name of the dataset containing the documents
            document_ids (list): List of document IDs to parse
        
        Returns:
            dict: API response for parse request
            
        Raises:
            ResponseError: If API returns an error response
            ValueError: If dataset is not found
        """
        logger.info(f"Starting parsing for {len(document_ids)} documents in dataset '{dataset_name}'")
        
        dataset = self.get_dataset(dataset_name=dataset_name)
        if not dataset.get("id"):
            logger.error(f"Dataset '{dataset_name}' not found")
            raise ValueError(f"Dataset '{dataset_name}' not found")
        
        dataset_id = dataset['id']
        
        url = f"{self.config.api_base_url}/datasets/{dataset_id}/chunks"
        
        data = {
            "document_ids": document_ids
        }
        
        try:
            response = make_request("POST", url, self.config.headers, data)
            return response
        except ResponseError as e:
            logger.error(f"Failed to start document parsing: {e.message}")
            raise
    
    def parsed_document_checker(self, dataset_name: str) -> int:
        """
        Check how many documents are still being processed.
        
        Args:
            dataset_name (str): Name of the dataset to check
        
        Returns:
            int: Count of documents still being processed
        """
        documents = self.list_documents(dataset_name=dataset_name)
        unparsed_doc_count = 0
        
        for doc in documents:
            if doc.get("run") != "DONE":
                unparsed_doc_count += 1
        
        return unparsed_doc_count
    
    def delete_documents(self, dataset_name: str, document_ids: Optional[List[str]] = None) -> bool:
        """
        Delete documents from a dataset.
        
        Args:
            dataset_name (str): Name of the dataset containing documents to delete
            document_ids (list, optional): List of document IDs to delete. 
                                          If None, deletes all documents. Defaults to None.
        
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        logger.info(f"Deleting documents from dataset '{dataset_name}'")
        
        try:
            datasets = self.rag_object.list_datasets(name=dataset_name)
            
            if not datasets:
                logger.warning(f"Dataset '{dataset_name}' not found")
                return False
            
            dataset = datasets[0]
            
            # If no document IDs specified, get all document IDs
            if document_ids is None:
                documents = self.list_documents(dataset_name=dataset_name)
                document_ids = [doc["id"] for doc in documents]
            
            if not document_ids:
                logger.info(f"No documents to delete in dataset '{dataset_name}'")
                return True
            
            logger.info(f"Deleting {len(document_ids)} documents")
            dataset.delete_documents(ids=document_ids)
            logger.info(f"Documents deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting documents from dataset '{dataset_name}': {str(e)}")
            return False 