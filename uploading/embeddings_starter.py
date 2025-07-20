"""
Embeddings starter for ChatGPT conversations using Ollama all-minilm.

This module provides basic functionality to generate embeddings from ChatGPT export data.
"""

import json
import requests
from typing import List, Dict, Any, Optional
import numpy as np
from dataclasses import dataclass


@dataclass
class ConversationChunk:
    """Represents a chunk of conversation to be embedded."""
    conversation_id: str
    chunk_id: str
    text: str
    metadata: Dict[str, Any]


class OllamaEmbeddings:
    """Handle embeddings generation using Ollama all-minilm model."""
    
    def __init__(self, model: str = "all-minilm", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host
        self.embed_endpoint = f"{host}/api/embeddings"
        
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for a single text."""
        try:
            response = requests.post(
                self.embed_endpoint,
                json={
                    "model": self.model,
                    "prompt": text
                }
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts."""
        embeddings = []
        for i, text in enumerate(texts):
            print(f"Generating embedding {i+1}/{len(texts)}...", end='\r')
            embedding = self.generate_embedding(text)
            embeddings.append(embedding)
        print()
        return embeddings


class ConversationProcessor:
    """Process ChatGPT conversations for embedding generation."""
    
    def __init__(self, embeddings_client: OllamaEmbeddings):
        self.embeddings = embeddings_client
        
    def extract_conversation_text(self, conversation: Dict[str, Any]) -> List[ConversationChunk]:
        """Extract text chunks from a conversation."""
        chunks = []
        
        # Extract basic metadata
        conv_id = conversation.get('id', 'unknown')
        title = conversation.get('title', 'Untitled')
        
        # Extract messages from mapping structure
        mapping = conversation.get('mapping', {})
        messages = []
        
        for node_id, node in mapping.items():
            if node.get('message'):
                msg = node['message']
                if msg.get('content') and msg['content'].get('parts'):
                    # Handle parts that might be strings or dicts
                    parts = msg['content']['parts']
                    text_parts = []
                    for part in parts:
                        if isinstance(part, str):
                            text_parts.append(part)
                        elif isinstance(part, dict) and 'text' in part:
                            text_parts.append(part['text'])
                    content = ' '.join(text_parts)
                    role = msg.get('author', {}).get('role', 'unknown')
                    messages.append({
                        'role': role,
                        'content': content
                    })
        
        # Create chunks (for now, one chunk per conversation)
        if messages:
            # Combine all messages into one text
            full_text = f"Title: {title}\n\n"
            for msg in messages:
                full_text += f"{msg['role'].upper()}: {msg['content']}\n\n"
            
            chunk = ConversationChunk(
                conversation_id=conv_id,
                chunk_id=f"{conv_id}_full",
                text=full_text[:8000],  # Limit chunk size
                metadata={
                    'title': title,
                    'message_count': len(messages)
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    def process_conversations_file(self, file_path: str, limit: int = None) -> Dict[str, Any]:
        """Process conversations from a JSON file."""
        print(f"Loading conversations from {file_path}")
        
        with open(file_path, 'r') as f:
            conversations = json.load(f)
        
        if limit:
            conversations = conversations[:limit]
        
        print(f"Processing {len(conversations)} conversations...")
        
        all_chunks = []
        all_embeddings = []
        
        for i, conv in enumerate(conversations):
            print(f"Processing conversation {i+1}/{len(conversations)}...", end='\r')
            
            # Extract chunks
            chunks = self.extract_conversation_text(conv)
            
            # Generate embeddings for chunks
            for chunk in chunks:
                embedding = self.embeddings.generate_embedding(chunk.text)
                if embedding:
                    all_chunks.append(chunk)
                    all_embeddings.append(embedding)
        
        print(f"\nGenerated {len(all_embeddings)} embeddings")
        
        return {
            'chunks': all_chunks,
            'embeddings': all_embeddings
        }


def test_single_conversation():
    """Test embedding generation on a single conversation."""
    print("Testing Ollama all-minilm embeddings...")
    
    # Initialize embeddings client
    embeddings = OllamaEmbeddings()
    
    # Test with simple text
    test_text = "This is a test conversation about ChatGPT exports and embeddings."
    embedding = embeddings.generate_embedding(test_text)
    
    if embedding:
        print(f"✓ Successfully generated embedding with dimension: {len(embedding)}")
        print(f"  Sample values: {embedding[:5]}...")
        return True
    else:
        print("✗ Failed to generate embedding")
        return False


def process_shared_conversations(file_path: str):
    """Process shared conversations file."""
    print(f"\nProcessing shared conversations from: {file_path}")
    
    # Load shared conversations
    with open(file_path, 'r') as f:
        shared_convs = json.load(f)
    
    print(f"Found {len(shared_convs)} shared conversations")
    
    # Initialize clients
    embeddings = OllamaEmbeddings()
    
    # Generate embeddings for titles
    titles = [conv.get('title', 'Untitled') for conv in shared_convs[:5]]
    print(f"\nGenerating embeddings for {len(titles)} conversation titles...")
    
    title_embeddings = embeddings.generate_embeddings_batch(titles)
    
    # Display results
    for i, (title, embedding) in enumerate(zip(titles, title_embeddings)):
        if embedding:
            print(f"  {i+1}. {title[:50]}... - Embedding dim: {len(embedding)}")
        else:
            print(f"  {i+1}. {title[:50]}... - Failed to generate embedding")


if __name__ == "__main__":
    # First test basic embedding generation
    if test_single_conversation():
        # Then process shared conversations
        shared_conv_path = "/Users/ebowwa/Downloads/chatgpt-export/extracted_data/2025-07-20_Sunday_12-04-32/shared_conversations.json"
        process_shared_conversations(shared_conv_path)