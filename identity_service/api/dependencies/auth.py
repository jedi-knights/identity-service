"""Authentication dependencies for OAuth2 endpoints."""

from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession

from identity_service.api.dependencies.database import get_db_session
from identity_service.api.exceptions import InvalidClientError
from identity_service.application.use_cases.client_service import ClientService
from identity_service.domain.entities import Client
from identity_service.infrastructure.container import Container


@inject
async def authenticate_client(
    client_id: Annotated[str, Form()],
    client_secret: Annotated[str, Form()],
    db: AsyncSession = Depends(get_db_session),
    client_service: ClientService = Depends(Provide[Container.client_service]),
) -> Client:
    """Authenticate OAuth2 client for protected endpoints."""
    try:
        client_uuid = UUID(client_id)
    except ValueError:
        raise InvalidClientError("Invalid client_id format")

    client_service.client_repository.session = db
    client = await client_service.authenticate_client(client_uuid, client_secret)

    if not client:
        raise InvalidClientError()

    return client
