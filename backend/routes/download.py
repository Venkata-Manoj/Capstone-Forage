"""
Download API routes
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import logging

from database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/download/{report_id}")
async def download_report(report_id: str, format: str = "docx"):
    """
    Download generated report
    
    Args:
        report_id: Report ID
        format: File format (docx or pdf)
        
    Returns:
        File download response
    """
    try:
        # Get report info
        db = get_db()
        report = db.get_report(report_id)
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Check if generation is complete
        if report['status'] != 'completed':
            raise HTTPException(
                status_code=400,
                detail=f"Report is not ready. Status: {report['status']}"
            )
        
        # Get file path based on format
        if format.lower() == 'pdf':
            file_path = report.get('pdf_path')
            if not file_path:
                raise HTTPException(
                    status_code=404,
                    detail="PDF version not available"
                )
            media_type = 'application/pdf'
            filename = f"{report['title']}.pdf"
        else:
            file_path = report.get('docx_path')
            if not file_path:
                raise HTTPException(
                    status_code=404,
                    detail="DOCX version not available"
                )
            media_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            filename = f"{report['title']}.docx"
        
        # Check if file exists
        if not Path(file_path).exists():
            raise HTTPException(
                status_code=404,
                detail="File not found on server"
            )
        
        logger.info(f"Downloading report {report_id} as {format}")
        
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
