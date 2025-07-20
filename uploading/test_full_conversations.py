#!/usr/bin/env python3
"""
Test script to process full conversations with embeddings.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from embeddings_starter import OllamaEmbeddings, ConversationProcessor
import json

def main():
    # Initialize
    embeddings_client = OllamaEmbeddings()
    processor = ConversationProcessor(embeddings_client)
    
    # Path to full conversations
    conv_path = "/Users/ebowwa/Downloads/chatgpt-export/extracted_data/2025-07-20_Sunday_12-04-32/conversations.json"
    
    print("Processing full conversations with embeddings...")
    print("-" * 60)
    
    # Process first 3 conversations as a test
    results = processor.process_conversations_file(conv_path, limit=3)
    
    print("\nResults Summary:")
    print(f"  Total chunks processed: {len(results['chunks'])}")
    print(f"  Total embeddings generated: {len(results['embeddings'])}")
    
    # Show sample chunks
    print("\nSample chunks:")
    for i, chunk in enumerate(results['chunks'][:3]):
        print(f"\n{i+1}. Conversation: {chunk.metadata['title']}")
        print(f"   Messages: {chunk.metadata['message_count']}")
        print(f"   Text preview: {chunk.text[:200]}...")
        print(f"   Embedding shape: {len(results['embeddings'][i])}")
        
    # Calculate similarity between first two embeddings if available
    if len(results['embeddings']) >= 2:
        import numpy as np
        emb1 = np.array(results['embeddings'][0])
        emb2 = np.array(results['embeddings'][1])
        
        # Cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        print(f"\nCosine similarity between first two conversations: {similarity:.4f}")

if __name__ == "__main__":
    main()