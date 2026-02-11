"""Invoke tasks for development."""
from invoke import task


@task
def serve(ctx, host="0.0.0.0", port=8000, reload=True):
    """Start the development server."""
    reload_flag = "--reload" if reload else ""
    ctx.run(f"uvicorn identity_service.main:app --host {host} --port {port} {reload_flag}")


@task
def format(ctx):
    """Format code with black."""
    ctx.run("black identity_service tests")


@task
def lint(ctx):
    """Lint code with ruff."""
    ctx.run("ruff check identity_service tests")


@task
def typecheck(ctx):
    """Type check with mypy."""
    ctx.run("mypy identity_service")


@task
def test(ctx, verbose=False):
    """Run tests with pytest."""
    verbose_flag = "-v" if verbose else ""
    ctx.run(f"pytest {verbose_flag}")


@task
def test_cov(ctx):
    """Run tests with coverage."""
    ctx.run("pytest --cov=identity_service --cov-report=html --cov-report=term")


@task
def migrate(ctx, message):
    """Create a new database migration."""
    ctx.run(f'alembic revision --autogenerate -m "{message}"')


@task
def upgrade(ctx):
    """Upgrade database to latest migration."""
    ctx.run("alembic upgrade head")


@task
def downgrade(ctx):
    """Downgrade database by one migration."""
    ctx.run("alembic downgrade -1")


@task
def db_create(ctx):
    """Create database tables."""
    ctx.run("uv run python -m identity_service.cli db create")


@task
def db_drop(ctx):
    """Drop database tables."""
    ctx.run("uv run python -m identity_service.cli db drop")


@task
def create_user(ctx, username, email):
    """Create a new user."""
    ctx.run(f"uv run python -m identity_service.cli user create --username {username} --email {email}")


@task
def create_client(ctx, name, redirect_uri):
    """Create a new OAuth2 client."""
    ctx.run(
        f'uv run python -m identity_service.cli client create --name "{name}" --redirect-uri {redirect_uri}'
    )


@task
def docker_build(ctx):
    """Build Docker image."""
    ctx.run("docker build -t identity-service:latest .")


@task
def docker_up(ctx):
    """Start Docker Compose services."""
    ctx.run("docker-compose up -d")


@task
def docker_down(ctx):
    """Stop Docker Compose services."""
    ctx.run("docker-compose down")


@task
def docker_logs(ctx, service="app"):
    """View Docker Compose logs."""
    ctx.run(f"docker-compose logs -f {service}")


@task(pre=[format, lint, typecheck, test])
def check(ctx):
    """Run all checks (format, lint, typecheck, test)."""
    print("All checks passed!")
