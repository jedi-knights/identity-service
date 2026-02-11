"""Health check routes."""
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "service": "identity-service"}


@router.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "service": "Identity Service",
        "version": "0.1.0",
        "description": "OAuth2 identity service with Ports & Adapters architecture",
    }
