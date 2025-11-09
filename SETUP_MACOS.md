# Setup Guide for Apple Silicon Macs

This guide provides step-by-step instructions for setting up the PaddleOCR + Ollama application on Apple Silicon Macs (M1, M2, M3, etc.).

## Prerequisites

### 1. Install Homebrew (if not already installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install Python 3.11+ via Homebrew
```bash
brew install python@3.11
```

Verify installation:
```bash
python3 --version
```

### 3. Install uv (Fast Python Package Manager)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify installation:
```bash
uv --version
```

## Step-by-Step Setup

### Step 1: Clone the Repository
```bash
git clone <your-repo-url> paddleocr-project
cd paddleocr-project
```

### Step 2: Copy Environment Configuration
```bash
cp .env.example .env
```

You can edit `.env` to customize settings, but defaults work well.

### Step 3: Full Setup (Automatic)

Choose **one** of these options:


#### Using just
First, install `just`:
```bash
brew install just
```

Then run:
```bash
just setup
```

#### Option C: Manual uv setup
```bash
# Install dependencies
uv sync

# Download models (takes 5-10 minutes first time)
python src/scripts/setup_models.py

# Verify Ollama setup
python src/scripts/test_ollama.py
```

### Step 4: Install Ollama (Optional but Recommended)

Download and install Ollama from [ollama.ai](https://ollama.ai)

Then download models:
```bash
ollama pull llama2      # ~4GB
ollama pull mistral     # ~5GB
```

Start Ollama server in a separate terminal:
```bash
ollama serve
```

## Verification

Check that everything is set up correctly:

```bash
# Check system info
just info    # or: just info

# Test Ollama connection
just check-ollama    # or: just check-ollama

# Run on sample image
just run    # or: just run
```
