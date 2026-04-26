# AlphaForge — Code Structure & Conventions

> Single index for "how do we organise files and name things" across every module.
> When in doubt during a code review, point at one of these docs.

Each module has two files:

- **`files.md`** — directory layout, layered architecture, what goes where, anti-patterns.
- **`variables.md`** — naming conventions for variables, functions, types, constants, and domain vocabulary.

---

## Modules

| Module | Files | Variables |
|--------|-------|-----------|
| **Frontend** (Next.js + React + Tailwind) | [frontend/files.md](frontend/files.md) | [frontend/variables.md](frontend/variables.md) |
| **Backend** (FastAPI + SQLAlchemy async) | [backend/files.md](backend/files.md) | [backend/variables.md](backend/variables.md) |
| **LLM Gateway** (multi-provider, $0 cost wall) | [llm-gateway/files.md](llm-gateway/files.md) | [llm-gateway/variables.md](llm-gateway/variables.md) |
| **Screener** (offline ML pipeline + service) | [screener/files.md](screener/files.md) | [screener/variables.md](screener/variables.md) |

---

## Cross-module rules

These apply everywhere — no exceptions, regardless of language:

1. **One file = one responsibility.** A component, a service, an ORM class, a stage. Soft caps stated per module; exceeding them is a signal to split, not a comment to add.
2. **Names are descriptive, not abbreviated.** `selectedSourceSlug` over `s`, `total_invested_inr` over `total`. Industry-standard short names (`id`, `url`, `dto`, `pnl`, `rsi`) are fine.
3. **Booleans start with a question word.** `is_*`, `has_*`, `should_*`, `can_*`, `did_*`, `will_*`. A bare `disabled` is ambiguous on a multi-arg call.
4. **Units in numeric names.** `refresh_interval_ms`, `lookback_days`, `cost_usd`, `pnl_pct`. Never `time = 5000`.
5. **No paid SDKs / paid feeds without a flag.** The whole project is free-tier-first; if a paid integration ships later, it sits behind an explicit setting.
6. **Disclaimer required on financial payloads.** Anything returned from a route that contains positions, picks, or alpha must include the literal `"Not SEBI registered investment advice."` — and there is a test for it.
7. **Logs over prints.** Every module uses its language's logger (`alphaforge-logger` Python, `@alphaforge/logger` Node) with module-scoped names.
8. **Tests live next to the code they test** (frontend) or in a parallel `tests/` tree (Python).
9. **Async by default** for any I/O. Synchronous I/O calls are an immediate review block.
10. **Never log prompt/response bodies** in the LLM Gateway — metadata only.

---

## Casing summary across modules

| Concept | Frontend (TS) | Backend / LLM Gateway / Screener (Py) |
|---------|---------------|---------------------------------------|
| Variable / function | `camelCase` | `snake_case` |
| Class / type | `PascalCase` | `PascalCase` |
| Constant | `UPPER_SNAKE_CASE` | `UPPER_SNAKE_CASE` |
| File (component) | `PascalCase.tsx` | — |
| File (other) | `kebab.dot.case.ts` | `snake_case.py` |
| URL path segment | `kebab-case` | `kebab-case` |
| API query param | `snake_case` (matches backend) | `snake_case` |
| JSON wire field (raw DTO) | `snake_case` | `snake_case` |
| JSON field after transformer | `camelCase` | n/a (transformer is on the FE side) |
| Env var | `UPPER_SNAKE_CASE` namespace-prefixed | same |

---

## Adding a new module

When a new top-level module lands (e.g. `mobile/`, `bots/`, `data-lake/`):

1. Create `structure/<module>/files.md` describing layout + responsibilities.
2. Create `structure/<module>/variables.md` describing naming patterns specific to that module.
3. Add an entry to the **Modules** table above.
4. Link the new module from the root [PLAN.md](../PLAN.md) and [implement.txt](../implement.txt) trackers.

The two new files should follow the structure of the existing ones — short universal-rules section, casing matrix, variable/file templates, and a quick-reference card at the bottom.

---

## Where this connects to runtime docs

- [PLAN.md](../PLAN.md) — design plans per module (the "what we're building and why").
- [implement.txt](../implement.txt) — implementation logs per module (the "what shipped, when, and why").
- [CLAUDE.md](../CLAUDE.md) — high-level repo guardrails for AI agents.
- [docs/](../docs/) — narrative guides (`WHY.md`, `WHAT.md`, `HOW.md`, `GETTING_STARTED.md`).

`structure/` is the **enforcement** doc — it answers "what file should this go in" and "what should I name this variable" without anyone having to ask.
