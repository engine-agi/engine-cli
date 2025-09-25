# Engine Framework - Shared Docker Configuration

# Base Dockerfile Template
# Usage: Copy to Dockerfile in each repository and customize

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install Poetry as root
RUN pip install poetry==2.1.4

# Configure Poetry
RUN poetry config virtualenvs.create false

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /home/app

USER app
WORKDIR /home/app

# Copy dependency files
COPY --chown=app:app pyproject.toml poetry.lock README.md ./

# Create a temporary pyproject.toml without readme for Docker build
RUN sed 's/^readme = "README.md"//' pyproject.toml > pyproject.tmp && mv pyproject.tmp pyproject.toml

# Install Python dependencies
RUN poetry install --no-interaction --no-root

# Copy source code
COPY --chown=app:app . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command
CMD ["engine"]
