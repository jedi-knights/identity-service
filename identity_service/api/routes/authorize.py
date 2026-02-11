"""OAuth2 authorization endpoint."""

from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from identity_service.api.dependencies.database import get_db_session
from identity_service.api.exceptions import (
    InvalidClientError,
    InvalidRequestError,
    InvalidScopeError,
    UnsupportedResponseTypeError,
    AccessDeniedError,
)
from identity_service.application.use_cases.oauth2_service import OAuth2Service
from identity_service.infrastructure.container import Container

router = APIRouter(prefix="/oauth2", tags=["oauth2"])


@router.get("/authorize")
@inject
async def authorize_endpoint(
    response_type: Annotated[str, Query()],
    client_id: Annotated[str, Query()],
    redirect_uri: Annotated[str, Query()],
    scope: Annotated[str | None, Query()] = None,
    state: Annotated[str | None, Query()] = None,
    code_challenge: Annotated[str | None, Query()] = None,
    code_challenge_method: Annotated[str | None, Query()] = None,
    db: AsyncSession = Depends(get_db_session),
    oauth2_service: OAuth2Service = Depends(Provide[Container.oauth2_service]),
) -> dict:
    """OAuth2 authorization endpoint (RFC 6749 Section 3.1).

    This endpoint initiates the authorization code flow.
    In a real implementation, this would:
    1. Verify the user is authenticated (redirect to login if not)
    2. Display a consent screen showing what the client is requesting
    3. After user approval, create the authorization code and redirect

    For now, this returns information needed to build the consent screen.
    """
    if response_type != "code":
        raise UnsupportedResponseTypeError(f"Response type '{response_type}' is not supported")

    if not client_id or not redirect_uri:
        raise InvalidRequestError("Missing required parameters: client_id and redirect_uri")

    try:
        client_uuid = UUID(client_id)
    except ValueError:
        raise InvalidClientError("Invalid client_id format")

    oauth2_service.client_service.client_repository.session = db

    client = await oauth2_service.client_service.get_client_by_id(client_uuid)
    if not client:
        raise InvalidClientError("Invalid client_id")

    if not client.validate_redirect_uri(redirect_uri):
        raise InvalidRequestError("Invalid redirect_uri for this client")

    if not client.validate_grant_type("authorization_code"):
        raise InvalidClientError("Client not authorized for authorization_code grant")

    scopes = scope.split() if scope else client.scopes

    if code_challenge and code_challenge_method not in ["S256", "plain", None]:
        raise InvalidRequestError("Invalid code_challenge_method. Must be 'S256' or 'plain'")

    return {
        "client_id": str(client.id),
        "client_name": client.client_name,
        "redirect_uri": redirect_uri,
        "scopes": scopes,
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": code_challenge_method,
    }


@router.post("/authorize/approve")
@inject
async def authorize_approve_endpoint(
    client_id: Annotated[str, Form()],
    redirect_uri: Annotated[str, Form()],
    scope: Annotated[str, Form()],
    state: Annotated[str | None, Form()] = None,
    code_challenge: Annotated[str | None, Form()] = None,
    code_challenge_method: Annotated[str | None, Form()] = None,
    user_id: Annotated[str | None, Form()] = None,
    db: AsyncSession = Depends(get_db_session),
    oauth2_service: OAuth2Service = Depends(Provide[Container.oauth2_service]),
) -> RedirectResponse:
    """Approve authorization request and generate authorization code.

    In production, user_id would come from the authenticated session,
    not from form data.
    """
    if not user_id:
        raise AccessDeniedError("User authentication required")

    try:
        client_uuid = UUID(client_id)
        user_uuid = UUID(user_id)
    except ValueError:
        raise InvalidClientError("Invalid client_id or user_id format")

    oauth2_service.client_service.client_repository.session = db
    oauth2_service.authorization_code_repository.session = db

    client = await oauth2_service.client_service.get_client_by_id(client_uuid)
    if not client:
        raise InvalidClientError("Invalid client_id")

    if not client.validate_redirect_uri(redirect_uri):
        raise InvalidRequestError("Invalid redirect_uri for this client")

    scopes = scope.split()

    auth_code = await oauth2_service.create_authorization_code(
        client_id=client_uuid,
        user_id=user_uuid,
        redirect_uri=redirect_uri,
        scopes=scopes,
        state=state,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
    )

    redirect_url = f"{redirect_uri}?code={auth_code.code}"
    if state:
        redirect_url += f"&state={state}"

    return RedirectResponse(url=redirect_url, status_code=302)


@router.post("/authorize/deny")
async def authorize_deny_endpoint(
    redirect_uri: Annotated[str, Form()],
    state: Annotated[str | None, Form()] = None,
) -> RedirectResponse:
    """Deny authorization request."""
    redirect_url = f"{redirect_uri}?error=access_denied"
    if state:
        redirect_url += f"&state={state}"

    return RedirectResponse(url=redirect_url, status_code=302)
