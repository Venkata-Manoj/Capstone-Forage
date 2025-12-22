"""
File upload API routes
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import uuid
from typing import Optional
import logging

from config import settings
from database import get_db
from extractors import DocumentExtractor, extract_document
from rag import get_rag_pipeline

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    title: str = Form(...),
    student_name: Optional[str] = Form(None),
    roll_no: Optional[str] = Form(None),
    subject: Optional[str] = Form(None),
    faculty_name: Optional[str] = Form(None)
):
    """
    Upload reference file and extract content
    
    Args:
        file: Uploaded file
        title: Project title
        student_name: Student name (optional)
        roll_no: Roll number (optional)
        subject: Subject (optional)
        faculty_name: Faculty name (optional)
        
    Returns:
        File ID and extraction status
    """
    try:
        # Validate file type
        if not DocumentExtractor.is_supported(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported: PDF, DOCX, PPTX, images"
            )
        
        # Validate file size
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > settings.max_upload_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.max_upload_size / 1024 / 1024}MB"
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Save file
        file_path = Path(settings.upload_dir) / f"{file_id}_{file.filename}"
        with open(file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"File uploaded: {file.filename} ({file_size} bytes)")
        
        # Extract content
        try:
            extracted_data = extract_document(
                str(file_path),
                tesseract_cmd=settings.tesseract_cmd
            )
            
            # Process through RAG pipeline
            rag_pipeline = get_rag_pipeline(
                embedding_model=settings.embedding_model,
                index_dir=settings.faiss_index_dir
            )
            
            rag_stats = rag_pipeline.process_document(extracted_data, file_id)
            
            # Store metadata locally
            db = get_db()
            try:
                file_record = {
                    'id': file_id,
                    'filename': file.filename,
                    'file_path': str(file_path),
                    'file_size': file_size,
                    'title': title,
                    'student_name': student_name,
                    'roll_no': roll_no,
                    'subject': subject,
                    'faculty_name': faculty_name,
                    'extraction_status': 'completed',
                    'total_chunks': rag_stats['total_chunks'],
                    'metadata': extracted_data.get('metadata', {})
                }
                
                db.add_file(file_record)
                logger.info("File metadata saved locally")
            except Exception as e:
                logger.warning(f"Failed to save to local DB: {e}")
            
            logger.info(f"File processed successfully: {file_id}")
            
            return {
                'file_id': file_id,
                'filename': file.filename,
                'title': title,
                'extraction_status': 'completed',
                'stats': {
                    'total_chunks': rag_stats['total_chunks'],
                    'headings_found': len(extracted_data.get('headings', [])),
                    'sections_found': len(extracted_data.get('sections', []))
                }
            }
            
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/files")
async def list_files():
    """List all uploaded files"""
    try:
        db = get_db()
        files = db.get_files()
        return {'files': files}
    except Exception as e:
        logger.error(f"Failed to list files: {e}")
        return {'files': [], 'error': str(e)}


@router.get("/files/{file_id}")
async def get_file_info(file_id: str):
    """Get file information"""
    try:
        db = get_db()
        file_info = db.get_file(file_id)
        
        if not file_info:
            raise HTTPException(status_code=404, detail="File not found")
        
        return file_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get file info: {e}")
        raise HTTPException(status_code=500, detail=str(e))
