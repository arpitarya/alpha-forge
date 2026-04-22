# repo-context-mcp — Plan

Tool-agnostic MCP server that gives coding agents (Claude Code, GitHub Copilot, Cursor, Cline, Zed, Windsurf, or any future MCP-capable client) rich semantic and structural context over the AlphaForge monorepo.

## Goal

One local process, many clients. Every coding agent you use — today or tomorrow — gets the same view of the repo: semantic search, symbol lookup, recent changes, module overviews.

## Why MCP

- Transport-agnostic standard (stdio / SSE / HTTP)
- Supported natively by Claude Code, VS Code (Copilot), Cursor, Zed, Cline, Windsurf
- New clients adopt it by default — one integration point, no per-client code
- Runs as a local subprocess; zero network boundary by default

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Language | Python 3.14 | Match `llm-gateway/` sibling; reuse `alphaforge-llm-gateway` + embedding patterns |
| Transport | stdio (default) | Works universally across MCP clients |
| Vector store | Postgres + pgvector | Already running; tables live alongside existing `screener_pick_embeddings` |
| Embeddings | Gemini `text-embedding-004` (768d) | Free tier, already wired via Gemini API key in `.env` |
| Chunking | AST-aware for `.py` / `.ts` / `.tsx`, line-window for rest | Keep function/class boundaries when possible |
| Watcher | `watchfiles` | Debounced, cross-platform, minimal deps |
| Ignore rules | Parse `.gitignore` + built-in deny list | No `.venv`, `node_modules`, `dist`, `.next`, lockfiles |
| Package | PDM + `pdm-backend` | Matches repo convention |

## Phases

### Phase 1 — Scaffolding (this PR)
- Directory layout, `pyproject.toml`, `PLAN.md`, `implement.txt`
- Root doc wiring (`PLAN.md`, `implement.txt`, `CLAUDE.md`)

### Phase 2 — DB schema
- New table `repo_chunks` (separate from screener/conversation memory):
  - `id`, `path`, `chunk_index`, `start_line`, `end_line`, `symbol`, `kind`, `lang`
  - `content`, `content_hash`, `embedding Vector(768)`, `updated_at`
- Alembic migration in `backend/alembic/` (keeps all migrations in one place)

### Phase 3 — Indexer
- Walk repo respecting `.gitignore` + deny list
- Chunk files:
  - Python: `ast` → top-level defs/classes
  - TS/TSX/JS/JSX: regex-based symbol split (good enough v1)
  - Markdown: by `##` sections
  - Other: 80-line sliding window, 20-line overlap
- Skip unchanged chunks via `content_hash`
- Batch embed (respect Gemini 1 RPM free tier or use higher-quota model)
- CLI: `alphaforge-repo-context-index [--full|--changed]`

### Phase 4 — MCP server
- Tools exposed:
  - `search_code(query, k=8, lang?, path_prefix?)` — semantic search
  - `get_symbol(name, kind?)` — find function/class definitions
  - `module_overview(path)` — list key files + read nearest `CLAUDE.md` / `PLAN.md` / `README.md`
  - `recent_changes(limit=20, path?)` — `git log` wrapper with diffs
  - `read_file_range(path, start, end)` — safe bounded file read
- Resources exposed:
  - `repo://tree` — directory structure
  - `repo://claude-md` — aggregated CLAUDE.md files

### Phase 5 — Watcher
- `watchfiles` on repo root (respecting ignore rules)
- Debounced re-index of changed files only
- Optional — the indexer CLI + editor save hooks are sufficient for v1

### Phase 6 — Client configs
- Document `.vscode/mcp.json`, `.claude/settings.json`, Cursor, Cline snippets in `README.md`
- All point at the same local stdio binary

## Non-Goals (for now)

- Cloud hosting / multi-user — this is a personal tool
- Cross-repo context — scoped to AlphaForge
- Write operations (edits, commits) — read-only

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Gemini free tier (1 RPM embedding) slow on full reindex | Cache by `content_hash`; incremental re-index only touches changed chunks |
| pgvector index choice affects recall | Start with IVFFlat; swap to HNSW later if needed |
| MCP client API drift | Pin `mcp>=1.0.0`; the stable protocol surface is small |
