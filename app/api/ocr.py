"""OCR processing endpoints"""

import time
import uuid
import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status

from app.config import settings
from app.models.request import OCRUrlRequest
from app.models.response import OCRResponse, OCRResult, TextBox, ErrorResponse, ErrorDetail
from app.services.ocr_service import ocr_service
from app.services.image_service import image_service
from app.utils.exceptions import (
    OCRException,
    ImageValidationError,
    ImageDownloadError,
    ImageTooLargeError,
    OCRProcessingError
)
from app.utils.validators import validate_file_size, validate_image_format

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ocr", tags=["OCR"])


@router.post(
    "/upload",
    response_model=OCRResponse,
    status_code=status.HTTP_200_OK,
    summary="OCR from uploaded image file",
    description="Process an uploaded image file with OCR (PP-OCRv5 multilingual)"
)
async def ocr_upload(
    file: UploadFile = File(..., description="Image file to process"),
    det_thresh: Optional[float] = Form(default=0.3, description="Detection threshold (0.0-1.0)"),
    rec_thresh: Optional[float] = Form(default=0.7, description="Recognition threshold (0.0-1.0)")
) -> OCRResponse:
    """
    Process uploaded image file with OCR

    PP-OCRv5 automatically detects language (Simplified Chinese, Traditional Chinese,
    English, Japanese, Pinyin) without explicit specification.

    Args:
        file: Uploaded image file
        det_thresh: Text detection threshold
        rec_thresh: Text recognition threshold

    Returns:
        OCRResponse with detected text and bounding boxes

    Raises:
        HTTPException: If processing fails
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()

    try:
        logger.info(f"[{request_id}] Processing upload: {file.filename}")

        # Read file content
        file_content = await file.read()

        # Validate file size
        validate_file_size(len(file_content), settings.max_file_size)

        # Validate image format
        validate_image_format(file_content)

        # Load and preprocess image
        image = image_service.validate_and_load_image(file_content)
        image = image_service.preprocess_image(image)

        # Process with OCR
        detections = await ocr_service.process_image(
            image,
            det_thresh=det_thresh,
            rec_thresh=rec_thresh
        )

        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000

        # Build response
        text_boxes = [TextBox(**detection) for detection in detections]

        result = OCRResult(
            results=text_boxes,
            processing_time_ms=processing_time_ms,
            num_detections=len(text_boxes)
        )

        logger.info(
            f"[{request_id}] Successfully processed upload: "
            f"{len(text_boxes)} detections in {processing_time_ms:.2f}ms"
        )

        return OCRResponse(
            success=True,
            message="OCR processing completed successfully",
            data=result,
            request_id=request_id
        )

    except ImageTooLargeError as e:
        logger.warning(f"[{request_id}] File too large: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "success": False,
                "message": "Image file too large",
                "error": {"code": "IMAGE_TOO_LARGE", "detail": str(e)},
                "request_id": request_id
            }
        )

    except ImageValidationError as e:
        logger.warning(f"[{request_id}] Invalid image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "message": "Invalid image file",
                "error": {"code": "INVALID_IMAGE", "detail": str(e)},
                "request_id": request_id
            }
        )

    except OCRProcessingError as e:
        logger.error(f"[{request_id}] OCR processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "OCR processing failed",
                "error": {"code": "OCR_PROCESSING_ERROR", "detail": str(e)},
                "request_id": request_id
            }
        )

    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Internal server error",
                "error": {"code": "INTERNAL_ERROR", "detail": str(e)},
                "request_id": request_id
            }
        )


@router.post(
    "/url",
    response_model=OCRResponse,
    status_code=status.HTTP_200_OK,
    summary="OCR from image URL",
    description="Download and process image from URL with OCR (PP-OCRv5 multilingual)"
)
async def ocr_url(request: OCRUrlRequest) -> OCRResponse:
    """
    Download image from URL and process with OCR

    PP-OCRv5 automatically detects language (Simplified Chinese, Traditional Chinese,
    English, Japanese, Pinyin) without explicit specification.

    Args:
        request: OCR URL request with image URL and parameters

    Returns:
        OCRResponse with detected text and bounding boxes

    Raises:
        HTTPException: If processing fails
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()

    try:
        logger.info(f"[{request_id}] Processing URL: {request.image_url}")

        # Download image from URL
        image_content, content_type = await image_service.download_from_url(
            str(request.image_url),
            timeout=settings.image_download_timeout,
            max_size=settings.max_file_size
        )

        # Load and preprocess image
        image = image_service.validate_and_load_image(image_content)
        image = image_service.preprocess_image(image)

        # Process with OCR
        detections = await ocr_service.process_image(
            image,
            det_thresh=request.det_thresh,
            rec_thresh=request.rec_thresh
        )

        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000

        # Build response
        text_boxes = [TextBox(**detection) for detection in detections]

        result = OCRResult(
            results=text_boxes,
            processing_time_ms=processing_time_ms,
            num_detections=len(text_boxes)
        )

        logger.info(
            f"[{request_id}] Successfully processed URL: "
            f"{len(text_boxes)} detections in {processing_time_ms:.2f}ms"
        )

        return OCRResponse(
            success=True,
            message="OCR processing completed successfully",
            data=result,
            request_id=request_id
        )

    except ImageDownloadError as e:
        logger.warning(f"[{request_id}] Download failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "message": "Failed to download image",
                "error": {"code": "DOWNLOAD_ERROR", "detail": str(e)},
                "request_id": request_id
            }
        )

    except ImageTooLargeError as e:
        logger.warning(f"[{request_id}] Image too large: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "success": False,
                "message": "Image file too large",
                "error": {"code": "IMAGE_TOO_LARGE", "detail": str(e)},
                "request_id": request_id
            }
        )

    except ImageValidationError as e:
        logger.warning(f"[{request_id}] Invalid image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "message": "Invalid image file",
                "error": {"code": "INVALID_IMAGE", "detail": str(e)},
                "request_id": request_id
            }
        )

    except OCRProcessingError as e:
        logger.error(f"[{request_id}] OCR processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "OCR processing failed",
                "error": {"code": "OCR_PROCESSING_ERROR", "detail": str(e)},
                "request_id": request_id
            }
        )

    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Internal server error",
                "error": {"code": "INTERNAL_ERROR", "detail": str(e)},
                "request_id": request_id
            }
        )
