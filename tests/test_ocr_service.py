"""Unit tests for OCR service"""

import pytest
from app.services.ocr_service import OCRService


class TestOCRService:
    """Test OCR service functionality"""

    def test_singleton_pattern(self):
        """Test that OCRService follows singleton pattern"""
        service1 = OCRService()
        service2 = OCRService()
        assert service1 is service2

    def test_initial_state(self):
        """Test initial service state"""
        service = OCRService()
        # Before initialization, service should not be initialized
        # (unless it was initialized in the FastAPI lifespan)
        assert hasattr(service, '_initialized')

    # Note: Actual OCR processing tests require PaddleOCR models
    # Add integration tests when models are available
