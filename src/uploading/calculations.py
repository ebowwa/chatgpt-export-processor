"""
Calculation functions for ChatGPT export processing estimates.
"""

from typing import Dict, Any, Tuple
import os

class ProcessingCalculator:
    """Calculate time, storage, and resource estimates for processing."""
    
    # Based on observed performance
    EMBEDDING_TIME_PER_ITEM = 0.05  # seconds per conversation
    EMBEDDING_DIMENSION = 384
    BYTES_PER_FLOAT = 4
    
    def __init__(self):
        self.stats = {}
    
    def calculate_embedding_storage(self, num_items: int) -> Dict[str, Any]:
        """Calculate storage requirements for embeddings."""
        # Raw embedding storage
        embedding_bytes = num_items * self.EMBEDDING_DIMENSION * self.BYTES_PER_FLOAT
        
        # Metadata overhead (approximately 200 bytes per item)
        metadata_bytes = num_items * 200
        
        # Pickle overhead (approximately 10%)
        pickle_overhead = (embedding_bytes + metadata_bytes) * 0.1
        
        total_bytes = embedding_bytes + metadata_bytes + pickle_overhead
        
        return {
            'embedding_bytes': embedding_bytes,
            'metadata_bytes': metadata_bytes,
            'pickle_overhead': pickle_overhead,
            'total_bytes': total_bytes,
            'embedding_mb': embedding_bytes / (1024 * 1024),
            'total_mb': total_bytes / (1024 * 1024),
            'per_item_kb': total_bytes / num_items / 1024
        }
    
    def calculate_processing_time(self, num_items: int, batch_size: int = 100) -> Dict[str, Any]:
        """Calculate estimated processing time."""
        # Base processing time
        base_time = num_items * self.EMBEDDING_TIME_PER_ITEM
        
        # Batch overhead (loading, saving checkpoints)
        num_batches = (num_items + batch_size - 1) // batch_size
        batch_overhead = num_batches * 0.5  # 0.5 seconds per batch
        
        # I/O overhead for checkpoints (every 500 items)
        num_checkpoints = num_items // 500
        checkpoint_overhead = num_checkpoints * 2  # 2 seconds per checkpoint
        
        total_seconds = base_time + batch_overhead + checkpoint_overhead
        
        return {
            'base_processing_seconds': base_time,
            'batch_overhead_seconds': batch_overhead,
            'checkpoint_overhead_seconds': checkpoint_overhead,
            'total_seconds': total_seconds,
            'total_minutes': total_seconds / 60,
            'items_per_minute': num_items / (total_seconds / 60) if total_seconds > 0 else 0,
            'seconds_per_item': total_seconds / num_items if num_items > 0 else 0
        }
    
    def calculate_memory_usage(self, num_items: int, avg_text_size: int = 5000) -> Dict[str, Any]:
        """Calculate estimated memory usage during processing."""
        # Text storage in memory
        text_memory = num_items * avg_text_size
        
        # Embeddings in memory
        embeddings_memory = num_items * self.EMBEDDING_DIMENSION * self.BYTES_PER_FLOAT
        
        # Python object overhead (approximately 50%)
        python_overhead = (text_memory + embeddings_memory) * 0.5
        
        # Peak memory (during batch processing, only hold batch_size in memory)
        batch_size = 100
        peak_text = min(batch_size, num_items) * avg_text_size
        peak_embeddings = num_items * self.EMBEDDING_DIMENSION * self.BYTES_PER_FLOAT  # All embeddings
        peak_memory = peak_text + peak_embeddings + python_overhead
        
        return {
            'text_memory_mb': text_memory / (1024 * 1024),
            'embeddings_memory_mb': embeddings_memory / (1024 * 1024),
            'python_overhead_mb': python_overhead / (1024 * 1024),
            'total_memory_mb': (text_memory + embeddings_memory + python_overhead) / (1024 * 1024),
            'peak_memory_mb': peak_memory / (1024 * 1024)
        }
    
    def calculate_ollama_load(self, num_items: int, requests_per_second: float = 20) -> Dict[str, Any]:
        """Calculate Ollama server load."""
        total_requests = num_items
        time_seconds = total_requests / requests_per_second
        
        # Model memory (all-minilm is ~45MB)
        model_memory_mb = 45
        
        # Request queue memory (approximately 1KB per pending request)
        max_queue_size = min(100, num_items)  # Ollama typically queues up to 100
        queue_memory_kb = max_queue_size
        
        return {
            'total_requests': total_requests,
            'requests_per_second': requests_per_second,
            'processing_time_seconds': time_seconds,
            'processing_time_minutes': time_seconds / 60,
            'model_memory_mb': model_memory_mb,
            'queue_memory_kb': queue_memory_kb,
            'gpu_usage_estimate': 'Low (CPU-based model)'
        }
    
    def get_full_estimate(self, num_conversations: int) -> Dict[str, Any]:
        """Get complete processing estimate."""
        storage = self.calculate_embedding_storage(num_conversations)
        time = self.calculate_processing_time(num_conversations)
        memory = self.calculate_memory_usage(num_conversations)
        ollama = self.calculate_ollama_load(num_conversations)
        
        return {
            'conversations': num_conversations,
            'storage': storage,
            'time': time,
            'memory': memory,
            'ollama': ollama,
            'summary': {
                'total_time_minutes': round(time['total_minutes'], 1),
                'total_storage_mb': round(storage['total_mb'], 1),
                'peak_memory_mb': round(memory['peak_memory_mb'], 1),
                'cost': 'Free (using local Ollama)'
            }
        }
    
    def format_estimate_report(self, num_conversations: int) -> str:
        """Generate a human-readable estimate report."""
        estimate = self.get_full_estimate(num_conversations)
        
        report = f"""
=== ChatGPT Export Processing Estimate ===
Conversations: {num_conversations:,}

TIME ESTIMATES:
  Base processing: {estimate['time']['base_processing_seconds']:.0f}s ({estimate['time']['base_processing_seconds']/60:.1f} min)
  Batch overhead: {estimate['time']['batch_overhead_seconds']:.0f}s
  Checkpoint saves: {estimate['time']['checkpoint_overhead_seconds']:.0f}s
  ─────────────────────────────────────
  Total time: {estimate['time']['total_minutes']:.1f} minutes
  Speed: {estimate['time']['items_per_minute']:.0f} conversations/minute

STORAGE REQUIREMENTS:
  Embeddings: {estimate['storage']['embedding_mb']:.1f} MB
  Metadata: {estimate['storage']['metadata_bytes']/1024/1024:.1f} MB
  Overhead: {estimate['storage']['pickle_overhead']/1024/1024:.1f} MB
  ─────────────────────────────────────
  Total storage: {estimate['storage']['total_mb']:.1f} MB
  Per conversation: {estimate['storage']['per_item_kb']:.1f} KB

MEMORY USAGE:
  Text in memory: {estimate['memory']['text_memory_mb']:.1f} MB
  All embeddings: {estimate['memory']['embeddings_memory_mb']:.1f} MB
  Python overhead: {estimate['memory']['python_overhead_mb']:.1f} MB
  ─────────────────────────────────────
  Peak memory: {estimate['memory']['peak_memory_mb']:.1f} MB

OLLAMA SERVER LOAD:
  Total API calls: {estimate['ollama']['total_requests']:,}
  Request rate: {estimate['ollama']['requests_per_second']:.0f} req/s
  Model memory: {estimate['ollama']['model_memory_mb']} MB
  GPU usage: {estimate['ollama']['gpu_usage_estimate']}
"""
        return report


def analyze_current_export(export_path: str) -> Dict[str, Any]:
    """Analyze an actual ChatGPT export to get real statistics."""
    stats = {}
    
    # Check conversations.json
    conv_path = os.path.join(export_path, 'conversations.json')
    if os.path.exists(conv_path):
        import json
        with open(conv_path, 'r') as f:
            conversations = json.load(f)
        
        stats['num_conversations'] = len(conversations)
        
        # Sample conversation sizes
        total_messages = 0
        total_chars = 0
        
        for conv in conversations[:100]:  # Sample first 100
            if 'mapping' in conv:
                messages = 0
                chars = 0
                for node in conv['mapping'].values():
                    if node and 'message' in node and node['message'] and node['message'].get('content'):
                        messages += 1
                        content = node['message']['content']
                        if 'parts' in content:
                            for part in content['parts']:
                                if isinstance(part, str):
                                    chars += len(part)
                total_messages += messages
                total_chars += chars
        
        stats['avg_messages_per_conversation'] = total_messages / min(100, len(conversations))
        stats['avg_chars_per_conversation'] = total_chars / min(100, len(conversations))
    
    # Check file sizes
    files = ['conversations.json', 'user.json', 'message_feedback.json', 'shared_conversations.json']
    stats['file_sizes'] = {}
    
    for file in files:
        file_path = os.path.join(export_path, file)
        if os.path.exists(file_path):
            stats['file_sizes'][file] = os.path.getsize(file_path) / (1024 * 1024)  # MB
    
    return stats


if __name__ == "__main__":
    # Example calculations
    calculator = ProcessingCalculator()
    
    # Your actual data
    num_conversations = 13007
    
    print(calculator.format_estimate_report(num_conversations))
    
    # Analyze actual export if available
    export_path = "/Users/ebowwa/Downloads/chatgpt-export/user-data/2025-07-20_Sunday_12-04-32"
    if os.path.exists(export_path):
        print("\n=== Actual Export Analysis ===")
        stats = analyze_current_export(export_path)
        print(f"Conversations found: {stats.get('num_conversations', 'N/A'):,}")
        print(f"Avg messages/conversation: {stats.get('avg_messages_per_conversation', 'N/A'):.1f}")
        print(f"Avg characters/conversation: {stats.get('avg_chars_per_conversation', 'N/A'):,.0f}")
        print("\nFile sizes:")
        for file, size in stats.get('file_sizes', {}).items():
            print(f"  {file}: {size:.1f} MB")