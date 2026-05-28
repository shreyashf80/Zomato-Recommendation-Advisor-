from __future__ import annotations

import os
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from collections.abc import Callable
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

# Adjust sys.path to enable clean imports from app package
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import uuid
from app.config import get_settings
from app.data.repository import RestaurantRepository
from app.services.logging import correlation_id_ctx, logger, setup_logging
from app.services.orchestrator import build_use_case_from_settings
from app.api.routes import router as api_router

# Initialize application-wide logging formats
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Initialize repository and orchestrator service on startup
    settings = get_settings()
    logger.info("Initializing RestaurantRepository Parquet database...")
    
    # Load the preprocessed Parquet database
    repository = RestaurantRepository.from_parquet(settings.data_path)
    use_case = build_use_case_from_settings(settings=settings, repository=repository)
    
    # Attach to app state for access in route handlers
    app.state.repository = repository
    app.state.use_case = use_case
    logger.info("Database loaded and recommendation orchestrator ready.")
    
    yield
    # Clean up resources on shutdown if any
    logger.info("Shutting down API server...")


app = FastAPI(
    title="Zomato AI Recommendation Advisor API",
    description="Backend API for the Zomato AI Sushi recommendation system",
    version="1.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def add_correlation_id_middleware(request: Request, call_next: Callable) -> Response:
    # Extract existing correlation ID or generate a new random UUID
    cid = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    
    # Set the ContextVar value for the duration of this request
    token = correlation_id_ctx.set(cid)
    try:
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = cid
        return response
    finally:
        # Reset the ContextVar back to default value
        correlation_id_ctx.reset(token)


# Configure CORS to allow the React client to make cross-origin requests
settings = get_settings()
origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root health-check endpoint — Railway checks this to confirm the service is up.
@app.get("/")
def root() -> dict:
    return {
        "service": "Zomato AI Recommendation Advisor API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "api": "/api/v1",
    }


# Include the API router
app.include_router(api_router, prefix="/api/v1")


def run() -> None:
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    run()
