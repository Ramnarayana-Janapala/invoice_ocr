#!/usr/bin/env just --justfile

set shell := ["bash", "-c"]
# Display help message
help:
    @echo "PaddleOCR + Ollama Project - Available Commands"
    @echo "==============================================="
    @echo ""
    @echo "Setup & Installation:"
    @echo "  just setup              - Install dependencies and setup (full setup)"
    @echo "  just install            - Install project with uv"
    @echo "  just dev                - Install with dev dependencies"
    @echo "  just setup-models       - Download PaddleOCR models for offline use"
    @echo ""
    @echo "Development:"
    @echo "  just lint               - Run linting and formatting checks"
    @echo "  just format             - Auto-format code"
    @echo "  just test               - Run tests with coverage"
    @echo ""
    @echo "Running:"
    @echo "  just run                - Run OCR on a sample image"
    @echo "  just check-ollama       - Verify Ollama connection"
    @echo "  just cli                - Launch interactive CLI"
    @echo ""
    @echo "Maintenance:"
    @echo "  just clean              - Clean cache, models, __pycache__"
    @echo "  just clean-all          - Clean everything including .venv"

# Full setup: install deps, models, and verify Ollama
setup: install setup-models check-ollama
    @echo "✓ Setup complete! Your environment is ready."
    @echo "  Next: just run"

# Install dependencies with uv
install:
    @echo "Installing dependencies with uv..."
    uv sync
    @echo "✓ Dependencies installed"

# Install with dev dependencies
dev: install
    @echo "Installing dev dependencies..."
    uv sync --all-extras
    @echo "✓ Development environment ready"

# Download and cache PaddleOCR libraries
setup-models:
    @echo "Setting up PaddleOCR models..."
    mkdir -p data/models
    uv run python src/scripts/setup_models.py
    @echo "✓ Models downloaded"

# Verify Ollama connection and health
check-ollama:
    @echo "Checking Ollama connection..."
    uv run python src/scripts/test_ollama.py

# Run all linting checks
lint:
    @echo "Running linter..."
    uv run ruff check src/ tests/ --select E,F,W,I
    @echo "Running formatter check..."
    uv run black --check src/ tests/
    @echo "Running type checker..."
    uv run mypy src/paddleocr_app --ignore-missing-imports
    @echo "✓ Linting passed"

# Auto-format all code
format:
    @echo "Formatting code..."
    uv run black src/ tests/
    uv run ruff check --fix src/ tests/
    @echo "✓ Code formatted"

# Run test suite with coverage
test:
    @echo "Running tests..."
    uv run pytest tests/ -v --cov=paddleocr_app --cov-report=html
    @echo "✓ Tests passed. Coverage report: htmlcov/index.html"

# Run OCR on sample image
run:
    @echo "Running OCR example..."
    uv run paddleocr-app extract-invoice ./data/input/sample.png

run-model:
    @echo "Running OCR example... with a question"
    uv run ocr-integration ./data/input/sample.png --question "What is the total amount?"
# Clean cache and build artifacts
clean:
    @echo "Cleaning cache and artifacts..."
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    find . -type f -name ".DS_Store" -delete
    @echo "✓ Cache cleaned"

# Remove everything including virtual environment
clean-all: clean
    @echo "Removing virtual environment..."
    rm -rf .venv
    rm -f uv.lock
    @echo "✓ Full clean complete"


# Show project information
info:
    @echo "Project Configuration:"
    @.venv/bin/python3 -c "import sys; print(f'  Python: {sys.version.split()[0]}')"
    @uv --version | xargs -I {} echo "  uv: {}"
    @python3 -c "import platform; print(f'  Platform: {platform.platform()}')"
