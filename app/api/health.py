"""Health check endpoints"""

from fastapi import APIRouter, status

from app import __version__
from app.models.response import HealthResponse, ReadinessResponse
from app.services.ocr_service import ocr_service

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Simple liveness check to verify the service is running"
)
async def health_check() -> HealthResponse:
    """
    Basic health check endpoint

    Returns:
        HealthResponse with status and version
    """
    return HealthResponse(
        status="healthy",
        version=__version__
    )


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Readiness check to verify OCR service is initialized and ready"
)
async def readiness_check() -> ReadinessResponse:
    """
    Readiness check endpoint with OCR initialization status

    Returns:
        ReadinessResponse with detailed service status
    """
    is_initialized = ocr_service.is_initialized()
    is_gpu = ocr_service.is_gpu_available()

    return ReadinessResponse(
        status="ready" if is_initialized else "not_ready",
        ocr_initialized=is_initialized,
        gpu_available=is_gpu,
        version=__version__
    )
