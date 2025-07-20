#!/usr/bin/env python3
"""
Demo of what we can do with our current embeddings setup.
"""

import sys
import os
# Add parent directory to path so we can import from src.uploading
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.uploading.embeddings_starter import OllamaEmbeddings, ConversationProcessor
import numpy as np
import json
from typing import List, Tuple

class EmbeddingsDemo:
    """Demonstrate current capabilities with embeddings."""
    
    def __init__(self):
        self.embeddings_client = OllamaEmbeddings()
        self.processor = ConversationProcessor(self.embeddings_client)
        
    def semantic_search(self, query: str, embeddings: List[List[float]], texts: List[str], top_k: int = 3) -> List[Tuple[int, float, str]]:
        """Search for most similar texts to a query."""
        # Generate query embedding
        query_embedding = self.embeddings_client.generate_embedding(query)
        if not query_embedding:
            return []
        
        # Calculate similarities
        query_vec = np.array(query_embedding)
        similarities = []
        
        for i, emb in enumerate(embeddings):
            emb_vec = np.array(emb)
            # Cosine similarity
            sim = np.dot(query_vec, emb_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(emb_vec))
            similarities.append((i, sim, texts[i]))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def find_similar_conversations(self, target_idx: int, embeddings: List[List[float]], titles: List[str]) -> List[Tuple[int, float, str]]:
        """Find conversations similar to a target conversation."""
        target_emb = np.array(embeddings[target_idx])
        similarities = []
        
        for i, emb in enumerate(embeddings):
            if i == target_idx:
                continue
            emb_vec = np.array(emb)
            sim = np.dot(target_emb, emb_vec) / (np.linalg.norm(target_emb) * np.linalg.norm(emb_vec))
            similarities.append((i, sim, titles[i]))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:5]
    
    def cluster_conversations(self, embeddings: List[List[float]], titles: List[str], threshold: float = 0.7):
        """Simple clustering based on similarity threshold."""
        clusters = []
        used = set()
        
        embeddings_array = np.array(embeddings)
        
        for i in range(len(embeddings)):
            if i in used:
                continue
                
            cluster = [(i, titles[i])]
            used.add(i)
            
            for j in range(i + 1, len(embeddings)):
                if j in used:
                    continue
                    
                # Calculate similarity
                sim = np.dot(embeddings_array[i], embeddings_array[j]) / (
                    np.linalg.norm(embeddings_array[i]) * np.linalg.norm(embeddings_array[j])
                )
                
                if sim > threshold:
                    cluster.append((j, titles[j]))
                    used.add(j)
            
            clusters.append(cluster)
        
        return clusters


def main():
    demo = EmbeddingsDemo()
    
    print("=== Current Capabilities Demo ===\n")
    
    # Load and process some conversations
    conv_path = "/Users/ebowwa/Downloads/chatgpt-export/user-data/2025-07-20_Sunday_12-04-32/conversations.json"
    
    print("1. SEMANTIC SEARCH")
    print("-" * 40)
    
    # Process first 20 conversations for demo
    results = demo.processor.process_conversations_file(conv_path, limit=20)
    
    # Extract titles for display
    titles = [chunk.metadata['title'] for chunk in results['chunks']]
    
    # Demo: Search for conversations about specific topics
    queries = [
        "housing and apartments",
        "programming and coding",
        "UFC fighting sports"
    ]
    
    for query in queries:
        print(f"\nSearching for: \"{query}\"")
        matches = demo.semantic_search(query, results['embeddings'], titles)
        for idx, score, title in matches:
            print(f"  {score:.3f} - {title}")
    
    print("\n\n2. SIMILARITY DETECTION")
    print("-" * 40)
    
    # Find similar conversations to the first one
    if len(results['embeddings']) > 1:
        print(f"\nConversations similar to \"{titles[0]}\":")
        similar = demo.find_similar_conversations(0, results['embeddings'], titles)
        for idx, score, title in similar:
            print(f"  {score:.3f} - {title}")
    
    print("\n\n3. CONVERSATION CLUSTERING")
    print("-" * 40)
    
    # Cluster conversations by similarity
    clusters = demo.cluster_conversations(results['embeddings'], titles, threshold=0.3)
    
    print(f"\nFound {len(clusters)} conversation groups:")
    for i, cluster in enumerate(clusters):
        if len(cluster) > 1:
            print(f"\nGroup {i+1} ({len(cluster)} conversations):")
            for idx, title in cluster:
                print(f"  - {title}")
    
    print("\n\n4. WHAT ELSE WE CAN BUILD")
    print("-" * 40)
    print("\nWith full implementation, we could:")
    print("• Semantic search across all 13,007 conversations")
    print("• Find duplicate or near-duplicate conversations")
    print("• Generate topic summaries for conversation clusters")
    print("• Build a personal knowledge graph")
    print("• Create a 'conversation recommender' system")
    print("• Export similar conversations for fine-tuning")
    print("• Track topic evolution over time")
    print("• Build a personal AI assistant trained on your style")


if __name__ == "__main__":
    main()