"""
Viva Q&A generation from report content
"""
from typing import List, Dict
import logging

from .ai_client import get_ai_client

logger = logging.getLogger(__name__)


class VivaGenerator:
    """Generate viva questions and answers from report"""
    
    def __init__(self, ai_client=None):
        """
        Initialize viva generator
        
        Args:
            ai_client: AI client instance
        """
        self.ai_client = ai_client or get_ai_client()
    
    def generate_viva_pack(
        self,
        project_title: str,
        report_sections: Dict[str, str],
        num_questions: int = 15
    ) -> List[Dict]:
        """
        Generate viva questions and answers
        
        Args:
            project_title: Project title
            report_sections: Dictionary of section_name -> content
            num_questions: Number of questions to generate
            
        Returns:
            List of Q&A dictionaries
        """
        logger.info(f"Generating {num_questions} viva questions...")
        
        # Combine key sections for context
        context_sections = ['introduction', 'methodology', 'implementation', 'results']
        context = ""
        
        for section_name, content in report_sections.items():
            if any(key in section_name.lower() for key in context_sections):
                context += f"\n\n## {section_name}\n{content[:1000]}"  # Limit context
        
        prompt = f"""Based on the capstone project titled "{project_title}" and the following report content, generate {num_questions} viva voce examination questions with model answers.

Report Content:
{context}

Generate questions covering:
- Conceptual understanding (30%)
- Implementation details (30%)
- Results and analysis (20%)
- Future scope and improvements (20%)

For each question, provide:
1. The question
2. Difficulty level (Easy/Medium/Hard)
3. A concise model answer (2-3 sentences)

Format as:
Q1. [Question]
Difficulty: [Level]
Answer: [Model answer]

Generate all {num_questions} questions now."""
        
        response = self.ai_client.generate(
            prompt=prompt,
            max_tokens=3000,
            temperature=0.8
        )
        
        # Parse response into structured Q&A
        qa_list = self._parse_qa_response(response)
        
        logger.info(f"Generated {len(qa_list)} viva questions")
        return qa_list
    
    def _parse_qa_response(self, response: str) -> List[Dict]:
        """
        Parse AI response into structured Q&A list
        
        Args:
            response: AI generated response
            
        Returns:
            List of Q&A dictionaries
        """
        qa_list = []
        lines = response.split('\n')
        
        current_qa = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for question
            if line.startswith('Q') and '.' in line:
                # Save previous Q&A if exists
                if current_qa.get('question'):
                    qa_list.append(current_qa)
                
                # Start new Q&A
                question = line.split('.', 1)[1].strip()
                current_qa = {'question': question}
            
            # Check for difficulty
            elif line.startswith('Difficulty:'):
                difficulty = line.split(':', 1)[1].strip()
                current_qa['difficulty'] = difficulty
            
            # Check for answer
            elif line.startswith('Answer:'):
                answer = line.split(':', 1)[1].strip()
                current_qa['answer'] = answer
        
        # Add last Q&A
        if current_qa.get('question'):
            qa_list.append(current_qa)
        
        return qa_list
    
    def format_viva_pack(self, qa_list: List[Dict]) -> str:
        """
        Format Q&A list for document
        
        Args:
            qa_list: List of Q&A dictionaries
            
        Returns:
            Formatted text
        """
        output = "# VIVA VOCE PREPARATION\n\n"
        output += "## Questions and Model Answers\n\n"
        
        for i, qa in enumerate(qa_list, 1):
            output += f"**Q{i}. {qa.get('question', '')}**\n\n"
            
            difficulty = qa.get('difficulty', 'Medium')
            output += f"*Difficulty: {difficulty}*\n\n"
            
            answer = qa.get('answer', '')
            output += f"**Answer:** {answer}\n\n"
            output += "---\n\n"
        
        return output


# Global generator instance
_viva_generator_instance = None


def get_viva_generator() -> VivaGenerator:
    """Get or create global viva generator instance"""
    global _viva_generator_instance
    if _viva_generator_instance is None:
        _viva_generator_instance = VivaGenerator()
    return _viva_generator_instance
