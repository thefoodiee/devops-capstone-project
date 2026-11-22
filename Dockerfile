# Multi-stage Dockerfile for Cloud-Native Notes Application
# Stage 1: Build & Dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Final Runtime Image (Hardened, Non-root)
FROM python:3.11-slim AS runner

WORKDIR /app

# Install runtime PostgreSQL client library & curl for container health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create unprivileged application user for security (DevSecOps)
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -s /bin/bash -m appuser

# Copy installed python packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy application code
COPY --chown=appuser:appgroup . .

# Ensure entrypoint script is executable
RUN chmod +x docker-entrypoint.sh

# Switch to non-root user
USER appuser

EXPOSE 5000

# Container Healthcheck (Phase 3 & Kubernetes Liveness)
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

ENTRYPOINT ["/app/docker-entrypoint.sh"]
