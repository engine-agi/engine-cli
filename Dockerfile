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
RUN pip install poetry==1.8.3

# Configure Poetry
RUN poetry config virtualenvs.create false

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /home/app

USER app
WORKDIR /home/app

# Copy dependency files
COPY --chown=app:app pyproject.toml poetry.lock ./

# Create requirements.txt manually for main dependencies
RUN echo "click>=8.1.7,<9.0.0" > requirements.txt && \
    echo "pyyaml>=6.0.1,<7.0.0" >> requirements.txt && \
    echo "rich>=12.6.0,<13.0.0" >> requirements.txt && \
    echo "prompt-toolkit>=3.0.39,<4.0.0" >> requirements.txt && \
    echo "pydantic>=2.0.0,<3.0.0" >> requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY --chown=app:app . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command
CMD ["engine"]
