"""SmartRecruitAI FastAPI Application Main Module

This module initializes the FastAPI application with modular routers,
CORS configuration, and middleware setup.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import upload, analyze
from app.utils.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    logger.info("Starting SmartRecruitAI application...")
    yield
    logger.info("Shutting down SmartRecruitAI application...")


# Create FastAPI application
app = FastAPI(
    title="SmartRecruitAI",
    description="AI-powered resume analysis and job matching API",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(upload.router, tags=["Upload & UI"])
app.include_router(analyze.router, prefix="/api", tags=["Analysis API"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.0.0"}


@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {
        "message": "SmartRecruitAI API v2.0",
        "endpoints": {
            "upload": "/",
            "parse_resume": "/api/parse-resume",
            "analyze_match": "/api/analyze-match",
            "rewrite_bullets": "/api/rewrite-bullets",
            "export_docx": "/api/export/docx",
            "get_report": "/api/report/{id}",
            "docs": "/api/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
