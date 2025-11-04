# Frontend Service

**Port**: 8501
**Purpose**: Streamlit user interface for natural language data analysis

## Overview
This service provides the web-based UI for interacting with the system. It handles:
- Natural language query input
- Results visualization
- Query history
- Export functionality

## Features
- Interactive query interface
- Automatic visualization generation
- Real-time insights
- Debug panel
- Multi-language support

## Tech Stack
- Streamlit
- httpx (async HTTP client)
- Pandas (data manipulation)
- Matplotlib/Seaborn (visualization)

## Development
```bash
cd services/frontend
uv run streamlit run src/pages/Home.py
```

## Environment Variables
- `QUERY_SERVICE_URL`: Query service URL (default: http://query:8000)
- `RAG_SERVICE_URL`: RAG service URL (default: http://rag:8000)
- `DATABASE_SERVICE_URL`: Database service URL (default: http://database:8000)
