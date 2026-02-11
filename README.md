# Identity Service

> **Version**: 0.1.0 (MVP/Early Development)  
> **Status**: Development-ready with Docker support

A production-focused OAuth2 identity and authentication service built with Python 3.13 and FastAPI. Implements Hexagonal Architecture (Ports & Adapters) with clean separation of concerns, dependency injection, and comprehensive type safety.

## Overview

This service provides enterprise-grade OAuth2 authentication and authorization with token management, user lifecycle operations, and client application registration. Built following SOLID principles and Clean Architecture patterns for maximum maintainability and testability.

### Core Capabilities

- **OAuth2 Server**: Password grant and refresh token flows with full RFC compliance
- **JWT/JWK Token Management**: Secure token generation, validation, introspection, and revocation using Authlib
- **User Management**: Complete CRUD operations with secure bcrypt password hashing
- **Client Management**: OAuth2 client registration, configuration, and lifecycle management
- **Token Caching**: Redis-backed introspection caching for high-performance validation

### Technical Features

- **Hexagonal Architecture**: Clean separation between domain, application, infrastructure, and API layers
- **Dependency Injection**: Composition root pattern using dependency-injector for loose coupling
- **PostgreSQL**: Async SQLAlchemy ORM with Alembic migrations for schema versioning
- **Redis**: High-performance caching layer for token introspection
- **Modern Python**: Python 3.13 with comprehensive type hints and async/await throughout
- **CLI Tools**: Click-based management interface for administrative tasks
- **Task Automation**: Invoke-based task runner for development workflows
- **Testing**: Pytest with table-based parameterized testing and pytest-mock (7 test suites)
- **Code Quality**: Black formatting, Ruff linting, MyPy type checking
- **Docker Support**: Production-ready multi-container setup with Docker Compose
- **40+ Python modules**: Fully typed codebase with strict type checking enabled

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

### Architectural Principles

This codebase adheres to professional software engineering standards:

- **DRY** (Don't Repeat Yourself): Reusable components and abstractions throughout
- **SOLID Principles**: Single responsibility, open/closed, Liskov substitution, interface segregation, dependency inversion
- **Clean Architecture**: Dependencies flow inward; domain logic remains framework-agnostic
- **Repository Pattern**: Data access abstraction for testability and flexibility
- **Dependency Injection**: Constructor injection for loose coupling and testability
- **Async-First**: Non-blocking I/O throughout for maximum performance
- **Type Safety**: Comprehensive type hints with MyPy strict mode
- **Rule of Three**: Abstraction only after seeing patterns emerge three times

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

### Interactive Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Health & Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health status and dependencies |
| `GET` | `/` | Service information and version |

### OAuth2 Token Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/oauth2/token` | Token issuance (password & refresh_token grants) |
| `POST` | `/oauth2/introspect` | Token validation and metadata retrieval |
| `POST` | `/oauth2/revoke` | Token revocation |

**Supported Grant Types:**
- `password`: Resource Owner Password Credentials Grant
- `refresh_token`: Refresh Token Grant

### User Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/users` | Create a new user with credentials |
| `GET` | `/users/{user_id}` | Retrieve user details by ID |
| `POST` | `/users/{user_id}/deactivate` | Deactivate user account |

### Client Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/clients` | Register a new OAuth2 client application |
| `GET` | `/clients/{client_id}` | Retrieve client details by ID |
| `POST` | `/clients/{client_id}/deactivate` | Deactivate OAuth2 client |

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

The project follows a comprehensive testing approach with 7+ test modules covering unit and integration scenarios:

### Testing Philosophy

- **Unit Tests**: Test domain logic, entities, and use cases in isolation with mocked dependencies
- **Integration Tests**: Test API endpoints and database interactions with test fixtures
- **Parameterized Tests**: Use `@pytest.mark.parametrize` for table-based testing across multiple scenarios
- **Mock Strategy**: pytest-mock exclusively (no unittest.mock) for consistency
- **Test Isolation**: Each test is independent with proper setup/teardown
- **Async Testing**: pytest-asyncio for async test support with proper event loop management

### Test Coverage Areas

- User service operations (creation, authentication, deactivation)
- Client service operations (registration, validation)
- OAuth2 flows (password grant, refresh token)
- Token generation and validation
- Repository layer operations
- Domain entity validation

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

### Running Tests

```bash
# All tests
invoke test

# With coverage report
invoke test-cov

# Specific test file
uv run pytest tests/unit/test_user_service.py -v

# Specific test with verbose output
uv run pytest tests/unit/test_user_service.py::test_create_user -vv
```

## Project Structure

```
identity-service/
├── identity_service/           # Main package (40+ modules)
│   ├── domain/                 # Domain layer - Core business entities
│   │   ├── entities/           # User, Client, Token entities
│   │   ├── services/           # Domain services
│   │   └── value_objects/      # Value objects
│   ├── ports/                  # Port interfaces - Abstractions
│   │   ├── repositories/       # Repository interfaces
│   │   ├── cache/              # Cache interface
│   │   └── tokens/             # Token service interface
│   ├── adapters/               # Adapter implementations - External integrations
│   │   ├── postgres/           # PostgreSQL repository implementations
│   │   ├── redis/              # Redis cache implementation
│   │   └── jwt/                # JWT/JWK token service (Authlib)
│   ├── application/            # Application layer - Use cases
│   │   ├── use_cases/          # Business use cases (UserService, ClientService, OAuth2Service)
│   │   └── dto/                # Data transfer objects (Pydantic schemas)
│   ├── infrastructure/         # Infrastructure - Framework & config
│   │   ├── config/             # Settings and configuration management
│   │   ├── database/           # Database models, connections (SQLAlchemy)
│   │   └── container.py        # Dependency injection container
│   └── api/                    # API layer - HTTP interface
│       ├── routes/             # FastAPI endpoints (health, oauth2, users, clients)
│       ├── dependencies/       # FastAPI dependencies (auth, database sessions)
│       └── middleware/         # HTTP middleware (CORS, etc.)
├── tests/                      # Test suite (7+ test modules)
│   ├── unit/                   # Unit tests (services, entities)
│   ├── integration/            # Integration tests (API, database)
│   └── conftest.py             # Pytest fixtures and configuration
├── alembic/                    # Database migrations
│   └── versions/               # Migration scripts
├── scripts/                    # Utility scripts
│   └── generate_keys.py        # JWT key generation
├── docker-compose.yml          # Multi-container setup (app, postgres, redis)
├── Dockerfile                  # Production Docker image
├── pyproject.toml              # Project metadata & dependencies
├── tasks.py                    # Invoke task definitions
├── QUICKSTART.md               # Quick start guide
└── README.md                   # This file
```

## Project Status

### Current State (v0.1.0)

**✅ Complete:**
- Core OAuth2 flows (password grant, refresh token)
- User CRUD operations with secure password hashing
- Client registration and management
- Token introspection and revocation
- JWT/JWK token generation and validation
- Redis caching layer for performance
- Database migrations with Alembic
- Docker Compose development environment
- CLI tools for administration
- Comprehensive type hints throughout

**⚠️ In Progress / Future Enhancements:**
- Additional OAuth2 grant types (authorization code, client credentials)
- Enhanced test coverage (currently at ~40%, targeting 80%+)
- Production hardening (rate limiting, security headers, audit logging)
- Monitoring and observability (metrics, distributed tracing)
- API documentation improvements
- OpenID Connect support
- Multi-factor authentication (MFA)
- Social login integrations

### Deployment Readiness

- **Development**: ✅ Fully ready with Docker Compose
- **Staging**: ✅ Ready with configuration adjustments
- **Production**: ⚠️ Requires additional hardening (rate limiting, monitoring, secrets management)

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Follow** the architecture patterns (Hexagonal, SOLID, DRY)
4. **Write** tests for your changes (maintain or improve coverage)
5. **Run** code quality checks:
   ```bash
   invoke format  # Format code with Black
   invoke lint    # Lint with Ruff
   invoke typecheck  # Type check with MyPy
   invoke test    # Run test suite
   invoke check   # Run all checks
   ```
6. **Commit** your changes following conventional commits
7. **Push** to your branch (`git push origin feature/amazing-feature`)
8. **Open** a Pull Request with a clear description

### Code Standards

- Follow existing patterns and conventions
- Maintain type hints on all functions
- Keep cyclomatic complexity under 7
- Write self-documenting code with minimal comments
- Add tests for new functionality
- Update documentation as needed

## License

This project is licensed under the MIT License.

## Acknowledgments

- FastAPI for the excellent web framework
- Authlib for OAuth2/JWT implementation
- SQLAlchemy for database ORM
- dependency-injector for DI container
- The Hexagonal Architecture pattern

