# repo-context-mcp

Tool-agnostic MCP server that gives **any coding agent** (Claude Code, GitHub Copilot, Cursor, Cline, Zed, Windsurf — or anything that speaks MCP tomorrow) rich semantic + structural context over the AlphaForge monorepo.

One local process. Many clients. Same view.

---

## What it exposes

| Tool | Purpose |
|------|---------|
| `search_code(query, k, lang?, path_prefix?)` | Semantic search over all source files via pgvector |
| `get_symbol(name, kind?)` | Find a function / class / interface / type by name |
| `module_overview(path)` | Nearest CLAUDE.md + PLAN.md + README.md for any module |
| `recent_changes(limit, path?)` | Thin `git log` wrapper |
| `read_file_range(path, start, end)` | Bounded file read (max 500 lines) |

---

## How it works

```
[your editor]──MCP stdio──▶[alphaforge-repo-context-mcp]
                                 │
                                 ├── tools/ (search_code, get_symbol, …)
                                 ├── pgvector (repo_chunks table)
                                 └── Gemini text-embedding-004 (768d, free)
```

- Indexer walks the repo → chunks files (AST for Python, regex for TS/TSX, sections for MD) → embeds → writes to `repo_chunks`.
- Server runs over stdio — compatible with every current MCP client.
- Incremental re-index by `content_hash` — only changed chunks hit the embedding API.

---

## Setup

### 1. Install

```bash
cd repo-context-mcp
pdm install
```

### 2. Environment

The server reads from the repo-root `.env` / `.env.cred`. Required:

```
GEMINI_API_KEY=...
DATABASE_URL=postgresql+asyncpg://alphaforge:alphaforge@localhost:5432/alphaforge
```

### 3. Build the index (one-time)

```bash
pdm run index --full
```

Free-tier Gemini embedding paces at ~1 rpm, so the first run takes a while. Subsequent runs only embed changed chunks.

### 4. (Optional) Watch mode

```bash
pdm run index --watch
```

---

## Wire it into your editor

All clients use the same pattern — point at the local stdio command.

### Claude Code

Add to `.claude/settings.json` (or `~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "alpha-forge-context": {
      "command": "alphaforge-repo-context-mcp"
    }
  }
}
```

Or, without installing the console script:

```json
{
  "mcpServers": {
    "alpha-forge-context": {
      "command": "python",
      "args": ["-m", "alphaforge_repo_context.server"],
      "cwd": "/absolute/path/to/alpha-forge/repo-context-mcp"
    }
  }
}
```

### GitHub Copilot (VS Code)

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "alpha-forge-context": {
      "command": "alphaforge-repo-context-mcp"
    }
  }
}
```

### Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "alpha-forge-context": {
      "command": "alphaforge-repo-context-mcp"
    }
  }
}
```

### Cline / Zed / Windsurf

All use the same JSON shape under their respective `mcpServers` / `mcp.servers` keys. Paste the same command.

---

## CLI

```bash
alphaforge-repo-context-index --full     # full reindex
alphaforge-repo-context-index --watch    # watch + incremental
alphaforge-repo-context-mcp              # run MCP server (stdio)
```

---

## Schema

Single new table `repo_chunks` (pgvector). Created on first run — no manual migration needed for v1. See [PLAN.md](PLAN.md) for the schema + roadmap.

---

## License

MIT. See root [LICENSE](../LICENSE).
