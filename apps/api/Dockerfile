# Multi-stage Dockerfile for FastAPI backend with UV

# Stage 1: System dependencies with LaTeX (cached separately)
FROM python:3.13-slim as system-deps

# Install LaTeX packages first (rarely changes, ~500MB, should be cached)
RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-lang-portuguese \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Base image with all system dependencies
FROM system-deps as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_HTTP_TIMEOUT=120

# Install build dependencies and UV
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    libcairo2-dev \
    libpango1.0-dev \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/uv \
    && mv /root/.local/bin/uvx /usr/local/bin/uvx

# UV is now in /usr/local/bin which is in PATH by default

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml .
COPY uv.lock* .
COPY README.md .

# Install Python dependencies with UV (production only)
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Development stage
FROM base as development

# Install dev dependencies
RUN uv sync --frozen

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production

# Create non-root user and fix permissions
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app
USER appuser

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
