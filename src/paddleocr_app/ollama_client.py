"""
Ollama integration for local LLM inference.
Supports processing OCR results through language models.
"""
import logging
from typing import Optional
import requests
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class OllamaConfig:
    """Configuration for Ollama connection."""
    host: str = "http://localhost"
    port: int = 11434
    model: str = "llama2"
    timeout: int = 120
    
    @property
    def base_url(self) -> str:
        """Get base URL for Ollama API."""
        return f"{self.host}:{self.port}"


class OllamaClient:
    """
    Client for interacting with local Ollama instance.
    
    Useful for:
    - Summarizing OCR results
    - Correcting OCR errors via LLM
    - Extracting structured data from text
    """
    
    def __init__(self, config: Optional[OllamaConfig] = None):
        """
        Initialize Ollama client.
        
        Args:
            config: OllamaConfig instance. Defaults to localhost:11434
        """
        self.config = config or OllamaConfig()
        self._session = requests.Session()
        logger.info(f"Ollama client initialized: {self.config.base_url}")
    
    def health_check(self) -> bool:
        """
        Check if Ollama service is running.
        
        Returns:
            True if Ollama is accessible
        """
        try:
            response = self._session.get(
                f"{self.config.base_url}/api/tags",
                timeout=5,
            )
            is_healthy = response.status_code == 200
            if is_healthy:
                logger.info("✓ Ollama connection OK")
            return is_healthy
        except requests.RequestException as e:
            logger.error(f"✗ Ollama connection failed: {e}")
            return False
    
    def list_models(self) -> list:
        """
        List available models in Ollama.
        
        Returns:
            List of model names
        """
        try:
            response = self._session.get(
                f"{self.config.base_url}/api/tags",
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            data = response.json()
            models = [m["name"].split(":")[0] for m in data.get("models", [])]
            logger.info(f"Available models: {models}")
            return models
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    def generate(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Generate text using Ollama model.
        
        Args:
            prompt: Input prompt
            model: Model name. Defaults to config.model
            
        Returns:
            Generated text
        """
        model = model or self.config.model
        logger.info(f"Generating with model: {model}")
        
        try:
            response = self._session.post(
                f"{self.config.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            result = response.json()
            generated_text = result.get("response", "").strip()
            logger.debug(f"Generated text length: {len(generated_text)}")
            return generated_text
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
    
    def summarize_ocr_text(self, ocr_text: str, model: Optional[str] = None) -> str:
        """
        Summarize OCR extracted text using LLM.
        
        Args:
            ocr_text: Text extracted by OCR
            model: Model to use for summarization
            
        Returns:
            Summarized text
        """
        prompt = f"""Please summarize the following text concisely:

{ocr_text}

Summary:"""
        
        return self.generate(prompt, model)
    
    def correct_ocr_errors(self, ocr_text: str, model: Optional[str] = None) -> str:
        """
        Attempt to correct OCR errors using LLM.
        
        Args:
            ocr_text: Text with potential OCR errors
            model: Model to use for correction
            
        Returns:
            Corrected text
        """
        prompt = f"""The following text was extracted by OCR and may contain errors. 
Please correct any obvious spelling or grammar mistakes while preserving the original meaning:

{ocr_text}

Corrected text:"""
        
        return self.generate(prompt, model)
    
    def extract_entities(self, ocr_text: str, entity_types: str, model: Optional[str] = None) -> str:
        """
        Extract specific entities from OCR text using LLM.
        
        Args:
            ocr_text: Text extracted by OCR
            entity_types: Types to extract (e.g., "names, dates, prices")
            model: Model to use
            
        Returns:
            Extracted entities
        """
        prompt = f"""Extract the following from this text: {entity_types}

Text:
{ocr_text}

Entities:"""
        
        return self.generate(prompt, model)
    
    def close(self):
        """Close session."""
        self._session.close()
        logger.info("Ollama client closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def create_ollama_client(
    host: str = "http://localhost",
    port: int = 11434,
    model: str = "llama2",
) -> OllamaClient:
    """
    Factory function to create Ollama client.
    
    Args:
        host: Ollama host
        port: Ollama port
        model: Default model to use
        
    Returns:
        Initialized OllamaClient
    """
    config = OllamaConfig(host=host, port=port, model=model)
    return OllamaClient(config)
