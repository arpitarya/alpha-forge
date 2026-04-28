# AlphaForge — Code Conventions

The point of this folder is **predictability**. When you open any file in this repo, the filename should already tell you what's inside; when you open any directory, the layout should already tell you what each file does.

## Hard rules (apply everywhere)

| Limit | Value | Rationale |
|---|---|---|
| Max lines per file | **100** | If a file is longer, it's doing too much — split it. |
| Max lines for a `*_utils.py` / `*.utils.ts` | **50** | Utils are leaf-level helpers. Anything bigger is a service. |
| One responsibility per file | always | Filename = responsibility. |
| Imports + blank lines + docstring | counted in line limit | Yes, really — keeps imports honest. |

## File-naming rules

The filename suffix encodes the file's role. The prefix says **what domain it serves**.

- **Python**: `<domain>_<role>.py` → `portfolio_routes.py`, `auth_models.py`, `csv_parsing_utils.py`
- **TypeScript / JavaScript**: `<domain>.<role>.ts` → `portfolio.query.ts`, `holdings.utils.ts`

See:
- [python.md](python.md) — full Python convention
- [typescript.md](typescript.md) — full TS/JS convention
- [violations.md](violations.md) — current files in the repo that violate these rules; tackle one per PR

## Why suffixes (not just folders)

A folder tells you the domain. A suffix tells you the role. Together they collide into one obvious name:

```
backend/app/modules/portfolio/portfolio_routes.py     ← portfolio domain, route role
backend/app/modules/portfolio/portfolio_models.py     ← portfolio domain, model role
frontend/src/portfolio/portfolio.query.ts             ← portfolio domain, query role
```

You never have to read the file to know what's in it.

## When in doubt

- Bigger than the line limit? → Split. Don't argue the limit.
- Doesn't fit any role suffix? → It's probably wrong. Check the suffix list before inventing a new one.
- Truly novel kind of file? → Add a suffix to the convention before adding the file. Convention changes go in this folder.
