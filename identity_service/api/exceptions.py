"""OAuth2 compliant exceptions per RFC 6749."""

from typing import Optional

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse


class OAuth2Error(HTTPException):
    """Base OAuth2 error exception following RFC 6749 Section 5.2."""

    def __init__(
        self,
        error: str,
        error_description: Optional[str] = None,
        error_uri: Optional[str] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> None:
        self.error = error
        self.error_description = error_description
        self.error_uri = error_uri
        detail = {"error": error}
        if error_description:
            detail["error_description"] = error_description
        if error_uri:
            detail["error_uri"] = error_uri
        super().__init__(status_code=status_code, detail=detail)


class InvalidRequestError(OAuth2Error):
    """The request is missing a required parameter, includes an invalid parameter value."""

    def __init__(
        self, error_description: Optional[str] = None, error_uri: Optional[str] = None
    ) -> None:
        super().__init__(
            error="invalid_request",
            error_description=error_description,
            error_uri=error_uri,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class InvalidClientError(OAuth2Error):
    """Client authentication failed."""

    def __init__(
        self, error_description: Optional[str] = None, error_uri: Optional[str] = None
    ) -> None:
        super().__init__(
            error="invalid_client",
            error_description=error_description or "Client authentication failed",
            error_uri=error_uri,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class InvalidGrantError(OAuth2Error):
    """The provided authorization grant is invalid, expired, revoked, or does not match."""

    def __init__(
        self, error_description: Optional[str] = None, error_uri: Optional[str] = None
    ) -> None:
        super().__init__(
            error="invalid_grant",
            error_description=error_description or "Invalid authorization grant",
            error_uri=error_uri,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class UnauthorizedClientError(OAuth2Error):
    """The authenticated client is not authorized to use this grant type."""

    def __init__(
        self, error_description: Optional[str] = None, error_uri: Optional[str] = None
    ) -> None:
        super().__init__(
            error="unauthorized_client",
            error_description=error_description or "Client not authorized for this grant type",
            error_uri=error_uri,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class UnsupportedGrantTypeError(OAuth2Error):
    """The authorization grant type is not supported by the authorization server."""

    def __init__(
        self, error_description: Optional[str] = None, error_uri: Optional[str] = None
    ) -> None:
        super().__init__(
            error="unsupported_grant_type",
            error_description=error_description or "Grant type not supported",
            error_uri=error_uri,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class InvalidScopeError(OAuth2Error):
    """The requested scope is invalid, unknown, or malformed."""

    def __init__(
        self, error_description: Optional[str] = None, error_uri: Optional[str] = None
    ) -> None:
        super().__init__(
            error="invalid_scope",
            error_description=error_description or "Invalid scope",
            error_uri=error_uri,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class ServerError(OAuth2Error):
    """The authorization server encountered an unexpected condition."""

    def __init__(
        self, error_description: Optional[str] = None, error_uri: Optional[str] = None
    ) -> None:
        super().__init__(
            error="server_error",
            error_description=error_description or "The server encountered an unexpected error",
            error_uri=error_uri,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class TemporarilyUnavailableError(OAuth2Error):
    """The authorization server is currently unable to handle the request."""

    def __init__(
        self, error_description: Optional[str] = None, error_uri: Optional[str] = None
    ) -> None:
        super().__init__(
            error="temporarily_unavailable",
            error_description=error_description or "Service temporarily unavailable",
            error_uri=error_uri,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class AccessDeniedError(OAuth2Error):
    """The resource owner or authorization server denied the request."""

    def __init__(
        self, error_description: Optional[str] = None, error_uri: Optional[str] = None
    ) -> None:
        super().__init__(
            error="access_denied",
            error_description=error_description or "Access denied",
            error_uri=error_uri,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class UnsupportedResponseTypeError(OAuth2Error):
    """The authorization server does not support obtaining an access token using this method."""

    def __init__(
        self, error_description: Optional[str] = None, error_uri: Optional[str] = None
    ) -> None:
        super().__init__(
            error="unsupported_response_type",
            error_description=error_description or "Response type not supported",
            error_uri=error_uri,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
