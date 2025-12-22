"""
PDF conversion using LibreOffice
"""
import subprocess
from pathlib import Path
import logging
from config import settings

logger = logging.getLogger(__name__)


class PDFConverter:
    """Convert DOCX to PDF using LibreOffice"""
    
    def __init__(self, libreoffice_path: str = None):
        """
        Initialize PDF converter
        
        Args:
            libreoffice_path: Path to LibreOffice executable
        """
        self.libreoffice_path = libreoffice_path or settings.libreoffice_path
    
    def convert(self, docx_path: str, output_dir: str = None) -> str:
        """
        Convert DOCX to PDF
        
        Args:
            docx_path: Path to DOCX file
            output_dir: Output directory (default: same as input)
            
        Returns:
            Path to created PDF file
        """
        docx_path = Path(docx_path)
        
        if not docx_path.exists():
            raise FileNotFoundError(f"DOCX file not found: {docx_path}")
        
        # Determine output directory
        if output_dir is None:
            output_dir = docx_path.parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # Try LibreOffice conversion
        try:
            logger.info(f"Converting {docx_path.name} to PDF using LibreOffice...")
            
            cmd = [
                self.libreoffice_path,
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', str(output_dir),
                str(docx_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            if result.returncode == 0:
                pdf_path = output_dir / docx_path.with_suffix('.pdf').name
                if pdf_path.exists():
                    logger.info(f"PDF created successfully: {pdf_path}")
                    return str(pdf_path)
                else:
                    raise RuntimeError("PDF file not created")
            else:
                raise RuntimeError(f"LibreOffice conversion failed: {result.stderr}")
                
        except FileNotFoundError:
            logger.error(f"LibreOffice not found at: {self.libreoffice_path}")
            # Fallback to docx2pdf
            return self._convert_with_docx2pdf(docx_path, output_dir)
        except Exception as e:
            logger.error(f"LibreOffice conversion failed: {e}")
            # Fallback to docx2pdf
            return self._convert_with_docx2pdf(docx_path, output_dir)
    
    def _convert_with_docx2pdf(self, docx_path: Path, output_dir: Path) -> str:
        """
        Fallback conversion using docx2pdf
        
        Args:
            docx_path: Path to DOCX file
            output_dir: Output directory
            
        Returns:
            Path to created PDF
        """
        try:
            from docx2pdf import convert
            
            logger.info(f"Converting {docx_path.name} to PDF using docx2pdf...")
            
            pdf_path = output_dir / docx_path.with_suffix('.pdf').name
            convert(str(docx_path), str(pdf_path))
            
            if pdf_path.exists():
                logger.info(f"PDF created successfully: {pdf_path}")
                return str(pdf_path)
            else:
                raise RuntimeError("PDF file not created")
                
        except Exception as e:
            logger.error(f"docx2pdf conversion failed: {e}")
            raise RuntimeError(f"All PDF conversion methods failed: {e}")


def convert_to_pdf(docx_path: str, output_dir: str = None) -> str:
    """
    Convenience function to convert DOCX to PDF
    
    Args:
        docx_path: Path to DOCX file
        output_dir: Output directory
        
    Returns:
        Path to created PDF
    """
    converter = PDFConverter()
    return converter.convert(docx_path, output_dir)
