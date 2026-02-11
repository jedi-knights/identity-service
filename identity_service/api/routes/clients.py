"""Client management routes."""
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from identity_service.api.dependencies.database import get_db_session
from identity_service.application.dto.schemas import ClientCreate, ClientResponse, ClientWithSecret
from identity_service.application.use_cases.client_service import ClientService
from identity_service.infrastructure.container import Container

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("/", response_model=ClientWithSecret, status_code=status.HTTP_201_CREATED)
@inject
async def create_client(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_db_session),
    client_service: ClientService = Depends(Provide[Container.client_service]),
) -> ClientWithSecret:
    """Create a new OAuth2 client."""
    # Pass the session to repository
    client_service.client_repository.session = db

    client, plain_secret = await client_service.create_client(
        client_name=client_data.client_name,
        redirect_uris=client_data.redirect_uris,
        grant_types=client_data.grant_types,
        scopes=client_data.scopes,
        is_confidential=client_data.is_confidential,
    )

    return ClientWithSecret(
        id=client.id,
        client_name=client.client_name,
        client_secret=plain_secret,
        redirect_uris=client.redirect_uris,
        grant_types=client.grant_types,
        scopes=client.scopes,
        is_confidential=client.is_confidential,
        is_active=client.is_active,
        created_at=client.created_at,
        updated_at=client.updated_at,
    )


@router.get("/{client_id}", response_model=ClientResponse)
@inject
async def get_client(
    client_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    client_service: ClientService = Depends(Provide[Container.client_service]),
) -> ClientResponse:
    """Get a client by ID."""
    # Pass the session to repository
    client_service.client_repository.session = db

    client = await client_service.get_client_by_id(client_id)

    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    return ClientResponse(
        id=client.id,
        client_name=client.client_name,
        redirect_uris=client.redirect_uris,
        grant_types=client.grant_types,
        scopes=client.scopes,
        is_confidential=client.is_confidential,
        is_active=client.is_active,
        created_at=client.created_at,
        updated_at=client.updated_at,
    )


@router.post("/{client_id}/deactivate", response_model=ClientResponse)
@inject
async def deactivate_client(
    client_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    client_service: ClientService = Depends(Provide[Container.client_service]),
) -> ClientResponse:
    """Deactivate a client."""
    # Pass the session to repository
    client_service.client_repository.session = db

    try:
        client = await client_service.deactivate_client(client_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return ClientResponse(
        id=client.id,
        client_name=client.client_name,
        redirect_uris=client.redirect_uris,
        grant_types=client.grant_types,
        scopes=client.scopes,
        is_confidential=client.is_confidential,
        is_active=client.is_active,
        created_at=client.created_at,
        updated_at=client.updated_at,
    )
