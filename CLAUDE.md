# Khipu AI Refactor - Developer Guidelines

**Version**: 1.0
**Last Updated**: 2025-11-04
**Branch**: claude/refactor-011CUoU3TrMfaKcn1xH1TSs9

---

## 1. Project Context

### Quick Overview
Khipu AI is an intelligent data analysis assistant that translates natural language queries into SQL using LangChain and RAG. We are **refactoring from a MySQL monolith to a microservices architecture with Supabase/PostgreSQL**, using **UV for package management** and **Docker for containerization**. This enables maximum portability, scalability, and modern cloud-native features.

### Current Phase
**Setup / Microservices Architecture Design**

### Architecture Reference
**See INITIAL.md** (will be archived in `/docs/`) for:
- Complete refactor rationale (Monolith → Microservices)
- Database migration (MySQL → PostgreSQL/Supabase)
- UV and Docker setup
- Service architecture and responsibilities
- Milestone breakdown (12 milestones total)

**Do NOT re-read INITIAL.md unless**:
- Clarifying microservices architecture
- Reviewing service boundaries
- Understanding Docker/UV setup
- User explicitly requests architectural context

---

## 2. Development Philosophy

### A. Incremental Validation (CRITICAL)
- **Never** write >100 lines before testing
- **Always** test → commit → move forward
- **Each milestone** is a validated checkpoint
- **Especially important** for database layer changes

### B. Test-Driven Workflow
```
✅ Write code (50-100 lines)
✅ Write test
✅ Validate test passes
✅ Commit: [milestone-X] Description
✅ Update PROGRESS.md
✅ Continue to next step
```

### C. Token Efficiency
- Read PROGRESS.md to understand current state
- Read CLAUDE.md (this file) for standards
- Read INITIAL.md ONLY if architecture context needed
- Avoid re-reading large files unnecessarily

### D. Refactor-Specific Principles
- **Build incrementally**: One service at a time
- **Test each service independently** before integration
- **Use UV for all dependencies**: Fast, reliable, deterministic
- **Dockerize early**: Ensure portability from day one
- **Keep old monolith code** until all services validated
- **Document service APIs**: Clear contracts between services

---

## 3. Coding Standards

### A. Python Standards
- Python 3.11+ features
- **Type hints on ALL functions** (critical for microservices)
- **Async-first**: Use async/await for all I/O operations
- **Pydantic V2** for all request/response models (strict mode)
- **FastAPI** for all service APIs (except frontend)
- Use descriptive variable names
- Follow REST conventions for endpoints

### B. Service Layer Standards (FastAPI)
```python
# Good: Async, type-hinted, Pydantic models
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class SchemaRequest(BaseModel):
    tables: list[str] | None = None

class SchemaResponse(BaseModel):
    schema_info: str
    table_count: int

@app.post("/schema/info", response_model=SchemaResponse)
async def get_schema_info(request: SchemaRequest) -> SchemaResponse:
    """Get schema information for specified tables"""
    try:
        schema = await db_adapter.get_schema(request.tables)
        return SchemaResponse(
            schema_info=schema,
            table_count=len(request.tables) if request.tables else 0
        )
    except Exception as e:
        logger.error(f"Schema error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Bad: Sync, no types, no validation
@app.post("/schema")
def get_schema(tables):
    return db_adapter.get_schema(tables)
```

### C. File Organization (Microservices)
- **Max 500 lines per file**
- Each service follows FastAPI best practices:
  - `src/main.py`: FastAPI app initialization
  - `src/api/endpoints/`: Route definitions
  - `src/core/`: Business logic
  - `src/models/`: Pydantic models (request/response)
  - `src/utils/`: Utilities
- Group by feature within each service
- Keep services small and focused (single responsibility)

### D. Naming Conventions
- Functions: `verb_noun` (e.g., `get_schema`, `test_connection`)
- Classes: `PascalCase` (e.g., `DatabaseAdapter`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `POSTGRES_URI`)
- Files: `snake_case.py`

---

## 4. Testing Requirements

### A. Coverage Requirements
- **Database layer: 80%+ minimum** (critical for refactor)
- Service layer: 70%+
- UI components: 50%+ (focus on logic)

### B. Test Types Required
1. **Unit Tests** (`tests/test_database.py`):
   - Connection establishment
   - Schema introspection
   - Query execution
   - Error handling

2. **Integration Tests** (`tests/test_integration.py`):
   - LangChain + PostgreSQL
   - Full query pipeline
   - RAG integration

3. **Supabase Tests** (`tests/test_supabase_connection.py`):
   - Supabase client initialization
   - Connection validation
   - Auth token handling

### C. Test Structure
```python
# tests/test_database.py
import pytest
from src.utils.database import get_all_tables, test_database_connection

def test_connection_success():
    """Test successful PostgreSQL connection"""
    result = test_database_connection()
    assert result["success"] == True
    assert "tables" in result
    assert result["error"] is None

def test_get_all_tables():
    """Test retrieving all tables from PostgreSQL"""
    tables = get_all_tables()
    assert isinstance(tables, list)
    assert len(tables) > 0

def test_connection_failure():
    """Test connection with invalid credentials"""
    # Mock invalid credentials
    result = test_database_connection()
    assert result["success"] == False
    assert result["error"] is not None
```

### D. Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_database.py -v

# Run with coverage
pytest --cov=src tests/ --cov-report=html
```

---

## 5. Git Workflow

### A. Branch Strategy
- **Current Branch**: `claude/refactor-011CUoU3TrMfaKcn1xH1TSs9`
- **Commit After**: Each validated milestone
- **Push After**: Each milestone or daily (whichever first)

### B. Commit Format
```
[milestone-X] Short description

Examples:
[milestone-0] Setup refactor documentation (INITIAL, CLAUDE, PROGRESS)
[milestone-1] Add Supabase dependencies and environment config
[milestone-2] Refactor database.py for PostgreSQL compatibility
[milestone-3] Update config.py with Supabase variables
```

### C. Commit Checklist
Before committing:
- [ ] All tests pass (`pytest tests/ -v`)
- [ ] Code follows standards
- [ ] No debug prints or commented code
- [ ] PROGRESS.md updated
- [ ] Type hints added

---

## 6. Documentation Requirements

### A. Inline Documentation
```python
def get_schema(selected_tables: Optional[List[str]] = None) -> str:
    """
    Get schema information for selected tables using PostgreSQL.

    Args:
        selected_tables: List of table names to include. If None, uses all tables.

    Returns:
        Schema information as formatted string

    Raises:
        Exception: If database connection not initialized

    Note:
        This function now uses PostgreSQL system catalogs via SQLAlchemy.
    """
    # Implementation...
```

### B. Update PROGRESS.md After Each Milestone
- Mark milestone status (⏳/🔄/✅/❌)
- Update test counter
- Log commit hash
- Note any blockers or issues

### C. Migration Notes
When making breaking changes, document:
- What changed
- Why it changed
- How to migrate (for users)

---

## 7. Error Handling

### A. Database-Specific Error Handling
```python
from sqlalchemy.exc import SQLAlchemyError
import psycopg2

def get_all_tables() -> List[str]:
    """Get all tables from PostgreSQL"""
    try:
        inspector = inspect(engine)
        return inspector.get_table_names()
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error: {str(e)}")
        return []
    except psycopg2.Error as e:
        logger.error(f"PostgreSQL error: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return []
```

### B. Connection Error Handling
```python
def test_database_connection() -> Dict:
    """Test PostgreSQL/Supabase connection"""
    try:
        # Test connection
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DATABASE,
            port=POSTGRES_PORT
        )

        if conn:
            # Connection successful
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()

            cursor.close()
            conn.close()

            return {
                "success": True,
                "version": version[0],
                "error": None
            }
    except psycopg2.OperationalError as e:
        logger.error(f"Connection error: {str(e)}")
        return {
            "success": False,
            "version": None,
            "error": f"Connection failed: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            "success": False,
            "version": None,
            "error": str(e)
        }
```

---

## 8. Performance Guidelines

### A. Optimization Priorities
1. **Correctness** > Performance (always)
2. **Compatibility** > Optimization (during refactor)
3. **Readability** > Cleverness
4. **Connection Pooling** for PostgreSQL (use SQLAlchemy pool)
5. **Lazy Loading** for schema introspection

### B. PostgreSQL-Specific Performance
- Use prepared statements (SQLAlchemy handles this)
- Leverage PostgreSQL indexes
- Use EXPLAIN ANALYZE for slow queries
- Consider connection pooling for high-load scenarios

### C. Monitoring Points
- Database connection time
- Schema introspection time
- Query execution time
- LangChain query generation time

---

## 9. Communication Protocol

### A. When Starting Work
1. Read **PROGRESS.md** → Understand current milestone
2. Read **CLAUDE.md** (this file) → Refresh on standards
3. Check git log → Verify last validated commit
4. Optional: Read INITIAL.md if architecture context needed

### B. After Completing Milestone
1. Run all tests: `pytest tests/ -v`
2. Commit: `git commit -m "[milestone-X] Description"`
3. Push: `git push -u origin claude/refactor-011CUoU3TrMfaKcn1xH1TSs9`
4. Update PROGRESS.md with status, test count, commit hash

### C. If Interrupted
- Check PROGRESS.md for last completed milestone
- Check git log for last commit
- Resume from last validated checkpoint

---

## 10. Refactor-Specific Guidelines

### A. Database Migration Checklist
For each database function:
- [ ] Identify MySQL-specific code
- [ ] Research PostgreSQL equivalent
- [ ] Update function implementation
- [ ] Update type hints
- [ ] Write test
- [ ] Validate test passes
- [ ] Update documentation

### B. SQL Dialect Changes
```python
# MySQL
query = f"SHOW TABLES FROM {database}"
query = f"SELECT * FROM `table` WHERE `column` = 1"

# PostgreSQL
query = "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'"
query = f'SELECT * FROM "table" WHERE "column" = 1'
```

### C. Connection String Changes
```python
# Old (MySQL)
mysql_uri = f'mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:3306/{MYSQL_DATABASE}'

# New (PostgreSQL)
postgres_uri = f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}'
```

### D. LangChain Integration
```python
from langchain_community.utilities import SQLDatabase

# Ensure PostgreSQL URI format is correct
postgres_uri = f'postgresql+psycopg2://...'

# Initialize LangChain SQLDatabase
db = SQLDatabase.from_uri(postgres_uri)

# Update prompts to specify PostgreSQL syntax
system_prompt = """You are a PostgreSQL expert. Generate valid PostgreSQL queries.
Use double quotes for identifiers, not backticks.
Use PostgreSQL data types and functions."""
```

---

## 11. Related Documents

- **INITIAL.md** (`/docs/INITIAL.md` after archival) - Architectural decisions, refactor rationale
- **PROGRESS.md** (root) - Milestone tracking (read at start of each session)
- **readme.md** (root) - User-facing documentation (update after refactor complete)
- **.env.example** (root) - Environment template (update with Supabase vars)

---

## 12. Quick Reference

### Commands to Remember
```bash
# UV package management
uv --version
uv add <package>
uv pip compile pyproject.toml -o requirements.txt
uv run <command>

# Run specific service (local)
cd services/database/
uv run uvicorn src.main:app --reload --port 8003

# Run tests
pytest tests/ -v
pytest --cov=src tests/ --cov-report=html

# Docker operations
docker-compose up --build
docker-compose up database  # Single service
docker-compose logs -f query
docker-compose down

# Test service health
curl http://localhost:8003/health  # Database service
curl http://localhost:8001/health  # Query service
```

### Files to Update Per Milestone
- [ ] Service code (services/{service}/src/)
- [ ] Service tests (services/{service}/tests/)
- [ ] pyproject.toml (dependencies)
- [ ] requirements.txt (generated from pyproject.toml)
- [ ] Dockerfile (if needed)
- [ ] PROGRESS.md (status update)
- [ ] Git commit (validated work)

---

## 13. Environment Setup

### Required Environment Variables
```bash
# PostgreSQL/Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=db.your-project.supabase.co
POSTGRES_DATABASE=postgres
POSTGRES_PORT=5432

# LLM (unchanged)
DEFAULT_LLM_PROVIDER=ollama
OPENAI_API_KEY=your_key
OLLAMA_BASE_URL=http://localhost:11434
```

### Testing Environment
- Ensure you have access to a Supabase project OR local PostgreSQL
- Test connection before starting development
- Use test database (not production)

---

## 14. Key Principles (Remember Always)

1. ✅ **Small steps, frequent validation** (one service at a time)
2. ✅ **Test before moving forward** (each service independently)
3. ✅ **Commit validated milestones** (safe rollback points)
4. ✅ **Update PROGRESS.md after each milestone** (maintain context)
5. ✅ **Type hints everywhere** (critical for microservices)
6. ✅ **Use UV for all dependencies** (fast, reliable)
7. ✅ **Dockerize early** (ensure portability from start)
8. ✅ **Async-first** (all I/O operations)
9. ✅ **Pydantic models for all APIs** (type safety)
10. ✅ **Keep old monolith** until all services validated
11. ✅ **Document service contracts** (API specs)
12. ✅ **Test with real services** (Docker Compose)

---

## 15. Troubleshooting Common Issues

### Issue 1: psycopg2 Installation Fails
**Solution**:
```bash
# Use binary version
pip install psycopg2-binary

# Or install PostgreSQL dev headers first
# Ubuntu/Debian
sudo apt-get install libpq-dev python3-dev

# macOS
brew install postgresql
```

### Issue 2: SQLAlchemy Connection Fails
**Solution**:
- Verify connection string format
- Check firewall rules (Supabase requires internet access)
- Validate credentials in .env
- Test with psycopg2 directly first

### Issue 3: LangChain Generates MySQL Syntax
**Solution**:
- Update system prompts to specify PostgreSQL
- Add examples of PostgreSQL queries
- Test with various query types

---

**Last Review**: 2025-11-04
**Next Review**: After Milestone 2 (database layer refactor complete)

---

**Ready to start development! Begin with Milestone 0.**
