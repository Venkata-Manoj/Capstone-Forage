"""
Embedding generation using sentence-transformers
"""
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import numpy as np
import logging

logger = logging.getLogger(__name__)


class Embedder:
    """Generate embeddings for text chunks"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedder
        
        Args:
            model_name: Name of sentence-transformer model
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the embedding model"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Model loaded successfully. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def embed_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """
        Generate embeddings for text chunks
        
        Args:
            chunks: List of chunks with text and metadata
            
        Returns:
            Chunks with added embeddings
        """
        if not chunks:
            return []
        
        # Extract texts
        texts = [chunk['text'] for chunk in chunks]
        
        # Generate embeddings in batch
        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        # Add embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk['embedding'] = embedding
        
        logger.info(f"Generated {len(embeddings)} embeddings")
        return chunks
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        return self.model.encode(text, convert_to_numpy=True)
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings"""
        return self.model.get_sentence_embedding_dimension()


# Global embedder instance (lazy loaded)
_embedder_instance = None


def get_embedder(model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> Embedder:
    """
    Get or create global embedder instance
    
    Args:
        model_name: Name of embedding model
        
    Returns:
        Embedder instance
    """
    global _embedder_instance
    if _embedder_instance is None:
        _embedder_instance = Embedder(model_name)
    return _embedder_instance
