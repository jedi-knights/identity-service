"""Tests for OAuth2Service."""

import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from identity_service.application.use_cases.oauth2_service import OAuth2Service
from identity_service.domain.entities import User, Client, Token, AuthorizationCode


@pytest.mark.parametrize(
    "username,password,client_valid,user_valid,should_succeed",
    [
        ("testuser", "password123", True, True, True),
        ("testuser", "wrongpassword", True, False, False),
        ("testuser", "password123", False, True, False),
    ],
)
@pytest.mark.asyncio
async def test_password_grant(username, password, client_valid, user_valid, should_succeed, mocker):
    """Test password grant flow with various scenarios."""
    client_id = uuid4()
    user_id = uuid4()

    mock_user_service = mocker.Mock()
    mock_client_service = mocker.Mock()
    mock_token_service = mocker.Mock()
    mock_token_repo = mocker.Mock()
    mock_auth_code_repo = mocker.Mock()
    mock_cache = mocker.Mock()

    client = Client(
        client_name="Test Client",
        client_secret_hash="hashed",
        redirect_uris=["http://localhost"],
        grant_types=["password"],
        client_id=client_id,
        scopes=["read", "write"],
    )

    user = User(
        username=username,
        email="test@example.com",
        hashed_password="hashed",
        user_id=user_id,
    )

    mock_client_service.authenticate_client = mocker.AsyncMock(
        return_value=client if client_valid else None
    )
    mock_user_service.authenticate_user = mocker.AsyncMock(
        return_value=user if user_valid else None
    )

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
    mock_token_service.create_access_token.return_value = ("access_token", expires_at)
    mock_token_service.create_refresh_token.return_value = "refresh_token"

    token = Token(
        user_id=user_id,
        client_id=client_id,
        access_token="access_token",
        token_type="Bearer",
        expires_at=expires_at,
        scopes=["read", "write"],
        refresh_token="refresh_token",
    )
    mock_token_repo.create = mocker.AsyncMock(return_value=token)

    service = OAuth2Service(
        user_service=mock_user_service,
        client_service=mock_client_service,
        token_service=mock_token_service,
        token_repository=mock_token_repo,
        authorization_code_repository=mock_auth_code_repo,
        cache=mock_cache,
    )

    result = await service.password_grant(username, password, client_id, "secret", ["read"])

    if should_succeed:
        assert result is not None
        assert result.access_token == "access_token"
        assert result.refresh_token == "refresh_token"
    else:
        assert result is None


@pytest.mark.asyncio
async def test_authorization_code_grant_with_pkce(mocker):
    """Test authorization code grant with PKCE validation."""
    client_id = uuid4()
    user_id = uuid4()
    code = "test_code"
    code_verifier = "test_verifier_string_with_sufficient_length_for_security"

    import hashlib
    import base64

    code_challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
        .decode()
        .rstrip("=")
    )

    mock_user_service = mocker.Mock()
    mock_client_service = mocker.Mock()
    mock_token_service = mocker.Mock()
    mock_token_repo = mocker.Mock()
    mock_auth_code_repo = mocker.Mock()
    mock_cache = mocker.Mock()

    client = Client(
        client_name="Test Client",
        client_secret_hash="hashed",
        redirect_uris=["http://localhost/callback"],
        grant_types=["authorization_code"],
        client_id=client_id,
        scopes=["read"],
    )

    auth_code = AuthorizationCode(
        code=code,
        client_id=client_id,
        user_id=user_id,
        redirect_uri="http://localhost/callback",
        scopes=["read"],
        code_challenge=code_challenge,
        code_challenge_method="S256",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    mock_client_service.authenticate_client = mocker.AsyncMock(return_value=client)
    mock_auth_code_repo.get_by_code = mocker.AsyncMock(return_value=auth_code)
    mock_auth_code_repo.mark_as_used = mocker.AsyncMock(return_value=True)
    mock_auth_code_repo.delete = mocker.AsyncMock(return_value=True)

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
    mock_token_service.create_access_token.return_value = ("access_token", expires_at)
    mock_token_service.create_refresh_token.return_value = "refresh_token"

    token = Token(
        user_id=user_id,
        client_id=client_id,
        access_token="access_token",
        token_type="Bearer",
        expires_at=expires_at,
        scopes=["read"],
        refresh_token="refresh_token",
    )
    mock_token_repo.create = mocker.AsyncMock(return_value=token)

    service = OAuth2Service(
        user_service=mock_user_service,
        client_service=mock_client_service,
        token_service=mock_token_service,
        token_repository=mock_token_repo,
        authorization_code_repository=mock_auth_code_repo,
        cache=mock_cache,
    )

    result = await service.authorization_code_grant(
        code, client_id, "secret", "http://localhost/callback", code_verifier
    )

    assert result is not None
    assert result.access_token == "access_token"
    mock_auth_code_repo.mark_as_used.assert_called_once()
    mock_auth_code_repo.delete.assert_called_once()


@pytest.mark.asyncio
async def test_authorization_code_grant_invalid_pkce(mocker):
    """Test authorization code grant fails with invalid PKCE verifier."""
    client_id = uuid4()
    user_id = uuid4()
    code = "test_code"
    code_verifier = "wrong_verifier"

    mock_user_service = mocker.Mock()
    mock_client_service = mocker.Mock()
    mock_token_service = mocker.Mock()
    mock_token_repo = mocker.Mock()
    mock_auth_code_repo = mocker.Mock()
    mock_cache = mocker.Mock()

    client = Client(
        client_name="Test Client",
        client_secret_hash="hashed",
        redirect_uris=["http://localhost/callback"],
        grant_types=["authorization_code"],
        client_id=client_id,
        scopes=["read"],
    )

    auth_code = AuthorizationCode(
        code=code,
        client_id=client_id,
        user_id=user_id,
        redirect_uri="http://localhost/callback",
        scopes=["read"],
        code_challenge="valid_challenge",
        code_challenge_method="S256",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    mock_client_service.authenticate_client = mocker.AsyncMock(return_value=client)
    mock_auth_code_repo.get_by_code = mocker.AsyncMock(return_value=auth_code)

    service = OAuth2Service(
        user_service=mock_user_service,
        client_service=mock_client_service,
        token_service=mock_token_service,
        token_repository=mock_token_repo,
        authorization_code_repository=mock_auth_code_repo,
        cache=mock_cache,
    )

    result = await service.authorization_code_grant(
        code, client_id, "secret", "http://localhost/callback", code_verifier
    )

    assert result is None


@pytest.mark.asyncio
async def test_client_credentials_grant(mocker):
    """Test client credentials grant flow."""
    client_id = uuid4()

    mock_user_service = mocker.Mock()
    mock_client_service = mocker.Mock()
    mock_token_service = mocker.Mock()
    mock_token_repo = mocker.Mock()
    mock_auth_code_repo = mocker.Mock()
    mock_cache = mocker.Mock()

    client = Client(
        client_name="Test Client",
        client_secret_hash="hashed",
        redirect_uris=["http://localhost"],
        grant_types=["client_credentials"],
        client_id=client_id,
        scopes=["api:read", "api:write"],
    )

    mock_client_service.authenticate_client = mocker.AsyncMock(return_value=client)

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
    mock_token_service.create_access_token.return_value = ("access_token", expires_at)

    token = Token(
        user_id=client_id,
        client_id=client_id,
        access_token="access_token",
        token_type="Bearer",
        expires_at=expires_at,
        scopes=["api:read", "api:write"],
        refresh_token=None,
    )
    mock_token_repo.create = mocker.AsyncMock(return_value=token)

    service = OAuth2Service(
        user_service=mock_user_service,
        client_service=mock_client_service,
        token_service=mock_token_service,
        token_repository=mock_token_repo,
        authorization_code_repository=mock_auth_code_repo,
        cache=mock_cache,
    )

    result = await service.client_credentials_grant(client_id, "secret", ["api:read"])

    assert result is not None
    assert result.access_token == "access_token"
    assert result.refresh_token is None


@pytest.mark.asyncio
async def test_revoke_token_with_hint(mocker):
    """Test token revocation with token_type_hint."""
    client_id = uuid4()
    user_id = uuid4()

    mock_user_service = mocker.Mock()
    mock_client_service = mocker.Mock()
    mock_token_service = mocker.Mock()
    mock_token_repo = mocker.Mock()
    mock_auth_code_repo = mocker.Mock()
    mock_cache = mocker.Mock()

    token = Token(
        user_id=user_id,
        client_id=client_id,
        access_token="access_token",
        token_type="Bearer",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
        scopes=["read"],
        refresh_token="refresh_token",
    )

    mock_token_repo.get_by_refresh_token = mocker.AsyncMock(return_value=token)
    mock_token_repo.revoke = mocker.AsyncMock(return_value=True)
    mock_cache.delete = mocker.AsyncMock()

    service = OAuth2Service(
        user_service=mock_user_service,
        client_service=mock_client_service,
        token_service=mock_token_service,
        token_repository=mock_token_repo,
        authorization_code_repository=mock_auth_code_repo,
        cache=mock_cache,
    )

    result = await service.revoke_token("refresh_token", token_type_hint="refresh_token")

    assert result is True
    mock_token_repo.get_by_refresh_token.assert_called_once()
    mock_cache.delete.assert_called_once()
