"""Input validation utilities"""

import re
from typing import BinaryIO
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO

from app.utils.exceptions import ImageValidationError, ImageTooLargeError


ALLOWED_MIME_TYPES = [
    'image/jpeg',
    'image/png',
    'image/bmp',
    'image/webp'
]

# Private IP address ranges for SSRF protection
PRIVATE_IP_PATTERNS = [
    r'^127\.',  # Loopback
    r'^10\.',  # Private Class A
    r'^172\.(1[6-9]|2[0-9]|3[0-1])\.',  # Private Class B
    r'^192\.168\.',  # Private Class C
    r'^169\.254\.',  # Link-local
    r'^0\.',  # Current network
    r'^224\.',  # Multicast
    r'^240\.',  # Reserved
]


def validate_file_size(file_size: int, max_size: int) -> None:
    """
    Validate file size is within limits

    Args:
        file_size: Size of file in bytes
        max_size: Maximum allowed size in bytes

    Raises:
        ImageTooLargeError: If file size exceeds limit
    """
    if file_size > max_size:
        raise ImageTooLargeError(
            f"File size {file_size} bytes exceeds maximum allowed size {max_size} bytes"
        )


def validate_image_format(file_content: bytes) -> str:
    """
    Validate image format using PIL

    Args:
        file_content: Image file content as bytes

    Returns:
        Image format (e.g., 'JPEG', 'PNG')

    Raises:
        ImageValidationError: If image format is invalid or unsupported
    """
    try:
        image = Image.open(BytesIO(file_content))
        image_format = image.format

        if not image_format:
            raise ImageValidationError("Unable to determine image format")

        # Map PIL format to MIME type
        format_to_mime = {
            'JPEG': 'image/jpeg',
            'PNG': 'image/png',
            'BMP': 'image/bmp',
            'WEBP': 'image/webp'
        }

        mime_type = format_to_mime.get(image_format.upper())
        if not mime_type or mime_type not in ALLOWED_MIME_TYPES:
            raise ImageValidationError(
                f"Unsupported image format: {image_format}. "
                f"Allowed formats: JPEG, PNG, BMP, WEBP"
            )

        return image_format

    except ImageValidationError:
        raise
    except Exception as e:
        raise ImageValidationError(f"Invalid or corrupted image file: {str(e)}")


def validate_url_safety(url: str) -> None:
    """
    Validate URL for SSRF protection

    Args:
        url: URL to validate

    Raises:
        ImageValidationError: If URL is potentially unsafe
    """
    parsed = urlparse(url)

    # Check scheme
    if parsed.scheme not in ['http', 'https']:
        raise ImageValidationError(f"Invalid URL scheme: {parsed.scheme}. Only HTTP/HTTPS allowed")

    # Check hostname exists
    if not parsed.hostname:
        raise ImageValidationError("Invalid URL: missing hostname")

    # Check for localhost
    if parsed.hostname.lower() in ['localhost', '127.0.0.1', '::1']:
        raise ImageValidationError("Access to localhost is not allowed")

    # Check for private IP addresses
    for pattern in PRIVATE_IP_PATTERNS:
        if re.match(pattern, parsed.hostname):
            raise ImageValidationError("Access to private IP addresses is not allowed")

    # Check for file:// protocol bypass attempts
    if 'file' in parsed.scheme.lower():
        raise ImageValidationError("File protocol is not allowed")


def validate_content_type(content_type: str) -> None:
    """
    Validate HTTP content type header

    Args:
        content_type: Content-Type header value

    Raises:
        ImageValidationError: If content type is not an allowed image type
    """
    # Extract the MIME type (ignore parameters like charset)
    mime_type = content_type.split(';')[0].strip().lower()

    if mime_type not in ALLOWED_MIME_TYPES:
        raise ImageValidationError(
            f"Invalid content type: {mime_type}. "
            f"Allowed types: {', '.join(ALLOWED_MIME_TYPES)}"
        )
