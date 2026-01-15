"""OCR service using PaddleOCR with singleton pattern"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
import numpy as np
from PIL import Image

from app.config import Settings
from app.utils.exceptions import OCRInitializationError, OCRProcessingError

logger = logging.getLogger(__name__)


class OCRService:
    """Singleton service for PaddleOCR operations"""

    _instance: Optional['OCRService'] = None
    _lock = asyncio.Lock()
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize OCR service"""
        self._ocr = None
        self._settings: Optional[Settings] = None

    async def initialize(self, settings: Settings) -> None:
        """
        Initialize PaddleOCR engine with settings

        Args:
            settings: Application settings

        Raises:
            OCRInitializationError: If initialization fails
        """
        async with self._lock:
            if self._initialized:
                logger.info("OCR service already initialized")
                return

            try:
                logger.info("Initializing PaddleOCR engine...")
                self._settings = settings

                # Import PaddleOCR here to defer initialization
                from paddleocr import PaddleOCR

                # Initialize PaddleOCR with lang='ch' for PP-OCRv5 multilingual model
                # This single model handles Simplified Chinese, Traditional Chinese,
                # English, Japanese, and Pinyin automatically
                self._ocr = PaddleOCR(
                    use_angle_cls=settings.enable_text_orientation,
                    lang=settings.ocr_lang,  # 'ch' enables PP-OCRv5 multilingual model
                    use_gpu=settings.use_gpu,
                    det_db_thresh=settings.ocr_detection_threshold,
                    rec_batch_num=1,
                    show_log=False,  # Disable PaddleOCR's verbose logging
                    use_dilation=True,
                    det_db_box_thresh=0.5,
                )

                self._initialized = True
                logger.info(
                    f"OCR service initialized successfully "
                    f"(GPU: {settings.use_gpu}, Lang: {settings.ocr_lang})"
                )

            except Exception as e:
                logger.error(f"Failed to initialize OCR service: {str(e)}")
                raise OCRInitializationError(f"OCR initialization failed: {str(e)}")

    def is_initialized(self) -> bool:
        """Check if OCR service is initialized"""
        return self._initialized

    def is_gpu_available(self) -> bool:
        """Check if GPU is being used"""
        return self._settings.use_gpu if self._settings else False

    async def process_image(
        self,
        image_input: Any,
        det_thresh: Optional[float] = None,
        rec_thresh: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Process image and extract text with OCR

        Args:
            image_input: Image input (numpy array, PIL Image, or file path)
            det_thresh: Optional detection threshold override
            rec_thresh: Optional recognition threshold override

        Returns:
            List of detection results with text, confidence, and bounding boxes

        Raises:
            OCRProcessingError: If OCR processing fails
        """
        if not self._initialized:
            raise OCRProcessingError("OCR service not initialized")

        try:
            # Convert PIL Image to numpy array if needed
            if isinstance(image_input, Image.Image):
                image_input = np.array(image_input)

            # Run OCR inference
            # PP-OCRv5 with lang='ch' automatically detects language
            result = self._ocr.ocr(image_input, cls=self._settings.enable_text_orientation)

            # Process results
            processed_results = []

            if result and result[0]:
                for detection in result[0]:
                    # PaddleOCR result format: [box, (text, confidence)]
                    box = detection[0]
                    text, confidence = detection[1]

                    # Apply confidence thresholds if provided
                    if rec_thresh and confidence < rec_thresh:
                        continue

                    processed_results.append({
                        "text": text,
                        "confidence": float(confidence),
                        "box": [[float(x), float(y)] for x, y in box]
                    })

            logger.info(f"OCR processing completed: {len(processed_results)} detections")
            return processed_results

        except Exception as e:
            logger.error(f"OCR processing failed: {str(e)}")
            raise OCRProcessingError(f"OCR processing failed: {str(e)}")

    async def shutdown(self) -> None:
        """Cleanup OCR resources"""
        async with self._lock:
            if self._initialized:
                logger.info("Shutting down OCR service...")
                self._ocr = None
                self._initialized = False
                logger.info("OCR service shut down successfully")


# Global OCR service instance
ocr_service = OCRService()
