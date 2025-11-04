# RAG Service

**Port**: 8002
**Purpose**: Retrieval Augmented Generation for context-aware query enhancement

## Overview
This service provides document indexing and retrieval using FAISS vector store. It handles:
- Document processing and embedding
- Vector similarity search
- Context retrieval for query enhancement
- Domain-specific knowledge integration

## API Endpoints
- `GET /health` - Health check
- `POST /rag/index` - Index documents
- `POST /rag/retrieve` - Retrieve relevant context
- `GET /rag/status` - Index status

## Tech Stack
- FastAPI
- LangChain
- FAISS (vector store)
- OpenAI Embeddings (or Gemini)

## Development
```bash
cd services/rag
uv run uvicorn src.main:app --reload --port 8002
```

## Environment Variables
- `OPENAI_API_KEY`: OpenAI API key (for embeddings)
- `FAISS_INDEX_PATH`: Path to FAISS index storage
- `EMBEDDING_MODEL`: Embedding model (default: text-embedding-3-small)
