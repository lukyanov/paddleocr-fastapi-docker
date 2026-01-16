#!/usr/bin/env python3
"""
Pre-download PaddleOCR models during Docker build/startup

This script initializes PaddleOCR to trigger model downloads,
avoiding delays on first API request.
"""

import os
import sys
import logging

# Note: PaddleOCR 3.x downloads models to ~/.paddlex/official_models by default
# During Docker build (as root), this is /root/.paddlex
# The Dockerfile handles moving models to the appuser directory after download

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def download_models():
    """
    Download PaddleOCR models during build.

    Uses MODEL_VARIANT from environment but enables all optional features
    to ensure all auxiliary models are downloaded regardless of runtime config.
    """
    device = os.getenv('DEVICE', 'cpu')
    variant = os.getenv('MODEL_VARIANT', 'server')

    try:
        from app.config import get_model_variant_config
        from paddleocr import PaddleOCR

        model_config = get_model_variant_config(variant)

        logger.info(f"Downloading models...")
        logger.info(f"  Device: {device}")
        logger.info(f"  Variant: {variant}")
        logger.info(f"  Detection: {model_config.detection_model or 'default'}")
        logger.info(f"  Recognition: {model_config.recognition_model or 'default'}")
        logger.info(f"  + All optional feature models (orientation, unwarping)")

        ocr_kwargs = {
            # Enable all features to download all auxiliary models
            # This ensures no runtime downloads regardless of configuration
            "use_doc_orientation_classify": True,
            "use_doc_unwarping": True,
            "use_textline_orientation": True,
            "device": device,
        }

        # Apply model names from variant config
        if model_config.detection_model:
            ocr_kwargs["text_detection_model_name"] = model_config.detection_model
        if model_config.recognition_model:
            ocr_kwargs["text_recognition_model_name"] = model_config.recognition_model

        # Initialize PaddleOCR - this triggers model download
        PaddleOCR(**ocr_kwargs)

        logger.info("All models downloaded and cached")
        return True

    except Exception as e:
        logger.error(f"Model download failed: {str(e)}")
        return False


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("PaddleOCR Model Download Script")
    logger.info("=" * 60)

    success = download_models()

    if success:
        logger.info("=" * 60)
        logger.info("Model download script completed successfully")
        sys.exit(0)
    else:
        logger.error("=" * 60)
        logger.error("Model download script failed")
        sys.exit(1)
