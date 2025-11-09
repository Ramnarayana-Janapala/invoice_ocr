"""
Configuration management using Pydantic settings.
Reads from environment variables and .env file.
"""
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class OCRConfig(BaseSettings):
    """OCR configuration."""
    
    language: str = "en"
    model_dir: Path = Path.home() / ".paddleocr" / "models"
    use_gpu: bool = False
    enable_mkldnn: bool = True
    min_confidence: float = 0.5
    
    class Config:
        env_prefix = "OCR_"
        case_sensitive = False


class OllamaConfig(BaseSettings):
    """Ollama configuration."""
    
    enabled: bool = True
    host: str = "http://localhost"
    port: int = 11434
    model: str = "llama2"
    timeout: int = 120
    
    class Config:
        env_prefix = "OLLAMA_"
        case_sensitive = False


class AppConfig(BaseSettings):
    """Main application configuration."""
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[Path] = None
    
    # Data directories
    data_dir: Path = Path("./data")
    input_dir: Path = Path("./data/input")
    output_dir: Path = Path("./data/output")
    
    # Enable/disable features
    enable_batch_processing: bool = True
    save_results: bool = True
    
    # Sub-configs
    ocr: OCRConfig = OCRConfig()
    ollama: OllamaConfig = OllamaConfig()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        nested_delimiter = "__"
    
    def __init__(self, **data):
        """Initialize config and create necessary directories."""
        super().__init__(**data)
        # Create data directories
        self.data_dir.mkdir(exist_ok=True)
        self.input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)


# Global config instance
_config: Optional[AppConfig] = None


def load_config(config_path: Optional[Path] = None) -> AppConfig:
    """
    Load application configuration.
    
    Args:
        config_path: Path to .env file (optional)
        
    Returns:
        AppConfig instance
    """
    global _config
    
    if config_path:
        # Load from specific path
        import dotenv
        dotenv.load_dotenv(config_path)
    
    _config = AppConfig()
    return _config


def get_config() -> AppConfig:
    """
    Get global config instance.
    Initializes if not already loaded.
    
    Returns:
        AppConfig instance
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config
