"""Unit tests for ClientService."""
import pytest
from uuid import uuid4

from identity_service.application.use_cases.client_service import ClientService
from identity_service.domain.entities import Client


class TestClientService:
    """Tests for ClientService."""

    @pytest.fixture
    def mock_client_repository(self, mocker):
        """Mock client repository."""
        return mocker.Mock()

    @pytest.fixture
    def client_service(self, mock_client_repository):
        """Client service instance."""
        return ClientService(mock_client_repository)

    @pytest.mark.parametrize(
        "client_name,redirect_uris,grant_types,scopes,is_confidential",
        [
            (
                "Client 1",
                ["http://localhost:3000/callback"],
                ["password"],
                ["read"],
                True,
            ),
            (
                "Client 2",
                ["http://example.com/auth"],
                ["password", "refresh_token"],
                ["read", "write"],
                True,
            ),
            (
                "Public Client",
                ["http://public.com/callback"],
                ["authorization_code"],
                [],
                False,
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_create_client_success(
        self,
        client_service,
        mock_client_repository,
        client_name,
        redirect_uris,
        grant_types,
        scopes,
        is_confidential,
    ):
        """Test successful client creation."""
        # Setup
        client_id = uuid4()
        mock_client_repository.create.return_value = Client(
            client_name=client_name,
            client_secret_hash="hashed",
            redirect_uris=redirect_uris,
            grant_types=grant_types,
            client_id=client_id,
            scopes=scopes,
            is_confidential=is_confidential,
        )

        # Execute
        client, plain_secret = await client_service.create_client(
            client_name=client_name,
            redirect_uris=redirect_uris,
            grant_types=grant_types,
            scopes=scopes,
            is_confidential=is_confidential,
        )

        # Assert
        assert client.client_name == client_name
        assert client.redirect_uris == redirect_uris
        assert client.grant_types == grant_types
        assert client.scopes == scopes
        assert client.is_confidential == is_confidential
        assert plain_secret is not None
        assert len(plain_secret) > 0
        mock_client_repository.create.assert_called_once()

    @pytest.mark.parametrize(
        "client_id,client_secret,client_exists,secret_valid,client_active,should_authenticate",
        [
            (uuid4(), "valid_secret", True, True, True, True),
            (uuid4(), "invalid_secret", True, False, True, False),
            (uuid4(), "valid_secret", True, True, False, False),
            (uuid4(), "valid_secret", False, False, False, False),
        ],
    )
    @pytest.mark.asyncio
    async def test_authenticate_client(
        self,
        client_service,
        mock_client_repository,
        mocker,
        client_id,
        client_secret,
        client_exists,
        secret_valid,
        client_active,
        should_authenticate,
    ):
        """Test client authentication with various scenarios."""
        # Setup
        if client_exists:
            client = Client(
                client_name="Test Client",
                client_secret_hash="hashed_secret",
                redirect_uris=["http://localhost:3000/callback"],
                grant_types=["password"],
                client_id=client_id,
                is_active=client_active,
            )
            mock_client_repository.get_by_id.return_value = client
        else:
            mock_client_repository.get_by_id.return_value = None

        mocker.patch.object(client_service, "verify_secret", return_value=secret_valid)

        # Execute
        result = await client_service.authenticate_client(client_id, client_secret)

        # Assert
        if should_authenticate:
            assert result is not None
            assert result.id == client_id
        else:
            assert result is None

    @pytest.mark.parametrize(
        "grant_type,redirect_uri,client_active,grant_valid,uri_valid,should_validate",
        [
            ("password", "http://localhost:3000/callback", True, True, True, True),
            ("password", "http://invalid.com/callback", True, True, False, False),
            ("invalid_grant", "http://localhost:3000/callback", True, False, True, False),
            ("password", "http://localhost:3000/callback", False, True, True, False),
        ],
    )
    @pytest.mark.asyncio
    async def test_validate_client_grant(
        self,
        client_service,
        mock_client_repository,
        grant_type,
        redirect_uri,
        client_active,
        grant_valid,
        uri_valid,
        should_validate,
    ):
        """Test client grant validation with various scenarios."""
        # Setup
        client_id = uuid4()
        grant_types = ["password"] if grant_valid else ["refresh_token"]
        redirect_uris = ["http://localhost:3000/callback"] if uri_valid else ["http://other.com/callback"]

        client = Client(
            client_name="Test Client",
            client_secret_hash="hashed",
            redirect_uris=redirect_uris,
            grant_types=grant_types,
            client_id=client_id,
            is_active=client_active,
        )
        mock_client_repository.get_by_id.return_value = client

        # Execute
        result = await client_service.validate_client_grant(client_id, grant_type, redirect_uri)

        # Assert
        assert result == should_validate

    @pytest.mark.asyncio
    async def test_deactivate_client(self, client_service, mock_client_repository):
        """Test client deactivation."""
        # Setup
        client_id = uuid4()
        client = Client(
            client_name="Test Client",
            client_secret_hash="hashed",
            redirect_uris=["http://localhost:3000/callback"],
            grant_types=["password"],
            client_id=client_id,
            is_active=True,
        )
        mock_client_repository.get_by_id.return_value = client
        mock_client_repository.update.return_value = client

        # Execute
        result = await client_service.deactivate_client(client_id)

        # Assert
        assert result.is_active is False
        mock_client_repository.update.assert_called_once()
