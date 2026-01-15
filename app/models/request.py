"""Request data models"""

from pydantic import BaseModel, Field, HttpUrl, field_validator


class OCRUrlRequest(BaseModel):
    """Request model for URL-based OCR"""

    file_url: HttpUrl = Field(..., description="URL of file to process (image or PDF)")

    @field_validator('file_url')
    @classmethod
    def validate_url_scheme(cls, v):
        """Validate that URL uses HTTP or HTTPS scheme"""
        if v.scheme not in ['http', 'https']:
            raise ValueError('Only HTTP/HTTPS URLs are allowed')
        return v
