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


def download_models(device: str = 'cpu', variant: str = 'server'):
    """
    Initialize PaddleOCR to trigger model download

    Args:
        device: Device to use (cpu, gpu, cuda:0, etc.)
        variant: Model variant ('server' for higher accuracy, 'mobile' for smaller size)
    """
    try:
        logger.info(f"Starting model download (device={device}, variant={variant})")

        # Import model config from app (PYTHONPATH must include /app)
        from app.config import get_model_variant_config
        from paddleocr import PaddleOCR

        # Get model configuration for the specified variant
        model_config = get_model_variant_config(variant)

        # Build kwargs for PaddleOCR initialization
        ocr_kwargs = {
            "use_doc_orientation_classify": False,
            "use_doc_unwarping": False,
            "use_textline_orientation": False,
            "device": device,
        }

        # Apply model names from variant config (None means use PaddleOCR defaults)
        if model_config.detection_model:
            ocr_kwargs["text_detection_model_name"] = model_config.detection_model
        if model_config.recognition_model:
            ocr_kwargs["text_recognition_model_name"] = model_config.recognition_model

        logger.info(f"Using models: det={model_config.detection_model or 'default'}, "
                    f"rec={model_config.recognition_model or 'default'}")

        # Initialize PaddleOCR - this triggers model download
        ocr = PaddleOCR(**ocr_kwargs)

        logger.info("Model download completed successfully")
        logger.info("Models are cached and ready for use")

        return True

    except Exception as e:
        logger.error(f"Model download failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Get configuration from environment variables
    device = os.getenv('DEVICE', 'cpu')
    variant = os.getenv('MODEL_VARIANT', 'server')

    logger.info("=" * 60)
    logger.info("PaddleOCR Model Download Script")
    logger.info("=" * 60)
    logger.info(f"Device: {device}")
    logger.info(f"Model variant: {variant}")
    logger.info(f"Models will be downloaded to: ~/.paddlex/official_models")
    logger.info("=" * 60)

    success = download_models(device=device, variant=variant)

    if success:
        logger.info("Model download script completed successfully")
        sys.exit(0)
    else:
        logger.error("Model download script failed")
        sys.exit(1)
