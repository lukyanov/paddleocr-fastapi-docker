"""Image download and validation service"""

import logging
from io import BytesIO
from typing import Tuple
import aiohttp
from PIL import Image

from app.utils.exceptions import ImageDownloadError, ImageValidationError, ImageTooLargeError
from app.utils.validators import validate_url_safety, validate_content_type, validate_file_size

logger = logging.getLogger(__name__)


class ImageService:
    """Service for handling image downloads and validation"""

    @staticmethod
    async def download_from_url(
        url: str,
        timeout: int = 30,
        max_size: int = 10485760
    ) -> Tuple[bytes, str]:
        """
        Download image from URL with validation

        Args:
            url: Image URL to download
            timeout: Download timeout in seconds
            max_size: Maximum file size in bytes

        Returns:
            Tuple of (image_content, content_type)

        Raises:
            ImageDownloadError: If download fails
            ImageTooLargeError: If image exceeds size limit
            ImageValidationError: If URL is unsafe or content type is invalid
        """
        # Validate URL for SSRF protection
        validate_url_safety(url)

        try:
            logger.info(f"Downloading image from URL: {url}")

            timeout_obj = aiohttp.ClientTimeout(total=timeout)

            async with aiohttp.ClientSession(timeout=timeout_obj) as session:
                async with session.get(url) as response:
                    # Check response status
                    if response.status != 200:
                        raise ImageDownloadError(
                            f"Failed to download image: HTTP {response.status}"
                        )

                    # Validate content type
                    content_type = response.headers.get('Content-Type', '').lower()
                    validate_content_type(content_type)

                    # Check content length if available
                    content_length = response.headers.get('Content-Length')
                    if content_length:
                        validate_file_size(int(content_length), max_size)

                    # Download content with size limit
                    content = BytesIO()
                    total_size = 0

                    async for chunk in response.content.iter_chunked(8192):
                        total_size += len(chunk)
                        if total_size > max_size:
                            raise ImageTooLargeError(
                                f"Downloaded content exceeds maximum size of {max_size} bytes"
                            )
                        content.write(chunk)

                    image_content = content.getvalue()
                    logger.info(f"Successfully downloaded image: {total_size} bytes")

                    return image_content, content_type

        except (ImageDownloadError, ImageTooLargeError, ImageValidationError):
            raise
        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error downloading image: {str(e)}")
            raise ImageDownloadError(f"Failed to download image: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error downloading image: {str(e)}")
            raise ImageDownloadError(f"Failed to download image: {str(e)}")

    @staticmethod
    def validate_and_load_image(image_content: bytes) -> Image.Image:
        """
        Validate and load image from bytes

        Args:
            image_content: Image content as bytes

        Returns:
            PIL Image object

        Raises:
            ImageValidationError: If image is invalid or corrupted
        """
        try:
            # Open and validate image
            image = Image.open(BytesIO(image_content))

            # Verify image by loading it
            image.verify()

            # Re-open image after verify (verify closes the file)
            image = Image.open(BytesIO(image_content))

            # Convert to RGB if needed (for consistency)
            if image.mode not in ['RGB', 'L']:  # L is grayscale
                image = image.convert('RGB')

            logger.info(f"Image validated: {image.format}, {image.size}, {image.mode}")
            return image

        except Exception as e:
            logger.error(f"Image validation failed: {str(e)}")
            raise ImageValidationError(f"Invalid or corrupted image: {str(e)}")

    @staticmethod
    def preprocess_image(image: Image.Image, max_dimension: int = 4096) -> Image.Image:
        """
        Preprocess image for OCR (resize if too large)

        Args:
            image: PIL Image object
            max_dimension: Maximum width or height in pixels

        Returns:
            Preprocessed PIL Image
        """
        width, height = image.size

        # Resize if image is too large to prevent memory issues
        if width > max_dimension or height > max_dimension:
            logger.info(f"Resizing large image from {width}x{height}")

            if width > height:
                new_width = max_dimension
                new_height = int(height * (max_dimension / width))
            else:
                new_height = max_dimension
                new_width = int(width * (max_dimension / height))

            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            logger.info(f"Image resized to {new_width}x{new_height}")

        return image


# Global image service instance
image_service = ImageService()
