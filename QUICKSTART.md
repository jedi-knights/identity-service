# Quick Start Guide

Get the Identity Service running in minutes!

## Prerequisites

- Python 3.13+
- uv package manager
- Docker & Docker Compose (for easy setup)

## Option 1: Docker Compose (Recommended)

The fastest way to get started:

```bash
# Clone the repository
git clone https://github.com/jedi-knights/identity-service.git
cd identity-service

# Generate JWT keys
uv run python scripts/generate_keys.py

# Copy the keys to .env file
cp .env.example .env
# Edit .env and add the JWT keys from the previous step

# Start all services (PostgreSQL, Redis, App)
docker-compose up -d

# Run migrations
docker-compose exec app uv run alembic upgrade head

# Create an admin user
docker-compose exec app uv run python -m identity_service.cli user create

# Create an OAuth2 client
docker-compose exec app uv run python -m identity_service.cli client create

# View logs
docker-compose logs -f app
```

The service will be available at http://localhost:8000

## Option 2: Local Development

For local development without Docker:

```bash
# Clone the repository
git clone https://github.com/jedi-knights/identity-service.git
cd identity-service

# Install dependencies
uv sync --all-extras

# Generate JWT keys
uv run python scripts/generate_keys.py

# Create .env file
cp .env.example .env
# Edit .env with:
# - Database URL (PostgreSQL)
# - Redis URL
# - JWT keys (from generate_keys.py output)

# Run migrations
uv run alembic upgrade head

# Create test data
uv run python -m identity_service.cli user create
uv run python -m identity_service.cli client create

# Start the server
uv run python -m identity_service.cli serve --reload
```

## Testing the API

### Get an Access Token

```bash
curl -X POST http://localhost:8000/oauth2/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password" \
  -d "username=YOUR_USERNAME" \
  -d "password=YOUR_PASSWORD" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_in": 1800,
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "scope": "read write"
}
```

### Introspect a Token

```bash
curl -X POST http://localhost:8000/oauth2/introspect \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "token=YOUR_ACCESS_TOKEN"
```

### Health Check

```bash
curl http://localhost:8000/health
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development Commands

```bash
# Run tests
invoke test

# Run tests with coverage
invoke test-cov

# Format code
invoke format

# Lint code
invoke lint

# Type check
invoke typecheck

# Run all checks
invoke check
```

## Troubleshooting

### Database Connection Issues

- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Verify database exists: `createdb identity`

### Redis Connection Issues

- Ensure Redis is running
- Check REDIS_URL in .env

### JWT Key Issues

- Regenerate keys: `uv run python scripts/generate_keys.py`
- Ensure keys are properly base64 encoded
- Check .env file has JWT_PRIVATE_KEY and JWT_PUBLIC_KEY

### Migration Issues

- Reset database: `uv run alembic downgrade base`
- Rerun migrations: `uv run alembic upgrade head`

## Next Steps

- Read the [README.md](README.md) for detailed documentation
- Explore the API at http://localhost:8000/docs
- Check out the [Architecture Overview](README.md#architecture)
- Review the [Testing Strategy](README.md#testing-strategy)

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/jedi-knights/identity-service/issues
- Pull Requests: https://github.com/jedi-knights/identity-service/pulls
