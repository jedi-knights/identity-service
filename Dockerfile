# Use Python 3.13 slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock .python-version ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY identity_service ./identity_service
COPY alembic ./alembic
COPY alembic.ini ./

# Expose port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "uvicorn", "identity_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
