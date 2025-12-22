"""
RAG Pipeline - Unified interface for document processing and retrieval
"""
from typing import Dict, List
import logging
from pathlib import Path

from .chunker import TextChunker, chunk_document
from .embedder import get_embedder
from .vector_store import VectorStore
from .retriever import Retriever

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Complete RAG pipeline for document processing and retrieval"""
    
    def __init__(
        self,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        chunk_size: int = 800,
        index_dir: str = "./faiss_indexes"
    ):
        """
        Initialize RAG pipeline
        
        Args:
            embedding_model: Name of embedding model
            chunk_size: Size of text chunks
            index_dir: Directory to store FAISS indexes
        """
        self.chunk_size = chunk_size
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.chunker = TextChunker(chunk_size=chunk_size)
        self.embedder = get_embedder(embedding_model)
        self.vector_store = VectorStore(
            dimension=self.embedder.get_embedding_dimension()
        )
        self.retriever = Retriever(self.vector_store, self.embedder)
        
        logger.info("RAG pipeline initialized")
    
    def process_document(
        self,
        extracted_data: Dict,
        document_id: str
    ) -> Dict:
        """
        Process extracted document through RAG pipeline
        
        Args:
            extracted_data: Extracted document data
            document_id: Unique document identifier
            
        Returns:
            Processing statistics
        """
        logger.info(f"Processing document {document_id}")
        
        # Step 1: Chunk the document
        chunks = chunk_document(extracted_data, self.chunk_size)
        logger.info(f"Created {len(chunks)} chunks")
        
        # Step 2: Generate embeddings
        chunks_with_embeddings = self.embedder.embed_chunks(chunks)
        logger.info(f"Generated embeddings for {len(chunks_with_embeddings)} chunks")
        
        # Step 3: Add to vector store
        self.vector_store.add_chunks(chunks_with_embeddings)
        
        # Step 4: Save index
        index_path = self.index_dir / document_id
        self.vector_store.save(str(index_path))
        
        stats = {
            'document_id': document_id,
            'total_chunks': len(chunks),
            'vector_store_stats': self.vector_store.get_stats()
        }
        
        logger.info(f"Document processing complete: {stats}")
        return stats
    
    def load_document_index(self, document_id: str):
        """
        Load a previously saved document index
        
        Args:
            document_id: Document identifier
        """
        index_path = self.index_dir / document_id
        self.vector_store.load(str(index_path))
        logger.info(f"Loaded index for document {document_id}")
    
    def retrieve_context(
        self,
        query: str,
        top_k: int = 5
    ) -> str:
        """
        Retrieve context for a query
        
        Args:
            query: Query text
            top_k: Number of chunks to retrieve
            
        Returns:
            Combined context text
        """
        chunks = self.retriever.retrieve(query, top_k)
        context = self.retriever.get_context_window(chunks)
        return context
    
    def retrieve_for_section(
        self,
        section_name: str,
        project_title: str,
        top_k: int = 5
    ) -> str:
        """
        Retrieve context for a specific report section
        
        Args:
            section_name: Section name
            project_title: Project title
            top_k: Number of chunks to retrieve
            
        Returns:
            Combined context text
        """
        chunks = self.retriever.retrieve_for_section(
            section_name,
            project_title,
            top_k
        )
        context = self.retriever.get_context_window(chunks)
        return context
    
    def clear(self):
        """Clear the vector store"""
        self.vector_store.clear()
        logger.info("RAG pipeline cleared")


# Global pipeline instance
_pipeline_instance = None


def get_rag_pipeline(
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    chunk_size: int = 800,
    index_dir: str = "./faiss_indexes"
) -> RAGPipeline:
    """
    Get or create global RAG pipeline instance
    
    Args:
        embedding_model: Name of embedding model
        chunk_size: Size of text chunks
        index_dir: Directory to store indexes
        
    Returns:
        RAG pipeline instance
    """
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = RAGPipeline(embedding_model, chunk_size, index_dir)
    return _pipeline_instance
