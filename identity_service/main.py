"""Main FastAPI application."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from identity_service.api.routes import health, oauth2, users, clients
from identity_service.infrastructure.config.settings import get_settings
from identity_service.infrastructure.container import Container


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    container = Container()
    container.wire(
        modules=[
            "identity_service.api.routes.users",
            "identity_service.api.routes.clients",
            "identity_service.api.routes.oauth2",
        ]
    )
    app.state.container = container

    yield

    # Shutdown
    await container.database().close()
    await container.redis_client().close()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    # Include routers
    app.include_router(health.router)
    app.include_router(oauth2.router)
    app.include_router(users.router)
    app.include_router(clients.router)

    return app


app = create_app()
