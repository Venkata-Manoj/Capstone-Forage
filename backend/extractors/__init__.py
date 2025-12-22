"""
Unified document extractor - routes to appropriate extractor based on file type
"""
from pathlib import Path
from typing import Dict
import logging

from .pdf_extractor import extract_pdf
from .docx_extractor import extract_docx
from .pptx_extractor import extract_pptx
from .image_extractor import extract_image

logger = logging.getLogger(__name__)


class DocumentExtractor:
    """Unified document extraction interface"""
    
    SUPPORTED_EXTENSIONS = {
        '.pdf': 'pdf',
        '.docx': 'docx',
        '.doc': 'docx',
        '.pptx': 'pptx',
        '.ppt': 'pptx',
        '.png': 'image',
        '.jpg': 'image',
        '.jpeg': 'image',
        '.txt': 'text'
    }
    
    def __init__(self, tesseract_cmd: str = None):
        """
        Initialize document extractor
        
        Args:
            tesseract_cmd: Path to tesseract executable
        """
        self.tesseract_cmd = tesseract_cmd
    
    def extract(self, file_path: str) -> Dict:
        """
        Extract content from document
        
        Args:
            file_path: Path to document file
            
        Returns:
            Dictionary containing extracted content
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {extension}")
        
        file_type = self.SUPPORTED_EXTENSIONS[extension]
        
        logger.info(f"Extracting {file_type} file: {path.name}")
        
        try:
            if file_type == 'pdf':
                result = extract_pdf(file_path, self.tesseract_cmd)
            elif file_type == 'docx':
                result = extract_docx(file_path)
            elif file_type == 'pptx':
                result = extract_pptx(file_path)
            elif file_type == 'image':
                result = extract_image(file_path, self.tesseract_cmd)
            elif file_type == 'text':
                result = self._extract_text(file_path)
            else:
                raise ValueError(f"Handler not implemented for: {file_type}")
            
            # Add file metadata
            result['file_info'] = {
                'name': path.name,
                'extension': extension,
                'type': file_type,
                'size': path.stat().st_size
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting {file_type}: {e}")
            raise
    
    def _extract_text(self, file_path: str) -> Dict:
        """
        Extract plain text file
        
        Args:
            file_path: Path to text file
            
        Returns:
            Extracted content dictionary
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        return {
            'text': text,
            'headings': [],
            'sections': [],
            'images': [],
            'metadata': {}
        }
    
    @classmethod
    def is_supported(cls, file_path: str) -> bool:
        """
        Check if file type is supported
        
        Args:
            file_path: Path to file
            
        Returns:
            True if supported, False otherwise
        """
        extension = Path(file_path).suffix.lower()
        return extension in cls.SUPPORTED_EXTENSIONS


def extract_document(file_path: str, tesseract_cmd: str = None) -> Dict:
    """
    Convenience function to extract document content
    
    Args:
        file_path: Path to document file
        tesseract_cmd: Path to tesseract executable
        
    Returns:
        Extracted content dictionary
    """
    extractor = DocumentExtractor(tesseract_cmd)
    return extractor.extract(file_path)
