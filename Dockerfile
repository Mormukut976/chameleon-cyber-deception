FROM python:3.11-slim

LABEL maintainer="CloudDC"
LABEL description="Chameleon - Advanced Cyber Deception Framework"
LABEL version="2.0"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data/logs modules/ai/models

# Expose ports
EXPOSE 8050 8055 2222 8081 8082 8083

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8050/ || exit 1

# Run the framework
CMD ["python3", "main.py"]
