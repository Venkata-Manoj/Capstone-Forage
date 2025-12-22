"""
Test Ollama Connection and Fallback Logic
"""
import sys
import logging
from config import settings

# Force a fake model as primary to test fallback
print("Testing Fallback Logic...")
print(f"Original Primary Model: {settings.ollama_model}")
settings.ollama_model = "llama3.2" 
print(f"Set Primary Model to: {settings.ollama_model} (to force failure)")

from generators.ai_client import get_ai_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ollama():
    try:
        print("Initializing AI Client (Ollama)...")
        client = get_ai_client()
        
        print(f"Client Models Chain: {client.models}")
        
        prompt = "Explain quantum computing in one sentence."
        print(f"\nSending prompt: '{prompt}'")
        
        response = client.generate(prompt)
        
        print("\n--- Response ---")
        print(response)
        print("----------------")
        print("\nSUCCESS: Ollama seems to be working (Fallback successful if primary was invalid).")
        
    except Exception as e:
        print(f"\nERROR: Failed to use Ollama. Details: {e}")
        print("\nTroubleshooting:")
        print("1. Is Ollama running? (Try 'ollama serve' in a terminal)")
        print("2. Do you have ANY of the models pulled?")
        sys.exit(1)

if __name__ == "__main__":
    test_ollama()
