# ── Backend Dockerfile ──────────────────────────────────────────────────────
# Multi-stage build: deps stage caches pip installs separately from app code.
# Stage 1 – install Python dependencies
FROM python:3.11-slim AS deps

WORKDIR /app

# System-level build tools needed by some packages (e.g. pyarrow)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Stage 2 – runtime image
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy installed packages from deps stage
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Copy application source
COPY src/        ./src/
COPY scripts/    ./scripts/
COPY main.py     ./main.py

# Create the processed-data directory (Railway/Docker scratch space)
RUN mkdir -p data/processed data/raw/hf_cache

# Expose the port the app will listen on.
# $PORT is injected by Railway at runtime; default 8000 for local Docker use.
EXPOSE 8000

# Set Python path so `app.*` imports resolve under src/
ENV PYTHONPATH=/app/src

# Entrypoint: run ingest first, then start the API server.
# $PORT is provided by Railway; fallback to 8000 for local docker run.
CMD ["sh", "-c", "python scripts/ingest.py && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
