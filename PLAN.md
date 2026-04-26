# AlphaForge — Master Plan Index

Central index of all module-level plans. Each module maintains its own `PLAN.md` with full goals, phases, and design decisions.

## Module Plans

| Module | Plan | Status |
|--------|------|--------|
| **Screener** | [screener/PLAN.md](screener/PLAN.md) | Active |
| **LLM Gateway** | [llm-gateway/PLAN.md](llm-gateway/PLAN.md) | Implemented (Phase 1-12) |
| **Vector DB / Memory Lake** | [backend/PLAN_memory.md](backend/PLAN_memory.md) | Implemented |
| **Repo Context MCP** | [repo-context-mcp/PLAN.md](repo-context-mcp/PLAN.md) | Implemented (v0.1) |
| **Solar Orb UI** | [packages/solar-orb-ui/PLAN.md](packages/solar-orb-ui/PLAN.md) | Phases 1-4 components complete |
| **Solar Orb Ball** | [packages/solar-orb-ball/PLAN.md](packages/solar-orb-ball/PLAN.md) | Phase 1 complete (lib + playground) |

## Conventions

File layout + variable naming rules per module live under [structure/](structure/README.md):

| Module | Files | Variables |
|--------|-------|-----------|
| Frontend | [structure/frontend/files.md](structure/frontend/files.md) | [structure/frontend/variables.md](structure/frontend/variables.md) |
| Backend | [structure/backend/files.md](structure/backend/files.md) | [structure/backend/variables.md](structure/backend/variables.md) |
| LLM Gateway | [structure/llm-gateway/files.md](structure/llm-gateway/files.md) | [structure/llm-gateway/variables.md](structure/llm-gateway/variables.md) |
| Screener | [structure/screener/files.md](structure/screener/files.md) | [structure/screener/variables.md](structure/screener/variables.md) |
