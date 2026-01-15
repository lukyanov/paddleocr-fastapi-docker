"""Request data models"""

from pydantic import BaseModel, Field, HttpUrl, field_validator


class OCRUrlRequest(BaseModel):
    """Request model for URL-based OCR"""

    image_url: HttpUrl = Field(..., description="URL of image to process")

    @field_validator('image_url')
    @classmethod
    def validate_url_scheme(cls, v):
        """Validate that URL uses HTTP or HTTPS scheme"""
        if v.scheme not in ['http', 'https']:
            raise ValueError('Only HTTP/HTTPS URLs are allowed')
        return v
