"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
import os

from app.core.config import settings
from app.core.database import create_tables

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="A secure healthcare audio transcription platform",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)


@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.
    """
    logger.info(f"Starting {settings.app_name}")
    
    # Create audio storage directory
    os.makedirs(settings.audio_storage_path, exist_ok=True)
    logger.info(f"Audio storage path: {settings.audio_storage_path}")
    
    # Create database tables
    try:
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.
    """
    logger.info(f"Shutting down {settings.app_name}")


@app.get("/")
async def root():
    """
    Root endpoint for health check.
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "timestamp": "2025-11-05T00:00:00Z"
    }


# Import and include routers
from app.api import auth, recordings
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(recordings.router, prefix="/recordings", tags=["recordings"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
