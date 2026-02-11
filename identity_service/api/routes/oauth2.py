"""OAuth2 routes."""
from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from identity_service.api.dependencies.database import get_db_session
from identity_service.application.dto.schemas import TokenResponse, TokenIntrospection
from identity_service.application.use_cases.oauth2_service import OAuth2Service
from identity_service.infrastructure.container import Container

router = APIRouter(prefix="/oauth2", tags=["oauth2"])


@router.post("/token", response_model=TokenResponse)
@inject
async def token_endpoint(
    grant_type: Annotated[str, Form()],
    username: Annotated[str | None, Form()] = None,
    password: Annotated[str | None, Form()] = None,
    refresh_token: Annotated[str | None, Form()] = None,
    client_id: Annotated[str | None, Form()] = None,
    client_secret: Annotated[str | None, Form()] = None,
    scope: Annotated[str | None, Form()] = None,
    db: AsyncSession = Depends(get_db_session),
    oauth2_service: OAuth2Service = Depends(Provide[Container.oauth2_service]),
) -> TokenResponse:
    """OAuth2 token endpoint."""
    scopes = scope.split() if scope else None

    if grant_type == "password":
        if not username or not password or not client_id or not client_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required parameters for password grant",
            )

        try:
            client_uuid = UUID(client_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid client_id format"
            )

        # Pass the session to repositories via dependency override
        oauth2_service.user_service.user_repository.session = db
        oauth2_service.client_service.client_repository.session = db
        oauth2_service.token_repository.session = db

        token = await oauth2_service.password_grant(
            username, password, client_uuid, client_secret, scopes
        )

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        expires_in = int((token.expires_at - token.created_at).total_seconds())

        return TokenResponse(
            access_token=token.access_token,
            token_type=token.token_type,
            expires_in=expires_in,
            refresh_token=token.refresh_token,
            scope=" ".join(token.scopes) if token.scopes else None,
        )

    elif grant_type == "refresh_token":
        if not refresh_token or not client_id or not client_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required parameters for refresh_token grant",
            )

        try:
            client_uuid = UUID(client_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid client_id format"
            )

        # Pass the session to repositories
        oauth2_service.client_service.client_repository.session = db
        oauth2_service.token_repository.session = db

        token = await oauth2_service.refresh_token_grant(
            refresh_token, client_uuid, client_secret
        )

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        expires_in = int((token.expires_at - token.created_at).total_seconds())

        return TokenResponse(
            access_token=token.access_token,
            token_type=token.token_type,
            expires_in=expires_in,
            refresh_token=token.refresh_token,
            scope=" ".join(token.scopes) if token.scopes else None,
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported grant_type: {grant_type}",
        )


@router.post("/introspect", response_model=TokenIntrospection)
@inject
async def introspect_endpoint(
    token: Annotated[str, Form()],
    db: AsyncSession = Depends(get_db_session),
    oauth2_service: OAuth2Service = Depends(Provide[Container.oauth2_service]),
) -> TokenIntrospection:
    """OAuth2 token introspection endpoint."""
    # Pass the session to repositories
    oauth2_service.token_repository.session = db

    result = await oauth2_service.introspect_token(token)

    if not result:
        return TokenIntrospection(active=False)

    return TokenIntrospection(**result)


@router.post("/revoke")
@inject
async def revoke_endpoint(
    token: Annotated[str, Form()],
    db: AsyncSession = Depends(get_db_session),
    oauth2_service: OAuth2Service = Depends(Provide[Container.oauth2_service]),
) -> dict:
    """OAuth2 token revocation endpoint."""
    # Pass the session to repositories
    oauth2_service.token_repository.session = db

    success = await oauth2_service.revoke_token(token)

    return {"revoked": success}
