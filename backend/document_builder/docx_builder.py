"""
DOCX document builder for capstone reports
"""
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from typing import Dict, List, Optional
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DOCXBuilder:
    """Build capstone report DOCX documents"""
    
    def __init__(self):
        """Initialize DOCX builder"""
        self.doc = None
    
    def create_report(
        self,
        project_title: str,
        sections: Dict[str, str],
        metadata: Optional[Dict] = None,
        output_path: str = None
    ) -> str:
        """
        Create complete capstone report
        
        Args:
            project_title: Project title
            sections: Dictionary of section_name -> content
            metadata: Student/project metadata
            output_path: Path to save DOCX
            
        Returns:
            Path to created DOCX file
        """
        logger.info(f"Creating capstone report: {project_title}")
        
        # Create new document
        self.doc = Document()
        
        # Set up styles
        self._setup_styles()
        
        # Add page numbering (bottom right, 12pt) - will be added after title page
        self._add_page_numbers()
        
        # Build document sections
        self._add_cover_page(project_title, metadata)
        self.doc.add_page_break()
        
        self._add_declaration(metadata)
        self.doc.add_page_break()
        
        self._add_bonafide_certificate(project_title, metadata)
        self.doc.add_page_break()
        
        if sections.get('acknowledgement'):
            self._add_section("ACKNOWLEDGEMENT", sections['acknowledgement'])
            self.doc.add_page_break()
        
        if sections.get('abstract'):
            self._add_section("ABSTRACT", sections['abstract'])
            self.doc.add_page_break()
        
        # Table of contents placeholder
        self._add_toc_placeholder()
        self.doc.add_page_break()
        
        # Main content sections
        section_order = [
            ('Introduction', 'chapter1_introduction'),
            ('Problem Identification and Analysis', 'chapter2_problem_analysis'),
            ('Solution Design and Implementation', 'chapter3_solution_design'),
            ('Results and Recommendations', 'chapter4_results_recommendations'),
            ('Reflection on Learning and Personal Development', 'chapter5_reflection'),
            ('Conclusion', 'chapter6_conclusion')
        ]
        
        chapter_num = 1
        for display_name, key in section_order:
            if sections.get(key):
                self._add_chapter(chapter_num, display_name, sections[key])
                chapter_num += 1
        
        # References
        if sections.get('references'):
            self.doc.add_page_break()
            self._add_section("REFERENCES", sections['references'])
        
        # Appendices
        if sections.get('appendices'):
            self.doc.add_page_break()
            self._add_section("APPENDICES", sections['appendices'])
        
        # Save document
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"capstone_report_{timestamp}.docx"
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        self.doc.save(output_path)
        
        logger.info(f"Report saved to: {output_path}")
        return output_path
    
    def _setup_styles(self):
        """Set up document styles with formatting rules"""
        # Set document margins (1 inch = 914400 EMUs)
        sections = self.doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)
        
        styles = self.doc.styles
        
        # Normal style (Body Text)
        normal = styles['Normal']
        normal.font.name = 'Times New Roman'
        normal.font.size = Pt(12)
        normal_paragraph = normal.paragraph_format
        normal_paragraph.line_spacing = 1.5  # 1.5 line spacing
        normal_paragraph.first_line_indent = Inches(0.5)  # 0.5 inch first line indent
        normal_paragraph.space_after = Pt(12)  # Blank line between paragraphs
        normal_paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        
        # Heading 1 style (Chapter headings)
        heading1 = styles['Heading 1']
        heading1.font.name = 'Times New Roman'
        heading1.font.size = Pt(14)
        heading1.font.bold = True
        heading1.font.color.rgb = RGBColor(0, 0, 0)
        heading1_paragraph = heading1.paragraph_format
        heading1_paragraph.space_before = Pt(12)
        heading1_paragraph.space_after = Pt(6)
        heading1_paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        
        # Heading 2 style (Main subheadings)
        heading2 = styles['Heading 2']
        heading2.font.name = 'Times New Roman'
        heading2.font.size = Pt(12)
        heading2.font.bold = True
        heading2.font.color.rgb = RGBColor(0, 0, 0)
        heading2_paragraph = heading2.paragraph_format
        heading2_paragraph.space_before = Pt(12)
        heading2_paragraph.space_after = Pt(6)
        heading2_paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        
        # Heading 3 style (Nested subheadings)
        heading3 = styles['Heading 3']
        heading3.font.name = 'Times New Roman'
        heading3.font.size = Pt(12)
        heading3.font.bold = True
        heading3.font.color.rgb = RGBColor(0, 0, 0)
        heading3_paragraph = heading3.paragraph_format
        heading3_paragraph.space_before = Pt(6)
        heading3_paragraph.space_after = Pt(6)
        heading3_paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    def _add_page_numbers(self):
        """Add page numbers to footer (bottom right, 12pt)"""
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        
        for section in self.doc.sections:
            footer = section.footer
            paragraph = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
            paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            
            # Add page number field
            run = paragraph.add_run()
            run.font.name = 'Times New Roman'
            run.font.size = Pt(12)
            
            # Create page number field
            fldChar1 = OxmlElement('w:fldChar')
            fldChar1.set(qn('w:fldCharType'), 'begin')
            
            instrText = OxmlElement('w:instrText')
            instrText.set(qn('xml:space'), 'preserve')
            instrText.text = "PAGE"
            
            fldChar2 = OxmlElement('w:fldChar')
            fldChar2.set(qn('w:fldCharType'), 'end')
            
            run._r.append(fldChar1)
            run._r.append(instrText)
            run._r.append(fldChar2)
    
    def _add_cover_page(self, title: str, metadata: Dict):
        """Add cover page with proper formatting"""
        # Institution name
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 2.0  # Double spacing
        run = p.add_run(metadata.get('institution', '[INSTITUTION NAME]'))
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.font.bold = True
        
        self.doc.add_paragraph()
        self.doc.add_paragraph()
        
        # Project title (16pt, bold, centered, double-spaced)
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 2.0  # Double spacing
        run = p.add_run(title.upper())
        run.font.name = 'Times New Roman'
        run.font.size = Pt(16)
        run.font.bold = True
        
        self.doc.add_paragraph()
        self.doc.add_paragraph()
        
        # Subtitle
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 2.0
        run = p.add_run("A Capstone Project Report")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        
        self.doc.add_paragraph()
        self.doc.add_paragraph()
        
        # Student details
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 2.0
        run = p.add_run("Submitted by:")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.font.bold = True
        
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 2.0
        run = p.add_run(metadata.get('student_name', '[Student Name]'))
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 2.0
        run = p.add_run(f"Roll No: {metadata.get('roll_no', '[Roll Number]')}")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        self.doc.add_paragraph()
        self.doc.add_paragraph()
        
        # Department and year
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 2.0
        run = p.add_run(metadata.get('department', '[Department Name]'))
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 2.0
        
        # Use year from submission date if available, else use provided year or current year
        year = metadata.get('year')
        if not year and metadata.get('submission_date'):
            try:
                # Parse YYYY-MM-DD
                dt = datetime.strptime(metadata.get('submission_date'), "%Y-%m-%d")
                year = dt.year
            except:
                year = datetime.now().year
        
        if not year:
            year = datetime.now().year
            
        run = p.add_run(str(year))
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
    
    def _add_declaration(self, metadata: Dict):
        """Add declaration page"""
        self.doc.add_heading('DECLARATION', 0)
        
        # Format date
        date_str = "_______________"
        if metadata.get('submission_date'):
            try:
                dt = datetime.strptime(metadata.get('submission_date'), "%Y-%m-%d")
                date_str = dt.strftime("%d-%m-%Y")
            except:
                pass

        text = f"""I, {metadata.get('student_name', '[Student Name]')} (Roll No: {metadata.get('roll_no', '[Roll Number]')}), hereby declare that the capstone project work presented in this report is my own original work and has been carried out under the guidance of my faculty advisor.

The work has not been submitted elsewhere for any degree or diploma. All sources of information have been duly acknowledged.


Date: {date_str}                                    Signature: _______________
Place: _______________                                   {metadata.get('student_name', '[Student Name]')}"""
        
        self.doc.add_paragraph(text)
    
    def _add_bonafide_certificate(self, title: str, metadata: Dict):
        """Add bonafide certificate"""
        self.doc.add_heading('BONAFIDE CERTIFICATE', 0)
        
        # Format date
        date_str = "_______________"
        if metadata.get('submission_date'):
            try:
                dt = datetime.strptime(metadata.get('submission_date'), "%Y-%m-%d")
                date_str = dt.strftime("%d-%m-%Y")
            except:
                pass

        text = f"""This is to certify that the capstone project report titled "{title}" submitted by {metadata.get('student_name', '[Student Name]')} (Roll No: {metadata.get('roll_no', '[Roll Number]')}) in partial fulfillment of the requirements for the award of the degree of {metadata.get('degree', '[Degree Name]')} is a bonafide record of work carried out by them under my supervision and guidance.


Faculty Guide: _______________                          Head of Department: _______________
{metadata.get('faculty_name', '[Faculty Name]')}       {metadata.get('hod_name', '[HOD Name]')}

Date: {date_str}
Place: _______________"""
        
        self.doc.add_paragraph(text)
    
    def _add_toc_placeholder(self):
        """Add table of contents placeholder"""
        self.doc.add_heading('TABLE OF CONTENTS', 0)
        p = self.doc.add_paragraph()
        p.add_run('[Table of Contents will be generated when opened in Microsoft Word. ')
        p.add_run('Right-click and select "Update Field" to generate.]')
        p.italic = True
    
    def _add_section(self, title: str, content: str):
        """Add a section with title and content"""
        self.doc.add_heading(title, 0)
        
        # Split content into paragraphs
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                self.doc.add_paragraph(para.strip())
    
    def _add_chapter(self, chapter_num: int, title: str, content: str):
        """Add a numbered chapter"""
        self.doc.add_heading(f'CHAPTER {chapter_num}', 0)
        self.doc.add_heading(title.upper(), 1)
        
        # Split content into paragraphs
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # Check if it's a sub-sub-heading (starts with ###)
            if para.startswith('###'):
                heading_text = para.replace('###', '').strip()
                self.doc.add_heading(heading_text, 3)
            # Check if it's a sub-heading (starts with ##)
            elif para.startswith('##'):
                heading_text = para.replace('##', '').strip()
                self.doc.add_heading(heading_text, 2)
            else:
                self.doc.add_paragraph(para)


def build_capstone_report(
    project_title: str,
    sections: Dict[str, str],
    metadata: Dict,
    output_path: str
) -> str:
    """
    Convenience function to build capstone report
    
    Args:
        project_title: Project title
        sections: Dictionary of sections
        metadata: Project metadata
        output_path: Output file path
        
    Returns:
        Path to created DOCX
    """
    builder = DOCXBuilder()
    return builder.create_report(project_title, sections, metadata, output_path)
