"""
Ollama AI Client
Supports local LLM generation via Ollama with Fallback Support
"""
import logging
from typing import List, Optional
from ollama import Client, ResponseError
from config import settings

logger = logging.getLogger(__name__)


class AIClient:
    """Ollama AI Client with Fallback Support"""
    
    def __init__(self):
        """Initialize Ollama client"""
        self.provider = "ollama"
        self.base_url = settings.ollama_base_url
        
        # Build model list: Primary -> Fallback 1 -> Fallback 2
        self.models = [settings.ollama_model]
        if settings.ollama_model_fallback_1:
            self.models.append(settings.ollama_model_fallback_1)
        if settings.ollama_model_fallback_2:
            self.models.append(settings.ollama_model_fallback_2)
            
        logger.info(f"Ollama initialized. Models chain: {self.models}")
        
        try:
            self.client = Client(host=self.base_url)
        except Exception as e:
            logger.error(f"Failed to initialize Ollama client: {e}")
            raise
        
    def generate(
        self,
        prompt: str,
        max_tokens: int = None,
        temperature: float = None,
        system_message: str = None,
        json_mode: bool = False
    ) -> str:
        """
        Generate text using Ollama with automatic fallback
        """
        temperature = temperature or settings.temperature
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        options = {"temperature": temperature}
        if max_tokens:
            options["num_predict"] = max_tokens

        last_error = None
        
        # Try each model in the chain
        for model in self.models:
            try:
                logger.info(f"Attempting generation with model: {model} (JSON mode: {json_mode})")
                
                kwargs = {
                    'model': model,
                    'messages': messages,
                    'options': options
                }
                if json_mode:
                    kwargs['format'] = 'json'
                
                response = self.client.chat(**kwargs)
                
                content = response.get('message', {}).get('content', '')
                if content:
                    return content
                else:
                    raise ValueError("Empty response from Ollama")
                    
            except ResponseError as e:
                logger.warning(f"Ollama Error ({model}): {e.error}")
                last_error = e
                # If model not found, try next one
                if "not found" in str(e).lower():
                    continue
                # For other errors, maybe we should still try fallback? Let's assume yes.
                continue
                
            except Exception as e:
                logger.warning(f"Error ({model}): {e}")
                last_error = e
                continue
                
        # If we get here, all models updated
        logger.error("All AI models failed.")
        raise RuntimeError(f"All AI models failed. Last error: {last_error}")

    def generate_with_context(
        self,
        prompt: str,
        context: str,
        max_tokens: int = None,
        temperature: float = None
    ) -> str:
        """Generate text with retrieved context"""
        system_message = (
            "You are an expert academic writer helping to generate capstone project reports. "
            "Use the provided reference context to write comprehensive, well-structured content. "
            "Maintain an academic tone and ensure proper citations where appropriate."
        )
        
        full_prompt = f"""Reference Context:
{context}

Task:
{prompt}

Please generate comprehensive, well-written content based on the reference context above."""
        
        return self.generate(full_prompt, max_tokens, temperature, system_message)


# Global AI client instance
_ai_client_instance = None


def get_ai_client() -> AIClient:
    """Get or create global AI client instance"""
    global _ai_client_instance
    if _ai_client_instance is None:
        _ai_client_instance = AIClient()
    return _ai_client_instance
