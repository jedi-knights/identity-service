"""Unit tests for UserService."""
import pytest
from uuid import uuid4

from identity_service.application.use_cases.user_service import UserService
from identity_service.domain.entities import User


class TestUserService:
    """Tests for UserService."""

    @pytest.fixture
    def mock_user_repository(self, mocker):
        """Mock user repository."""
        mock = mocker.Mock()
        # Make async methods return coroutines
        mock.get_by_username = mocker.AsyncMock(return_value=None)
        mock.get_by_email = mocker.AsyncMock(return_value=None)
        mock.create = mocker.AsyncMock()
        mock.get_by_id = mocker.AsyncMock()
        mock.update = mocker.AsyncMock()
        return mock

    @pytest.fixture
    def user_service(self, mock_user_repository, mocker):
        """User service instance."""
        service = UserService(mock_user_repository)
        # Mock password hashing to avoid bcrypt issues in tests
        mocker.patch.object(service, "hash_password", return_value="hashed_password")
        mocker.patch.object(service, "verify_password", return_value=True)
        return service

    @pytest.mark.parametrize(
        "username,email,password",
        [
            ("user1", "user1@example.com", "password123"),
            ("user2", "user2@example.com", "securepass456"),
            ("admin", "admin@example.com", "adminpass789"),
        ],
    )
    @pytest.mark.asyncio
    async def test_create_user_success(
        self, user_service, mock_user_repository, username, email, password
    ):
        """Test successful user creation."""
        # Setup
        mock_user_repository.get_by_username.return_value = None
        mock_user_repository.get_by_email.return_value = None
        mock_user_repository.create.return_value = User(
            username=username,
            email=email,
            hashed_password="hashed",
            user_id=uuid4(),
        )

        # Execute
        user = await user_service.create_user(username, email, password)

        # Assert
        assert user.username == username
        assert user.email == email
        mock_user_repository.create.assert_called_once()

    @pytest.mark.parametrize(
        "existing_field,error_message",
        [
            ("username", "Username 'testuser' already exists"),
            ("email", "Email 'test@example.com' already exists"),
        ],
    )
    @pytest.mark.asyncio
    async def test_create_user_duplicate(
        self, user_service, mock_user_repository, existing_field, error_message
    ):
        """Test user creation with duplicate username or email."""
        # Setup
        existing_user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed",
            user_id=uuid4(),
        )

        if existing_field == "username":
            mock_user_repository.get_by_username.return_value = existing_user
            mock_user_repository.get_by_email.return_value = None
        else:
            mock_user_repository.get_by_username.return_value = None
            mock_user_repository.get_by_email.return_value = existing_user

        # Execute & Assert
        with pytest.raises(ValueError, match=error_message):
            await user_service.create_user("testuser", "test@example.com", "password")

    @pytest.mark.parametrize(
        "username,password,user_exists,password_valid,user_active,should_authenticate",
        [
            ("user1", "password", True, True, True, True),
            ("user2", "password", True, False, True, False),
            ("user3", "password", True, True, False, False),
            ("user4", "password", False, False, False, False),
        ],
    )
    @pytest.mark.asyncio
    async def test_authenticate_user(
        self,
        user_service,
        mock_user_repository,
        mocker,
        username,
        password,
        user_exists,
        password_valid,
        user_active,
        should_authenticate,
    ):
        """Test user authentication with various scenarios."""
        # Setup
        if user_exists:
            user = User(
                username=username,
                email=f"{username}@example.com",
                hashed_password="hashed_password",
                user_id=uuid4(),
                is_active=user_active,
            )
            mock_user_repository.get_by_username.return_value = user
        else:
            mock_user_repository.get_by_username.return_value = None

        mocker.patch.object(user_service, "verify_password", return_value=password_valid)

        # Execute
        result = await user_service.authenticate_user(username, password)

        # Assert
        if should_authenticate:
            assert result is not None
            assert result.username == username
        else:
            assert result is None

    @pytest.mark.asyncio
    async def test_deactivate_user(self, user_service, mock_user_repository):
        """Test user deactivation."""
        # Setup
        user_id = uuid4()
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed",
            user_id=user_id,
            is_active=True,
        )
        mock_user_repository.get_by_id.return_value = user
        mock_user_repository.update.return_value = user

        # Execute
        result = await user_service.deactivate_user(user_id)

        # Assert
        assert result.is_active is False
        mock_user_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_activate_user(self, user_service, mock_user_repository):
        """Test user activation."""
        # Setup
        user_id = uuid4()
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed",
            user_id=user_id,
            is_active=False,
        )
        mock_user_repository.get_by_id.return_value = user
        mock_user_repository.update.return_value = user

        # Execute
        result = await user_service.activate_user(user_id)

        # Assert
        assert result.is_active is True
        mock_user_repository.update.assert_called_once()
