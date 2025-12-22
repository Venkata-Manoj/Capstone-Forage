"""
PDF document extraction with heading detection and OCR fallback
"""
import PyPDF2
from PIL import Image
import pytesseract
from pathlib import Path
from typing import Dict, List, Optional
import logging
import io
import re

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extract content from PDF files"""
    
    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize PDF extractor
        
        Args:
            tesseract_cmd: Path to tesseract executable
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    
    def extract(self, file_path: str) -> Dict:
        """
        Extract text, headings, images, and tables from PDF
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary containing extracted content
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                result = {
                    'text': '',
                    'headings': [],
                    'sections': [],
                    'images': [],
                    'pages': len(pdf_reader.pages),
                    'metadata': {}
                }
                
                # Extract metadata
                if pdf_reader.metadata:
                    result['metadata'] = {
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', '')
                    }
                
                # Extract text from each page
                full_text = []
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            full_text.append(page_text)
                            # Detect headings using heuristics
                            headings = self._detect_headings(page_text, page_num)
                            result['headings'].extend(headings)
                        else:
                            # Try OCR if no text extracted
                            logger.info(f"No text on page {page_num}, attempting OCR")
                            ocr_text = self._ocr_page(page)
                            if ocr_text:
                                full_text.append(ocr_text)
                    except Exception as e:
                        logger.error(f"Error extracting page {page_num}: {e}")
                
                result['text'] = '\n\n'.join(full_text)
                
                # Extract sections based on headings
                result['sections'] = self._extract_sections(result['text'], result['headings'])
                
                logger.info(f"Extracted {len(result['headings'])} headings from {result['pages']} pages")
                return result
                
        except Exception as e:
            logger.error(f"Error extracting PDF: {e}")
            raise
    
    def _detect_headings(self, text: str, page_num: int) -> List[Dict]:
        """
        Detect headings using text patterns
        
        Args:
            text: Page text
            page_num: Page number
            
        Returns:
            List of detected headings
        """
        headings = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Heuristics for heading detection:
            # 1. All caps (likely heading)
            # 2. Numbered sections (1., 1.1, etc.)
            # 3. Short lines (< 100 chars) followed by longer content
            # 4. Common heading keywords
            
            is_heading = False
            level = 1
            
            # Check for numbered sections
            numbered_match = re.match(r'^(\d+\.)+\s+(.+)$', line)
            if numbered_match:
                is_heading = True
                level = numbered_match.group(1).count('.')
            
            # Check for all caps (but not too long)
            elif line.isupper() and len(line) < 100:
                is_heading = True
                level = 1
            
            # Check for common heading keywords
            elif any(keyword in line.lower() for keyword in [
                'introduction', 'abstract', 'conclusion', 'methodology',
                'literature review', 'implementation', 'results',
                'references', 'appendix', 'acknowledgement', 'chapter'
            ]):
                is_heading = True
                level = 1 if 'chapter' in line.lower() else 2
            
            if is_heading:
                headings.append({
                    'text': line,
                    'level': min(level, 6),  # Cap at H6
                    'page': page_num,
                    'line': i
                })
        
        return headings
    
    def _extract_sections(self, text: str, headings: List[Dict]) -> List[Dict]:
        """
        Extract sections based on detected headings
        
        Args:
            text: Full document text
            headings: List of detected headings
            
        Returns:
            List of sections with content
        """
        if not headings:
            return [{'title': 'Content', 'content': text, 'level': 1}]
        
        sections = []
        lines = text.split('\n')
        
        for i, heading in enumerate(headings):
            section = {
                'title': heading['text'],
                'level': heading['level'],
                'page': heading['page']
            }
            
            # Find content between this heading and next
            start_line = heading['line']
            end_line = headings[i + 1]['line'] if i + 1 < len(headings) else len(lines)
            
            content_lines = lines[start_line + 1:end_line]
            section['content'] = '\n'.join(content_lines).strip()
            
            sections.append(section)
        
        return sections
    
    def _ocr_page(self, page) -> Optional[str]:
        """
        Perform OCR on a PDF page
        
        Args:
            page: PDF page object
            
        Returns:
            Extracted text or None
        """
        try:
            # This is a simplified OCR approach
            # In production, you'd extract images from the page and OCR them
            logger.warning("OCR not fully implemented for PDF pages")
            return None
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return None


def extract_pdf(file_path: str, tesseract_cmd: Optional[str] = None) -> Dict:
    """
    Convenience function to extract PDF content
    
    Args:
        file_path: Path to PDF file
        tesseract_cmd: Path to tesseract executable
        
    Returns:
        Extracted content dictionary
    """
    extractor = PDFExtractor(tesseract_cmd)
    return extractor.extract(file_path)
