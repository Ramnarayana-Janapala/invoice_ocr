"""Sample tests for OCR and Ollama modules."""
import pytest
from pathlib import Path
from paddleocr_app.config import AppConfig, OCRConfig, OllamaConfig


class TestConfig:
    """Test configuration management."""
    
    def test_ocr_config_defaults(self):
        """Test OCR config defaults."""
        config = OCRConfig()
        assert config.language == "en"
        assert config.use_gpu is False
        assert config.enable_mkldnn is True
        assert config.min_confidence == 0.5
    
    def test_ollama_config_defaults(self):
        """Test Ollama config defaults."""
        config = OllamaConfig()
        assert config.enabled is True
        assert config.port == 11434
        assert config.host == "http://localhost"
        assert config.model == "llama2"


class TestImports:
    """Test that modules import correctly."""
    
    def test_import_ocr_engine(self):
        """Test OCR engine import."""
        from paddleocr_app.ocr import create_ocr_engine
        assert callable(create_ocr_engine)
    
    def test_import_ollama_client(self):
        """Test Ollama client import."""
        from paddleocr_app.ollama_client import create_ollama_client
        assert callable(create_ollama_client)
    
    def test_import_cli(self):
        """Test CLI import."""
        from paddleocr_app.cli import app
        assert app is not None


# Run tests with: uv run pytest tests/ -v
