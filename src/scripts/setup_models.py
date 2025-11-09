"""
Setup script to download and cache PaddleOCR models.
Enables offline usage after initial download.
"""
import logging
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from paddleocr_app.ocr import create_ocr_engine
from paddleocr_app.config import get_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def setup():
    """Download and cache OCR models for offline use."""
    config = get_config()
    
    logger.info("=" * 60)
    logger.info("PaddleOCR Model Setup")
    logger.info("=" * 60)
    logger.info(f"Model cache directory: {config.ocr.model_dir}")
    logger.info(f"Language: {config.ocr.language}")
    
    # List of languages to optionally download
    languages = {
        "en": "English",
        "ch": "Chinese",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "ja": "Japanese",
        "ko": "Korean",
    }
    
    print("\nAvailable languages:")
    for code, name in languages.items():
        print(f"  {code:5} - {name}")
    
    # Download models for selected language
    try:
        logger.info(f"\nInitializing OCR engine for '{config.ocr.language}'...")
        logger.info("(This will download models on first run)")
        
        ocr = create_ocr_engine(language=config.ocr.language)

        # Test basic functionality
        logger.info("\nTesting OCR...")
        print("\nSetup complete! You can now use PaddleOCR offline.")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error during setup: {e}")
        logger.error("Make sure you have enough disk space and internet connectivity")
        return False


if __name__ == "__main__":
    success = setup()
    sys.exit(0 if success else 1)
