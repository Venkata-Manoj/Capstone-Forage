"""
Deterministic Generator - Generates reports mirroring a reference structure exactly
"""
import logging
import json
from typing import Dict, Any

from .ai_client import get_ai_client

logger = logging.getLogger(__name__)


class DeterministicGenerator:
    """Generates reports strictly following a reference structure"""
    
    def __init__(self, ai_client=None):
        self.ai_client = ai_client or get_ai_client()
        
    def generate_report(self, reference_structure: Dict, inputs: Dict) -> Dict:
        """
        Generate a full report based on structure and inputs
        
        Args:
            reference_structure: The JSON structure extracted from reference file
            inputs: User inputs (domain, problem, tech stack, etc.)
            
        Returns:
            JSON object with the generated report content
        """
        
        # Construct the prompt using the EXACT template provided
        system_prompt = """You are a deterministic Capstone Report Generator. Your job is to generate a report that **exactly mirrors the structure of the provided reference document**.

You must strictly follow the reference’s:
* Section titles
* Headings
* Sub-headings
* Minute key points
* Order and hierarchy
* Formatting logic

No creativity in structure. No generic templates. No reordering. No renaming.
Your output must be a **structural clone** of the reference file.

You ALWAYS output **exactly one JSON object**, matching the schema in the User Prompt.

---

## **HARD RULES**

### **1. Adopt the exact structure of the reference file**
* **You must adopt the structure of the reference file exactly, and generate a complete mirror of it using the titles/headings/key points exactly as they appear, populated with the user’s project-specific data.**

### **2. Exact Structure Enforcement**
* Use the same section titles, headings, sub-headings, and key points from `reference_structure`.
* Case-sensitive, character-sensitive.
* Do NOT modify, delete, rename, merge, or add any structural element.

### **3. Content Rules**
* For each key point in the reference, generate detailed project-specific content using the user’s inputs.
* If information is missing, explicitly state that information is missing while **preserving the structure**.
* Write clear technical paragraphs following the order of the key points.

### **4. Output Format (JSON Only)**
The output **must** follow the schema in the User Prompt.
No text outside JSON.
No markdown.
No explanations.

If ANY mismatch occurs → return the fallback JSON.

### **5. Determinism**
* Temperature = 0
* Zero hallucinations
* No improvisation

### **6. Tone**
* Professional
* Academic
* Specific to the project
* No generic capstone templates
"""

        user_prompt_template = """
You are given:

### **1. `reference_structure`**
{reference_structure_json}

### **2. `inputs`**
{inputs_json}

---

# **Your Task**

Using ONLY `reference_structure` + `inputs`:

⚠️ **Generate a complete, full capstone report that mirrors the reference document exactly.**
⚠️ **Adopt the reference structure 1:1 and populate it with the user’s content.**
⚠️ **Never alter any title, heading, sub-heading, or key point.**

Output a **single JSON object** following this schema:

```json
{{
  "reportTitle": "string",
  "mirrorsReference": true,
  "sections": [
    {{
      "title": "string (exactly from reference_structure)",
      "subsections": [
        {{
          "heading": "string (exact match)",
          "keyPoints": ["string", "... (exact order from reference_structure)"],
          "content": "string (detailed explanation expanding each key point using user inputs)"
        }}
      ],
      "sectionNotes": "string (optional)"
    }}
  ],
  "metadata": {{
    "sourceReferenceId": "{source_ref_id}",
    "generationTimestamp": "{timestamp}"
  }}
}}
```

---

# **Fallback Condition**

If **any** mismatch with the reference structure occurs (titles/headings/order/keyPoints):

Return exactly:

```json
{{
  "reportTitle": "",
  "mirrorsReference": false,
  "sections": [],
  "metadata": {{ "sourceReferenceId": "", "generationTimestamp": "" }}
}}
```
"""
        
        # Prepare data for prompt
        import datetime
        timestamp = datetime.datetime.now().isoformat()
        source_ref_id = inputs.get('file_id', 'unknown')
        
        user_prompt = user_prompt_template.format(
            reference_structure_json=json.dumps(reference_structure, indent=2),
            inputs_json=json.dumps(inputs, indent=2),
            source_ref_id=source_ref_id,
            timestamp=timestamp
        )
        
        logger.info("Sending deterministic generation request to AI...")
        
        try:
            # Use a large context window if possible, or standard
            # We need a large max_tokens because the full report is being generated in one go
            # Gemini 1.5 Flash/Pro is ideal here.
            response_text = self.ai_client.generate(
                prompt=user_prompt,
                system_message=system_prompt,
                max_tokens=8192, # Max out output tokens
                temperature=0.0,
                json_mode=True
            )
            
            # Clean up response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
                
            report_data = json.loads(response_text)
            
            # Basic validation
            if not report_data.get('mirrorsReference', False):
                logger.warning("AI returned fallback JSON or indicated mismatch.")
                
            return report_data
            
        except json.JSONDecodeError:
            logger.error("Failed to parse generated report as JSON")
            raise ValueError("AI failed to generate valid JSON report")
        except Exception as e:
            logger.error(f"Deterministic generation failed: {e}")
            raise


# Global instance
_deterministic_generator = None

def get_deterministic_generator() -> DeterministicGenerator:
    global _deterministic_generator
    if _deterministic_generator is None:
        _deterministic_generator = DeterministicGenerator()
    return _deterministic_generator
