"""
Image OCR extraction using Tesseract
"""
from PIL import Image
import pytesseract
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ImageExtractor:
    """Extract text from images using OCR"""
    
    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize image extractor
        
        Args:
            tesseract_cmd: Path to tesseract executable
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    
    def extract(self, file_path: str) -> Dict:
        """
        Extract text from image using OCR
        
        Args:
            file_path: Path to image file
            
        Returns:
            Dictionary containing extracted content
        """
        try:
            # Open and preprocess image
            image = Image.open(file_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
            
            result = {
                'text': text.strip(),
                'headings': [],
                'sections': [],
                'images': [{'source': file_path}],
                'metadata': {
                    'width': image.width,
                    'height': image.height,
                    'format': image.format
                }
            }
            
            # Simple heading detection from OCR text
            if result['text']:
                lines = result['text'].split('\n')
                for i, line in enumerate(lines):
                    line = line.strip()
                    # Detect potential headings (short lines, all caps, etc.)
                    if line and (line.isupper() or len(line) < 50):
                        result['headings'].append({
                            'text': line,
                            'level': 1,
                            'line': i
                        })
            
            logger.info(f"Extracted {len(result['text'])} characters from image via OCR")
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting image: {e}")
            raise


def extract_image(file_path: str, tesseract_cmd: Optional[str] = None) -> Dict:
    """
    Convenience function to extract image content
    
    Args:
        file_path: Path to image file
        tesseract_cmd: Path to tesseract executable
        
    Returns:
        Extracted content dictionary
    """
    extractor = ImageExtractor(tesseract_cmd)
    return extractor.extract(file_path)
