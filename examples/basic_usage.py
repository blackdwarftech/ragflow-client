#!/usr/bin/env python3
"""Official basic usage example for ragflow-client."""

import os
from ragflow_client import RagFlowClient
from ragflow_client.utils.api_utils import ResponseError

# Initialize client with environment variables
client = RagFlowClient()

# Configuration
dataset_name = "example_dataset"
session_name = "example_session"
document_paths = [
    "document.pdf", 
    "document2.xlsx" 
]

try:
    # Dataset lifecycle
    print("\n=== Dataset Management ===")
    client.create_dataset(dataset_name)
    print(f"Created dataset: {dataset_name}")
    
    # Document operations
    print("\n=== Document Processing ===")
    upload_result = client.upload_document(dataset_name, document_paths)
    print(f"Uploaded {upload_result['count']} documents")
    
    # Chat workflow
    print("\n=== Chat Session ===")
    client.create_session(dataset_name, session_name)
    
    questions = [
        "Summarize the key features of this client library",
        "What installation steps are required?",
        "How do I handle API errors?"
    ]
    
    for question in questions:
        print(f"\nQ: {question}")
        response = client.chat(dataset_name, session_name, question)
        print(f"A: {response}\n{'='*50}")

except ResponseError as e:
    print(f"API Error ({e.status_code}): {e.message}")
except FileNotFoundError as e:
    print(f"Missing file: {str(e)}")
except Exception as e:
    print(f"Unexpected error: {str(e)}")
finally:
    print("\n=== Cleanup ===")
    client.delete_documents(dataset_name)
    client.delete_dataset(dataset_name)
    print("Cleaned up resources")

if __name__ == "__main__":
    print("=== RagFlow Client Basic Example ===")
