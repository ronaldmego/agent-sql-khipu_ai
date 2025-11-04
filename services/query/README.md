# Query Service

**Port**: 8001
**Purpose**: Natural language to SQL query generation using LangChain

## Overview
This service translates natural language questions into SQL queries using LangChain and LLMs. It handles:
- NL to SQL conversion
- LLM provider abstraction (Gemini, OpenAI)
- Query validation
- Result formatting

## API Endpoints
- `GET /health` - Health check
- `POST /query/generate` - Generate SQL from natural language
- `POST /query/execute` - Generate and execute SQL query
- `GET /query/history` - Query history (future)

## Tech Stack
- FastAPI
- LangChain
- LangChain-Gemini
- LangChain-OpenAI
- httpx (for database service calls)

## Development
```bash
cd services/query
uv run uvicorn src.main:app --reload --port 8001
```

## Environment Variables
- `DATABASE_SERVICE_URL`: Database service URL (default: http://database:8000)
- `LLM_PROVIDER`: LLM provider (gemini, openai)
- `GEMINI_API_KEY`: Gemini API key
- `OPENAI_API_KEY`: OpenAI API key
- `DEFAULT_TEMPERATURE`: LLM temperature (default: 0.7)
