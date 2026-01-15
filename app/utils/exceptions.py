"""Custom exception classes"""


class OCRException(Exception):
    """Base exception for OCR-related errors"""
    pass


class ImageValidationError(OCRException):
    """Raised when image format is invalid or corrupted"""
    pass


class ImageDownloadError(OCRException):
    """Raised when image download from URL fails"""
    pass


class ImageTooLargeError(OCRException):
    """Raised when image exceeds size limit"""
    pass


class OCRProcessingError(OCRException):
    """Raised when OCR processing fails"""
    pass


class OCRInitializationError(OCRException):
    """Raised when OCR engine fails to initialize"""
    pass
