"""
Structure Extractor - Extracts exact structure from reference documents
"""
import logging
import json
from typing import Dict, Optional

from .ai_client import get_ai_client
from extractors import extract_document

logger = logging.getLogger(__name__)


class StructureExtractor:
    """Extracts structural hierarchy from documents"""
    
    def __init__(self, ai_client=None):
        self.ai_client = ai_client or get_ai_client()
        
    def extract_structure(self, file_path: str) -> Dict:
        """
        Extract structure from a file
        
        Args:
            file_path: Path to the reference file
            
        Returns:
            JSON object containing the structure
        """
        # 1. Extract raw text
        try:
            doc_content = extract_document(file_path)
            # Combine text parts if it's a complex extraction, or just use 'text'
            raw_text = doc_content.get('text', '')
            
            # If text is too long, we might need to truncate or chunk
            # For structure extraction, the Table of Contents or first few pages are usually most critical
            # But for "minute key points", we need the whole thing.
            # Let's assume we can pass a significant chunk. 
            # If it's huge, we might need a map-reduce strategy, but for now let's try direct.
            # Truncate to ~50k chars to be safe with context windows if needed, 
            # but Gemini 1.5 Pro (if used) has huge context.
            # Let's use a reasonable limit for safety.
            if len(raw_text) > 100000:
                logger.warning("Document too large, truncating for structure extraction")
                raw_text = raw_text[:100000]
                
        except Exception as e:
            logger.error(f"Failed to extract document content: {e}")
            raise ValueError(f"Could not read file: {e}")

        # 2. Extract structure using LLM
        prompt = """You are a Structure Extractor. Your task is to analyze the provided document text and extract its exact structure into a JSON format.

You must identify:
1. Section Titles (e.g., "1. Introduction")
2. Headings (e.g., "1.1 Background")
3. Sub-headings (e.g., "1.1.1 Context")
4. Key Points: For each lowest-level section, extract the key points covered as a list of strings. Be specific but concise.

Output strictly valid JSON matching this schema:
{
  "sections": [
    {
      "title": "Section Title",
      "subsections": [
        {
          "heading": "Subsection Heading",
          "keyPoints": [
            "Key point 1",
            "Key point 2"
          ]
        }
      ]
    }
  ]
}

If a section has no subsections, use the section title as the heading for a single subsection.
Do not include content, only the structure and key points.
"""

        try:
            response_text = self.ai_client.generate(
                prompt=prompt,
                system_message="You are a JSON-only output machine.",
                max_tokens=4000,
                temperature=0.0,  # Deterministic
                json_mode=True
            )
            
            # Clean up response if it contains markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
                
            structure = json.loads(response_text)
            return structure
            
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response as JSON")
            logger.debug(f"Raw response: {response_text}")
            raise ValueError("Failed to extract valid structure from document")
        except Exception as e:
            logger.error(f"Structure extraction failed: {e}")
            raise

# Global instance
_structure_extractor = None

def get_structure_extractor() -> StructureExtractor:
    global _structure_extractor
    if _structure_extractor is None:
        _structure_extractor = StructureExtractor()
    return _structure_extractor
