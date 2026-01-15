"""Application configuration using Pydantic Settings"""

import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = Field(default="PaddleOCR FastAPI Service", description="Application name")
    debug: bool = Field(default=False, description="Debug mode")
    version: str = Field(default="1.0.0", description="Application version")

    # OCR Configuration
    # PP-OCRv5 uses lang='ch' which automatically handles multilingual text
    # (Simplified Chinese, Traditional Chinese, English, Japanese, Pinyin)
    ocr_lang: str = Field(default="ch", description="OCR language (ch enables PP-OCRv5 multilingual model)")
    use_gpu: bool = Field(default=False, description="Enable GPU acceleration")
    ocr_detection_threshold: float = Field(default=0.3, ge=0.0, le=1.0, description="Text detection threshold")
    ocr_recognition_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Text recognition threshold")
    enable_doc_orientation: bool = Field(default=False, description="Enable document orientation detection")
    enable_text_orientation: bool = Field(default=True, description="Enable text orientation classification")

    # File Upload Configuration
    max_file_size: int = Field(default=10485760, description="Maximum file size in bytes (10MB)")
    allowed_image_types: List[str] = Field(
        default=["image/jpeg", "image/png", "image/bmp", "image/webp"],
        description="Allowed image MIME types"
    )
    allowed_extensions: List[str] = Field(
        default=["jpg", "jpeg", "png", "bmp", "webp"],
        description="Allowed file extensions"
    )

    # Network Configuration
    image_download_timeout: int = Field(default=30, description="Timeout for image downloads in seconds")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    workers: int = Field(default=1, description="Number of worker processes")


# Global settings instance
settings = Settings()
