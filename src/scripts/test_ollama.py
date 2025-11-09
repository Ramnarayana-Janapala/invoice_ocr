"""
Test Ollama connection and display available models.
Helps verify setup before using LLM features.
"""
import logging
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from paddleocr_app.ollama_client import create_ollama_client
from paddleocr_app.config import get_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def test_ollama():
    """Test Ollama connection and display available models."""
    config = get_config()
    
    print("=" * 60)
    print("Ollama Connection Test")
    print("=" * 60)
    print(f"Host: {config.ollama.host}")
    print(f"Port: {config.ollama.port}")
    print(f"Default Model: {config.ollama.model}")
    print()
    
    # Create client
    ollama = create_ollama_client(
        host=config.ollama.host,
        port=config.ollama.port,
        model=config.ollama.model,
    )
    
    # Check health
    print("Checking connection...")
    if ollama.health_check():
        print("✓ Successfully connected to Ollama!\n")
        
        # List models
        print("Available models:")
        models = ollama.list_models()
        
        if models:
            for model in models:
                print(f"  - {model}")
            print()
            
            # Test generation with first available model
            if config.ollama.model in models:
                test_model = config.ollama.model
            else:
                test_model = models[0]
                print(f"Note: {config.ollama.model} not found, using {test_model}\n")
            
            print(f"Testing generation with '{test_model}'...")
            try:
                response = ollama.generate(
                    "Say 'Hello from Ollama!' in exactly those words.",
                    model=test_model
                )
                print(f"✓ Generation successful!")
                print(f"Response: {response}\n")
                return True
            except Exception as e:
                logger.error(f"✗ Generation failed: {e}")
                return False
        else:
            print("⚠ No models found in Ollama")
            print("Please download a model first:")
            print("  ollama pull llama2")
            print("  ollama pull mistral")
            print("  ollama pull neural-chat")
            print()
            return False
    else:
        print("✗ Could not connect to Ollama\n")
        print("Make sure Ollama is running:")
        print(f"  Expected at: {config.ollama.host}:{config.ollama.port}")
        print()
        print("Start Ollama with:")
        print("  ollama serve")
        print()
        return False


if __name__ == "__main__":
    success = test_ollama()
    print("=" * 60)
    sys.exit(0 if success else 1)
