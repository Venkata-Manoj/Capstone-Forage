"""
Section-wise report generation using AI and RAG
"""
from typing import Dict, Optional
import logging

from .ai_client import get_ai_client
from rag import get_rag_pipeline

logger = logging.getLogger(__name__)


class SectionGenerator:
    """Generate individual report sections using AI"""
    
    # Section templates and prompts
    SECTION_PROMPTS = {
        'abstract': """Write a concise Abstract (150-300 words) for a capstone project titled "{title}".

The abstract should:
●	Provide a concise summary (150-300 words) of the capstone project. Mention the primary problem, the purpose of the project, and key outcomes or solutions.

Use the reference context to ensure accuracy.""",
        
        'chapter1_introduction': """Write Chapter 1: Introduction for a capstone project titled "{title}".

This chapter must include the following subsections (use ## for subsection headings):

## Background Information
Present the background of the problem or opportunity you are addressing.

## Project Objectives
State the purpose and key goals of your capstone project.

## Significance
Discuss why the project is important and how it contributes to your field or society.

## Scope
Define the boundaries of the project, including what is and is not included.

## Methodology Overview
Briefly outline the approach you will follow in addressing the problem.

Use the reference context to create detailed, well-structured content. Target approximately 500 words for this chapter.""",
        
        'chapter2_problem_analysis': """Write Chapter 2: Problem Identification and Analysis for "{title}".

This chapter must include the following subsections (use ## for subsection headings):

## Description of the Problem
Detail the main issue or challenge you are addressing.

## Evidence of the Problem
Present any data, research, or case examples that demonstrate the existence of the problem.

## Stakeholders
Identify the key groups or individuals affected by the problem.

## Supporting Data/Research
Provide evidence or references that support your analysis.

Use the reference context to create detailed, well-structured content. Target approximately 500 words for this chapter.""",
        
        'chapter3_solution_design': """Write Chapter 3: Solution Design and Implementation for "{title}".

This chapter must include the following subsections (use ## for subsection headings):

## Development and Design Process
Outline the process followed for developing the solution or system.

## Tools and Technologies Used
List the key tools, software, and technologies utilized in the project.

## Solution Overview
Provide a detailed description of the solution or project design.

## Engineering Standards Applied
List any relevant engineering standards (ISO, IEEE, etc.) and explain how they are applied to your project.

## Solution Justification
Discuss how the inclusion of standards impacts the project's design and success.

Use the reference context to create detailed, well-structured content. Target approximately 600 words for this chapter.""",
        
        'chapter4_results_recommendations': """Write Chapter 4: Results and Recommendations for "{title}".

This chapter must include the following subsections (use ## for subsection headings):

## Evaluation of Results
Analyze the effectiveness of your solution (outcome/Output parameters) in addressing the problem.

## Challenges Encountered
Highlight any difficulties faced during the implementation process and how they were overcome.

## Possible Improvements
Discuss any limitations or potential improvements to the solution.

## Recommendations
Offer recommendations for further research, development, or deployment of the solution.

Use the reference context to create detailed, well-structured content. Target approximately 500 words for this chapter.""",
        
        'chapter5_reflection': """Write Chapter 5: Reflection on Learning and Personal Development for "{title}".

In this chapter, reflect on the learning journey throughout the capstone project. The purpose is to provide an opportunity to assess growth, both academically and professionally, during the course of the project.

This chapter must include the following subsections (use ## for subsection headings):

## Key Learning Outcomes

### Academic Knowledge
Reflect on the key concepts, theories, and methodologies from your field of study that were applied or gained throughout the project. How did this project deepen your understanding of your chosen discipline?

### Technical Skills
Discuss any technical skills you developed during the project. This could include software tools, programming languages, engineering techniques, or industry-specific practices you learned to apply.

### Problem-Solving and Critical Thinking
Describe how your problem-solving skills evolved. What complex issues did you encounter, and how did you tackle them using the skills you acquired during your academic training?

## Challenges Encountered and Overcome

### Personal and Professional Growth
Describe the major challenges you faced during the project. How did these challenges help you grow personally and professionally? Reflect on any moments of doubt or frustration, and how you navigated through them.

### Collaboration and Communication
Discuss your experience working with teammates, stakeholders, or supervisors. What did you learn about teamwork, communication, and leadership? Were there any challenges in coordination or idea-sharing, and how did you resolve them? (if applicable)

## Application of Engineering Standards
Reflect on how the application of engineering standards and best practices shaped the project outcome. What engineering principles and industry standards did you follow, and how did they contribute to the success of your solution?

## Insights into the Industry
Share your thoughts on how this project has provided you with a better understanding of real-world industry practices. What did you learn about the professional environment, and how will this influence your career path or future endeavors?

## Conclusion of Personal Development
Summarize how the capstone project has contributed to your overall personal development. How has the experience helped you in shaping your career goals, enhancing your skill set, and preparing you for future professional opportunities?

Use the reference context to create thoughtful, reflective content. Target approximately 600 words for this chapter.""",
        
        'chapter6_conclusion': """Write Chapter 6: Conclusion for "{title}".

This chapter should:
●	Summarize the key findings, emphasizing the problem, the solution, and its impact.
●	Reiterate the value and significance of the project.

Use the reference context. Target approximately 300 words for this chapter.""",
        
        'references': """Generate a References section for "{title}".

●	Cite all sources used in the report (articles, textbooks, websites, etc.), following the required citation style (APA).

Based on the reference context, create a list of properly formatted APA citations for sources that would be relevant to this project.""",
        
        'appendices': """Generate an Appendices section for "{title}".

●	Include any additional material like code snippets, user manuals, diagrams, or raw data.

Based on the reference context, suggest and describe relevant appendices that would support this capstone project report."""
    }
    
    def __init__(self, rag_pipeline=None, ai_client=None):
        """
        Initialize section generator
        
        Args:
            rag_pipeline: RAG pipeline instance
            ai_client: AI client instance
        """
        self.rag_pipeline = rag_pipeline or get_rag_pipeline()
        self.ai_client = ai_client or get_ai_client()
    
    def generate_section(
        self,
        section_name: str,
        project_title: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Generate a specific report section
        
        Args:
            section_name: Name of section to generate
            project_title: Project title
            metadata: Additional metadata (student name, etc.)
            
        Returns:
            Generated section content
        """
        section_key = section_name.lower().replace(' ', '_')
        
        if section_key not in self.SECTION_PROMPTS:
            logger.warning(f"No template for section: {section_name}")
            return self._generate_generic_section(section_name, project_title)
        
        # Retrieve relevant context
        context = self.rag_pipeline.retrieve_for_section(
            section_name,
            project_title,
            top_k=5
        )
        
        # Get prompt template
        prompt_template = self.SECTION_PROMPTS[section_key]
        prompt = prompt_template.format(title=project_title)
        
        # Generate content
        logger.info(f"Generating {section_name} section...")
        content = self.ai_client.generate_with_context(
            prompt=prompt,
            context=context,
            max_tokens=2000,
            temperature=0.7
        )
        
        logger.info(f"Generated {section_name} ({len(content)} characters)")
        return content
    
    def _generate_generic_section(
        self,
        section_name: str,
        project_title: str
    ) -> str:
        """Generate a generic section without specific template"""
        context = self.rag_pipeline.retrieve_context(
            f"{project_title} {section_name}",
            top_k=5
        )
        
        prompt = f"""Write a comprehensive {section_name} section for the capstone project titled "{project_title}".
        
Use the reference context to create detailed, well-structured content appropriate for an academic capstone report."""
        
        return self.ai_client.generate_with_context(
            prompt=prompt,
            context=context,
            max_tokens=1500
        )
    
    def generate_acknowledgement(
        self,
        student_name: Optional[str] = None,
        faculty_name: Optional[str] = None,
        institution: Optional[str] = None
    ) -> str:
        """Generate acknowledgement section with editable placeholders"""
        return f"""●	Mention individuals, mentors, or organizations who contributed to your project.

[Edit this section to acknowledge those who helped you:]

I would like to express my sincere gratitude to [Supervisor/Advisor Name: {faculty_name or '_______________'}] for their invaluable guidance and support throughout this capstone project.

I am thankful to [Institution Name: {institution or '_______________'}] for providing the necessary resources and facilities.

I would also like to thank [Mention other individuals/organizations: _______________] for their contributions.

Finally, I express my heartfelt thanks to my family and friends for their constant encouragement.


{student_name or '[Student Name]'}"""
    
    def generate_declaration(
        self,
        student_name: Optional[str] = None,
        roll_no: Optional[str] = None
    ) -> str:
        """Generate declaration section"""
        return f"""DECLARATION

I, {student_name or '[Student Name]'} (Roll No: {roll_no or '[Roll Number]'}), hereby declare that the capstone project work presented in this report is my own original work and has been carried out under the guidance of my faculty advisor.

The work has not been submitted elsewhere for any degree or diploma. All sources of information have been duly acknowledged.


Date: _______________                                    Signature: _______________
Place: _______________                                   {student_name or '[Student Name]'}"""


# Global generator instance
_generator_instance = None


def get_section_generator() -> SectionGenerator:
    """Get or create global section generator instance"""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = SectionGenerator()
    return _generator_instance
