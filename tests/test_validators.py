"""Unit tests for validators"""

import pytest
from app.utils.validators import (
    validate_file_size,
    validate_url_safety,
)
from app.utils.exceptions import ImageTooLargeError, ImageValidationError


class TestValidators:
    """Test validation functions"""

    def test_validate_file_size_valid(self):
        """Test file size validation with valid size"""
        # Should not raise exception
        validate_file_size(1000, 10000)

    def test_validate_file_size_too_large(self):
        """Test file size validation with too large file"""
        with pytest.raises(ImageTooLargeError):
            validate_file_size(10000, 1000)

    def test_validate_url_safety_valid_http(self):
        """Test URL validation with valid HTTP URL"""
        # Should not raise exception
        validate_url_safety("http://example.com/image.jpg")

    def test_validate_url_safety_valid_https(self):
        """Test URL validation with valid HTTPS URL"""
        # Should not raise exception
        validate_url_safety("https://example.com/image.jpg")

    def test_validate_url_safety_localhost(self):
        """Test URL validation rejects localhost"""
        with pytest.raises(ImageValidationError):
            validate_url_safety("http://localhost/image.jpg")

    def test_validate_url_safety_private_ip(self):
        """Test URL validation rejects private IPs"""
        with pytest.raises(ImageValidationError):
            validate_url_safety("http://192.168.1.1/image.jpg")

    def test_validate_url_safety_file_protocol(self):
        """Test URL validation rejects file:// protocol"""
        with pytest.raises(ImageValidationError):
            validate_url_safety("file:///etc/passwd")

    def test_validate_url_safety_invalid_scheme(self):
        """Test URL validation rejects invalid schemes"""
        with pytest.raises(ImageValidationError):
            validate_url_safety("ftp://example.com/image.jpg")
