"""
Main FastAPI application module.
"""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router as api_router
from app.core.registry import TransformationRegistry
from app.transformations.filter import FilterTransformation
from app.transformations.map import MapTransformation
from app.transformations.uppercase import UppercaseTransformation
from app.utils.logger import setup_logger
from config.settings import (API_DESCRIPTION, API_TITLE, API_VERSION,
                             API_VERSIONS, CURRENT_API_VERSION)

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info(
        f"Starting Mini Data Transformer API (App Version: {API_VERSION}, "
        f"API Version: {CURRENT_API_VERSION} {API_VERSIONS[CURRENT_API_VERSION]})"
    )
    yield
    # Shutdown
    logger.info("Shutting down Mini Data Transformer API")


# Create FastAPI app
app = FastAPI(
    title=f"{API_TITLE} {CURRENT_API_VERSION}",
    description=f"""
{API_DESCRIPTION}

## API Versioning
- Current API Version: {CURRENT_API_VERSION} ({API_VERSIONS[CURRENT_API_VERSION]})
- Application Version: {API_VERSION}

## Authentication
All endpoints except `/api/v1/heartbeat` require authentication using JWT tokens.
""",
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register built-in transformations
TransformationRegistry.register(FilterTransformation)
TransformationRegistry.register(MapTransformation)
TransformationRegistry.register(UppercaseTransformation)

# Include API router with versioning
app.include_router(api_router, prefix="/api")


@app.get("/api/v1/heartbeat")
async def get_heartbeat():
    """Get the API health status."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": API_VERSION,
        "api_version": CURRENT_API_VERSION,
    }


@app.get("/api/v1/server-info")
async def get_server_info():
    """Get server configuration information."""
    return {
        "status": "operational",
        "version": API_VERSION,
        "api_version": CURRENT_API_VERSION,
        "upload_config": {
            "supported_formats": ["csv"],
            "automatic_engine_selection": True,
            "engine_selection_rules": {"pandas": "Files <= 1GB", "dask": "Files > 1GB (automatic)"},
        },
        "engines": {
            "pandas": {"description": "Standard processing engine for smaller files"},
            "dask": {"description": "Distributed processing engine automatically used for files > 1GB"},
        },
    }
