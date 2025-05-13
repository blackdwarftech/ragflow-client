#!/usr/bin/env python3
"""Command line interface for ragflow-client."""

import os
import sys
import argparse
import logging
import json
from typing import List, Optional, Dict, Any

from ragflow_client import RagFlowClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ragflow-cli")

def setup_parser() -> argparse.ArgumentParser:
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(
        description="RagFlow Client CLI - Interact with RagFlow from the command line",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Global arguments
    parser.add_argument("--api-key", help="RagFlow API key (overrides environment variable)")
    parser.add_argument("--base-url", help="RagFlow base URL (overrides environment variable)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Dataset commands
    dataset_parser = subparsers.add_parser("dataset", help="Dataset operations")
    dataset_subparsers = dataset_parser.add_subparsers(dest="dataset_command", help="Dataset command")
    
    # Create dataset
    create_dataset_parser = dataset_subparsers.add_parser("create", help="Create a dataset")
    create_dataset_parser.add_argument("name", help="Dataset name")
    
    # Get dataset
    get_dataset_parser = dataset_subparsers.add_parser("get", help="Get dataset information")
    get_dataset_parser.add_argument("name", help="Dataset name")
    
    # Delete dataset
    delete_dataset_parser = dataset_subparsers.add_parser("delete", help="Delete a dataset")
    delete_dataset_parser.add_argument("name", help="Dataset name")
    
    # List datasets - not directly supported by API, but could be added
    
    # Document commands
    document_parser = subparsers.add_parser("document", help="Document operations")
    document_subparsers = document_parser.add_subparsers(dest="document_command", help="Document command")
    
    # Upload document
    upload_document_parser = document_subparsers.add_parser("upload", help="Upload document to dataset")
    upload_document_parser.add_argument("dataset", help="Dataset name")
    upload_document_parser.add_argument("files", nargs="+", help="File paths to upload")
    upload_document_parser.add_argument("--no-progress", action="store_true", help="Disable progress bar")
    
    # List documents
    list_documents_parser = document_subparsers.add_parser("list", help="List documents in dataset")
    list_documents_parser.add_argument("dataset", help="Dataset name")
    
    # Delete documents
    delete_documents_parser = document_subparsers.add_parser("delete", help="Delete documents from dataset")
    delete_documents_parser.add_argument("dataset", help="Dataset name")
    delete_documents_parser.add_argument("--document-ids", nargs="*", help="Document IDs to delete (if none, deletes all)")
    
    # Chat commands
    chat_parser = subparsers.add_parser("chat", help="Chat operations")
    chat_subparsers = chat_parser.add_subparsers(dest="chat_command", help="Chat command")
    
    # Create session
    create_session_parser = chat_subparsers.add_parser("create-session", help="Create a chat session")
    create_session_parser.add_argument("dataset", help="Dataset name")
    create_session_parser.add_argument("session", help="Session name")
    
    # List sessions
    list_sessions_parser = chat_subparsers.add_parser("list-sessions", help="List chat sessions")
    list_sessions_parser.add_argument("dataset", help="Dataset name")
    
    # Delete session
    delete_session_parser = chat_subparsers.add_parser("delete-session", help="Delete a chat session")
    delete_session_parser.add_argument("dataset", help="Dataset name")
    delete_session_parser.add_argument("session", help="Session name")
    
    # Send message
    send_message_parser = chat_subparsers.add_parser("send", help="Send a chat message")
    send_message_parser.add_argument("dataset", help="Dataset name")
    send_message_parser.add_argument("session", help="Session name")
    send_message_parser.add_argument("message", help="Message to send")
    
    # Interactive chat
    interactive_parser = chat_subparsers.add_parser("interactive", help="Start interactive chat session")
    interactive_parser.add_argument("dataset", help="Dataset name")
    interactive_parser.add_argument("session", help="Session name")
    
    return parser

def handle_dataset_commands(client: RagFlowClient, args: argparse.Namespace) -> Dict[str, Any]:
    """Handle dataset-related commands."""
    if args.dataset_command == "create":
        result = client.create_dataset(args.name)
        return {"message": f"Dataset '{args.name}' created successfully", "result": result}
    
    elif args.dataset_command == "get":
        result = client.get_dataset(args.name)
        return {"result": result}
    
    elif args.dataset_command == "delete":
        success = client.delete_dataset(args.name)
        if success:
            return {"message": f"Dataset '{args.name}' deleted successfully"}
        else:
            return {"error": f"Failed to delete dataset '{args.name}'"}
    
    else:
        return {"error": f"Unknown dataset command: {args.dataset_command}"}

def handle_document_commands(client: RagFlowClient, args: argparse.Namespace) -> Dict[str, Any]:
    """Handle document-related commands."""
    if args.document_command == "upload":
        # Verify files exist
        valid_files = []
        for file_path in args.files:
            if os.path.isfile(file_path):
                valid_files.append(file_path)
            else:
                logger.warning(f"File not found: {file_path}")
        
        if not valid_files:
            return {"error": "No valid files to upload"}
        
        result = client.upload_document(
            args.dataset, 
            valid_files, 
            show_progress=not args.no_progress
        )
        return {
            "message": f"Uploaded {len(valid_files)} document(s) to dataset '{args.dataset}'",
            "result": result
        }
    
    elif args.document_command == "list":
        documents = client.list_documents(args.dataset)
        return {
            "message": f"Found {len(documents)} documents in dataset '{args.dataset}'",
            "documents": documents
        }
    
    elif args.document_command == "delete":
        if args.document_ids:
            success = client.delete_documents(args.dataset, args.document_ids)
            message = f"Deleted {len(args.document_ids)} document(s) from dataset '{args.dataset}'"
        else:
            success = client.delete_documents(args.dataset)
            message = f"Deleted all documents from dataset '{args.dataset}'"
        
        if success:
            return {"message": message}
        else:
            return {"error": f"Failed to delete documents from dataset '{args.dataset}'"}
    
    else:
        return {"error": f"Unknown document command: {args.document_command}"}

def handle_chat_commands(client: RagFlowClient, args: argparse.Namespace) -> Dict[str, Any]:
    """Handle chat-related commands."""
    if args.chat_command == "create-session":
        result = client.create_session(args.dataset, args.session)
        return {
            "message": f"Created chat session '{args.session}' for dataset '{args.dataset}'",
            "result": result
        }
    
    elif args.chat_command == "list-sessions":
        result = client.list_sessions(args.dataset)
        sessions = result.get("data", [])
        return {
            "message": f"Found {len(sessions)} sessions for dataset '{args.dataset}'",
            "sessions": sessions
        }
    
    elif args.chat_command == "delete-session":
        result = client.delete_session(args.dataset, args.session)
        return {
            "message": f"Deleted chat session '{args.session}' from dataset '{args.dataset}'",
            "result": result
        }
    
    elif args.chat_command == "send":
        response = client.chat(args.dataset, args.session, args.message)
        return {
            "response": response
        }
    
    elif args.chat_command == "interactive":
        print(f"\nStarting interactive chat with dataset '{args.dataset}', session '{args.session}'")
        print("Type 'exit' or 'quit' to end the session.\n")
        
        while True:
            try:
                user_input = input("\n> ")
                if user_input.lower() in ["exit", "quit"]:
                    print("Ending chat session.")
                    break
                
                if not user_input.strip():
                    continue
                
                print("Processing...")
                response = client.chat(args.dataset, args.session, user_input)
                print(f"\nRagFlow: {response}")
                
            except KeyboardInterrupt:
                print("\nEnding chat session.")
                break
            except Exception as e:
                print(f"\nError: {str(e)}")
        
        return {"message": "Interactive chat session ended"}
    
    else:
        return {"error": f"Unknown chat command: {args.chat_command}"}

def main():
    """Run the CLI."""
    parser = setup_parser()
    args = parser.parse_args()
    
    # Set log level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize client
    try:
        client = RagFlowClient(api_key=args.api_key, base_url=args.base_url)
    except Exception as e:
        logger.error(f"Failed to initialize RagFlow client: {str(e)}")
        sys.exit(1)
    
    # Handle commands
    try:
        if args.command == "dataset":
            result = handle_dataset_commands(client, args)
        elif args.command == "document":
            result = handle_document_commands(client, args)
        elif args.command == "chat":
            result = handle_chat_commands(client, args)
        else:
            # If no command specified, show help
            if not args.command:
                parser.print_help()
                sys.exit(0)
            result = {"error": f"Unknown command: {args.command}"}
        
        # Print result as JSON, except for interactive chat
        if not (args.command == "chat" and args.chat_command == "interactive"):
            print(json.dumps(result, indent=2, default=str))
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 