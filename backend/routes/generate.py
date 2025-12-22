"""
Report generation API routes
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
import uuid
import logging
import json
from pathlib import Path
from datetime import datetime

from config import settings
from database import get_db
from rag import get_rag_pipeline
from generators.section_generator import get_section_generator
from generators.viva_generator import get_viva_generator
from document_builder.docx_builder import build_capstone_report
from document_builder.pdf_converter import convert_to_pdf

logger = logging.getLogger(__name__)

router = APIRouter()


# Local storage helpers (Removed - managed by database.py)


class GenerateRequest(BaseModel):
    """Request model for report generation"""
    file_id: str
    title: str
    student_name: Optional[str] = None
    roll_no: Optional[str] = None
    department: Optional[str] = None
    institution: Optional[str] = None
    faculty_name: Optional[str] = None
    year: Optional[int] = None
    submission_date: Optional[str] = None
    degree: Optional[str] = "Bachelor of Technology"


@router.post("/generate")
async def generate_report(
    request: GenerateRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate capstone report from uploaded file
    
    Args:
        request: Generation request with file_id and metadata
        background_tasks: FastAPI background tasks
        
    Returns:
        Report ID and generation status
    """
    try:
        # Generate report ID
        report_id = str(uuid.uuid4())
        
        # Create report record
        report_record = {
            'id': report_id,
            'file_id': request.file_id,
            'title': request.title,
            'student_name': request.student_name,
            'roll_no': request.roll_no,
            'department': request.department,
            'institution': request.institution,
            'faculty_name': request.faculty_name,
            'year': request.year,
            'submission_date': request.submission_date,
            'degree': request.degree,
            'status': 'generating',
            'created_at': datetime.now().isoformat()
        }
        
        # Save to local database
        db = get_db()
        db.add_report(report_record)
        logger.info("Report metadata saved locally")
        
        # Start generation in background
        background_tasks.add_task(
            generate_report_task,
            report_id,
            request.file_id,
            request.dict()
        )
        
        logger.info(f"Report generation started: {report_id}")
        
        return {
            'report_id': report_id,
            'status': 'generating',
            'message': 'Report generation started. Check status endpoint for progress.'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def generate_report_task(report_id: str, file_id: str, metadata: Dict):
    """
    Background task to generate report
    
    Args:
        report_id: Report ID
        file_id: Reference file ID
        metadata: Project metadata
    """
    db = get_db()
    
    def update_status(status: str, **kwargs):
        """Helper to update status locally"""
        try:
            db.update_report_status(report_id, status, **kwargs)
        except Exception as e:
            logger.error(f"Failed to update status: {e}")
    
    try:
        # Update status
        update_status('processing')
        
        # Load RAG pipeline with document index
        rag_pipeline = get_rag_pipeline(
            embedding_model=settings.embedding_model,
            index_dir=settings.faiss_index_dir
        )
        rag_pipeline.load_document_index(file_id)
        
        # Get generators
        section_gen = get_section_generator()
        viva_gen = get_viva_generator()
        
        # Generate all sections
        logger.info(f"Generating sections for report {report_id}")
        
        sections = {}
        
        # Generate standard sections
        section_names = [
            'abstract',
            'chapter1_introduction',
            'chapter2_problem_analysis',
            'chapter3_solution_design',
            'chapter4_results_recommendations',
            'chapter5_reflection',
            'chapter6_conclusion',
            'references',
            'appendices'
        ]
        
        for section_name in section_names:
            logger.info(f"Generating {section_name}...")
            sections[section_name] = section_gen.generate_section(
                section_name,
                metadata['title'],
                metadata
            )
        
        # Generate acknowledgement
        sections['acknowledgement'] = section_gen.generate_acknowledgement(
            metadata.get('student_name'),
            metadata.get('faculty_name'),
            metadata.get('institution')
        )
        
        # Generate viva Q&A
        logger.info("Generating viva Q&A...")
        viva_qa = viva_gen.generate_viva_pack(
            metadata['title'],
            sections,
            num_questions=15
        )
        sections['viva_qa'] = viva_gen.format_viva_pack(viva_qa)
        
        # Build DOCX
        logger.info("Building DOCX document...")
        output_dir = Path(settings.generated_dir) / report_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        docx_path = output_dir / f"{report_id}.docx"
        
        build_capstone_report(
            project_title=metadata['title'],
            sections=sections,
            metadata=metadata,
            output_path=str(docx_path)
        )
        
        # Convert to PDF
        logger.info("Converting to PDF...")
        try:
            pdf_path = convert_to_pdf(str(docx_path), str(output_dir))
        except Exception as e:
            logger.error(f"PDF conversion failed: {e}")
            pdf_path = None
        
        # Update report record
        update_status(
            'completed',
            docx_path=str(docx_path),
            pdf_path=pdf_path,
            completed_at=datetime.now().isoformat()
        )
        
        logger.info(f"Report generation completed: {report_id}")
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        
        # Update status to failed
        update_status('failed', error_message=str(e))


@router.get("/reports")
async def list_reports():
    """List all generated reports"""
    try:
        db = get_db()
        reports = db.get_reports()
        # Sort by creation time desc (simple string sort works for isoformat)
        reports.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return {'reports': reports}
    except Exception as e:
        logger.error(f"Failed to list reports: {e}")
        return {'reports': [], 'error': str(e)}


@router.get("/reports/{report_id}")
async def get_report_info(report_id: str):
    """Get report information"""
    try:
        db = get_db()
        report = db.get_report(report_id)
        if report:
            return report
        
        raise HTTPException(status_code=404, detail="Report not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get report info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Deterministic Generation ---

from generators.structure_extractor import get_structure_extractor
from generators.deterministic_generator import get_deterministic_generator

class DeterministicGenerateRequest(BaseModel):
    """Request model for deterministic report generation"""
    file_id: str
    inputs: Dict[str, Any]  # Project specific inputs (domain, tech stack, etc.)


@router.post("/generate/deterministic")
async def generate_deterministic_report(
    request: DeterministicGenerateRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate a report strictly mirroring the reference file structure
    """
    try:
        # Generate report ID
        report_id = str(uuid.uuid4())
        
        # Create report record
        report_record = {
            'id': report_id,
            'file_id': request.file_id,
            'title': request.inputs.get('title', 'Untitled Report'),
            'status': 'generating',
            'type': 'deterministic',
            'created_at': datetime.now().isoformat()
        }
        
        # Save metadata (Supabase or Local)
        # Save metadata locally
        db = get_db()
        db.add_report(report_record)
            
        # Start background task
        background_tasks.add_task(
            run_deterministic_generation,
            report_id,
            request.file_id,
            request.inputs
        )
        
        return {
            'report_id': report_id,
            'status': 'generating',
            'message': 'Deterministic report generation started.'
        }
        
    except Exception as e:
        logger.error(f"Failed to start deterministic generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def run_deterministic_generation(report_id: str, file_id: str, inputs: Dict):
    """Background task for deterministic generation"""
    
    def update_status(status: str, **kwargs):
        db = get_db()
        db.update_report_status(report_id, status, **kwargs)

    try:
        update_status('processing_structure')
        
        # 1. Get file path
        # Assuming file_id maps to a path in uploads (need a way to resolve this)
        # For now, assuming file_id IS the filename or we search for it
        upload_dir = Path(settings.upload_dir)
        # Simple search for file with this ID (assuming ID is part of filename or we have a mapping)
        # In a real app, we'd look up the path. 
        # Let's assume file_id is the filename for now or we find it.
        file_path = None
        for f in upload_dir.glob(f"*{file_id}*"):
            file_path = f
            break
            
        if not file_path:
            # Fallback: maybe file_id is just the name
            if (upload_dir / file_id).exists():
                file_path = upload_dir / file_id
        
        if not file_path:
            raise FileNotFoundError(f"File not found for ID: {file_id}")
            
        # 2. Extract Structure
        logger.info(f"Extracting structure from {file_path}")
        structure_extractor = get_structure_extractor()
        structure = structure_extractor.extract_structure(str(file_path))
        
        update_status('generating_content')
        
        # 3. Generate Report
        logger.info("Generating deterministic content...")
        det_generator = get_deterministic_generator()
        
        # Add file_id to inputs for the prompt
        inputs['file_id'] = file_id
        
        report_json = det_generator.generate_report(structure, inputs)
        
        # 4. Save JSON output
        output_dir = Path(settings.generated_dir) / report_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        json_path = output_dir / "report.json"
        with open(json_path, 'w') as f:
            json.dump(report_json, f, indent=2)
            
        # 5. Build DOCX (Optional/TODO: Need a builder that takes this JSON structure)
        # For now, we just save the JSON as the result
        
        update_status(
            'completed',
            json_path=str(json_path),
            completed_at=datetime.now().isoformat()
        )
        logger.info(f"Deterministic generation completed: {report_id}")
        
    except Exception as e:
        logger.error(f"Deterministic generation failed: {e}")
        update_status('failed', error_message=str(e))

