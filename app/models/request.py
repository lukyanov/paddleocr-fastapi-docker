"""Request data models"""

from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator


class OCRUploadRequest(BaseModel):
    """Request model for image upload OCR (form data)"""

    det_thresh: Optional[float] = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Text detection threshold"
    )
    rec_thresh: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Text recognition threshold"
    )


class OCRUrlRequest(BaseModel):
    """Request model for URL-based OCR"""

    image_url: HttpUrl = Field(..., description="URL of image to process")
    det_thresh: Optional[float] = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Text detection threshold"
    )
    rec_thresh: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Text recognition threshold"
    )

    @field_validator('image_url')
    @classmethod
    def validate_url_scheme(cls, v):
        """Validate that URL uses HTTP or HTTPS scheme"""
        if v.scheme not in ['http', 'https']:
            raise ValueError('Only HTTP/HTTPS URLs are allowed')
        return v
