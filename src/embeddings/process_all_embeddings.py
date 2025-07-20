#!/usr/bin/env python3
"""
Process conversations and save embeddings for reuse.
"""

from .client import EmbeddingsClient
from .processor import ConversationProcessor, ConversationChunk
import json
import numpy as np
import pickle
from datetime import datetime
import time
import os
import argparse
import logging
from typing import List, Dict, Any, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_conversations(
    conversations_path: str,
    output_dir: str,
    batch_size: int = 100,
    limit: Optional[int] = None,
    embeddings_host: str = "http://localhost:11434",
    embeddings_model: str = "all-minilm"
) -> Tuple[List[Dict[str, Any]], List[List[float]]]:
    """
    Process conversations in batches and save embeddings.
    
    Args:
        conversations_path: Path to conversations JSON file
        output_dir: Directory to save embeddings
        batch_size: Number of conversations to process at once
        limit: Optional limit on number of conversations to process
        embeddings_host: Ollama server URL
        embeddings_model: Ollama model name
        
    Returns:
        Tuple of (chunks metadata, embeddings)
    """
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize processors
    embeddings_client = EmbeddingsClient(
        model=embeddings_model,
        host=embeddings_host
    )
    processor = ConversationProcessor()
    
    logger.info(f"Loading conversations from {conversations_path}")
    with open(conversations_path, 'r') as f:
        all_conversations = json.load(f)
    
    if limit:
        all_conversations = all_conversations[:limit]
        
    total_convs = len(all_conversations)
    logger.info(f"Total conversations to process: {total_convs:,}")
    logger.info(f"Processing in batches of {batch_size}")
    
    # Process in batches
    all_chunks = []
    all_embeddings = []
    
    start_time = time.time()
    
    for batch_start in range(0, total_convs, batch_size):
        batch_end = min(batch_start + batch_size, total_convs)
        batch_conversations = all_conversations[batch_start:batch_end]
        
        logger.info(f"Processing batch {batch_start//batch_size + 1} ({batch_start}-{batch_end} of {total_convs})")
        
        batch_start_time = time.time()
        
        # Process this batch
        for i, conv in enumerate(batch_conversations):
            global_idx = batch_start + i
            if global_idx % 10 == 0:
                print(f"  Processing conversation {global_idx + 1}/{total_convs}...", end='\r')
            
            try:
                # Extract chunks
                chunks = processor.extract_conversation_text(conv)
                
                # Generate embeddings for chunks
                for chunk in chunks:
                    embedding = embeddings_client.generate_embedding(chunk.text)
                    if embedding:
                        all_chunks.append({
                            'conversation_id': chunk.conversation_id,
                            'chunk_id': chunk.chunk_id,
                            'title': chunk.metadata['title'],
                            'message_count': chunk.metadata['message_count'],
                            'text_preview': chunk.text[:200]
                        })
                        all_embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Error processing conversation {global_idx}: {e}")
                continue
        
        batch_time = time.time() - batch_start_time
        logger.info(f"Batch completed in {batch_time:.1f}s ({len(all_embeddings)} total embeddings so far)")
        
        # Save checkpoint every 500 conversations
        if (batch_end % 500 == 0 or batch_end == total_convs) and all_embeddings:
            checkpoint_file = os.path.join(output_dir, f'embeddings_checkpoint_{batch_end}.pkl')
            logger.info(f"Saving checkpoint to {checkpoint_file}")
            with open(checkpoint_file, 'wb') as f:
                pickle.dump({
                    'chunks': all_chunks,
                    'embeddings': all_embeddings,
                    'processed_count': batch_end,
                    'timestamp': datetime.now().isoformat()
                }, f)
    
    total_time = time.time() - start_time
    
    # Save final results
    logger.info("-" * 60)
    logger.info(f"Processing complete!")
    logger.info(f"Total time: {total_time/60:.1f} minutes")
    logger.info(f"Total embeddings generated: {len(all_embeddings):,}")
    logger.info(f"Average time per conversation: {total_time/total_convs:.2f}s")
    
    # Save final embeddings
    final_file = os.path.join(output_dir, 'all_embeddings.pkl')
    logger.info(f"Saving final embeddings to {final_file}")
    with open(final_file, 'wb') as f:
        pickle.dump({
            'chunks': all_chunks,
            'embeddings': all_embeddings,
            'total_conversations': total_convs,
            'embedding_count': len(all_embeddings),
            'timestamp': datetime.now().isoformat()
        }, f)
    
    # Save as numpy array for efficient operations
    np_file = os.path.join(output_dir, 'embeddings_matrix.npy')
    logger.info(f"Saving numpy matrix to {np_file}")
    np.save(np_file, np.array(all_embeddings))
    
    # Save metadata as JSON for easy access
    metadata_file = os.path.join(output_dir, 'embeddings_metadata.json')
    logger.info(f"Saving metadata to {metadata_file}")
    with open(metadata_file, 'w') as f:
        json.dump({
            'chunks': all_chunks,
            'total_conversations': total_convs,
            'embedding_count': len(all_embeddings),
            'embedding_dim': 384,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    
    logger.info("All embeddings saved successfully!")
    logger.info(f"  - Pickle file: {final_file}")
    logger.info(f"  - Numpy matrix: {np_file}")
    logger.info(f"  - Metadata JSON: {metadata_file}")
    
    return all_chunks, all_embeddings


def main():
    parser = argparse.ArgumentParser(
        description="Process ChatGPT conversations and generate embeddings"
    )
    parser.add_argument(
        "conversations_file",
        help="Path to conversations JSON file"
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="./embeddings_output",
        help="Output directory for embeddings (default: ./embeddings_output)"
    )
    parser.add_argument(
        "-b", "--batch-size",
        type=int,
        default=100,
        help="Batch size for processing (default: 100)"
    )
    parser.add_argument(
        "-l", "--limit",
        type=int,
        help="Limit number of conversations to process"
    )
    parser.add_argument(
        "--host",
        default="http://localhost:11434",
        help="Ollama server URL (default: http://localhost:11434)"
    )
    parser.add_argument(
        "--model",
        default="all-minilm",
        help="Ollama model name (default: all-minilm)"
    )
    
    args = parser.parse_args()
    
    # Test connection first
    client = EmbeddingsClient(host=args.host, model=args.model)
    if not client.test_connection():
        logger.error(f"Cannot connect to Ollama server at {args.host}")
        logger.error("Make sure Ollama is running: ollama serve")
        return 1
    
    # Process conversations
    process_conversations(
        conversations_path=args.conversations_file,
        output_dir=args.output_dir,
        batch_size=args.batch_size,
        limit=args.limit,
        embeddings_host=args.host,
        embeddings_model=args.model
    )
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())