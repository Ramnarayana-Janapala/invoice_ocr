# PaddleOCR + Ollama Application

A Python application for OCR (Optical Character Recognition) using PaddleOCR with local LLM integration via Ollama. Optimized for Apple Silicon (M1/M2/M3) Macs.

## 🎯 Features

- **PaddleOCR Integration**: Fast, accurate OCR with multilingual support
- **Apple Silicon Native**: Optimized for ARM64 processors
- **Ollama Integration**: Post-process OCR results with local LLMs
- **Cross-Platform**: Reproducible setup across machines with `uv` and `just`
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
- [just](https://github.com/casey/just) - Task runners

## 🚀 Quick Start

### 1. Clone and Navigate
```bash
git clone <your-repo>
```

### 2. Full Setup (Recommended)
```bash
just setup
```

This will:
- Install all dependencies with `uv`
- Download and cache PaddleOCR models
- Verify Ollama connection
- Create necessary directories

### 3. Run OCR
```bash
just run             # Using just
```

## 📚 Installation Methods

### justfile
```bash
just help             # See all commands
just install          # Install dependencies
just dev              # Install with dev tools
just setup-models     # Download models
just check-ollama     # Test Ollama
just clean-all        # Clean the environment
```

###Manual with uv
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

#### RUN Examples
```bash
just run
just run-model
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

## 🧪 Testing

```bash
# Run all tests
just test  
```

## 🔍 Ollama Setup

### Install Ollama
Visit [ollama.ai](https://ollama.ai) and download for macOS.

### Download Models
```bash
# In another terminal
ollama serve        # Start Ollama server
# In another terminal, download models
ollama pull mistral
```

### Verify Connection
```bash
just check-ollama          # with just
```

### Issue: "PaddleOCR models not found"
```bash
just setup-models
just test
```

### Issue: "Ollama connection refused"
```bash
# Make sure Ollama is running
ollama serve
```
