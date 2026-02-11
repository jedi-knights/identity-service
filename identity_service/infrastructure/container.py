"""Dependency injection container."""
from authlib.jose import JsonWebKey
from dependency_injector import containers, providers
from redis.asyncio import Redis

from identity_service.adapters.jwt import JWTTokenService
from identity_service.adapters.postgres.repositories import (
    PostgresUserRepository,
    PostgresClientRepository,
    PostgresTokenRepository,
)
from identity_service.adapters.redis import RedisCache
from identity_service.application.use_cases.client_service import ClientService
from identity_service.application.use_cases.oauth2_service import OAuth2Service
from identity_service.application.use_cases.user_service import UserService
from identity_service.infrastructure.config.settings import Settings, get_settings
from identity_service.infrastructure.database.connection import DatabaseConnection


class Container(containers.DeclarativeContainer):
    """Application dependency injection container."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "identity_service.api.routes.users",
            "identity_service.api.routes.clients",
            "identity_service.api.routes.oauth2",
        ]
    )

    # Configuration
    config = providers.Singleton(get_settings)

    # Database
    database = providers.Singleton(DatabaseConnection, settings=config)

    # Redis
    redis_client = providers.Singleton(
        Redis.from_url, url=config.provided.redis_url, decode_responses=False
    )

    # Cache adapter
    cache = providers.Singleton(RedisCache, redis_client=redis_client)

    # Token service
    token_service = providers.Singleton(
        JWTTokenService,
        private_key=providers.Callable(
            lambda settings: JsonWebKey.import_key(settings.jwt_private_key)
            if settings.jwt_private_key
            else None,
            settings=config,
        ),
        public_key=providers.Callable(
            lambda settings: JsonWebKey.import_key(settings.jwt_public_key)
            if settings.jwt_public_key
            else None,
            settings=config,
        ),
        algorithm=config.provided.jwt_algorithm,
        issuer=config.provided.jwt_issuer,
        access_token_expire_minutes=config.provided.access_token_expire_minutes,
        refresh_token_expire_days=config.provided.refresh_token_expire_days,
    )

    # Repositories (factory providers for session-based repositories)
    user_repository = providers.Factory(
        PostgresUserRepository, session=providers.Dependency(instance_of=object)
    )

    client_repository = providers.Factory(
        PostgresClientRepository, session=providers.Dependency(instance_of=object)
    )

    token_repository = providers.Factory(
        PostgresTokenRepository, session=providers.Dependency(instance_of=object)
    )

    # Application services (factory providers)
    user_service = providers.Factory(UserService, user_repository=user_repository)

    client_service = providers.Factory(ClientService, client_repository=client_repository)

    oauth2_service = providers.Factory(
        OAuth2Service,
        user_service=user_service,
        client_service=client_service,
        token_service=token_service,
        token_repository=token_repository,
        cache=cache,
    )
