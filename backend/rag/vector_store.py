"""
FAISS vector store for similarity search
"""
import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    """FAISS-based vector store for chunk embeddings"""
    
    def __init__(self, dimension: int = 384, index_path: Optional[str] = None):
        """
        Initialize vector store
        
        Args:
            dimension: Embedding dimension
            index_path: Path to save/load index
        """
        self.dimension = dimension
        self.index_path = index_path
        self.index = None
        self.chunks = []
        
        # Create or load index
        if index_path and Path(index_path).exists():
            self.load(index_path)
        else:
            self._create_index()
    
    def _create_index(self):
        """Create a new FAISS index"""
        # Using IndexFlatL2 for exact search (good for small-medium datasets)
        # For larger datasets, consider IndexIVFFlat or IndexHNSWFlat
        self.index = faiss.IndexFlatL2(self.dimension)
        logger.info(f"Created new FAISS index with dimension {self.dimension}")
    
    def add_chunks(self, chunks: List[Dict]):
        """
        Add chunks with embeddings to the index
        
        Args:
            chunks: List of chunks with 'embedding' field
        """
        if not chunks:
            return
        
        # Extract embeddings
        embeddings = np.array([chunk['embedding'] for chunk in chunks], dtype='float32')
        
        # Add to index
        self.index.add(embeddings)
        
        # Store chunks (without embeddings to save memory)
        for chunk in chunks:
            chunk_copy = chunk.copy()
            # Remove embedding from stored chunk
            if 'embedding' in chunk_copy:
                del chunk_copy['embedding']
            self.chunks.append(chunk_copy)
        
        logger.info(f"Added {len(chunks)} chunks to vector store. Total: {len(self.chunks)}")
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5
    ) -> List[Tuple[Dict, float]]:
        """
        Search for similar chunks
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of (chunk, distance) tuples
        """
        if self.index.ntotal == 0:
            logger.warning("Vector store is empty")
            return []
        
        # Ensure query is 2D array
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Search
        distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        # Return chunks with distances
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.chunks):
                results.append((self.chunks[idx], float(dist)))
        
        logger.info(f"Found {len(results)} similar chunks")
        return results
    
    def save(self, index_path: Optional[str] = None):
        """
        Save index and chunks to disk
        
        Args:
            index_path: Path to save index (without extension)
        """
        path = index_path or self.index_path
        if not path:
            raise ValueError("No index path specified")
        
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(path.with_suffix('.index')))
        
        # Save chunks
        with open(path.with_suffix('.chunks'), 'wb') as f:
            pickle.dump(self.chunks, f)
        
        logger.info(f"Saved vector store to {path}")
    
    def load(self, index_path: str):
        """
        Load index and chunks from disk
        
        Args:
            index_path: Path to load index from (without extension)
        """
        path = Path(index_path)
        
        # Load FAISS index
        index_file = path.with_suffix('.index')
        if not index_file.exists():
            raise FileNotFoundError(f"Index file not found: {index_file}")
        
        self.index = faiss.read_index(str(index_file))
        
        # Load chunks
        chunks_file = path.with_suffix('.chunks')
        if chunks_file.exists():
            with open(chunks_file, 'rb') as f:
                self.chunks = pickle.load(f)
        
        logger.info(f"Loaded vector store from {path}. Total chunks: {len(self.chunks)}")
    
    def clear(self):
        """Clear the vector store"""
        self._create_index()
        self.chunks = []
        logger.info("Vector store cleared")
    
    def get_stats(self) -> Dict:
        """Get vector store statistics"""
        return {
            'total_chunks': len(self.chunks),
            'index_size': self.index.ntotal,
            'dimension': self.dimension
        }
