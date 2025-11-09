"""
PaddleOCR Application - OCR with Ollama integration for Apple Silicon
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__description__ = "OCR application with PaddleOCR and Ollama integration"

from .ocr import PaddleOCREngine, OCRResult, create_ocr_engine
from .ollama_client import OllamaClient, OllamaConfig, create_ollama_client
from .config import AppConfig, get_config, load_config

__all__ = [
    "PaddleOCREngine",
    "OCRResult",
    "create_ocr_engine",
    "OllamaClient",
    "OllamaConfig",
    "create_ollama_client",
    "AppConfig",
    "get_config",
    "load_config",
]
