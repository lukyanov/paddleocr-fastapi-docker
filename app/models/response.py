"""Response data models"""

from typing import List, Optional
from pydantic import BaseModel, Field


class TextBox(BaseModel):
    """Individual text detection result"""

    text: str = Field(..., description="Detected text content")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Recognition confidence score")
    box: List[List[float]] = Field(..., description="4-point polygon bounding box [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]")


class OCRResult(BaseModel):
    """Complete OCR processing result"""

    text: str = Field(..., description="All detected text concatenated with newlines")
    text_boxes: List[TextBox] = Field(default_factory=list, description="List of detected text boxes")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    num_detections: int = Field(..., description="Number of text detections")


class OCRResponse(BaseModel):
    """Success response wrapper"""

    success: bool = Field(default=True, description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[OCRResult] = Field(None, description="OCR result data")
    request_id: str = Field(..., description="Unique request identifier")


class ErrorDetail(BaseModel):
    """Error details"""

    code: str = Field(..., description="Error code")
    detail: str = Field(..., description="Detailed error message")


class ErrorResponse(BaseModel):
    """Error response wrapper"""

    success: bool = Field(default=False, description="Operation success status")
    message: str = Field(..., description="Error message")
    error: ErrorDetail = Field(..., description="Error details")
    request_id: str = Field(..., description="Unique request identifier")


class HealthResponse(BaseModel):
    """Health check response"""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")


class ReadinessResponse(BaseModel):
    """Readiness check response"""

    status: str = Field(..., description="Service status")
    ocr_initialized: bool = Field(..., description="OCR engine initialization status")
    gpu_available: bool = Field(..., description="GPU availability status")
    version: str = Field(..., description="Application version")
