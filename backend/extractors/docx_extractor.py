"""
DOCX document extraction with heading and formatting preservation
"""
from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class DOCXExtractor:
    """Extract content from DOCX files"""
    
    def extract(self, file_path: str) -> Dict:
        """
        Extract text, headings, images, and tables from DOCX
        
        Args:
            file_path: Path to DOCX file
            
        Returns:
            Dictionary containing extracted content
        """
        try:
            doc = Document(file_path)
            
            result = {
                'text': '',
                'headings': [],
                'sections': [],
                'images': [],
                'tables': [],
                'metadata': {}
            }
            
            # Extract core properties
            if doc.core_properties:
                result['metadata'] = {
                    'title': doc.core_properties.title or '',
                    'author': doc.core_properties.author or '',
                    'subject': doc.core_properties.subject or ''
                }
            
            # Extract paragraphs and detect headings
            full_text = []
            current_section = None
            section_content = []
            
            for para_idx, para in enumerate(doc.paragraphs):
                text = para.text.strip()
                if not text:
                    continue
                
                # Check if paragraph is a heading
                style_name = para.style.name if para.style else ''
                is_heading = style_name.startswith('Heading')
                
                if is_heading:
                    # Save previous section
                    if current_section:
                        result['sections'].append({
                            'title': current_section['text'],
                            'level': current_section['level'],
                            'content': '\n'.join(section_content).strip()
                        })
                        section_content = []
                    
                    # Extract heading level
                    level = 1
                    if 'Heading' in style_name:
                        try:
                            level = int(style_name.split()[-1])
                        except:
                            level = 1
                    
                    heading = {
                        'text': text,
                        'level': min(level, 6),
                        'paragraph': para_idx
                    }
                    result['headings'].append(heading)
                    current_section = heading
                else:
                    # Regular paragraph
                    full_text.append(text)
                    if current_section:
                        section_content.append(text)
            
            # Save last section
            if current_section and section_content:
                result['sections'].append({
                    'title': current_section['text'],
                    'level': current_section['level'],
                    'content': '\n'.join(section_content).strip()
                })
            
            result['text'] = '\n\n'.join(full_text)
            
            # Extract tables
            for table_idx, table in enumerate(doc.tables):
                table_data = []
                for row in table.rows:
                    row_data = [cell.text.strip() for cell in row.cells]
                    table_data.append(row_data)
                
                result['tables'].append({
                    'index': table_idx,
                    'data': table_data,
                    'rows': len(table.rows),
                    'cols': len(table.columns)
                })
            
            # Extract images (inline shapes)
            for shape_idx, shape in enumerate(doc.inline_shapes):
                result['images'].append({
                    'index': shape_idx,
                    'type': 'inline_shape'
                })
            
            logger.info(f"Extracted {len(result['headings'])} headings, "
                       f"{len(result['tables'])} tables, "
                       f"{len(result['images'])} images from DOCX")
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting DOCX: {e}")
            raise


def extract_docx(file_path: str) -> Dict:
    """
    Convenience function to extract DOCX content
    
    Args:
        file_path: Path to DOCX file
        
    Returns:
        Extracted content dictionary
    """
    extractor = DOCXExtractor()
    return extractor.extract(file_path)
