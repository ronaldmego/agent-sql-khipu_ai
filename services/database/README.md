# Database Service

**Port**: 8003
**Purpose**: PostgreSQL/Supabase database adapter and connection management

## Overview
This service provides a REST API for database operations. It handles:
- PostgreSQL connection pooling (asyncpg)
- Schema introspection
- Query execution
- Table metadata

## API Endpoints
- `GET /health` - Health check
- `GET /schema/tables` - List all tables
- `POST /schema/info` - Get schema information for specific tables
- `POST /execute/query` - Execute SQL query

## Tech Stack
- FastAPI
- asyncpg (async PostgreSQL driver)
- Pydantic V2 (validation)
- SQLAlchemy (optional, for compatibility)

## Development
```bash
cd services/database
uv run uvicorn src.main:app --reload --port 8003
```

## Environment Variables
- `POSTGRES_URL`: PostgreSQL connection string
- `POSTGRES_HOST`: Database host
- `POSTGRES_PORT`: Database port (default: 5432)
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DATABASE`: Database name
