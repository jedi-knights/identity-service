"""Command-line interface using Click."""
import asyncio
import secrets
from typing import Optional

import click
import uvicorn
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from identity_service.domain.entities import User, Client
from identity_service.infrastructure.config.settings import get_settings
from identity_service.infrastructure.database.models import Base
from identity_service.adapters.postgres.repositories import (
    PostgresUserRepository,
    PostgresClientRepository,
)


@click.group()
def app() -> None:
    """Identity Service CLI."""
    pass


@app.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
def serve(host: str, port: int, reload: bool) -> None:
    """Start the FastAPI server."""
    click.echo(f"Starting server on {host}:{port}")
    uvicorn.run(
        "identity_service.main:app",
        host=host,
        port=port,
        reload=reload,
    )


@app.group()
def db() -> None:
    """Database commands."""
    pass


@db.command("create")
def db_create() -> None:
    """Create database tables."""
    settings = get_settings()

    async def create_tables() -> None:
        engine = create_async_engine(settings.database_url, echo=True)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()

    click.echo("Creating database tables...")
    asyncio.run(create_tables())
    click.echo("Database tables created successfully!")


@db.command("drop")
@click.confirmation_option(prompt="Are you sure you want to drop all tables?")
def db_drop() -> None:
    """Drop all database tables."""
    settings = get_settings()

    async def drop_tables() -> None:
        engine = create_async_engine(settings.database_url, echo=True)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()

    click.echo("Dropping database tables...")
    asyncio.run(drop_tables())
    click.echo("Database tables dropped successfully!")


@app.group()
def user() -> None:
    """User management commands."""
    pass


@user.command("create")
@click.option("--username", prompt=True, help="Username")
@click.option("--email", prompt=True, help="Email address")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="Password")
def user_create(username: str, email: str, password: str) -> None:
    """Create a new user."""
    settings = get_settings()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def create_user() -> None:
        engine = create_async_engine(settings.database_url)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            repo = PostgresUserRepository(session)
            hashed_password = pwd_context.hash(password)
            user_entity = User(username=username, email=email, hashed_password=hashed_password)
            created_user = await repo.create(user_entity)
            click.echo(f"User created successfully!")
            click.echo(f"  ID: {created_user.id}")
            click.echo(f"  Username: {created_user.username}")
            click.echo(f"  Email: {created_user.email}")

        await engine.dispose()

    asyncio.run(create_user())


@app.group()
def client() -> None:
    """Client management commands."""
    pass


@client.command("create")
@click.option("--name", prompt=True, help="Client name")
@click.option(
    "--redirect-uri", multiple=True, required=True, help="Redirect URIs (can be specified multiple times)"
)
@click.option(
    "--grant-type",
    multiple=True,
    default=["password", "refresh_token"],
    help="Grant types (can be specified multiple times)",
)
@click.option("--scope", multiple=True, help="Scopes (can be specified multiple times)")
def client_create(
    name: str, redirect_uri: tuple, grant_type: tuple, scope: Optional[tuple]
) -> None:
    """Create a new OAuth2 client."""
    settings = get_settings()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def create_client() -> None:
        engine = create_async_engine(settings.database_url)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            repo = PostgresClientRepository(session)

            # Generate client secret
            plain_secret = secrets.token_urlsafe(32)
            hashed_secret = pwd_context.hash(plain_secret)

            client_entity = Client(
                client_name=name,
                client_secret_hash=hashed_secret,
                redirect_uris=list(redirect_uri),
                grant_types=list(grant_type),
                scopes=list(scope) if scope else [],
            )

            created_client = await repo.create(client_entity)

            click.echo(f"Client created successfully!")
            click.echo(f"  ID: {created_client.id}")
            click.echo(f"  Name: {created_client.client_name}")
            click.echo(f"  Secret: {plain_secret}")
            click.echo(f"  Redirect URIs: {', '.join(created_client.redirect_uris)}")
            click.echo(f"  Grant Types: {', '.join(created_client.grant_types)}")
            click.echo(f"  Scopes: {', '.join(created_client.scopes) if created_client.scopes else 'None'}")
            click.echo("")
            click.echo("⚠️  IMPORTANT: Save the client secret! It won't be shown again.")

        await engine.dispose()

    asyncio.run(create_client())


if __name__ == "__main__":
    app()
