"""
Embeddings client for generating embeddings using Ollama.
"""

import requests
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class EmbeddingsClient:
    """Client for generating embeddings using Ollama models."""
    
    def __init__(
        self, 
        model: str = "all-minilm", 
        host: str = "http://localhost:11434",
        timeout: int = 30
    ):
        """
        Initialize the embeddings client.
        
        Args:
            model: The Ollama model to use for embeddings
            host: The Ollama server host URL
            timeout: Request timeout in seconds
        """
        self.model = model
        self.host = host
        self.timeout = timeout
        self.embed_endpoint = f"{host}/api/embeddings"
        
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text.
        
        Args:
            text: The text to embed
            
        Returns:
            List of floats representing the embedding, or None if failed
        """
        try:
            response = requests.post(
                self.embed_endpoint,
                json={
                    "model": self.model,
                    "prompt": text
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except requests.exceptions.RequestException as e:
            logger.error(f"Error generating embedding: {e}")
            return None
        except KeyError:
            logger.error(f"Unexpected response format from Ollama")
            return None
    
    def generate_embeddings_batch(
        self, 
        texts: List[str], 
        show_progress: bool = True
    ) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            show_progress: Whether to show progress indicators
            
        Returns:
            List of embeddings (or None for failed items)
        """
        embeddings = []
        for i, text in enumerate(texts):
            if show_progress:
                print(f"Generating embedding {i+1}/{len(texts)}...", end='\r')
            embedding = self.generate_embedding(text)
            embeddings.append(embedding)
        if show_progress:
            print()
        return embeddings
    
    def test_connection(self) -> bool:
        """
        Test if the Ollama server is accessible.
        
        Returns:
            True if server is accessible, False otherwise
        """
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False