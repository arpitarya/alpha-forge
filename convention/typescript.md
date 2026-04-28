# TypeScript / JavaScript Convention

## Filename grammar

```
<domain>.<role>.ts        # for non-component files
<Component>.tsx           # for React components (PascalCase, no role suffix)
```

The dot (not underscore) is intentional — TS tooling treats `*.foo.ts` as a recognized extension family (`*.test.ts`, `*.d.ts`, etc.).

## Role suffixes

| Suffix | Holds | Line cap |
|---|---|---|
| `*.query.ts` | TanStack React Query hooks (`useQuery`, `useMutation`) | 100 |
| `*.api.ts` | Axios calls — one function per endpoint, returns typed data | 100 |
| `*.store.ts` | Zustand stores | 100 |
| `*.hook.ts` | Custom React hooks that aren't queries (e.g. `useDebounce`) | 100 |
| `*.utils.ts` | Pure functions, no React, no I/O | **50** |
| `*.types.ts` | `interface`, `type`, `enum` only | 50 |
| `*.schema.ts` | Zod schemas / runtime validators | 50 |
| `*.constants.ts` | `UPPER_SNAKE` exports | 50 |
| `*.test.ts` / `*.test.tsx` | Vitest / Jest tests | 100 |
| `Component.tsx` | One React component per file (PascalCase filename) | 100 |
| `index.ts` | Barrel re-exports only — no logic | 50 |

## Layout

Per-domain folders under `frontend/src/modules/<name>/` (when modules land):

```
frontend/src/modules/portfolio/
├── index.ts                          # barrel
├── PortfolioPage.tsx                 # top-level component
├── HoldingsTable.tsx                 # leaf component
├── portfolio.query.ts                # usePortfolioQuery, useSyncSourceMutation
├── portfolio.api.ts                  # fetchHoldings(), syncSource()
├── portfolio.store.ts                # selected source, filter state
├── portfolio.types.ts                # Holding, Source, AssetClass
└── portfolio.utils.ts                # formatPnL, classifyAsset (≤ 50 lines)
```

## Components

- One component per `.tsx` file. Filename = component name, PascalCase.
- No role suffix — `.tsx` itself signals "React component".
- ≤ 100 lines. If a component is bigger, extract subcomponents into sibling files.
- Co-locate styles inline (Tailwind) — no separate `.module.css` files.
- Hooks defined inside a component file are *only* used by that component. Anything reusable goes into `*.hook.ts` or `*.query.ts`.

## Imports

- Path aliases over relative climbs: `@/modules/portfolio/portfolio.api` beats `../../portfolio/portfolio.api`.
- A module's `index.ts` is its public surface. Other modules import from the index, not from internal files.
- `*.utils.ts` and `*.types.ts` import only from stdlib / npm — never from `*.api`, `*.store`, etc.

## Line-count discipline

When a `*.query.ts` hits 100, split by domain group:
- `holdings.query.ts` (queries about holdings)
- `sources.query.ts`  (queries about broker sources)

A 400-line `queries.ts` is the smell this convention exists to eliminate. Pick a noun, make a file.

## Components > 100 lines

Extract:
1. Subcomponents (`<HoldingRow />`, `<SourceCard />`)
2. Pure helpers → `<domain>.utils.ts`
3. Data hooks → `<domain>.query.ts`
4. Local state → `<domain>.store.ts`

If after extraction it's still big, the component is doing two things — split it into two pages/views.

## Tooling alignment

- **Biome v2** — formats and lints. Configured for the conventions above.
- **ESLint v9 (flat config)** — Next.js-specific rules layered on top.
- **TypeScript strict** — no `any` without an inline justification comment.
