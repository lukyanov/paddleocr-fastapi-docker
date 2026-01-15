"""Pytest configuration and fixtures"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def test_settings():
    """Test settings fixture"""
    return settings
