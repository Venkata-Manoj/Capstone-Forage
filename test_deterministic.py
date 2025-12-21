"""
Test script for deterministic generation
"""
import sys
import os
import asyncio
import json
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from generators.structure_extractor import get_structure_extractor
from generators.deterministic_generator import get_deterministic_generator

async def test_deterministic_flow():
    print("1. Creating dummy reference file...")
    # Create a dummy text file to act as reference
    ref_content = """
    1. Introduction
    1.1 Background
    The background of this project is...
    1.2 Problem Statement
    The problem is...
    
    2. Methodology
    2.1 Proposed System
    We propose...
    """
    
    ref_path = Path("test_reference.txt")
    with open(ref_path, "w") as f:
        f.write(ref_content)
        
    print("2. Testing Structure Extraction...")
    extractor = get_structure_extractor()
    try:
        structure = extractor.extract_structure(str(ref_path))
        print("Structure Extracted:")
        print(json.dumps(structure, indent=2))
    except Exception as e:
        print(f"Extraction failed: {e}")
        return

    print("\n3. Testing Deterministic Generation...")
    generator = get_deterministic_generator()
    
    inputs = {
        "title": "AI Powered Farming",
        "domain": "Agriculture",
        "problem": "Farmers lack real-time advice",
        "solution": "A web app with AI chatbot",
        "tech_stack": "React, Python, Gemini"
    }
    
    try:
        report = generator.generate_report(structure, inputs)
        print("\nReport Generated:")
        print(json.dumps(report, indent=2))
        
        if report.get("mirrorsReference"):
            print("\nSUCCESS: Report mirrors reference!")
        else:
            print("\nFAILURE: Report does not mirror reference.")
            
    except Exception as e:
        print(f"Generation failed: {e}")
    
    # Cleanup
    if ref_path.exists():
        os.remove(ref_path)

if __name__ == "__main__":
    asyncio.run(test_deterministic_flow())
