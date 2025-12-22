"""
Text chunking for RAG pipeline
Splits extracted text into semantic chunks with overlap
"""
from typing import List, Dict
import re
import logging

logger = logging.getLogger(__name__)


class TextChunker:
    """Chunk text into semantic blocks for embedding"""
    
    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 200,
        min_chunk_size: int = 100
    ):
        """
        Initialize text chunker
        
        Args:
            chunk_size: Target size of each chunk in characters
            chunk_overlap: Overlap between chunks for continuity
            min_chunk_size: Minimum chunk size to keep
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
    
    def chunk_by_sections(self, sections: List[Dict]) -> List[Dict]:
        """
        Chunk text by sections with metadata preservation
        
        Args:
            sections: List of sections from document extraction
            
        Returns:
            List of chunks with metadata
        """
        chunks = []
        
        for section in sections:
            title = section.get('title', '')
            content = section.get('content', '')
            level = section.get('level', 1)
            
            if not content:
                continue
            
            # Split section content into chunks
            section_chunks = self._split_text(content)
            
            # Add metadata to each chunk
            for i, chunk_text in enumerate(section_chunks):
                if len(chunk_text) < self.min_chunk_size:
                    continue
                
                chunks.append({
                    'text': chunk_text,
                    'metadata': {
                        'section_title': title,
                        'section_level': level,
                        'chunk_index': i,
                        'page': section.get('page'),
                        'slide': section.get('slide')
                    }
                })
        
        logger.info(f"Created {len(chunks)} chunks from {len(sections)} sections")
        return chunks
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Chunk plain text without section information
        
        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of chunks with metadata
        """
        chunks = []
        chunk_texts = self._split_text(text)
        
        for i, chunk_text in enumerate(chunk_texts):
            if len(chunk_text) < self.min_chunk_size:
                continue
            
            chunk = {
                'text': chunk_text,
                'metadata': metadata or {}
            }
            chunk['metadata']['chunk_index'] = i
            chunks.append(chunk)
        
        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks
    
    def _split_text(self, text: str) -> List[str]:
        """
        Split text into chunks with overlap
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        # Split by paragraphs first
        paragraphs = re.split(r'\n\s*\n', text)
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            para_size = len(para)
            
            # If single paragraph exceeds chunk size, split it
            if para_size > self.chunk_size:
                # Save current chunk if any
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = []
                    current_size = 0
                
                # Split large paragraph by sentences
                sentences = self._split_sentences(para)
                temp_chunk = []
                temp_size = 0
                
                for sent in sentences:
                    sent_size = len(sent)
                    if temp_size + sent_size > self.chunk_size and temp_chunk:
                        chunks.append(' '.join(temp_chunk))
                        # Keep overlap
                        overlap_text = ' '.join(temp_chunk[-2:]) if len(temp_chunk) >= 2 else ''
                        temp_chunk = [overlap_text] if overlap_text else []
                        temp_size = len(overlap_text)
                    
                    temp_chunk.append(sent)
                    temp_size += sent_size
                
                if temp_chunk:
                    chunks.append(' '.join(temp_chunk))
            
            # Add paragraph to current chunk
            elif current_size + para_size > self.chunk_size:
                # Save current chunk
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                
                # Start new chunk with overlap
                if self.chunk_overlap > 0 and current_chunk:
                    overlap_para = current_chunk[-1]
                    current_chunk = [overlap_para, para]
                    current_size = len(overlap_para) + para_size
                else:
                    current_chunk = [para]
                    current_size = para_size
            else:
                current_chunk.append(para)
                current_size += para_size
        
        # Add remaining chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]


def chunk_document(extracted_data: Dict, chunk_size: int = 800) -> List[Dict]:
    """
    Convenience function to chunk extracted document
    
    Args:
        extracted_data: Extracted document data
        chunk_size: Target chunk size
        
    Returns:
        List of chunks with metadata
    """
    chunker = TextChunker(chunk_size=chunk_size)
    
    # Prefer chunking by sections if available
    if extracted_data.get('sections'):
        return chunker.chunk_by_sections(extracted_data['sections'])
    else:
        return chunker.chunk_text(
            extracted_data.get('text', ''),
            metadata=extracted_data.get('metadata', {})
        )
