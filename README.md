# RagFlow Client

A Python client library for interacting with the RagFlow API. This package provides a clean interface for creating and managing datasets, documents, and chat assistants through the RagFlow platform.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
  - [Dataset Management](#dataset-management)
  - [Document Management](#document-management)
  - [Chat Assistant Management](#chat-assistant-management)
  - [Session Management](#session-management)
  - [Chat Functionality](#chat-functionality)
- [Examples](#examples)
- [CLI Usage](#cli-usage)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Installation

You can install the RagFlow client package using pip:

```bash
pip install ragflow-client
```

## Configuration

The client requires RagFlow API credentials to function. You can provide these in two ways:

### Using environment variables

Create a `.env` file in your project root:

```
RAGFLOW_API_KEY=your_api_key_here
RAGFLOW_BASE_URL=https://your.ragflow.instance
```

Then the client will automatically load these credentials:

```python
from ragflow_client import RagFlowClient

client = RagFlowClient()  # Loads credentials from environment variables
```

### Passing credentials directly

```python
from ragflow_client import RagFlowClient

client = RagFlowClient(
    api_key="your_api_key_here",
    base_url="https://your.ragflow.instance"
)
```

## Getting Started

Here's a quick example to get started with the RagFlow client:

```python
from ragflow_client import RagFlowClient

# Initialize client
client = RagFlowClient()

# Create a dataset
dataset_name = "my_dataset"
client.create_dataset(dataset_name)

# Upload documents
file_paths = ["document1.pdf", "document2.docx"]
client.upload_document(dataset_name, file_paths)

# Create a session for chat
session_name = "my_session"
client.create_session(dataset_name, session_name)

# Chat with the documents
response = client.chat(dataset_name, session_name, "What information can you provide about these documents?")
print(response)
```

## API Reference

### Dataset Management

#### Create a dataset

```python
dataset_result = client.create_dataset(dataset_name)
```

**Parameters:**
- `dataset_name` (str): Name of the dataset to create

**Returns:**
- dict: API response containing dataset information

**Raises:**
- ValueError: If required credentials are missing
- ResponseError: If API returns an error response

#### Get dataset information

```python
dataset = client.get_dataset(dataset_name)
```

**Parameters:**
- `dataset_name` (str): Name of the dataset to retrieve

**Returns:**
- dict: Dataset information including ID and other properties

**Raises:**
- ValueError: If required credentials are missing or dataset is not found

#### Delete a dataset

```python
success = client.delete_dataset(dataset_name)
```

**Parameters:**
- `dataset_name` (str): Name of the dataset to delete

**Returns:**
- bool: True if deletion was successful, False otherwise

**Raises:**
- ValueError: If required credentials are missing

### Document Management

#### Upload documents

```python
# Upload a single document
result = client.upload_document(dataset_name, "path/to/document.pdf")

# Upload multiple documents
result = client.upload_document(dataset_name, ["doc1.pdf", "doc2.docx"])

# Upload without progress bar
result = client.upload_document(dataset_name, file_paths, show_progress=False)
```

**Parameters:**
- `dataset_name` (str): Name of the dataset to upload documents to
- `file_paths` (str or list): Path to file or list of file paths to upload
- `show_progress` (bool, optional): Whether to show progress bar. Defaults to True.

**Returns:**
- dict: Upload status and list of uploaded documents

**Raises:**
- ValueError: If required credentials are missing or dataset is not found
- FileNotFoundError: If any of the files don't exist

#### List documents

```python
documents = client.list_documents(dataset_name)
```

**Parameters:**
- `dataset_name` (str): Name of the dataset to list documents from

**Returns:**
- list: List of document information dictionaries

**Raises:**
- ValueError: If required credentials are missing or dataset is not found

#### Delete documents

```python
# Delete specific documents
success = client.delete_documents(dataset_name, document_ids=["doc_id1", "doc_id2"])

# Delete all documents in dataset
success = client.delete_documents(dataset_name)
```

**Parameters:**
- `dataset_name` (str): Name of the dataset containing documents to delete
- `document_ids` (list, optional): List of document IDs to delete. If None, deletes all documents.

**Returns:**
- bool: True if deletion was successful, False otherwise

**Raises:**
- ValueError: If required credentials are missing

### Chat Assistant Management

#### Create a chat assistant

```python
assistant = client.create_chat_assistant(
    dataset_name, 
    temperature=0.3, 
    top_p=1.0, 
    presence_penalty=0.4
)
```

**Parameters:**
- `dataset_name` (str): Name of the dataset to create assistant for
- `temperature` (float, optional): LLM temperature parameter. Defaults to 0.3.
- `top_p` (float, optional): LLM top_p parameter. Defaults to 1.0.
- `presence_penalty` (float, optional): LLM presence penalty. Defaults to 0.4.

**Returns:**
- dict: API response containing chat assistant information

**Raises:**
- ValueError: If required credentials are missing or dataset is not found
- ResponseError: If API returns an error response

**Note:** In most cases, you don't need to explicitly create a chat assistant as it will be automatically created when needed by the chat method.

### Session Management

#### Create a session

```python
session = client.create_session(dataset_name, session_name)
```

**Parameters:**
- `dataset_name` (str): Name of the dataset to create session for
- `session_name` (str): Name of the session to create

**Returns:**
- dict: API response containing session information

**Raises:**
- ValueError: If required credentials are missing or chat assistant is not found
- ResponseError: If API returns an error response

#### List sessions

```python
sessions = client.list_sessions(dataset_name)
```

**Parameters:**
- `dataset_name` (str): Name of the dataset to list sessions for

**Returns:**
- dict: API response containing list of sessions

**Raises:**
- ValueError: If required credentials are missing or chat assistant not found
- ResponseError: If API returns an error response

#### Delete a session

```python
result = client.delete_session(dataset_name, session_name)
```

**Parameters:**
- `dataset_name` (str): Name of the dataset containing the session
- `session_name` (str): Name of the session to delete

**Returns:**
- dict: API response or status information

**Raises:**
- ValueError: If required credentials are missing or chat session not found
- ResponseError: If API returns an error response

### Chat Functionality

#### Send a chat message

```python
# Simple usage - returns just the answer string
answer = client.chat(dataset_name, session_name, user_message)

# Get full response details
response = client.chat(dataset_name, session_name, user_message, stream=False)
```

**Parameters:**
- `dataset_name` (str): Name of the dataset to chat with
- `session_name` (str): Name of the chat session to use
- `user_message` (str): User's message to send
- `stream` (bool, optional): Whether to stream the response. Defaults to False.

**Returns:**
- str or dict: If successful, returns the answer string. Otherwise, returns full response dict.

**Raises:**
- ValueError: If required credentials are missing or chat assistant/session not found
- ResponseError: If API returns an error response

**Note:** If the session doesn't exist, it will be created automatically. If the chat assistant doesn't exist, it will also be created automatically.

## Examples

### Complete Workflow Example

```python
import os
from ragflow_client import RagFlowClient

# Initialize client
client = RagFlowClient()

# Create a dataset
dataset_name = "research_papers"
client.create_dataset(dataset_name)
print(f"Dataset '{dataset_name}' created")

# Upload documents
pdf_folder = "research_pdfs"
files = ["document1.pdf", "document2.docx", "document3.txt", "document4.xlsx"]
upload_result = client.upload_document(dataset_name, pdf_files)
print(f"Uploaded {upload_result['count']} documents")

# Create a session
session_name = "research_session"

# Ask questions
questions = [
    "What are the main findings from these research papers?",
    "Summarize the methodologies used in these papers",
    "What are the common limitations mentioned in these studies?"
]

for question in questions:
    print(f"\nQ: {question}")
    answer = client.chat(dataset_name, session_name, question)
    print(f"A: {answer}")

# Cleanup
client.delete_session(dataset_name, session_name)
client.delete_documents(dataset_name)
client.delete_dataset(dataset_name)
print("Cleanup completed")
```

### Error Handling Example

```python
from ragflow_client import RagFlowClient
from ragflow_client.utils.api_utils import ResponseError

client = RagFlowClient()

try:
    # Try to get a non-existent dataset
    dataset = client.get_dataset("non_existent_dataset")
    
    # Check if dataset was found
    if not dataset.get("id"):
        print("Dataset not found, creating it...")
        client.create_dataset("non_existent_dataset")
    
    # Try to chat with a non-existent session
    response = client.chat("non_existent_dataset", "new_session", "Hello")
    print(f"Response: {response}")
    
except ValueError as e:
    print(f"Validation error: {str(e)}")
except ResponseError as e:
    print(f"API error (Status {e.status_code}): {e.message}")
except Exception as e:
    print(f"Unexpected error: {str(e)}")
```

## CLI Usage

The RagFlow client package also includes a command-line interface for interacting with the API:

```bash
# Show help
ragflow --help

# Create a dataset
ragflow dataset create my_dataset

# Upload documents
ragflow document upload my_dataset document1.pdf document2.pdf

# Create a session
ragflow chat create-session my_dataset my_session

# List all sessions
ragflow chat list-sessions my_dataset

# Send a chat message
ragflow chat send my_dataset my_session "What information is in these documents?"

# Interactive chat mode
ragflow chat interactive my_dataset my_session
```

You can provide API credentials via environment variables or command-line options:

```bash
ragflow --api-key YOUR_API_KEY --base-url YOUR_BASE_URL dataset create my_dataset
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**:
   - Ensure your API key is correct
   - Check that your base URL has the correct format without trailing slashes

2. **Document Upload Issues**:
   - Verify file paths are correct and the files exist
   - Check file permissions
   - Ensure document formats are supported (PDF, DOCX, TXT, etc.)

3. **Chat Response Issues**:
   - Verify the dataset contains properly parsed documents
   - Ensure the question is clear and relevant to the document content

### Enabling Debug Logging

To help troubleshoot issues, you can enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

client = RagFlowClient()
# The client will now log detailed debug information
```

## Contributing

Contributions to RagFlow Client are welcome! Please feel free to submit a Pull Request.
