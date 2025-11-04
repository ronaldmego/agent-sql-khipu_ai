# Khipu AI - Refactor to Supabase/PostgreSQL

**Created**: 2025-11-04
**Last Updated**: 2025-11-04
**Status**: Setup Phase - Refactor Branch

---

## 1. Project Vision

### Problem Statement
The current Khipu AI implementation is tightly coupled to MySQL. This limits:
- Modern database features (JSONB, advanced indexing)
- Cloud-native deployment options
- Real-time capabilities
- Integration with modern backend-as-a-service platforms

### Solution Overview
Refactor Khipu AI to work with **Supabase/PostgreSQL** while maintaining the core functionality:
- Natural language to SQL queries
- Automated table analysis
- Intelligent insights generation
- RAG-enhanced responses

### Success Criteria (MVP)
- [ ] Full PostgreSQL/Supabase connectivity replacing MySQL
- [ ] All existing core features working (NL to SQL, insights, RAG)
- [ ] Improved schema introspection using PostgreSQL features
- [ ] Tests passing with PostgreSQL backend
- [ ] Documentation updated
- [ ] Easy setup with Supabase (cloud or self-hosted)

---

## 2. Architecture Decisions

### System Architecture
```
User Interface (Streamlit)
        ↓
Service Layer (Data Processing, RAG, State Management)
        ↓
Database Layer (PostgreSQL Adapter)
        ↓
Supabase/PostgreSQL Database
        ↓
Vector Store (FAISS) + LLM (OpenAI/Ollama)
```

### Design Patterns
- [x] **Microservices Architecture**: Separate services for UI, Query Processing, RAG, and Database
- [x] **Adapter Pattern**: Create database abstraction for easy provider switching
- [x] **Containerization**: Each service in Docker container with docker-compose orchestration
- [x] **API-First**: Inter-service communication via REST/gRPC
- [x] **RAG Enhancement**: Dedicated RAG service with LangChain

**Decision**: Refactor to **microservices architecture** for maximum portability and scalability:
1. **Frontend Service**: Streamlit UI (can run standalone or in container)
2. **Query Service**: LangChain SQL query generation
3. **RAG Service**: Document processing and context retrieval
4. **Database Service**: PostgreSQL/Supabase adapter layer

This enables:
- Independent deployment and scaling
- Technology flexibility per service
- Easy local development with Docker
- Production-ready containerization

---

## 3. Technical Stack

### Core Technologies (CHANGED)
- **Language**: Python 3.11+
- **Framework**: Streamlit (Frontend Service)
- **Database**: ~~MySQL~~ → **PostgreSQL (via Supabase)**
- **Package Manager**: **UV** (modern, fast Python package manager)
- **Dependency Management**: **pyproject.toml** + **requirements.txt** (dual format for compatibility)
- **Database Driver**: ~~mysql-connector-python~~ → **asyncpg** (async-first for performance)
- **Containerization**: **Docker** + **docker-compose**
- **Inter-service Communication**: FastAPI REST endpoints

### Additional Tools (UPDATED)
- **Validation**: Pydantic V2 (strict mode)
- **LLM Framework**: LangChain (Query & RAG services)
- **LLM Providers**: OpenAI, Ollama (configurable)
- **Vector Store**: FAISS (RAG service)
- **RAG**: LangChain Community
- **API Framework**: FastAPI (for service APIs)
- **Supabase Client**: For auth, real-time features
- **Process Management**: docker-compose (orchestration)
- **Package Management**: UV (fast, reliable dependency resolution)

### Key Dependencies Changes
```diff
# Remove
- mysql-connector-python>=9.1.0

# Add (via UV + pyproject.toml)
+ asyncpg>=0.29.0  # Async PostgreSQL driver
+ supabase>=2.3.0  # Supabase client
+ sqlalchemy[asyncio]>=2.0.36  # Async SQLAlchemy
+ fastapi>=0.115.0  # Service APIs
+ uvicorn[standard]>=0.32.0  # ASGI server
+ httpx>=0.28.0  # Async HTTP client for inter-service calls
+ pydantic>=2.10.3  # Already present, ensure V2
```

**New Files**:
- `pyproject.toml` (UV primary, includes all metadata)
- `requirements.txt` (generated from pyproject.toml for compatibility)
- `Dockerfile` (per service)
- `docker-compose.yml` (orchestration)

**Rationale**:
- **PostgreSQL**: Superior JSON support, full-text search, extensibility
- **Supabase**: Instant APIs, auth, real-time subscriptions
- **UV**: 10-100x faster than pip, reliable dependency resolution, better UX
- **Docker**: Consistent environments, easy local development, production-ready
- **Microservices**: Independent scaling, technology flexibility, fault isolation
- **AsyncPG**: High-performance async PostgreSQL driver (3x faster than psycopg2)
- **FastAPI**: Modern, fast, type-safe API framework for inter-service communication

---

## 4. Project Structure (Microservices)

```
khipu-ai-refactor/
├── services/                      # ⚠️ NEW: Microservices
│   ├── frontend/                  # Streamlit UI Service
│   │   ├── src/
│   │   │   ├── pages/
│   │   │   │   └── Home.py
│   │   │   ├── components/
│   │   │   │   ├── query_interface.py
│   │   │   │   ├── visualization.py
│   │   │   │   ├── history_view.py
│   │   │   │   └── debug_panel.py
│   │   │   ├── layouts/
│   │   │   │   ├── header.py
│   │   │   │   └── footer.py
│   │   │   └── utils/
│   │   │       └── api_client.py  # HTTP client for other services
│   │   ├── pyproject.toml
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── .env.example
│   │
│   ├── query/                     # Query Processing Service (FastAPI)
│   │   ├── src/
│   │   │   ├── main.py           # FastAPI app
│   │   │   ├── api/
│   │   │   │   └── endpoints/
│   │   │   │       ├── query.py
│   │   │   │       └── health.py
│   │   │   ├── core/
│   │   │   │   ├── config.py
│   │   │   │   ├── chains.py     # LangChain SQL chains
│   │   │   │   └── prompts.py
│   │   │   ├── models/
│   │   │   │   ├── request.py    # Pydantic request models
│   │   │   │   └── response.py   # Pydantic response models
│   │   │   └── utils/
│   │   │       ├── llm_provider.py
│   │   │       └── query_utils.py
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── .env.example
│   │
│   ├── rag/                       # RAG Service (FastAPI)
│   │   ├── src/
│   │   │   ├── main.py           # FastAPI app
│   │   │   ├── api/
│   │   │   │   └── endpoints/
│   │   │   │       ├── retrieve.py
│   │   │   │       ├── index.py
│   │   │   │       └── health.py
│   │   │   ├── core/
│   │   │   │   ├── config.py
│   │   │   │   ├── vector_store.py
│   │   │   │   └── embeddings.py
│   │   │   ├── models/
│   │   │   │   ├── request.py
│   │   │   │   └── response.py
│   │   │   └── utils/
│   │   │       └── document_processing.py
│   │   ├── docs/                 # Documents for RAG
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── .env.example
│   │
│   └── database/                  # Database Service (FastAPI)
│       ├── src/
│       │   ├── main.py           # FastAPI app
│       │   ├── api/
│       │   │   └── endpoints/
│       │   │       ├── schema.py
│       │   │       ├── execute.py
│       │   │       └── health.py
│       │   ├── core/
│       │   │   ├── config.py
│       │   │   ├── connection.py  # PostgreSQL connection
│       │   │   └── adapter.py     # Database adapter
│       │   ├── models/
│       │   │   ├── request.py
│       │   │   └── response.py
│       │   └── utils/
│       │       └── query_executor.py
│       ├── tests/
│       ├── pyproject.toml
│       ├── requirements.txt
│       ├── Dockerfile
│       └── .env.example
│
├── scripts/                       # Utility scripts
│   ├── setup_uv.sh               # ⚠️ NEW: Install UV
│   ├── generate_requirements.sh  # ⚠️ NEW: Generate requirements.txt from pyproject.toml
│   ├── test_all.sh               # ⚠️ NEW: Run tests for all services
│   └── postgresql/
│       ├── init_db.py
│       └── load_data.py
│
├── tests/                         # ⚠️ Integration tests (cross-service)
│   ├── test_e2e.py
│   └── test_integration.py
│
├── docs/                          # Documentation
│   └── architecture.md
│
├── docker-compose.yml             # ⚠️ NEW: Orchestration
├── docker-compose.dev.yml         # ⚠️ NEW: Development overrides
├── .dockerignore                  # ⚠️ NEW
├── .gitignore
├── INITIAL.md                     # This file
├── CLAUDE.md
├── PROGRESS.md
├── readme.md                      # ⚠️ UPDATE
└── LICENSE

⚠️ = New or changed files
```

### Service Responsibilities

| Service | Port | Purpose | Tech Stack |
|---------|------|---------|------------|
| **frontend** | 8501 | Streamlit UI | Streamlit, httpx |
| **query** | 8001 | NL→SQL, query generation | FastAPI, LangChain, asyncpg |
| **rag** | 8002 | Document retrieval, context | FastAPI, LangChain, FAISS |
| **database** | 8003 | PostgreSQL adapter | FastAPI, asyncpg, SQLAlchemy |
| **postgres** | 5432 | PostgreSQL/Supabase | PostgreSQL 16+ |

---

## 5. Development Workflow

### Git Strategy
- **Current Branch**: `claude/refactor-011CUoU3TrMfaKcn1xH1TSs9`
- **Main Branch**: `main` (will merge after validation)
- **Commit Format**: `[milestone-X] Short description`
- **Push Strategy**: After each validated milestone

### Testing Strategy
- **Unit Tests**: Database adapter functions
- **Integration Tests**: Supabase connection, LangChain queries
- **E2E Tests**: Full query flow (NL → SQL → Results)
- **Coverage Target**: 70% minimum (starting point for refactor)

### Refactor Philosophy
- **Incremental Migration**: Replace piece by piece
- **Backward Compatibility**: Consider migration path for existing users
- **Test-Driven**: Write tests for PostgreSQL before removing MySQL code

---

## 6. UV & Package Management

### Why UV?
UV is a modern Python package manager and project manager written in Rust. It's:
- **10-100x faster** than pip
- **Reliable**: Deterministic dependency resolution
- **All-in-one**: Replaces pip, pip-tools, virtualenv, pyenv
- **Compatible**: Works with existing `pyproject.toml` and `requirements.txt`

### UV Setup
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version

# Create project with UV
cd services/database/
uv init

# Add dependency
uv add fastapi uvicorn[standard] asyncpg

# Generate requirements.txt for Docker compatibility
uv pip compile pyproject.toml -o requirements.txt

# Run application
uv run uvicorn src.main:app --reload
```

### Dual Format Strategy
We maintain BOTH `pyproject.toml` and `requirements.txt`:
- **pyproject.toml**: Primary source, managed by UV
- **requirements.txt**: Generated from pyproject.toml for Docker/CI compatibility

**Workflow**:
1. Add dependency: `uv add <package>`
2. Generate requirements: `uv pip compile pyproject.toml -o requirements.txt`
3. Commit both files

### Service-Specific Dependencies
Each service has its own `pyproject.toml`:
- **database**: asyncpg, fastapi, sqlalchemy
- **query**: langchain, langchain-openai, fastapi
- **rag**: langchain, faiss-cpu, fastapi
- **frontend**: streamlit, httpx, pandas

---

## 7. Environment Configuration

### Required Variables (.env)
```bash
# Database Configuration (NEW)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key  # For admin operations

# PostgreSQL Direct Connection (optional, for advanced use)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=db.your-project.supabase.co
POSTGRES_DATABASE=postgres
POSTGRES_PORT=5432

# LLM Provider Configuration (UNCHANGED)
DEFAULT_LLM_PROVIDER=ollama
DEFAULT_TEMPERATURE=0.7

# OpenAI Configuration (UNCHANGED)
OPENAI_API_KEY=your_key_here
OPENAI_DEFAULT_MODEL=gpt-4o-mini

# Ollama Configuration (UNCHANGED)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=deepseek-r1
OLLAMA_INSIGHTS_MODEL=deepseek-r1:14b

# Feature Flags (NEW)
ENABLE_REALTIME=false  # Future: Supabase real-time subscriptions
ENABLE_ROW_LEVEL_SECURITY=false  # Future: RLS for multi-tenant
```

---

## 8. Docker & Containerization

### Docker Strategy
Each service has its own Dockerfile optimized for:
- **Multi-stage builds**: Reduce image size
- **UV caching**: Leverage UV's cache for fast rebuilds
- **Security**: Non-root user, minimal base image

### Dockerfile Template (per service)
```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml requirements.txt ./

# Install dependencies
RUN uv pip install --system --no-cache -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/

# Set ownership
RUN chown -R appuser:appuser /app

USER appuser

# Expose port (varies per service)
EXPOSE 8000

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose Architecture
```yaml
version: '3.8'

services:
  database:
    build: ./services/database
    ports:
      - "8003:8000"
    environment:
      - POSTGRES_URL=${SUPABASE_URL}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  query:
    build: ./services/query
    ports:
      - "8001:8000"
    depends_on:
      - database
    environment:
      - DATABASE_SERVICE_URL=http://database:8000
      - LLM_PROVIDER=${DEFAULT_LLM_PROVIDER}

  rag:
    build: ./services/rag
    ports:
      - "8002:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}

  frontend:
    build: ./services/frontend
    ports:
      - "8501:8501"
    depends_on:
      - query
      - rag
      - database
    environment:
      - QUERY_SERVICE_URL=http://query:8000
      - RAG_SERVICE_URL=http://rag:8000
      - DATABASE_SERVICE_URL=http://database:8000

networks:
  default:
    driver: bridge
```

### Development vs Production
- **docker-compose.yml**: Base configuration
- **docker-compose.dev.yml**: Development overrides (hot reload, debug mode)
- **docker-compose.prod.yml**: Production overrides (replicas, resource limits)

### Running Services
```bash
# Start all services
docker-compose up --build

# Start specific service
docker-compose up database

# Development mode (hot reload)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# View logs
docker-compose logs -f query

# Stop all services
docker-compose down
```

---

## 9. Migration Challenges & Solutions

### Challenge 1: SQL Dialect Differences
**Problem**: MySQL and PostgreSQL have different syntax
- MySQL uses backticks `` ` `` for identifiers
- PostgreSQL uses double quotes `"`
- Data types differ (e.g., `TINYINT` vs `SMALLINT`)

**Solution**:
- Update LangChain prompts to generate PostgreSQL-compatible SQL
- Test query generation extensively
- Add dialect-specific handling in database adapter

### Challenge 2: LangChain SQLDatabase Integration
**Problem**: LangChain's SQLDatabase class needs proper PostgreSQL URI

**Solution**:
```python
# Old (MySQL)
mysql_uri = f'mysql+mysqlconnector://{user}:{pwd}@{host}/{db}'

# New (PostgreSQL)
postgres_uri = f'postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}'
# or
postgres_uri = f'postgresql+asyncpg://{user}:{pwd}@{host}:{port}/{db}'
```

### Challenge 3: Schema Introspection
**Problem**: MySQL `SHOW TABLES` → PostgreSQL system catalogs

**Solution**: Use SQLAlchemy inspector (already partially implemented)
```python
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
```

### Challenge 4: Connection Pooling
**Problem**: Need efficient connection management for PostgreSQL

**Solution**: Use SQLAlchemy's built-in pooling or asyncpg's pool

---

## 8. Milestones Overview (Microservices Refactor)

### Phase 1: Project Setup (Milestones 0-2)

**M0: Documentation & Planning**
- [x] INITIAL.md created (architecture decisions)
- [x] CLAUDE.md created (development guidelines)
- [ ] PROGRESS.md created (milestone tracking)
- [ ] Git branch confirmed: `claude/refactor-011CUoU3TrMfaKcn1xH1TSs9`

**M1: UV Setup & Base Structure**
- [ ] Install UV: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [ ] Create root `pyproject.toml` (project metadata)
- [ ] Create `services/` directory structure
- [ ] Create `.dockerignore` and update `.gitignore`
- [ ] Test UV: `uv --version`

**M2: Database Service (Foundation)**
- [ ] Create `services/database/` structure
- [ ] Create `pyproject.toml` for database service
- [ ] Add dependencies: asyncpg, fastapi, sqlalchemy, pydantic
- [ ] Generate `requirements.txt`: `uv pip compile pyproject.toml -o requirements.txt`
- [ ] Create `src/main.py` (FastAPI app skeleton)
- [ ] Create health check endpoint
- [ ] Create `Dockerfile` for database service
- [ ] Test service runs: `uv run uvicorn src.main:app --reload`

---

### Phase 2: Core Services (Milestones 3-6)

**M3: Database Service - PostgreSQL Integration**
- [ ] Create `src/core/connection.py` (asyncpg connection pool)
- [ ] Create `src/core/adapter.py` (PostgreSQL adapter)
- [ ] Add endpoints: `/schema/tables`, `/schema/info`, `/execute/query`
- [ ] Add Pydantic models for requests/responses
- [ ] Write unit tests
- [ ] Test with Supabase/PostgreSQL
- [ ] Validate asyncpg performance

**M4: Query Service (LangChain SQL)**
- [ ] Create `services/query/` structure
- [ ] Create `pyproject.toml` with LangChain dependencies
- [ ] Create FastAPI app with endpoints: `/query/generate`, `/query/execute`
- [ ] Port LangChain chains from old codebase
- [ ] Update prompts for PostgreSQL syntax
- [ ] Add httpx client for database service calls
- [ ] Write integration tests
- [ ] Create `Dockerfile`

**M5: RAG Service**
- [ ] Create `services/rag/` structure
- [ ] Create `pyproject.toml` with FAISS, LangChain dependencies
- [ ] Create FastAPI app with endpoints: `/rag/retrieve`, `/rag/index`
- [ ] Port vector store logic
- [ ] Add document processing utilities
- [ ] Write tests
- [ ] Create `Dockerfile`

**M6: Frontend Service**
- [ ] Create `services/frontend/` structure
- [ ] Create `pyproject.toml` with Streamlit, httpx
- [ ] Port Streamlit components from old codebase
- [ ] Create `api_client.py` (HTTP client for services)
- [ ] Update UI to call Query, RAG, Database services via HTTP
- [ ] Test local Streamlit app
- [ ] Create `Dockerfile`

---

### Phase 3: Docker & Orchestration (Milestones 7-8)

**M7: Docker Compose Setup**
- [ ] Create `docker-compose.yml` with all 4 services
- [ ] Add PostgreSQL service (or use Supabase URL)
- [ ] Configure networking (bridge network for services)
- [ ] Add health checks
- [ ] Create `docker-compose.dev.yml` (dev overrides, hot reload)
- [ ] Test: `docker-compose up --build`
- [ ] Validate inter-service communication

**M8: Environment & Secrets Management**
- [ ] Create `.env.example` for each service
- [ ] Create root `.env.example` (docker-compose variables)
- [ ] Add validation for required environment variables
- [ ] Test with missing variables (graceful errors)
- [ ] Document environment setup in readme.md

---

### Phase 4: Testing & Validation (Milestones 9-10)

**M9: Integration Testing**
- [ ] Create `tests/test_integration.py` (cross-service tests)
- [ ] Test: Frontend → Query → Database flow
- [ ] Test: Frontend → RAG → Query flow
- [ ] Test: Error handling across services
- [ ] Test: All services running in Docker
- [ ] Validate performance benchmarks

**M10: End-to-End Testing**
- [ ] Create `tests/test_e2e.py`
- [ ] Test full user flow: NL query → SQL → Results → Visualization
- [ ] Test RAG-enhanced queries
- [ ] Test insights generation
- [ ] Test export functionality
- [ ] Validate 70%+ test coverage

---

### Phase 5: Cleanup & Documentation (Milestones 11-12)

**M11: Code Cleanup**
- [ ] Remove old monolithic code (src/, config/)
- [ ] Archive scripts/mysql/ to docs/legacy/
- [ ] Remove mysql-connector-python from requirements
- [ ] Clean up unused dependencies
- [ ] Run linters (ruff, black)
- [ ] Validate all tests pass

**M12: Documentation & Handoff**
- [ ] Update readme.md with microservices setup
- [ ] Create docs/architecture.md with diagrams
- [ ] Create docs/api.md (API documentation for services)
- [ ] Create docs/deployment.md (Docker, cloud deployment)
- [ ] Add migration guide (MySQL → PostgreSQL)
- [ ] Archive INITIAL.md to docs/
- [ ] Final commit and push

---

## 9. Performance & Cost Targets

### Performance
- API Response Time: <2000ms (same as MySQL)
- Database Query Time: <500ms (should improve with PostgreSQL)
- End-to-End Latency: <3s (unchanged)
- Schema Introspection: <1s (should improve)

### Cost (Supabase Free Tier)
- Database: 500MB free (sufficient for MVP)
- API Requests: Unlimited on free tier
- Bandwidth: 2GB/month free

**Note**: For production, consider Supabase Pro ($25/month) or self-hosted PostgreSQL

---

## 10. Testing Strategy

### Test Coverage Goals
- Database adapter: 90%+ (critical for reliability)
- Service layer: 70%+
- UI components: 50%+ (focus on logic, not Streamlit widgets)

### Test Types
1. **Unit Tests** (`tests/test_database.py`):
   - Connection establishment
   - Schema introspection
   - Query execution
   - Error handling

2. **Integration Tests** (`tests/test_integration.py`):
   - LangChain + PostgreSQL
   - RAG + PostgreSQL
   - Full query pipeline

3. **Supabase-Specific Tests** (`tests/test_supabase_connection.py`):
   - Supabase client initialization
   - Auth token validation
   - Direct vs SQLAlchemy access

---

## 11. Risks & Mitigation

### Risk 1: Breaking Changes
**Impact**: High
**Probability**: Medium
**Mitigation**:
- Keep MySQL code in separate branch until PostgreSQL fully validated
- Create migration script for users
- Extensive testing before merge to main

### Risk 2: LangChain Compatibility Issues
**Impact**: High
**Probability**: Low
**Mitigation**:
- LangChain supports PostgreSQL well
- Test early and often
- Fallback to direct SQLAlchemy if needed

### Risk 3: Missing PostgreSQL Features in Prompts
**Impact**: Medium
**Probability**: Medium
**Mitigation**:
- Update LLM prompts to specify PostgreSQL syntax
- Test with various query types
- Add prompt examples for PostgreSQL-specific features

---

## 12. Future Enhancements (Post-Refactor)

### Short-term (After MVP)
- [ ] Use PostgreSQL JSONB for storing query history
- [ ] Implement full-text search on table descriptions
- [ ] Add support for PostgreSQL views and materialized views

### Medium-term
- [ ] Integrate Supabase Auth for multi-user support
- [ ] Use Supabase real-time for live query notifications
- [ ] Implement Row-Level Security (RLS) for multi-tenant

### Long-term
- [ ] Support for PostGIS (geospatial queries)
- [ ] Integration with pgvector for semantic search
- [ ] Advanced PostgreSQL features (CTEs, window functions)

---

## 13. Decision Log

### Decision 1: psycopg2 vs asyncpg
**Date**: 2025-11-04
**Decision**: Start with **psycopg2-binary**
**Rationale**:
- Simpler synchronous interface matches current codebase
- Better LangChain compatibility
- Easier migration path
- Can migrate to asyncpg later if performance needed

### Decision 2: Direct Supabase Client vs SQLAlchemy
**Date**: 2025-11-04
**Decision**: Use **SQLAlchemy** as primary interface
**Rationale**:
- LangChain requires SQLAlchemy
- More portable (easier to switch providers)
- Keep Supabase client for future features (auth, real-time)

### Decision 3: Keep FAISS or Migrate to pgvector?
**Date**: 2025-11-04
**Decision**: Keep **FAISS** for MVP
**Rationale**:
- FAISS works well for current use case
- Avoid scope creep
- Can migrate to pgvector in Phase 2

---

## 14. Handoff to CLAUDE.md

Once INITIAL.md is complete:
1. ✅ Archive this document to `/docs/INITIAL.md`
2. ✅ Create CLAUDE.md with iterative work guidelines
3. ✅ Create PROGRESS.md for milestone tracking
4. ✅ Begin Milestone 0 implementation

**Note**: CLAUDE.md should reference INITIAL.md ONLY for architectural clarifications.

---

## 15. Resources & References

### Documentation
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [LangChain SQL Agents](https://python.langchain.com/docs/use_cases/sql/)
- [SQLAlchemy PostgreSQL Dialect](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html)

### Migration Guides
- [MySQL to PostgreSQL Migration](https://wiki.postgresql.org/wiki/Converting_from_other_Databases_to_PostgreSQL#MySQL)
- [Supabase Quickstart](https://supabase.com/docs/guides/database/overview)

---

**Document Status**: ✅ Complete
**Ready for**: CLAUDE.md creation and Milestone 0 kickoff
