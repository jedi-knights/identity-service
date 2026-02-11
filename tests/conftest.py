"""Pytest configuration and fixtures."""
import pytest
from uuid import uuid4


@pytest.fixture
def mock_user_id():
    """Fixture for a mock user ID."""
    return uuid4()


@pytest.fixture
def mock_client_id():
    """Fixture for a mock client ID."""
    return uuid4()


@pytest.fixture
def sample_user_data():
    """Fixture for sample user data."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword123",
    }


@pytest.fixture
def sample_client_data():
    """Fixture for sample client data."""
    return {
        "client_name": "Test Client",
        "redirect_uris": ["http://localhost:3000/callback"],
        "grant_types": ["password", "refresh_token"],
        "scopes": ["read", "write"],
    }
