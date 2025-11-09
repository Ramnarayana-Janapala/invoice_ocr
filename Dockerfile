FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PaddleOCR
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy project files
COPY . .

# Install dependencies
RUN uv sync

# Download models
RUN python src/scripts/setup_models.py

# Create data directories
RUN mkdir -p data/input data/output

# Set entry point
ENTRYPOINT ["uv", "run", "python", "-m", "paddleocr_app.cli"]
CMD ["--help"]
