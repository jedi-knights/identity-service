"""Unit tests for domain entities."""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from identity_service.domain.entities import User, Client, Token


class TestUser:
    """Tests for User entity."""

    @pytest.mark.parametrize(
        "username,email,is_active,expected_active",
        [
            ("user1", "user1@example.com", True, True),
            ("user2", "user2@example.com", False, False),
            ("user3", "user3@example.com", True, True),
        ],
    )
    def test_user_creation(self, username, email, is_active, expected_active):
        """Test user entity creation with various states."""
        user = User(
            username=username,
            email=email,
            hashed_password="hashed_pwd",
            is_active=is_active,
        )

        assert user.username == username
        assert user.email == email
        assert user.is_active == expected_active
        assert user.id is not None

    def test_user_deactivate(self):
        """Test user deactivation."""
        user = User(username="test", email="test@example.com", hashed_password="pwd")
        assert user.is_active is True

        user.deactivate()
        assert user.is_active is False

    def test_user_activate(self):
        """Test user activation."""
        user = User(
            username="test", email="test@example.com", hashed_password="pwd", is_active=False
        )
        assert user.is_active is False

        user.activate()
        assert user.is_active is True

    def test_user_update_password(self):
        """Test password update."""
        user = User(username="test", email="test@example.com", hashed_password="old_pwd")
        old_password = user.hashed_password
        old_updated_at = user.updated_at

        user.update_password("new_pwd")

        assert user.hashed_password == "new_pwd"
        assert user.hashed_password != old_password


class TestClient:
    """Tests for Client entity."""

    @pytest.mark.parametrize(
        "redirect_uri,should_validate",
        [
            ("http://localhost:3000/callback", True),
            ("http://example.com/callback", False),
            ("http://localhost:8080/auth", False),
        ],
    )
    def test_validate_redirect_uri(self, redirect_uri, should_validate):
        """Test redirect URI validation."""
        client = Client(
            client_name="Test Client",
            client_secret_hash="hashed",
            redirect_uris=["http://localhost:3000/callback"],
            grant_types=["password"],
        )

        assert client.validate_redirect_uri(redirect_uri) == should_validate

    @pytest.mark.parametrize(
        "grant_type,should_validate",
        [
            ("password", True),
            ("refresh_token", True),
            ("authorization_code", False),
            ("client_credentials", False),
        ],
    )
    def test_validate_grant_type(self, grant_type, should_validate):
        """Test grant type validation."""
        client = Client(
            client_name="Test Client",
            client_secret_hash="hashed",
            redirect_uris=["http://localhost:3000/callback"],
            grant_types=["password", "refresh_token"],
        )

        assert client.validate_grant_type(grant_type) == should_validate

    def test_client_deactivate(self):
        """Test client deactivation."""
        client = Client(
            client_name="Test Client",
            client_secret_hash="hashed",
            redirect_uris=["http://localhost:3000/callback"],
            grant_types=["password"],
        )
        assert client.is_active is True

        client.deactivate()
        assert client.is_active is False


class TestToken:
    """Tests for Token entity."""

    @pytest.mark.parametrize(
        "expires_delta,is_expired",
        [
            (timedelta(hours=1), False),
            (timedelta(minutes=30), False),
            (timedelta(hours=-1), True),
            (timedelta(days=-1), True),
        ],
    )
    def test_token_expiration(self, expires_delta, is_expired):
        """Test token expiration check."""
        token = Token(
            user_id=uuid4(),
            client_id=uuid4(),
            access_token="test_token",
            token_type="Bearer",
            expires_at=datetime.utcnow() + expires_delta,
            scopes=["read"],
        )

        assert token.is_expired() == is_expired

    def test_token_creation(self):
        """Test token entity creation."""
        user_id = uuid4()
        client_id = uuid4()
        expires_at = datetime.utcnow() + timedelta(hours=1)

        token = Token(
            user_id=user_id,
            client_id=client_id,
            access_token="access_token_value",
            token_type="Bearer",
            expires_at=expires_at,
            scopes=["read", "write"],
            refresh_token="refresh_token_value",
        )

        assert token.user_id == user_id
        assert token.client_id == client_id
        assert token.access_token == "access_token_value"
        assert token.token_type == "Bearer"
        assert token.expires_at == expires_at
        assert token.scopes == ["read", "write"]
        assert token.refresh_token == "refresh_token_value"
        assert token.id is not None
