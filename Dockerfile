# ── Backend Dockerfile ──────────────────────────────────────────────────────
# 3-stage build strategy:
#   Stage 1 (deps)    – install Python packages; cached between builds unless requirements.txt changes
#   Stage 2 (ingest)  – run the data ingestion during the IMAGE BUILD so the Parquet artifact
#                        is baked in. Railway never has to ingest at startup → port binds instantly.
#   Stage 3 (runtime) – lean final image; just app code + pre-built Parquet + installed packages.

# ──────────────────────────────────────────────────────────────────────────────
# Stage 1 – install Python dependencies
# ──────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS deps

WORKDIR /app

# Build tools required by pyarrow / pandas native extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ──────────────────────────────────────────────────────────────────────────────
# Stage 2 – data ingestion (runs ONCE at build time, not at every deploy/start)
# ──────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS ingest

WORKDIR /app

# Reuse the already-installed packages from the deps stage
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Copy only the code needed to run the ingestion
COPY src/      ./src/
COPY scripts/  ./scripts/

ENV PYTHONPATH=/app/src

# Accept env vars for dataset location and budget thresholds via build-args so
# the Parquet is built with the same config used at runtime.
ARG DATASET_ID=ManikaSaini/zomato-restaurant-recommendation
ARG DATA_PATH=./data/processed/restaurants.parquet
ARG BUDGET_LOW_MAX=500
ARG BUDGET_MEDIUM_MAX=1500

ENV DATASET_ID=$DATASET_ID \
    DATA_PATH=$DATA_PATH \
    BUDGET_LOW_MAX=$BUDGET_LOW_MAX \
    BUDGET_MEDIUM_MAX=$BUDGET_MEDIUM_MAX

RUN mkdir -p data/processed data/raw/hf_cache

# ⬇️  The expensive step: download + process 52 k rows → Parquet.
# Runs during `docker build` / Railway image build — never at container start.
RUN python scripts/ingest.py


# ──────────────────────────────────────────────────────────────────────────────
# Stage 3 – lean runtime image
# ──────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Installed packages
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Application source
COPY src/     ./src/
COPY main.py  ./main.py

# Pre-built Parquet artifact — no network call needed at startup
COPY --from=ingest /app/data/processed/ ./data/processed/

ENV PYTHONPATH=/app/src

# $PORT is injected by Railway at runtime; fallback 8000 for local docker run
EXPOSE 8000

# Start command: just boot uvicorn — ingest is already done
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
