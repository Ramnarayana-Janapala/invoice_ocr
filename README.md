# PaddleOCR + Ollama Application

A Python application for OCR (Optical Character Recognition) using PaddleOCR with local LLM integration via Ollama. Optimized for Apple Silicon (M1/M2/M3) Macs.

## 🎯 Features

- **PaddleOCR Integration**: Fast, accurate OCR with multilingual support
- **Apple Silicon Native**: Optimized for ARM64 processors
- **Ollama Integration**: Post-process OCR results with local LLMs
- **Cross-Platform**: Reproducible setup across machines with `uv`, `make`, and `just`
- **CLI & Python API**: Command-line interface and programmatic access
- **Batch Processing**: Process multiple images efficiently
- **Configuration Management**: Environment-based configuration with `.env` support

## 📋 Prerequisites

### Required
- Python 3.9+ (3.11+ recommended)
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- macOS with Apple Silicon (or Intel)

### Optional
- [Ollama](https://ollama.ai) - For LLM features (highly recommended)
- [Make](https://www.gnu.org/software/make/) or [just](https://github.com/casey/just) - Task runners

## 🚀 Quick Start

### 1. Clone and Navigate
```bash
git clone <your-repo>
cd paddleocr-project
```

### 2. Full Setup (Recommended)
```bash
# Using make
make setup

# Or using just
just setup
```

This will:
- Install all dependencies with `uv`
- Download and cache PaddleOCR models
- Verify Ollama connection
- Create necessary directories

### 3. Run OCR
```bash
make run              # Using make
# or
just run             # Using just
```

## 📚 Installation Methods

### Option A: Makefile (Traditional)
```bash
make help              # See all commands
make install           # Install dependencies
make dev               # Install with dev tools
make setup-models      # Download models
make check-ollama      # Test Ollama
```

### Option B: justfile (Modern, Recommended)
```bash
just help             # See all commands
just install          # Install dependencies
just dev              # Install with dev tools
just setup-models     # Download models
just check-ollama     # Test Ollama
```

### Option C: Manual with uv
```bash
# Install with uv
uv sync                # Install dependencies
uv sync --all-extras   # Install with dev dependencies

# Download models
python src/scripts/setup_models.py

# Test Ollama
python src/scripts/test_ollama.py
```

## 🖼️ Usage

### Command Line Interface

#### Process Single Image
```bash
paddleocr-app process --image photo.jpg --language en
# or
uv run python -m paddleocr_app.cli process --image photo.jpg
```

#### Process with LLM Correction
```bash
paddleocr-app process --image photo.jpg --use-llm
```

#### Batch Process
```bash
paddleocr-app batch --input-dir ./images --pattern "*.jpg"
```

#### Check System
```bash
paddleocr-app check    # System config and service health
paddleocr-app info     # Application configuration
```

### Python API

```python
from paddleocr_app import create_ocr_engine, create_ollama_client
from pathlib import Path

# Initialize OCR
ocr = create_ocr_engine(language="en")

# Process image
results = ocr.process_image(Path("photo.jpg"))

# Get full text
text = ocr.extract_full_text(Path("photo.jpg"))

# Optional: Post-process with LLM
ollama = create_ollama_client()
if ollama.health_check():
    corrected = ollama.correct_ocr_errors(text)
    summarized = ollama.summarize_ocr_text(text)
```

## ⚙️ Configuration

### Environment Variables
Create a `.env` file (copy from `.env.example`):

```env
# OCR
OCR_LANGUAGE=en
OCR_MIN_CONFIDENCE=0.5
OCR_USE_GPU=false

# Ollama
OLLAMA_ENABLED=true
OLLAMA_HOST=http://localhost
OLLAMA_PORT=11434
OLLAMA_MODEL=llama2

# Application
LOG_LEVEL=INFO
DATA_DIR=./data
```

### Python Configuration
```python
from paddleocr_app import get_config

config = get_config()
print(config.ocr.language)
print(config.ollama.model)
```

## 🧪 Testing

```bash
# Run all tests
make test          # with make
just test          # with just
uv run pytest      # manual

# With coverage report
uv run pytest --cov=paddleocr_app --cov-report=html
# Open htmlcov/index.html
```

## 🔍 Ollama Setup

### Install Ollama
Visit [ollama.ai](https://ollama.ai) and download for macOS.

### Download Models
```bash
# In another terminal
ollama serve        # Start Ollama server

# In another terminal, download models
ollama pull llama2
ollama pull mistral
ollama pull neural-chat
```

### Verify Connection
```bash
make check-ollama          # with make
just check-ollama          # with just
python src/scripts/test_ollama.py  # manual
```

## 📁 Project Structure

```
paddleocr-project/
├── pyproject.toml              # Project config with dependencies
├── uv.lock                     # Lock file for reproducibility
├── Makefile                    # Traditional task runner
├── justfile                    # Modern task runner
├── .env.example                # Configuration template
├── README.md
│
├── src/
│   ├── paddleocr_app/
│   │   ├── __init__.py
│   │   ├── ocr.py             # PaddleOCR wrapper
│   │   ├── ollama_client.py   # Ollama integration
│   │   ├── config.py          # Configuration management
│   │   └── cli.py             # CLI with Typer
│   │
│   └── scripts/
│       ├── setup_models.py     # Download and cache models
│       └── test_ollama.py      # Test Ollama connection
│
├── tests/
│   ├── __init__.py
│   └── test_config.py          # Sample tests
│
├── config/
│   └── settings.yaml           # App configuration (optional)
│
└── data/
    ├── input/                  # Input images
    ├── output/                 # OCR results
    └── models/                 # Cached models
```

## 🔧 Common Commands

| Task | Make | Just | Manual |
|------|------|------|--------|
| Full setup | `make setup` | `just setup` | See above |
| Install deps | `make install` | `just install` | `uv sync` |
| Download models | `make setup-models` | `just setup-models` | `python src/scripts/setup_models.py` |
| Run tests | `make test` | `just test` | `uv run pytest` |
| Format code | `make format` | `just format` | `uv run black src/` |
| Lint | `make lint` | `just lint` | `uv run ruff check src/` |
| Clean cache | `make clean` | `just clean` | `find . -name __pycache__ -delete` |

## 🆘 Troubleshooting

### Issue: "PaddleOCR models not found"
```bash
# Re-download models
make setup-models
# or
just setup-models
```

### Issue: "Ollama connection refused"
```bash
# Make sure Ollama is running
ollama serve

# In another terminal, check status
make check-ollama
```

### Issue: "No module named paddleocr"
```bash
# Reinstall dependencies
uv sync --fresh
```

### Issue: Apple Silicon performance slow
- Models are cached in `~/.paddleocr/models` after first run
- CPU optimization (MKLDNN) is enabled by default
- GPU is disabled by default (not available for Ollama on Apple Silicon)

## 📦 Dependencies

### Core
- **paddleocr**: OCR engine
- **paddlepaddle**: ML framework
- **opencv-python**: Image processing
- **pillow**: Image handling

### Integration
- **requests**: HTTP client for Ollama
- **typer**: CLI framework
- **rich**: Terminal UI

### Configuration
- **pydantic**: Settings validation
- **python-dotenv**: Environment management

### Development
- **pytest**: Testing
- **black**: Code formatting
- **ruff**: Linting
- **mypy**: Type checking

## 🚢 Deployment

### Docker (Optional)
```bash
docker build -t paddleocr-app .
docker run -v $(pwd)/data:/app/data paddleocr-app
```

### Cloud/Server
Since models are cached after first run, distribute the cached models:
```bash
# Copy this directory to production
~/.paddleocr/models
```

## 📝 Contributing

1. Fork and clone
2. Create feature branch: `git checkout -b feature/xyz`
3. Format code: `make format`
4. Run tests: `make test`
5. Push and create pull request

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Support

- **GitHub Issues**: Report bugs and request features
- **Documentation**: See docstrings in source code
- **PaddleOCR**: https://github.com/PaddlePaddle/PaddleOCR
- **Ollama**: https://ollama.ai

## 🎓 Learn More

- [PaddleOCR Documentation](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/README.md)
- [Ollama Models](https://ollama.ai/library)
- [uv Documentation](https://github.com/astral-sh/uv)
- [justfile Guide](https://just.systems/)

---

**Built for Apple Silicon • Optimized for Offline Use • LLM-Enhanced**
