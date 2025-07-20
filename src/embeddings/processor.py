"""
Conversation processor for extracting and chunking ChatGPT conversations.
"""

from typing import List, Dict, Any, Optional, Generator
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ConversationChunk:
    """Represents a chunk of conversation to be embedded."""
    conversation_id: str
    chunk_id: str
    text: str
    metadata: Dict[str, Any]


class ConversationProcessor:
    """Process ChatGPT conversations for embedding generation."""
    
    def __init__(self, max_chunk_length: int = 8000):
        """
        Initialize the conversation processor.
        
        Args:
            max_chunk_length: Maximum length of text chunks
        """
        self.max_chunk_length = max_chunk_length
        
    def extract_conversation_text(self, conversation: Dict[str, Any]) -> List[ConversationChunk]:
        """
        Extract text chunks from a conversation.
        
        Args:
            conversation: The conversation data dictionary
            
        Returns:
            List of conversation chunks
        """
        chunks = []
        
        # Extract basic metadata
        conv_id = conversation.get('id', 'unknown')
        title = conversation.get('title', 'Untitled')
        
        # Extract messages from mapping structure
        messages = self._extract_messages(conversation)
        
        if messages:
            # Create chunks from messages
            full_text = self._format_conversation(title, messages)
            
            # For now, create one chunk per conversation
            # TODO: Implement proper chunking for very long conversations
            chunk = ConversationChunk(
                conversation_id=conv_id,
                chunk_id=f"{conv_id}_full",
                text=full_text[:self.max_chunk_length],
                metadata={
                    'title': title,
                    'message_count': len(messages),
                    'truncated': len(full_text) > self.max_chunk_length
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    def _extract_messages(self, conversation: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract messages from conversation mapping structure."""
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
                    
                    if text_parts:
                        content = ' '.join(text_parts)
                        role = msg.get('author', {}).get('role', 'unknown')
                        messages.append({
                            'role': role,
                            'content': content
                        })
        
        return messages
    
    def _format_conversation(self, title: str, messages: List[Dict[str, str]]) -> str:
        """Format messages into a single text string."""
        lines = [f"Title: {title}", ""]
        
        for msg in messages:
            role = msg['role'].upper()
            content = msg['content']
            lines.append(f"{role}: {content}")
            lines.append("")
        
        return "\n".join(lines)
    
    def process_conversations_generator(
        self,
        conversations: List[Dict[str, Any]]
    ) -> Generator[ConversationChunk, None, None]:
        """
        Process conversations as a generator to save memory.
        
        Args:
            conversations: List of conversation dictionaries
            
        Yields:
            ConversationChunk objects
        """
        for i, conv in enumerate(conversations):
            try:
                chunks = self.extract_conversation_text(conv)
                for chunk in chunks:
                    yield chunk
            except Exception as e:
                logger.error(f"Error processing conversation {i}: {e}")
                continue