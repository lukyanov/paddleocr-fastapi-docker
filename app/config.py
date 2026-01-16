"""Application configuration using Pydantic Settings"""

import os
from typing import List, Dict, Optional
from dataclasses import dataclass
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


@dataclass(frozen=True)
class ModelVariantConfig:
    """Configuration for a PaddleOCR model variant"""
    detection_model: Optional[str] = None  # None means use PaddleOCR default
    recognition_model: Optional[str] = None


# Model variant configurations
# Add new variants here - they'll be available in both build and runtime
MODEL_VARIANTS: Dict[str, ModelVariantConfig] = {
    "server": ModelVariantConfig(
        # Server models (default) - higher accuracy, larger size
        detection_model=None,  # Uses PaddleOCR default (PP-OCRv5_server_det)
        recognition_model=None,  # Uses PaddleOCR default (PP-OCRv5_server_rec)
    ),
    "mobile": ModelVariantConfig(
        # Mobile models - smaller and faster, slightly lower accuracy
        detection_model="PP-OCRv5_mobile_det",
        recognition_model="PP-OCRv5_mobile_rec",
    ),
}


def get_model_variant_config(variant: str) -> ModelVariantConfig:
    """Get model configuration for a variant, with fallback to server"""
    return MODEL_VARIANTS.get(variant, MODEL_VARIANTS["server"])


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
    # PP-OCRv5 automatically handles multilingual text
    # (Simplified Chinese, Traditional Chinese, English, Japanese, Pinyin)
    device: str = Field(default="cpu", description="Device to use for OCR (cpu, gpu, or specific device like cuda:0)")
    model_variant: str = Field(default="server", description="Model variant: 'server' for higher accuracy, 'mobile' for smaller/faster")
    enable_doc_orientation: bool = Field(default=False, description="Enable document orientation detection")
    enable_doc_unwarping: bool = Field(default=False, description="Enable document unwarping")
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
    port: int = Field(default=8080, description="Server port")
    workers: int = Field(default=1, description="Number of worker processes")


# Global settings instance
settings = Settings()
