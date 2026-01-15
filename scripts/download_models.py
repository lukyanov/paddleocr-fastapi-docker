#!/usr/bin/env python3
"""
Pre-download PaddleOCR models during Docker build/startup

This script initializes PaddleOCR to trigger model downloads,
avoiding delays on first API request.
"""

import os
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def download_models(device: str = 'cpu'):
    """
    Initialize PaddleOCR to trigger model download

    Args:
        device: Device to use (cpu, gpu, cuda:0, etc.)
    """
    try:
        logger.info(f"Starting model download (device={device})")

        from paddleocr import PaddleOCR

        # Initialize PaddleOCR for PP-OCRv5 multilingual model
        # This triggers download of detection, recognition, and classification models
        ocr = PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            device=device
        )

        logger.info("Model download completed successfully")
        logger.info("Models are cached and ready for use")

        return True

    except Exception as e:
        logger.error(f"Model download failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Get configuration from environment variables
    device = os.getenv('DEVICE', 'cpu')

    logger.info("=" * 60)
    logger.info("PaddleOCR Model Download Script")
    logger.info("=" * 60)
    logger.info(f"Device: {device}")
    logger.info(f"Model cache: {os.getenv('PADDLEOCR_HOME', 'default')}")
    logger.info("=" * 60)

    success = download_models(device=device)

    if success:
        logger.info("Model download script completed successfully")
        sys.exit(0)
    else:
        logger.error("Model download script failed")
        sys.exit(1)
