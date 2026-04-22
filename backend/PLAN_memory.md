# Vector DB / Memory Lake — Plan

## Goal
Add semantic search and RAG to AlphaForge's AI chat using pgvector on existing PostgreSQL, eliminating the need for a separate vector database service.

## Design Decisions
- **pgvector** over hosted vector DBs (Pinecone, Weaviate): zero new infrastructure, single PostgreSQL instance
- **Gemini text-embedding-004** (free, 768-dim) over local sentence-transformers: no RAM overhead, state-of-the-art quality
- **Direct httpx** over LangChain PGVector abstraction: simpler session management, fewer hidden dependencies
- **RAG_CHAT QueryType** added to gateway: Gemini first (best context window), Groq fallback

## Architecture
```
Screener picks → POST /screener/picks → background embed → screener_pick_embeddings (pgvector)
User message → search_picks + search_memory → augmented system prompt → LLM → reply
Reply + user message → save_turn → conversation_memories (pgvector)
```

## Phases Completed
1. pgvector compiled from source (v0.8.0) for PostgreSQL 16
2. `pgvector>=0.3.0` added to backend/pyproject.toml
3. Embedding settings added to config.py
4. `backend/app/models/memory.py` — ScreenerPickEmbedding, ConversationMemory ORM models
5. Alembic auto-generated migration (all tables including pgvector)
6. `backend/app/services/embedding.py` — EmbeddingService (Gemini + mock fallback)
7. `backend/app/services/memory.py` — MemoryService (index, search picks + conversations)
8. LLM gateway: RAG_CHAT QueryType, routing, system prompt
9. `backend/app/services/ai_service.py` — full RAG chat() implementation
10. `backend/app/routes/ai.py` — updated ChatRequest/Response, /ai/memory/search endpoint
11. `backend/app/routes/screener.py` — auto-embed on push, backfill endpoint
12. `backend/app/main.py` — embedding service lifecycle in lifespan()

## Status: Complete — 2026-04-22
