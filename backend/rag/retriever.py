"""
Retriever for RAG pipeline - combines query embedding and vector search
"""
from typing import List, Dict
import logging

from .embedder import get_embedder
from .vector_store import VectorStore

logger = logging.getLogger(__name__)


class Retriever:
    """Retrieve relevant chunks for a query"""
    
    def __init__(self, vector_store: VectorStore, embedder=None):
        """
        Initialize retriever
        
        Args:
            vector_store: Vector store instance
            embedder: Embedder instance (optional, will use global if not provided)
        """
        self.vector_store = vector_store
        self.embedder = embedder or get_embedder()
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float = None
    ) -> List[Dict]:
        """
        Retrieve relevant chunks for a query
        
        Args:
            query: Query text
            top_k: Number of chunks to retrieve
            min_similarity: Minimum similarity threshold (optional)
            
        Returns:
            List of relevant chunks with scores
        """
        # Generate query embedding
        query_embedding = self.embedder.embed_text(query)
        
        # Search vector store
        results = self.vector_store.search(query_embedding, top_k)
        
        # Filter by similarity if threshold provided
        if min_similarity is not None:
            # Convert L2 distance to similarity score (inverse)
            results = [
                (chunk, dist) for chunk, dist in results
                if self._distance_to_similarity(dist) >= min_similarity
            ]
        
        # Format results
        retrieved_chunks = []
        for chunk, distance in results:
            chunk_with_score = chunk.copy()
            chunk_with_score['similarity_score'] = self._distance_to_similarity(distance)
            chunk_with_score['distance'] = distance
            retrieved_chunks.append(chunk_with_score)
        
        logger.info(f"Retrieved {len(retrieved_chunks)} chunks for query")
        return retrieved_chunks
    
    def retrieve_for_section(
        self,
        section_name: str,
        project_title: str,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Retrieve chunks relevant for a specific report section
        
        Args:
            section_name: Name of the section (e.g., "Introduction", "Methodology")
            project_title: Project title for context
            top_k: Number of chunks to retrieve
            
        Returns:
            List of relevant chunks
        """
        # Create section-specific query
        query = f"{project_title} - {section_name}"
        
        # Add section-specific keywords
        section_keywords = {
            'Introduction': 'overview background objectives scope',
            'Literature Review': 'existing work related research previous studies',
            'Methodology': 'approach methods techniques implementation process',
            'System Design': 'architecture design structure components modules',
            'Implementation': 'development code programming implementation details',
            'Results': 'outcomes results findings observations data',
            'Conclusion': 'summary conclusions achievements outcomes',
            'Future Scope': 'future enhancements improvements extensions'
        }
        
        if section_name in section_keywords:
            query += f" {section_keywords[section_name]}"
        
        return self.retrieve(query, top_k)
    
    def _distance_to_similarity(self, distance: float) -> float:
        """
        Convert L2 distance to similarity score (0-1)
        
        Args:
            distance: L2 distance
            
        Returns:
            Similarity score (higher is more similar)
        """
        # Simple inverse transformation
        # For L2 distance, smaller is better, so we invert it
        return 1.0 / (1.0 + distance)
    
    def get_context_window(
        self,
        chunks: List[Dict],
        max_tokens: int = 3000
    ) -> str:
        """
        Combine chunks into a context window with token limit
        
        Args:
            chunks: List of chunks
            max_tokens: Maximum tokens (approximated as chars/4)
            
        Returns:
            Combined context text
        """
        context_parts = []
        current_tokens = 0
        max_chars = max_tokens * 4  # Rough approximation
        
        for chunk in chunks:
            text = chunk['text']
            metadata = chunk.get('metadata', {})
            
            # Add section title if available
            section_title = metadata.get('section_title', '')
            if section_title:
                header = f"\n## {section_title}\n"
                text = header + text
            
            chunk_chars = len(text)
            
            if current_tokens + chunk_chars > max_chars:
                break
            
            context_parts.append(text)
            current_tokens += chunk_chars
        
        return '\n\n'.join(context_parts)
