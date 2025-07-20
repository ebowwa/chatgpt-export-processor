#!/usr/bin/env python3
"""
Process ALL conversations and save embeddings for reuse.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from embeddings_starter import OllamaEmbeddings, ConversationProcessor
import json
import numpy as np
import pickle
from datetime import datetime
import time

def process_all_conversations(conv_path: str, output_dir: str, batch_size: int = 100):
    """Process all conversations in batches and save embeddings."""
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize processors
    embeddings_client = OllamaEmbeddings()
    processor = ConversationProcessor(embeddings_client)
    
    print(f"Loading conversations from {conv_path}")
    with open(conv_path, 'r') as f:
        all_conversations = json.load(f)
    
    total_convs = len(all_conversations)
    print(f"Total conversations to process: {total_convs:,}")
    print(f"Processing in batches of {batch_size}")
    print("-" * 60)
    
    # Process in batches
    all_chunks = []
    all_embeddings = []
    
    start_time = time.time()
    
    for batch_start in range(0, total_convs, batch_size):
        batch_end = min(batch_start + batch_size, total_convs)
        batch_conversations = all_conversations[batch_start:batch_end]
        
        print(f"\nProcessing batch {batch_start//batch_size + 1} ({batch_start}-{batch_end} of {total_convs})")
        
        batch_start_time = time.time()
        
        # Process this batch
        for i, conv in enumerate(batch_conversations):
            global_idx = batch_start + i
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
                print(f"\n  Error processing conversation {global_idx}: {e}")
                continue
        
        batch_time = time.time() - batch_start_time
        print(f"\n  Batch completed in {batch_time:.1f}s ({len(all_embeddings)} total embeddings so far)")
        
        # Save checkpoint every 500 conversations
        if (batch_end % 500 == 0 or batch_end == total_convs) and all_embeddings:
            checkpoint_file = os.path.join(output_dir, f'embeddings_checkpoint_{batch_end}.pkl')
            print(f"  Saving checkpoint to {checkpoint_file}")
            with open(checkpoint_file, 'wb') as f:
                pickle.dump({
                    'chunks': all_chunks,
                    'embeddings': all_embeddings,
                    'processed_count': batch_end,
                    'timestamp': datetime.now().isoformat()
                }, f)
    
    total_time = time.time() - start_time
    
    # Save final results
    print("\n" + "-" * 60)
    print(f"Processing complete!")
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Total embeddings generated: {len(all_embeddings):,}")
    print(f"Average time per conversation: {total_time/total_convs:.2f}s")
    
    # Save final embeddings
    final_file = os.path.join(output_dir, 'all_embeddings.pkl')
    print(f"\nSaving final embeddings to {final_file}")
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
    print(f"Saving numpy matrix to {np_file}")
    np.save(np_file, np.array(all_embeddings))
    
    # Save metadata as JSON for easy access
    metadata_file = os.path.join(output_dir, 'embeddings_metadata.json')
    print(f"Saving metadata to {metadata_file}")
    with open(metadata_file, 'w') as f:
        json.dump({
            'chunks': all_chunks,
            'total_conversations': total_convs,
            'embedding_count': len(all_embeddings),
            'embedding_dim': 384,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    
    print("\n✓ All embeddings saved successfully!")
    print(f"  - Pickle file: {final_file}")
    print(f"  - Numpy matrix: {np_file}")
    print(f"  - Metadata JSON: {metadata_file}")
    
    return all_chunks, all_embeddings


def main():
    # Paths
    conv_path = "/Users/ebowwa/Downloads/chatgpt-export/extracted_data/2025-07-20_Sunday_12-04-32/conversations.json"
    output_dir = "/Users/ebowwa/Downloads/chatgpt-export/embeddings_output"
    
    # Check if we want to process all or just test
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        print("Processing ALL conversations (this will take ~30 minutes)...")
        process_all_conversations(conv_path, output_dir, batch_size=100)
    else:
        print("Test mode: Processing first 100 conversations only")
        print("Run with --all flag to process all 13,007 conversations")
        print("Example: python process_all_embeddings.py --all")
        print("-" * 60)
        
        # Process only first 100 for testing
        with open(conv_path, 'r') as f:
            all_conversations = json.load(f)
        
        # Save first 100 to temp file
        temp_file = '/tmp/test_conversations.json'
        with open(temp_file, 'w') as f:
            json.dump(all_conversations[:100], f)
        
        process_all_conversations(temp_file, output_dir + '_test', batch_size=20)


if __name__ == "__main__":
    main()