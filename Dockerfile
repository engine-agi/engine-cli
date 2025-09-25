# Engine Framework - Shared Docker Configuration

# Base Dockerfile Template
# Usage: Copy to Dockerfile in each repository and customize

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /home/app

USER app
WORKDIR /home/app

# Install Poetry
RUN pip install poetry==2.1.4

# Configure Poetry
RUN poetry config virtualenvs.create false

# Copy dependency files
COPY --chown=app:app pyproject.toml poetry.lock ./

# Install Python dependencies
RUN poetry install --only=main --no-dev --no-interaction

# Copy source code
COPY --chown=app:app . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command
CMD ["engine"]
