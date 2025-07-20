#!/usr/bin/env python3
"""
Search interface for pre-computed ChatGPT conversation embeddings.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import json
import pickle
from typing import List, Tuple, Optional
from embeddings_starter import OllamaEmbeddings
import argparse
from datetime import datetime

class ConversationSearcher:
    """Search through pre-computed conversation embeddings."""
    
    def __init__(self, embeddings_dir: str):
        """Initialize with path to embeddings directory."""
        self.embeddings_dir = embeddings_dir
        self.embeddings_client = OllamaEmbeddings()
        
        # Load embeddings and metadata
        self._load_embeddings()
        
    def _load_embeddings(self):
        """Load pre-computed embeddings and metadata."""
        # Load numpy matrix for fast operations
        matrix_path = os.path.join(self.embeddings_dir, 'embeddings_matrix.npy')
        metadata_path = os.path.join(self.embeddings_dir, 'embeddings_metadata.json')
        
        if not os.path.exists(matrix_path) or not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Embeddings not found in {self.embeddings_dir}. Run process_all_embeddings.py first.")
        
        print(f"Loading embeddings from {self.embeddings_dir}...")
        self.embeddings_matrix = np.load(matrix_path)
        
        with open(metadata_path, 'r') as f:
            self.metadata = json.load(f)
        
        self.chunks = self.metadata['chunks']
        print(f"Loaded {len(self.chunks):,} conversation embeddings")
        print(f"Total conversations processed: {self.metadata['total_conversations']:,}")
        
    def search(self, query: str, top_k: int = 10) -> List[Tuple[float, dict]]:
        """Search for conversations similar to query."""
        # Generate query embedding
        print(f"\nSearching for: '{query}'")
        query_embedding = self.embeddings_client.generate_embedding(query)
        
        if not query_embedding:
            print("Failed to generate query embedding")
            return []
        
        # Calculate similarities
        query_vec = np.array(query_embedding)
        
        # Efficient batch cosine similarity
        # Normalize query vector
        query_norm = query_vec / np.linalg.norm(query_vec)
        
        # Normalize all embeddings (if not already normalized)
        norms = np.linalg.norm(self.embeddings_matrix, axis=1, keepdims=True)
        normalized_embeddings = self.embeddings_matrix / (norms + 1e-8)  # Add small epsilon to avoid division by zero
        
        # Compute similarities
        similarities = np.dot(normalized_embeddings, query_norm)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Return results with metadata
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            chunk_info = self.chunks[idx]
            results.append((score, chunk_info))
        
        return results
    
    def find_similar_to_conversation(self, conversation_id: str, top_k: int = 10) -> List[Tuple[float, dict]]:
        """Find conversations similar to a specific conversation."""
        # Find the conversation in our chunks
        target_idx = None
        for i, chunk in enumerate(self.chunks):
            if chunk['conversation_id'] == conversation_id:
                target_idx = i
                break
        
        if target_idx is None:
            print(f"Conversation {conversation_id} not found")
            return []
        
        # Get embedding
        target_embedding = self.embeddings_matrix[target_idx]
        target_norm = target_embedding / np.linalg.norm(target_embedding)
        
        # Calculate similarities
        norms = np.linalg.norm(self.embeddings_matrix, axis=1, keepdims=True)
        normalized_embeddings = self.embeddings_matrix / (norms + 1e-8)
        similarities = np.dot(normalized_embeddings, target_norm)
        
        # Get top-k+1 (excluding self)
        top_indices = np.argsort(similarities)[-(top_k+1):][::-1]
        
        # Return results excluding self
        results = []
        for idx in top_indices:
            if idx != target_idx:
                score = float(similarities[idx])
                chunk_info = self.chunks[idx]
                results.append((score, chunk_info))
        
        return results[:top_k]
    
    def get_statistics(self) -> dict:
        """Get statistics about the indexed conversations."""
        # Basic stats
        stats = {
            'total_embeddings': len(self.chunks),
            'total_conversations': self.metadata['total_conversations'],
            'embedding_dimension': self.metadata['embedding_dim'],
            'index_created': self.metadata['timestamp']
        }
        
        # Message count distribution
        message_counts = [chunk['message_count'] for chunk in self.chunks]
        stats['message_stats'] = {
            'min': min(message_counts),
            'max': max(message_counts),
            'avg': sum(message_counts) / len(message_counts),
            'total': sum(message_counts)
        }
        
        # Title analysis
        titles = [chunk['title'] for chunk in self.chunks]
        unique_titles = set(titles)
        stats['unique_titles'] = len(unique_titles)
        stats['duplicate_conversations'] = len(titles) - len(unique_titles)
        
        return stats


def interactive_search(searcher: ConversationSearcher):
    """Run interactive search interface."""
    print("\n=== ChatGPT Conversation Search ===")
    print("Type your search query (or 'quit' to exit, 'stats' for statistics)")
    print("-" * 50)
    
    while True:
        query = input("\nSearch: ").strip()
        
        if query.lower() == 'quit':
            break
        
        if query.lower() == 'stats':
            stats = searcher.get_statistics()
            print(f"\nIndex Statistics:")
            print(f"  Total embeddings: {stats['total_embeddings']:,}")
            print(f"  Unique conversations: {stats['total_conversations']:,}")
            print(f"  Unique titles: {stats['unique_titles']:,}")
            print(f"  Duplicate conversations: {stats['duplicate_conversations']:,}")
            print(f"  Message statistics:")
            print(f"    Total messages: {stats['message_stats']['total']:,}")
            print(f"    Avg per conversation: {stats['message_stats']['avg']:.1f}")
            print(f"    Range: {stats['message_stats']['min']}-{stats['message_stats']['max']}")
            print(f"  Index created: {stats['index_created']}")
            continue
        
        if not query:
            continue
        
        # Search
        results = searcher.search(query, top_k=10)
        
        if not results:
            print("No results found")
            continue
        
        print(f"\nTop {len(results)} results:")
        print("-" * 80)
        
        for i, (score, chunk) in enumerate(results, 1):
            print(f"\n{i}. Score: {score:.3f}")
            print(f"   Title: {chunk['title']}")
            print(f"   Messages: {chunk['message_count']}")
            print(f"   Preview: {chunk['text_preview'][:150]}...")
            print(f"   ID: {chunk['conversation_id']}")
        
        # Ask if user wants to find similar conversations
        if len(results) > 0:
            print("\nEnter a result number to find similar conversations (or press Enter to continue):")
            choice = input("Choice: ").strip()
            
            if choice.isdigit() and 1 <= int(choice) <= len(results):
                idx = int(choice) - 1
                selected = results[idx][1]
                print(f"\nFinding conversations similar to: {selected['title']}")
                
                similar = searcher.find_similar_to_conversation(selected['conversation_id'], top_k=5)
                
                print(f"\nSimilar conversations:")
                for j, (sim_score, sim_chunk) in enumerate(similar, 1):
                    print(f"  {j}. {sim_score:.3f} - {sim_chunk['title']}")


def main():
    parser = argparse.ArgumentParser(description='Search through ChatGPT conversation embeddings')
    parser.add_argument('--embeddings-dir', default='/Users/ebowwa/Downloads/chatgpt-export/embeddings_output',
                        help='Directory containing embeddings')
    parser.add_argument('--query', help='One-time search query')
    parser.add_argument('--top-k', type=int, default=10, help='Number of results to return')
    
    args = parser.parse_args()
    
    try:
        searcher = ConversationSearcher(args.embeddings_dir)
        
        if args.query:
            # One-time search
            results = searcher.search(args.query, top_k=args.top_k)
            
            print(f"\nTop {len(results)} results for '{args.query}':")
            for i, (score, chunk) in enumerate(results, 1):
                print(f"\n{i}. Score: {score:.3f}")
                print(f"   Title: {chunk['title']}")
                print(f"   Messages: {chunk['message_count']}")
                print(f"   Preview: {chunk['text_preview'][:200]}...")
        else:
            # Interactive mode
            interactive_search(searcher)
            
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nPlease run: python process_all_embeddings.py --all")
        sys.exit(1)


if __name__ == "__main__":
    main()