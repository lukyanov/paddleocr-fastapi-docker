"""Integration tests for API endpoints"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_health_check(self, client: TestClient):
        """Test basic health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_readiness_check(self, client: TestClient):
        """Test readiness check endpoint"""
        response = client.get("/health/ready")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "ocr_initialized" in data
        assert "gpu_available" in data
        assert "version" in data


class TestRootEndpoint:
    """Test root endpoint"""

    def test_root(self, client: TestClient):
        """Test root endpoint returns service info"""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "ocr_engine" in data
        assert "multilingual_support" in data


class TestOCREndpoints:
    """Test OCR endpoints"""

    def test_upload_endpoint_exists(self, client: TestClient):
        """Test upload endpoint exists"""
        # Without file, should return 422 (validation error)
        response = client.post("/api/v1/ocr/upload")
        assert response.status_code in [422, 400]

    def test_url_endpoint_exists(self, client: TestClient):
        """Test URL endpoint exists"""
        # Without URL, should return 422 (validation error)
        response = client.post("/api/v1/ocr/url", json={})
        assert response.status_code in [422, 400]

    def test_url_endpoint_invalid_url(self, client: TestClient):
        """Test URL endpoint with invalid URL format"""
        response = client.post(
            "/api/v1/ocr/url",
            json={
                "image_url": "not-a-valid-url",
                "det_thresh": 0.3,
                "rec_thresh": 0.7
            }
        )
        assert response.status_code == 422  # Validation error

    # Note: Actual OCR testing requires PaddleOCR models to be initialized
    # and test images to be available. Add those tests when running in CI/CD
    # with proper model setup.
