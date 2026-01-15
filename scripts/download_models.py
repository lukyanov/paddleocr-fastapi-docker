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


def download_models(lang: str = 'ch', use_gpu: bool = False):
    """
    Initialize PaddleOCR to trigger model download

    Args:
        lang: Language code (default 'ch' for PP-OCRv5 multilingual model)
        use_gpu: Whether to use GPU acceleration
    """
    try:
        logger.info(f"Starting model download (lang={lang}, use_gpu={use_gpu})")

        from paddleocr import PaddleOCR

        # Initialize PaddleOCR with lang='ch' for PP-OCRv5 multilingual model
        # This triggers download of detection, recognition, and classification models
        ocr = PaddleOCR(
            use_angle_cls=True,
            lang=lang,
            use_gpu=use_gpu,
            show_log=True  # Show download progress
        )

        logger.info("Model download completed successfully")
        logger.info("Models are cached and ready for use")

        return True

    except Exception as e:
        logger.error(f"Model download failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Get configuration from environment variables
    lang = os.getenv('OCR_LANG', 'ch')
    use_gpu = os.getenv('USE_GPU', 'false').lower() == 'true'

    logger.info("=" * 60)
    logger.info("PaddleOCR Model Download Script")
    logger.info("=" * 60)
    logger.info(f"Language: {lang}")
    logger.info(f"GPU: {use_gpu}")
    logger.info(f"Model cache: {os.getenv('PADDLEOCR_HOME', 'default')}")
    logger.info("=" * 60)

    success = download_models(lang=lang, use_gpu=use_gpu)

    if success:
        logger.info("Model download script completed successfully")
        sys.exit(0)
    else:
        logger.error("Model download script failed")
        sys.exit(1)
