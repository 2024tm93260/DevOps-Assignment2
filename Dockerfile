# ==================== Multi-stage Build ====================
# Stage 1: Builder - Install dependencies
FROM python:3.11-slim AS builder

# Set build arguments
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=1.3.0

# Labels for metadata
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.authors="2024tm93122"
LABEL org.opencontainers.image.url="https://github.com/2024tm93122/aceest-fitness"
LABEL org.opencontainers.image.documentation="https://github.com/2024tm93122/aceest-fitness/blob/main/README.md"
LABEL org.opencontainers.image.source="https://github.com/2024tm93122/aceest-fitness"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.revision="${VCS_REF}"
LABEL org.opencontainers.image.vendor="BITS Pilani"
LABEL org.opencontainers.image.title="ACEest Fitness API"
LABEL org.opencontainers.image.description="Flask-based fitness tracking API with workout logging, progress tracking, and health metrics"

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Create working directory
WORKDIR /app

# Install system dependencies for Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ==================== Stage 2: Runtime ====================
FROM python:3.11-slim AS runtime

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    GUNICORN_WORKERS=2 \
    GUNICORN_THREADS=4 \
    GUNICORN_TIMEOUT=30 \
    GUNICORN_KEEPALIVE=5 \
    GUNICORN_MAX_REQUESTS=1000 \
    GUNICORN_MAX_REQUESTS_JITTER=50 \
    PORT=8000

# Install only runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r appuser && \
    useradd -r -g appuser -u 1000 -m -s /sbin/nologin appuser

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser tests/ ./tests/
COPY --chown=appuser:appuser requirements.txt .
COPY --chown=appuser:appuser entrypoint.sh .

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/instance && \
    chown -R appuser:appuser /app && \
    chmod +x /app/entrypoint.sh

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

# Alternative CMD if entrypoint needs to be overridden
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "--timeout", "30", "app.app:create_app()"]
