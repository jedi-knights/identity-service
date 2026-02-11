# Identity Service

A Python 3.13 FastAPI OAuth2 identity service implementing Ports & Adapters (Hexagonal Architecture) with dependency injection as the composition root.

## Features

- **OAuth2 Implementation**: Full OAuth2 server with password and refresh token grant types
- **Ports & Adapters Architecture**: Clean separation between business logic and infrastructure
- **Dependency Injection**: Using dependency-injector for composition root
- **JWT/JWK Support**: Token generation and validation with Authlib
- **PostgreSQL**: Async SQLAlchemy with Alembic migrations
- **Redis**: Caching layer for token introspection
- **Modern Python**: Python 3.13 with type hints and async/await
- **CLI Tools**: Click-based CLI for user and client management
- **Task Runner**: Invoke for common development tasks
- **Comprehensive Tests**: Pytest with table-based testing and pytest-mock
- **Docker Support**: Multi-container setup with Docker Compose

## Architecture

This project follows the **Ports & Adapters** (Hexagonal Architecture) pattern:

```
identity_service/
├── domain/              # Domain layer (entities, value objects)
│   └── entities/        # Core business entities (User, Client, Token)
├── ports/               # Port interfaces
│   ├── repositories/    # Repository interfaces
│   ├── cache/           # Cache interface
│   └── tokens/          # Token service interface
├── adapters/            # Adapter implementations
│   ├── postgres/        # PostgreSQL repositories
│   ├── redis/           # Redis cache
│   └── jwt/             # JWT token service with Authlib
├── application/         # Application layer
│   ├── use_cases/       # Business use cases
│   └── dto/             # Data transfer objects
├── infrastructure/      # Infrastructure
│   ├── config/          # Configuration management
│   ├── database/        # Database models and connection
│   └── container.py     # Dependency injection container
└── api/                 # API layer (FastAPI)
    ├── routes/          # API endpoints
    ├── dependencies/    # FastAPI dependencies
    └── middleware/      # Middleware
```

### Key Principles

- **DRY** (Don't Repeat Yourself): Reusable components and abstractions
- **SOLID**: Single responsibility, open/closed, dependency inversion
- **Clean Architecture**: Dependencies point inward, business logic independent of frameworks
- **Rule of Threes**: Refactor when patterns emerge three times

## Prerequisites

- Python 3.13+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (optional)

## Installation

### Using uv (Recommended)

```bash
# Install uv if not already installed
pip install uv

# Clone the repository
git clone https://github.com/jedi-knights/identity-service.git
cd identity-service

# Install dependencies
uv sync --all-extras

# Copy environment file
cp .env.example .env
```

### Environment Configuration

Edit `.env` and configure:

1. **Database URL**: PostgreSQL connection string
2. **Redis URL**: Redis connection string
3. **JWT Keys**: Generate RSA keys for JWT signing

#### Generate JWT Keys

```bash
# Generate private key
ssh-keygen -t rsa -b 2048 -m PEM -f jwtRS256.key -N ""

# Generate public key
ssh-keygen -f jwtRS256.key -e -m PKCS8 > jwtRS256.key.pub

# Set in .env (base64 encode for single line)
JWT_PRIVATE_KEY=$(cat jwtRS256.key | base64 -w 0)
JWT_PUBLIC_KEY=$(cat jwtRS256.key.pub | base64 -w 0)
```

## Database Setup

### Run Migrations

```bash
# Create tables
uv run alembic upgrade head

# Or use invoke task
invoke upgrade
```

### Create Initial Data

```bash
# Create a user
uv run python -m identity_service.cli user create

# Create an OAuth2 client
uv run python -m identity_service.cli client create \
  --name "My Application" \
  --redirect-uri http://localhost:3000/callback \
  --grant-type password \
  --grant-type refresh_token
```

## Running the Service

### Development Server

```bash
# Using CLI
uv run python -m identity_service.cli serve --reload

# Using invoke
invoke serve

# Using uvicorn directly
uv run uvicorn identity_service.main:app --reload
```

### Production Server

```bash
uv run uvicorn identity_service.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Compose

```bash
# Start all services (PostgreSQL, Redis, App)
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

## API Endpoints

### Health Check

- `GET /health` - Service health status
- `GET /` - Service information

### OAuth2

- `POST /oauth2/token` - Token endpoint (password & refresh_token grants)
- `POST /oauth2/introspect` - Token introspection
- `POST /oauth2/revoke` - Token revocation

### Users

- `POST /users` - Create a new user
- `GET /users/{user_id}` - Get user by ID
- `POST /users/{user_id}/deactivate` - Deactivate user

### Clients

- `POST /clients` - Create a new OAuth2 client
- `GET /clients/{client_id}` - Get client by ID
- `POST /clients/{client_id}/deactivate` - Deactivate client

## Usage Examples

### Obtain Access Token (Password Grant)

```bash
curl -X POST http://localhost:8000/oauth2/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password" \
  -d "username=testuser" \
  -d "password=securepassword123" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

### Refresh Access Token

```bash
curl -X POST http://localhost:8000/oauth2/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token" \
  -d "refresh_token=YOUR_REFRESH_TOKEN" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

### Introspect Token

```bash
curl -X POST http://localhost:8000/oauth2/introspect \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "token=YOUR_ACCESS_TOKEN"
```

## Development

### Code Quality

```bash
# Format code
invoke format

# Lint code
invoke lint

# Type check
invoke typecheck

# Run all checks
invoke check
```

### Testing

```bash
# Run tests
invoke test

# Run tests with coverage
invoke test-cov

# Run specific test file
uv run pytest tests/unit/test_user_service.py -v
```

### Database Migrations

```bash
# Create a new migration
invoke migrate "Add new column"

# Upgrade to latest
invoke upgrade

# Downgrade one version
invoke downgrade
```

## CLI Commands

### Database

```bash
# Create tables
uv run python -m identity_service.cli db create

# Drop tables
uv run python -m identity_service.cli db drop
```

### User Management

```bash
# Create user (interactive)
uv run python -m identity_service.cli user create
```

### Client Management

```bash
# Create client (interactive)
uv run python -m identity_service.cli client create
```

## Testing Strategy

Tests follow table-based testing with pytest-mock:

- **Unit Tests**: Test domain logic and use cases in isolation
- **Integration Tests**: Test API endpoints with mocked dependencies
- **Parameterized Tests**: Use `@pytest.mark.parametrize` for multiple scenarios
- **No unittest.mock**: Use pytest-mock exclusively for mocking

Example:

```python
@pytest.mark.parametrize(
    "username,email,should_succeed",
    [
        ("user1", "user1@example.com", True),
        ("user2", "user2@example.com", True),
    ],
)
@pytest.mark.asyncio
async def test_create_user(username, email, should_succeed):
    # Test implementation
    pass
```

## Project Structure

```
identity-service/
├── identity_service/           # Main package
│   ├── domain/                 # Domain layer
│   ├── ports/                  # Port interfaces
│   ├── adapters/               # Adapter implementations
│   ├── application/            # Application services
│   ├── infrastructure/         # Infrastructure code
│   ├── api/                    # API layer
│   ├── main.py                 # FastAPI application
│   └── cli.py                  # CLI commands
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
├── alembic/                    # Database migrations
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Docker image definition
├── pyproject.toml              # Project dependencies
├── tasks.py                    # Invoke tasks
└── README.md                   # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the architecture patterns
4. Add tests for your changes
5. Run code quality checks (`invoke check`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License.

## Acknowledgments

- FastAPI for the excellent web framework
- Authlib for OAuth2/JWT implementation
- SQLAlchemy for database ORM
- dependency-injector for DI container
- The Hexagonal Architecture pattern

