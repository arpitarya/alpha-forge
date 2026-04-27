# Graph Report - alpha-forge  (2026-04-27)

## Corpus Check
- 178 files · ~401,971 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1345 nodes · 2485 edges · 44 communities detected
- Extraction: 59% EXTRACTED · 41% INFERRED · 0% AMBIGUOUS · INFERRED: 1013 edges (avg confidence: 0.61)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 88|Community 88]]
- [[_COMMUNITY_Community 89|Community 89]]
- [[_COMMUNITY_Community 90|Community 90]]
- [[_COMMUNITY_Community 91|Community 91]]
- [[_COMMUNITY_Community 92|Community 92]]
- [[_COMMUNITY_Community 93|Community 93]]
- [[_COMMUNITY_Community 94|Community 94]]
- [[_COMMUNITY_Community 95|Community 95]]

## God Nodes (most connected - your core abstractions)
1. `LLMProvider` - 88 edges
2. `QueryType` - 56 edges
3. `LLMResponse` - 50 edges
4. `MemoryService` - 44 edges
5. `RateLimits` - 39 edges
6. `alphaforge-logger — Structured rotating-file + console logger.` - 38 edges
7. `WalkForwardSplit` - 37 edges
8. `BaseLLMProvider` - 37 edges
9. `LLMGateway` - 35 edges
10. `Holding` - 34 edges

## Surprising Connections (you probably didn't know these)
- `Not SEBI Registered Disclaimer` --semantically_similar_to--> `Screener Disclaimers Block`  [INFERRED] [semantically similar]
  README.md → screener/PLAN.md
- `Screener Feature Importance Report` --semantically_similar_to--> `Benchmark Screener Output Fixture`  [INFERRED] [semantically similar]
  screener/reports/feature_importance.txt → llm-gateway/src/alphaforge_llm_gateway/benchmark_data/screener_output.txt
- `LLM Gateway Plan` --semantically_similar_to--> `repo-context-mcp Plan`  [INFERRED] [semantically similar]
  llm-gateway/PLAN.md → mcp/PLAN.md
- `pgvector Extension` --semantically_similar_to--> `repo_chunks Table`  [INFERRED] [semantically similar]
  backend/PLAN_memory.md → mcp/PLAN.md
- `alphaforge-logger — Structured rotating-file + console logger.` --uses--> `LLMGateway`  [INFERRED]
  packages/logger-py/src/alphaforge_logger/__init__.py → llm-gateway/src/alphaforge_llm_gateway/gateway.py

## Hyperedges (group relationships)
- **Screener 7-Phase Pipeline** — screener_phase1_data_pipeline, screener_phase2_feature_engineering, screener_phase3_dataset, screener_phase4_model_training, screener_phase5_backtesting, screener_phase6_live_screener, screener_phase7_jupyter_integration [EXTRACTED 1.00]
- **Model Comparison: LightGBM vs XGBoost vs Baseline** — screener_lightgbm_model, screener_xgboost_model, screener_baseline_rules, screener_walk_forward_cv [EXTRACTED 1.00]
- **Solar Terminal Design Language Stack** — design_system_solar_terminal, gemini_stitch_workflow, loading_page_design, terminal_dark_design, terminal_light_design [INFERRED 0.85]
- **5 Free LLM Providers** — llm_gateway_provider_gemini, llm_gateway_provider_groq, llm_gateway_provider_huggingface, llm_gateway_provider_openrouter, llm_gateway_provider_ollama [EXTRACTED 1.00]
- **AlphaForge Core Documentation Set** — docs_why, docs_what, docs_how, docs_getting_started [EXTRACTED 1.00]
- **pgvector-backed Memory & Repo Context** — memory_concept_pgvector, memory_concept_screener_pick_embeddings, memory_concept_conversation_memory, mcp_concept_repo_chunks [EXTRACTED 1.00]
- **Solar Terminal Dark Dashboard Composition** — screen_terminal_dark, widget_top_nav_dark, widget_alpha_brief_dark, widget_solar_orb_dark, widget_watchlist_dark, widget_net_worth_dark, widget_allocation_dark, widget_voice_footer_dark, widget_left_icon_rail_dark [INFERRED 0.90]
- **Brand asset served as Next.js static file** — frontend_logo, frontend_public_static_assets, alphaforge_brand_identity [INFERRED 0.75]

## Communities

### Community 0 - "Community 0"
Cohesion: 0.04
Nodes (117): BaseLLMProvider, Abstract base class for LLM providers — all providers implement this., Interface every LLM provider adapter must implement., Return the provider's default model., Shared OpenAI-compatible completion call used by all providers., BaseLLMProvider, BenchmarkReport, BenchmarkResult (+109 more)

### Community 1 - "Community 1"
Cohesion: 0.03
Nodes (82): ABC, AllocationSlice, HoldingsAggregator, Holdings aggregator + treemap layout + simple rebalance suggestions.  The aggreg, Tiny squarified-treemap layout — good enough for ≤24 cells.      Splits the box, Read-only roll-up over the registered BrokerSource instances., RebalanceDrift, RebalanceSuggestion (+74 more)

### Community 2 - "Community 2"
Cohesion: 0.02
Nodes (121): login(), LoginRequest, Authentication endpoints — register, login, token refresh., # TODO: persist user to DB, hash password, return token, # TODO: verify credentials, return token, register(), RegisterRequest, TokenResponse (+113 more)

### Community 3 - "Community 3"
Cohesion: 0.04
Nodes (87): initial schema with pgvector memory  Revision ID: 640eee61bc50 Revises:  Create, upgrade(), ai_chat(), ai_screener(), AnalysisRequest, AnalysisResponse, analyze_stock(), ChatMessage (+79 more)

### Community 4 - "Community 4"
Cohesion: 0.04
Nodes (65): BaseSettings, BrokerName, Chunk, chunk_file(), _chunk_markdown(), _chunk_python(), _chunk_ts_like(), _chunk_window() (+57 more)

### Community 5 - "Community 5"
Cohesion: 0.05
Nodes (59): BacktestEngine, CostModel, _load_model(), Phase 5.1 + 5.2 — Backtest Engine with Indian Market Cost Model.  Simulates trad, Compute approximate round-trip cost as a percentage.          Assumes entry_valu, Record of a single simulated trade., Walk-forward backtest engine for stock screener strategies.      Modes:     1. M, Initialize backtest engine.          Args:             top_n: Number of top pick (+51 more)

### Community 6 - "Community 6"
Cohesion: 0.04
Nodes (61): Screener Backtest Comparison Report, Strategy: baseline_momentum_top5 (best PF), Strategy: lightgbm_top5, Strategy: xgboost_top5, Class Imbalance 1:21 (4.5% positive), Screener Dataset Stats Output, LLM Gateway Module (implement.txt entry), Vector DB / Memory Lake Module (+53 more)

### Community 7 - "Community 7"
Cohesion: 0.04
Nodes (58): Vector DB Memory Lake Implementation Log, Vector DB Memory Lake Plan, Benchmark Screener Output Fixture, Benchmark SHAP Explanation Fixture, Getting Started Doc, How AlphaForge Works, What AlphaForge Is, Why AlphaForge Exists (+50 more)

### Community 8 - "Community 8"
Cohesion: 0.05
Nodes (6): PortfolioHeader(), useDashboardStats(), useDashboardTicker(), useHoldings(), TerminalStats(), TerminalTicker()

### Community 9 - "Community 9"
Cohesion: 0.08
Nodes (34): check_benchmarks(), compute_all_metrics(), compute_cagr(), compute_calmar_ratio(), compute_max_drawdown(), compute_portfolio_metrics(), compute_sharpe_ratio(), _compute_sortino() (+26 more)

### Community 10 - "Community 10"
Cohesion: 0.06
Nodes (16): AppShell(), Badge(), BootStep(), Card(), CardHeader(), Chip(), CountUp(), HudCorners() (+8 more)

### Community 11 - "Community 11"
Cohesion: 0.1
Nodes (11): BaseBroker, BaseBroker, BrokerOrder, BrokerPosition, Abstract broker interface — all broker integrations implement this., Interface every broker adapter must implement., Zerodha Kite Connect broker adapter., # TODO: use kiteconnect SDK to generate session (+3 more)

### Community 12 - "Community 12"
Cohesion: 0.1
Nodes (23): Accessibility Rules (4.5:1 contrast), Bloomberg-meets-modern-dark Aesthetic Rationale, Color Palette (Dark Theme tokens), Component Patterns (Cards, Buttons, Inputs), Iconography (Lucide React), Solar Terminal Design System, Spacing & Layout Grid, Typography (JetBrains Mono) (+15 more)

### Community 13 - "Community 13"
Cohesion: 0.2
Nodes (12): cmd_holdings(), cmd_rebalance(), cmd_reset(), cmd_sources(), cmd_sync(), cmd_treemap(), cmd_upload(), cmd_upload_all() (+4 more)

### Community 14 - "Community 14"
Cohesion: 0.18
Nodes (10): Base, Base, Async database engine and session factory., Alembic env.py — async migration runner., Holding, Order, Portfolio management endpoints., Watchlist (+2 more)

### Community 15 - "Community 15"
Cohesion: 0.11
Nodes (11): MarketDataService, Market data service — fetches quotes, history, indices from Indian exchanges., Aggregates market data from NSE, BSE, and third-party providers., Fetch real-time quote for a symbol., # TODO: integrate with data provider (NSE API / broker feed / third-party), Fetch major Indian indices — NIFTY 50, SENSEX, BANK NIFTY, NIFTY IT, etc., # TODO: scrape/fetch from NSE/BSE, Fetch historical OHLCV candles. (+3 more)

### Community 16 - "Community 16"
Cohesion: 0.13
Nodes (15): get_indices(), get_price_history(), get_quote(), IndexSummary, Market data endpoints — quotes, charts, screeners, indices., Fetch real-time quote for a given NSE/BSE symbol., # TODO: integrate with market data provider, Fetch major Indian market indices — NIFTY 50, SENSEX, BANK NIFTY, etc. (+7 more)

### Community 17 - "Community 17"
Cohesion: 0.2
Nodes (13): compute_momentum_features(), compute_price_action_features(), compute_technical_features(), compute_trend_features(), compute_volatility_features(), compute_volume_features(), Phase 2.1 — Technical Indicators.  Computes ~30 technical indicators per stock u, Volatility indicators: Bollinger Bands, ATR, Keltner Channel. (+5 more)

### Community 18 - "Community 18"
Cohesion: 0.15
Nodes (13): apply_rules(), evaluate_baseline(), Phase 4.1 — Baseline Technical Rules Strategy.  Simple rule-based screener for c, Run baseline strategy on dataset and compute performance metrics.      Args:, RSI(14) < 35 — stock is oversold territory., Volume > 2× 20-day average (VOL_SMA_RATIO > 2.0)., MACD histogram is positive (bullish momentum)., Price is above SMA(50) — uptrend confirmation. (+5 more)

### Community 19 - "Community 19"
Cohesion: 0.2
Nodes (13): compute_shap_values(), describe_feature(), explain_pick(), explain_picks(), _explain_without_shap(), format_explanations(), Phase 6.2 — SHAP-Based Signal Explanation.  For each pick from the daily scan, g, Compute SHAP values for the given features.      Args:         model: Trained mo (+5 more)

### Community 20 - "Community 20"
Cohesion: 0.15
Nodes (11): get_symbol(), module_overview(), MCP server — exposes repo-context tools over stdio.  Launch via:     python -m a, Semantic search over the AlphaForge codebase.      Returns chunks ranked by cosi, Look up a function, class, interface, or type by name.      `kind` may be one of, Summarize a module: nearest CLAUDE.md / PLAN.md / README.md + file listing., Recent git commits — optionally scoped to a path., Read a bounded slice of a repo file. Max 500 lines per call. (+3 more)

### Community 21 - "Community 21"
Cohesion: 0.18
Nodes (13): Solar Terminal Landing Page (Dark Theme), Solar Terminal Dark Theme, Amber/Orange Accent Token, Dark Background Token, Allocation Card, Alpha Brief Panel, Left Icon Rail, Net Worth Card (+5 more)

### Community 22 - "Community 22"
Cohesion: 0.21
Nodes (11): clear_index_cache(), compute_all_relative_strength(), compute_relative_strength(), _compute_returns(), _load_index_close(), Phase 2.2 — Relative Strength Features.  Computes stock returns relative to benc, Compute relative strength vs all available benchmarks.      Args:         stock_, Clear the cached index data (e.g., between runs). (+3 more)

### Community 23 - "Community 23"
Cohesion: 0.23
Nodes (11): download_ohlcv_batch(), fetch_ohlcv(), get_date_range(), load_filtered_universe(), Step 1.2 — Historical OHLCV Download.  Downloads 2 years of daily OHLCV data for, Save OHLCV data to Parquet file. Merges with existing if incremental., Main entry point: download OHLCV for all filtered stocks.      Args:         inc, Load yfinance symbols from the filtered universe CSV. (+3 more)

### Community 24 - "Community 24"
Cohesion: 0.27
Nodes (9): compute_classification_label(), compute_forward_return(), compute_labels(), compute_labels_for_symbol(), Phase 3.1 — Target Variable Labeler.  Computes forward-looking labels for the ML, Compute labels for a single stock by loading its OHLCV parquet.      Args:, Compute the N-day forward return from Adjusted Close prices.      Forward return, Convert forward return to binary classification label.      1 = stock returned > (+1 more)

### Community 25 - "Community 25"
Cohesion: 0.24
Nodes (9): clear_fundamental_cache(), compute_52w_return(), compute_fundamental_features(), _fetch_fundamentals(), Phase 2.3 — Fundamental Features.  Fetches PE, PB, market cap, 52-week return, a, Clear the cached fundamental data., Fetch fundamental data for a single stock from yfinance.      Returns a dict wit, Compute rolling 252-day (52-week) return from Close prices. (+1 more)

### Community 26 - "Community 26"
Cohesion: 0.2
Nodes (10): Solar Terminal Landing Page (Light Theme), Solar Terminal Light Theme Tokens, Allocation Card (Light), Alpha Brief Panel (Light), Net Worth Card (Light), Risk Analysis Panel (Light), Central Solar Orb (Light), Top Navigation Bar (Light) (+2 more)

### Community 27 - "Community 27"
Cohesion: 0.31
Nodes (9): AlphaForge Logo, AlphaForge Brand Identity, Stylized 'A' Brand Mark, Forge/Molten Metal Visual Metaphor, Geometric Modern Sans-Serif Style, Horizontal Mark + Wordmark Layout, Light Neutral Background, Orange-to-Amber Gradient (+1 more)

### Community 28 - "Community 28"
Cohesion: 0.33
Nodes (7): Light Solar Terminal Theme, Centered Logo Card, AlphaForge Loading Screen, Loading Progress Bar, App Boot/Splash Purpose, Terminal Metadata Corners, ALPHA FORGE Wordmark

### Community 29 - "Community 29"
Cohesion: 0.33
Nodes (5): get_logger(), Centralized logging configuration for AlphaForge backend.  Thin wrapper around t, Configure and return the application root logger., Return a child logger under the ``alphaforge`` namespace., setup_logging()

### Community 30 - "Community 30"
Cohesion: 0.33
Nodes (1): Security utilities — password hashing, JWT tokens.

### Community 31 - "Community 31"
Cohesion: 0.5
Nodes (2): handleUpload(), onAfter()

### Community 34 - "Community 34"
Cohesion: 0.67
Nodes (2): health_check(), Health check endpoints.

### Community 35 - "Community 35"
Cohesion: 0.67
Nodes (1): Backend test: health check.

### Community 37 - "Community 37"
Cohesion: 0.67
Nodes (3): AlphaForge Brand Identity, AlphaForge Logo (frontend/public/logo.png), Frontend Public Static Assets Folder

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (2): Solar Terminal Design Tokens, @alphaforge/solar-orb-ui README

### Community 88 - "Community 88"
Cohesion: 1.0
Nodes (1): Get aggregated portfolio summary with all holdings.

### Community 89 - "Community 89"
Cohesion: 1.0
Nodes (1): List all open intraday and delivery positions.

### Community 90 - "Community 90"
Cohesion: 1.0
Nodes (1): List recent order history.

### Community 91 - "Community 91"
Cohesion: 1.0
Nodes (1): # TODO: fetch from DB + broker sync

### Community 92 - "Community 92"
Cohesion: 1.0
Nodes (1): # TODO: fetch from broker API

### Community 93 - "Community 93"
Cohesion: 1.0
Nodes (1): # TODO: fetch from broker API

### Community 94 - "Community 94"
Cohesion: 1.0
Nodes (1): Dark Charcoal Typography

### Community 95 - "Community 95"
Cohesion: 1.0
Nodes (1): Two-Tier Stacked Wordmark

## Knowledge Gaps
- **317 isolated node(s):** `Phase 3.1 — Target Variable Labeler.  Computes forward-looking labels for the ML`, `Compute the N-day forward return from Adjusted Close prices.      Forward return`, `Convert forward return to binary classification label.      1 = stock returned >`, `Compute all labels for a single stock's OHLCV DataFrame.      Args:         df:`, `Compute labels for a single stock by loading its OHLCV parquet.      Args:` (+312 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 30`** (6 nodes): `security.py`, `create_access_token()`, `decode_access_token()`, `hash_password()`, `Security utilities — password hashing, JWT tokens.`, `verify_password()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (5 nodes): `SourcesPanel.tsx`, `formatTime()`, `handleUpload()`, `onAfter()`, `statusVariant()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (3 nodes): `health.py`, `health_check()`, `Health check endpoints.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (3 nodes): `test_health.py`, `Backend test: health check.`, `test_health_check()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (2 nodes): `Solar Terminal Design Tokens`, `@alphaforge/solar-orb-ui README`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 88`** (1 nodes): `Get aggregated portfolio summary with all holdings.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 89`** (1 nodes): `List all open intraday and delivery positions.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 90`** (1 nodes): `List recent order history.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 91`** (1 nodes): `# TODO: fetch from DB + broker sync`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 92`** (1 nodes): `# TODO: fetch from broker API`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 93`** (1 nodes): `# TODO: fetch from broker API`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 94`** (1 nodes): `Dark Charcoal Typography`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 95`** (1 nodes): `Two-Tier Stacked Wordmark`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `LLMProvider` connect `Community 0` to `Community 1`, `Community 4`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Why does `run_full_backtest()` connect `Community 5` to `Community 2`, `Community 18`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `build_features_for_symbol()` connect `Community 2` to `Community 17`, `Community 22`, `Community 25`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Are the 84 inferred relationships involving `LLMProvider` (e.g. with `LLMGateway` and `LLMGateway — main entry point that ties providers, router, rate limiter, and cos`) actually correct?**
  _`LLMProvider` has 84 INFERRED edges - model-reasoned connections that need verification._
- **Are the 52 inferred relationships involving `QueryType` (e.g. with `LLMGateway` and `LLMGateway — main entry point that ties providers, router, rate limiter, and cos`) actually correct?**
  _`QueryType` has 52 INFERRED edges - model-reasoned connections that need verification._
- **Are the 48 inferred relationships involving `LLMResponse` (e.g. with `LLMGateway` and `LLMGateway — main entry point that ties providers, router, rate limiter, and cos`) actually correct?**
  _`LLMResponse` has 48 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `MemoryService` (e.g. with `ChatMessage` and `ChatRequest`) actually correct?**
  _`MemoryService` has 34 INFERRED edges - model-reasoned connections that need verification._