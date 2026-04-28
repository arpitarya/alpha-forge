# Convention Violations — Current State

A snapshot of files in the repo that violate [README.md](README.md) line limits as of the convention rollout. **The convention is binding for new code; this list is the legacy backlog.** Tackle one row per PR.

## Backend (Python) — `> 100` lines

✅ **Cleared.** Every backend file is now ≤ 100 lines and every `*_utils.py` ≤ 50 lines.

The previous violations were resolved as follows:
- `csv_sources.py` (345) → `zerodha_csv.py`, `zerodha_coin_csv.py`, `groww_csv.py`, `dezerv_csv.py`, `wint_wealth_csv.py` + `_csv_helper.py`
- `memory_service.py` (249) → `memory_service.py` + `memory_repo.py` + `memory_utils.py` + `memory_helper.py`
- `aggregator.py` (233) → `aggregator.py` + `aggregator_types.py` + `treemap_helper.py`
- `portfolio_routes.py` (220) → `portfolio_routes.py` + `sources_routes.py` + `sources_helper.py` + `otp_routes.py`
- `zerodha_kite.py` (211) → `zerodha_kite.py` + `zerodha_kite_helper.py` (Playwright + enctoken cache)
- `groww.py` (209) → `groww.py` + `groww_helper.py` + `groww_mapper.py`
- `dashboard_routes.py` (201) → `dashboard_routes.py` + `dashboard_schemas.py` + `dashboard_seed.py`
- `angel_one.py` (174) → `angel_one.py` + `angel_one_helper.py`
- `wint_wealth.py` (172) → `wint_wealth.py` + `wint_wealth_helper.py`
- `ai_service.py` (168) → `ai_service.py` + `ai_helper.py` + `ai_utils.py`
- `llm_routes.py` (160) → `llm_routes.py` + `benchmark_routes.py` + `llm_schemas.py`
- `base.py` (158) → `base.py` + `broker_schemas.py`
- `screener_routes.py` (132) → `screener_routes.py` + `screener_schemas.py` + `screener_helper.py`
- `embedding_service.py` (122) → `embedding_service.py` + `embedding_utils.py`
- `ai_routes.py` (119) → `ai_routes.py` + `ai_schemas.py`
- `zerodha_coin.py` (106) → trimmed inline

## Frontend (TS/TSX) — `> 100` lines

✅ **Cleared as of frontend module rollout.** All frontend files now ≤ 100 lines, all `*.utils.ts` ≤ 50.

The previous violations were resolved as follows:
- `frontend/src/lib/queries.ts` (486) → split into `<domain>.query.ts` files under `frontend/src/modules/<name>/`
- `frontend/src/lib/api.ts` (120) → reduced to the axios client only; per-domain `<domain>.api.ts` under each module
- `frontend/src/components/portfolio/SourcesPanel.tsx` (325) → split into `SourcesPanel`, `SourceRow`, `SourceActions`, `SourceOtpDialog`, `useSourceRow.hook.ts`, `sources.utils.ts`
- `frontend/src/components/portfolio/Ledger.tsx` (103) → split into `Ledger`, `LedgerRow`, `ledger.utils.ts`

## How to track progress

When you split a file, drop its row from this list in the same PR. When everything is gone, delete this file.
