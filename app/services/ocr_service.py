"""OCR service using PaddleOCR with singleton pattern"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, Any, List
import numpy as np
from PIL import Image

from app.config import Settings, get_model_variant_config
from app.utils.exceptions import OCRInitializationError, OCRProcessingError

logger = logging.getLogger(__name__)

# Thread pool for running blocking OCR operations without blocking the event loop
# This allows health check endpoints to respond while OCR is processing
_ocr_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="ocr_worker")


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

                # Get model configuration for the specified variant
                model_config = get_model_variant_config(settings.model_variant)

                # Initialize PaddleOCR for PP-OCRv5 multilingual model
                # This single model handles Simplified Chinese, Traditional Chinese,
                # English, Japanese, and Pinyin automatically
                ocr_kwargs = {
                    "use_doc_orientation_classify": settings.enable_doc_orientation,
                    "use_doc_unwarping": settings.enable_doc_unwarping,
                    "use_textline_orientation": settings.enable_text_orientation,
                    "device": settings.device,
                    "enable_mkldnn": settings.enable_mkldnn,
                }

                # Apply model names from variant config (None means use PaddleOCR defaults)
                if model_config.detection_model:
                    ocr_kwargs["text_detection_model_name"] = model_config.detection_model
                if model_config.recognition_model:
                    ocr_kwargs["text_recognition_model_name"] = model_config.recognition_model

                self._ocr = PaddleOCR(**ocr_kwargs)

                self._initialized = True
                logger.info(
                    f"OCR service initialized successfully "
                    f"(Device: {settings.device}, Variant: {settings.model_variant})"
                )

            except Exception as e:
                logger.error(f"Failed to initialize OCR service: {str(e)}")
                raise OCRInitializationError(f"OCR initialization failed: {str(e)}")

    def is_initialized(self) -> bool:
        """Check if OCR service is initialized"""
        return self._initialized

    def get_device(self) -> str:
        """Get the device being used"""
        return self._settings.device if self._settings else "cpu"

    async def process_image(
        self,
        image_input: Any,
    ) -> List[Dict[str, Any]]:
        """
        Process image and extract text with OCR

        Args:
            image_input: Image input (numpy array, PIL Image, or file path)

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

            # Run OCR inference in thread pool to avoid blocking the event loop
            # This allows health check endpoints to respond during OCR processing
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(_ocr_executor, self._ocr.predict, image_input)

            # Process results
            processed_results = []

            if result:
                for res in result:
                    # PaddleOCR 3.x result format:
                    # res['rec_texts'] - list of recognized text strings
                    # res['rec_scores'] - list of confidence scores
                    # res['dt_polys'] - list of detection polygons
                    texts = res.get('rec_texts', [])
                    scores = res.get('rec_scores', [])
                    boxes = res.get('dt_polys', [])

                    for text, confidence, box in zip(texts, scores, boxes):
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
                # Shutdown thread pool executor
                _ocr_executor.shutdown(wait=False)
                logger.info("OCR service shut down successfully")


# Global OCR service instance
ocr_service = OCRService()
