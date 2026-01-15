"""FastAPI application entry point"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config import settings
from app.api import health, ocr
from app.services.ocr_service import ocr_service

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events

    Initializes OCR service on startup and cleans up on shutdown
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{__version__}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Device: {settings.device}")

    try:
        await ocr_service.initialize(settings)
        logger.info("Application startup completed")
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down application...")
    await ocr_service.shutdown()
    logger.info("Application shutdown completed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Production-ready OCR service using PaddleOCR PP-OCRv5 models with automatic multilingual detection",
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(ocr.router)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with service information
    """
    return {
        "service": settings.app_name,
        "version": __version__,
        "status": "running",
        "ocr_engine": "PaddleOCR PP-OCRv5",
        "multilingual_support": [
            "Simplified Chinese",
            "Traditional Chinese",
            "English",
            "Japanese",
            "Pinyin"
        ],
        "docs": "/docs" if settings.debug else "disabled",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
