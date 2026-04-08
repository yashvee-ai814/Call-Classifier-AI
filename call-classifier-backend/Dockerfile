# ─────────────────────────────────────────────────────────────────────────────
# Call Classifier Backend — Dockerfile
#
# Uses a two-stage build:
#   Stage 1 (builder): installs Python dependencies with uv
#   Stage 2 (runtime): copies only what's needed to run the app — keeping the
#                      final image small and free of build-time tools
#
# To build:  docker build -t call-classifier-backend .
# To run:    docker run -p 8000:8000 call-classifier-backend
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: dependency installer ─────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Borrow the uv binary directly from its official image — no pip needed
# uv is a fast Python package manager (https://github.com/astral-sh/uv)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy the dependency manifest first.
# Docker caches each instruction as a "layer". By copying pyproject.toml before
# the source code, Docker can reuse the cached dependency layer on rebuilds
# as long as pyproject.toml hasn't changed — saving a lot of time.
COPY pyproject.toml ./

# Install all dependencies into a virtual environment at /app/.venv
# --no-dev skips development-only dependencies (linters, test tools, etc.)
RUN uv sync --no-dev

# ── Stage 2: runtime image ────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Security best practice: never run application code as root inside a container.
# We create an unprivileged user called "appuser" for this purpose.
RUN useradd -m -u 1000 appuser

# Copy the installed virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy the application source code
COPY . .

# Add the virtual environment's binaries to PATH so we can run uvicorn directly
ENV PATH="/app/.venv/bin:$PATH"

# Give the non-root user ownership of the entire /app directory
RUN chown -R appuser:appuser /app

# Switch to the non-root user for all subsequent commands
USER appuser

# Declare which port the container will listen on (documentation only — you still
# need -p 8000:8000 when running the container)
EXPOSE 8000

# Health check: Docker will call this every 30 s to verify the app is alive.
# If it fails 3 times in a row the container is marked "unhealthy".
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/docs')"

# Start the uvicorn ASGI server
# main:app  →  the "app" object inside main.py
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]