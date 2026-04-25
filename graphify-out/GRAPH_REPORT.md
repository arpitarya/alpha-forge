# Graph Report - .  (2026-04-26)

## Corpus Check
- 179 files · ~278,715 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1258 nodes · 2411 edges · 61 communities detected
- Extraction: 69% EXTRACTED · 31% INFERRED · 0% AMBIGUOUS · INFERRED: 748 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_LLM Provider Adapters|LLM Provider Adapters]]
- [[_COMMUNITY_AI Routes & Schemas|AI Routes & Schemas]]
- [[_COMMUNITY_Backtest Engine|Backtest Engine]]
- [[_COMMUNITY_Repo Context Chunking|Repo Context Chunking]]
- [[_COMMUNITY_Screener Reports & Plans|Screener Reports & Plans]]
- [[_COMMUNITY_Memory & Docs Cross-Refs|Memory & Docs Cross-Refs]]
- [[_COMMUNITY_Trade & Logger Packages|Trade & Logger Packages]]
- [[_COMMUNITY_Config & Env Settings|Config & Env Settings]]
- [[_COMMUNITY_Portfolio Metrics|Portfolio Metrics]]
- [[_COMMUNITY_Broker Abstraction|Broker Abstraction]]
- [[_COMMUNITY_Feature Orchestrator|Feature Orchestrator]]
- [[_COMMUNITY_DB Models & Migrations|DB Models & Migrations]]
- [[_COMMUNITY_LLM CLI & Routes|LLM CLI & Routes]]
- [[_COMMUNITY_Dataset Assembly|Dataset Assembly]]
- [[_COMMUNITY_Solar Terminal Design System|Solar Terminal Design System]]
- [[_COMMUNITY_React Query Hooks|React Query Hooks]]
- [[_COMMUNITY_NSE Supplementary Fetchers|NSE Supplementary Fetchers]]
- [[_COMMUNITY_Market Data Service|Market Data Service]]
- [[_COMMUNITY_NSE Deal Features|NSE Deal Features]]
- [[_COMMUNITY_Daily Stock Scan|Daily Stock Scan]]
- [[_COMMUNITY_Market API Routes|Market API Routes]]
- [[_COMMUNITY_Baseline Rule Strategy|Baseline Rule Strategy]]
- [[_COMMUNITY_SHAP Explanation|SHAP Explanation]]
- [[_COMMUNITY_Brand Identity|Brand Identity]]
- [[_COMMUNITY_MCP Server Tools|MCP Server Tools]]
- [[_COMMUNITY_Relative Strength Features|Relative Strength Features]]
- [[_COMMUNITY_Feature Importance Reports|Feature Importance Reports]]
- [[_COMMUNITY_Drift Detection & Retrain|Drift Detection & Retrain]]
- [[_COMMUNITY_OHLCV Download|OHLCV Download]]
- [[_COMMUNITY_Universe Fetcher|Universe Fetcher]]
- [[_COMMUNITY_Dark Theme Landing Page|Dark Theme Landing Page]]
- [[_COMMUNITY_Auth Routes|Auth Routes]]
- [[_COMMUNITY_Light Theme Landing Page|Light Theme Landing Page]]
- [[_COMMUNITY_Backend Logging|Backend Logging]]
- [[_COMMUNITY_Security & JWT|Security & JWT]]
- [[_COMMUNITY_Loading Screen|Loading Screen]]
- [[_COMMUNITY_Initial pgvector Migration|Initial pgvector Migration]]
- [[_COMMUNITY_Portfolio Cards UI|Portfolio Cards UI]]
- [[_COMMUNITY_Health Endpoint|Health Endpoint]]
- [[_COMMUNITY_Health Tests|Health Tests]]
- [[_COMMUNITY_Root Layout|Root Layout]]
- [[_COMMUNITY_Home Page|Home Page]]
- [[_COMMUNITY_Header Component|Header Component]]
- [[_COMMUNITY_Sidebar Component|Sidebar Component]]
- [[_COMMUNITY_Risk Analysis UI|Risk Analysis UI]]
- [[_COMMUNITY_Screener Picks UI|Screener Picks UI]]
- [[_COMMUNITY_Alpha Brief UI|Alpha Brief UI]]
- [[_COMMUNITY_Solar Orb Animation|Solar Orb Animation]]
- [[_COMMUNITY_Market Overview UI|Market Overview UI]]
- [[_COMMUNITY_AI Chat UI|AI Chat UI]]
- [[_COMMUNITY_Query Providers|Query Providers]]
- [[_COMMUNITY_AI Prompt Templates|AI Prompt Templates]]
- [[_COMMUNITY_tsup Build Config|tsup Build Config]]
- [[_COMMUNITY_Card Primitive|Card Primitive]]
- [[_COMMUNITY_Icon Primitive|Icon Primitive]]
- [[_COMMUNITY_Divider Primitive|Divider Primitive]]
- [[_COMMUNITY_Chip Primitive|Chip Primitive]]
- [[_COMMUNITY_Badge Primitive|Badge Primitive]]
- [[_COMMUNITY_Input Primitive|Input Primitive]]
- [[_COMMUNITY_Frontend Logo Asset|Frontend Logo Asset]]
- [[_COMMUNITY_Solar Orb Tokens & README|Solar Orb Tokens & README]]

## God Nodes (most connected - your core abstractions)
1. `LLMProvider` - 89 edges
2. `QueryType` - 57 edges
3. `LLMResponse` - 51 edges
4. `MemoryService` - 45 edges
5. `RateLimits` - 40 edges
6. `alphaforge-logger — Structured rotating-file + console logger.` - 39 edges
7. `WalkForwardSplit` - 38 edges
8. `BaseLLMProvider` - 38 edges
9. `LLMGateway` - 36 edges
10. `ProviderConfig` - 32 edges

## Surprising Connections (you probably didn't know these)
- `Wordmark()` --colored_with--> `Dark Charcoal Typography`  [EXTRACTED]
  /Users/arpitarya/my_programs/alpha-forge/packages/solar-orb-ui/src/components/Logo.tsx → logo.png
- `Wordmark()` --arranged_as--> `Two-Tier Stacked Wordmark`  [EXTRACTED]
  /Users/arpitarya/my_programs/alpha-forge/packages/solar-orb-ui/src/components/Logo.tsx → logo.png
- `Wordmark()` --uses_style--> `Geometric Modern Sans-Serif Style`  [EXTRACTED]
  /Users/arpitarya/my_programs/alpha-forge/packages/solar-orb-ui/src/components/Logo.tsx → logo.png
- `Screener Disclaimers Block` --semantically_similar_to--> `Not SEBI Registered Disclaimer`  [INFERRED] [semantically similar]
  screener/PLAN.md → README.md
- `Benchmark Screener Output Fixture` --semantically_similar_to--> `Screener Feature Importance Report`  [INFERRED] [semantically similar]
  llm-gateway/src/alphaforge_llm_gateway/benchmark_data/screener_output.txt → screener/reports/feature_importance.txt

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

### Community 0 - "LLM Provider Adapters"
Cohesion: 0.04
Nodes (97): BaseLLMProvider, Abstract base class for LLM providers — all providers implement this., Interface every LLM provider adapter must implement., Return the provider's default model., Shared OpenAI-compatible completion call used by all providers., BaseLLMProvider, BenchmarkReport, BenchmarkResult (+89 more)

### Community 1 - "AI Routes & Schemas"
Cohesion: 0.05
Nodes (66): ai_chat(), ai_screener(), AnalysisRequest, AnalysisResponse, analyze_stock(), ChatMessage, ChatRequest, ChatResponse (+58 more)

### Community 2 - "Backtest Engine"
Cohesion: 0.05
Nodes (59): BacktestEngine, CostModel, _load_model(), Phase 5.1 + 5.2 — Backtest Engine with Indian Market Cost Model.  Simulates trad, Compute approximate round-trip cost as a percentage.          Assumes entry_valu, Record of a single simulated trade., Walk-forward backtest engine for stock screener strategies.      Modes:     1. M, Initialize backtest engine.          Args:             top_n: Number of top pick (+51 more)

### Community 3 - "Repo Context Chunking"
Cohesion: 0.06
Nodes (42): Chunk, chunk_file(), _chunk_markdown(), _chunk_python(), _chunk_ts_like(), _chunk_window(), content_hash(), detect_lang() (+34 more)

### Community 4 - "Screener Reports & Plans"
Cohesion: 0.04
Nodes (61): Screener Backtest Comparison Report, Strategy: baseline_momentum_top5 (best PF), Strategy: lightgbm_top5, Strategy: xgboost_top5, Class Imbalance 1:21 (4.5% positive), Screener Dataset Stats Output, LLM Gateway Module (implement.txt entry), Vector DB / Memory Lake Module (+53 more)

### Community 5 - "Memory & Docs Cross-Refs"
Cohesion: 0.04
Nodes (58): Vector DB Memory Lake Implementation Log, Vector DB Memory Lake Plan, Benchmark Screener Output Fixture, Benchmark SHAP Explanation Fixture, Getting Started Doc, How AlphaForge Works, What AlphaForge Is, Why AlphaForge Exists (+50 more)

### Community 6 - "Trade & Logger Packages"
Cohesion: 0.07
Nodes (34): Enum, createLogger(), get_logger(), getLogger(), Centralized logging configuration for AlphaForge Python services.  Usage::, Return a child logger under the given *namespace*.      Example::          logge, Configure and return the application root logger.      Resolution order for ever, setup_logging() (+26 more)

### Community 7 - "Config & Env Settings"
Cohesion: 0.06
Nodes (6): BaseSettings, _find_repo_root(), Configuration for the repo-context MCP server.  Reads from environment (and the, Walk up from this file to find the repo root (has .git)., Settings, alphaforge-logger — Structured rotating-file + console logger.

### Community 8 - "Portfolio Metrics"
Cohesion: 0.09
Nodes (34): check_benchmarks(), compute_all_metrics(), compute_cagr(), compute_calmar_ratio(), compute_max_drawdown(), compute_portfolio_metrics(), compute_sharpe_ratio(), _compute_sortino() (+26 more)

### Community 9 - "Broker Abstraction"
Cohesion: 0.1
Nodes (24): ABC, available_models(), complete(), health_check(), name(), BaseBroker, authenticate(), BaseBroker (+16 more)

### Community 10 - "Feature Orchestrator"
Cohesion: 0.09
Nodes (29): build_features_for_symbol(), build_features_for_universe(), compute_interaction_features(), Phase 2.5 — Feature Orchestrator.  Combines all feature groups (technical, relat, Build features for all stocks in the filtered universe.      Args:         max_s, Compute derived/interaction features from existing features.      These capture, Build all features for a single stock.      Args:         symbol: NSE symbol (e., clear_fundamental_cache() (+21 more)

### Community 11 - "DB Models & Migrations"
Cohesion: 0.11
Nodes (24): Base, Base, get_db(), Async database engine and session factory., do_run_migrations(), Alembic env.py — async migration runner., run_migrations_offline(), run_migrations_online() (+16 more)

### Community 12 - "LLM CLI & Routes"
Cohesion: 0.17
Nodes (20): _build_parser(), _format_response(), main(), _read_input(), _run(), analyze_screener(), AnalyzeRequest, ChatMessage (+12 more)

### Community 13 - "Dataset Assembly"
Cohesion: 0.14
Nodes (20): apply_quality_filters(), build_dataset(), build_single_stock_dataset(), compute_dataset_stats(), _get_available_symbols(), Phase 3.2 — Dataset Assembly.  Combines features (Phase 2) + labels (Phase 3.1), Apply data quality rules to the assembled dataset.      Rules:     1. Drop rows, Compute and format dataset statistics as a text report. (+12 more)

### Community 14 - "Solar Terminal Design System"
Cohesion: 0.1
Nodes (23): Accessibility Rules (4.5:1 contrast), Bloomberg-meets-modern-dark Aesthetic Rationale, Color Palette (Dark Theme tokens), Component Patterns (Cards, Buttons, Inputs), Iconography (Lucide React), Solar Terminal Design System, Spacing & Layout Grid, Typography (JetBrains Mono) (+15 more)

### Community 15 - "React Query Hooks"
Cohesion: 0.17
Nodes (20): useAIChat(), useAnalyzeScreener(), useAnalyzeStock(), useBenchmarkResults(), useCancelOrder(), useExplainPicks(), useHistory(), useIndices() (+12 more)

### Community 16 - "NSE Supplementary Fetchers"
Cohesion: 0.2
Nodes (17): fetch_all_nse_supplementary(), fetch_block_deals(), fetch_bulk_deals(), fetch_delivery_data(), fetch_fii_dii_activity(), fetch_index_data(), _nse_date(), Step 1.3 + 1.4 — Supplementary NSE Data & Index Benchmarks.  Fetches delivery %, (+9 more)

### Community 17 - "Market Data Service"
Cohesion: 0.13
Nodes (11): MarketDataService, Market data service — fetches quotes, history, indices from Indian exchanges., Aggregates market data from NSE, BSE, and third-party providers., Fetch real-time quote for a symbol., # TODO: integrate with data provider (NSE API / broker feed / third-party), Fetch major Indian indices — NIFTY 50, SENSEX, BANK NIFTY, NIFTY IT, etc., # TODO: scrape/fetch from NSE/BSE, Fetch historical OHLCV candles. (+3 more)

### Community 18 - "NSE Deal Features"
Cohesion: 0.21
Nodes (15): clear_nse_cache(), compute_deal_features(), compute_delivery_features(), compute_nse_features(), _load_block_deals(), _load_bulk_deals(), _load_delivery_data(), Phase 2.4 — NSE-Specific Features.  Computes features from delivery %, bulk/bloc (+7 more)

### Community 19 - "Daily Stock Scan"
Cohesion: 0.21
Nodes (15): compute_features_latest(), get_available_symbols(), get_universe_symbols(), load_model(), predict_and_rank(), Phase 6.1 — Daily Stock Scan Script.  Run after market close (~3:45 PM IST) to s, Load a trained model and its metadata.      Args:         model_type: 'lightgbm', Predict probabilities and rank stocks.      Args:         features: DataFrame wi (+7 more)

### Community 20 - "Market API Routes"
Cohesion: 0.2
Nodes (15): get_indices(), get_price_history(), get_quote(), IndexSummary, Market data endpoints — quotes, charts, screeners, indices., Fetch real-time quote for a given NSE/BSE symbol., # TODO: integrate with market data provider, Fetch major Indian market indices — NIFTY 50, SENSEX, BANK NIFTY, etc. (+7 more)

### Community 21 - "Baseline Rule Strategy"
Cohesion: 0.2
Nodes (13): apply_rules(), evaluate_baseline(), Phase 4.1 — Baseline Technical Rules Strategy.  Simple rule-based screener for c, Run baseline strategy on dataset and compute performance metrics.      Args:, RSI(14) < 35 — stock is oversold territory., Volume > 2× 20-day average (VOL_SMA_RATIO > 2.0)., MACD histogram is positive (bullish momentum)., Price is above SMA(50) — uptrend confirmation. (+5 more)

### Community 22 - "SHAP Explanation"
Cohesion: 0.24
Nodes (13): compute_shap_values(), describe_feature(), explain_pick(), explain_picks(), _explain_without_shap(), format_explanations(), Phase 6.2 — SHAP-Based Signal Explanation.  For each pick from the daily scan, g, Compute SHAP values for the given features.      Args:         model: Trained mo (+5 more)

### Community 23 - "Brand Identity"
Cohesion: 0.18
Nodes (13): AlphaForge Logo, AlphaForge Brand Identity, Stylized 'A' Brand Mark, Dark Charcoal Typography, Forge/Molten Metal Visual Metaphor, Geometric Modern Sans-Serif Style, Horizontal Mark + Wordmark Layout, Light Neutral Background (+5 more)

### Community 24 - "MCP Server Tools"
Cohesion: 0.21
Nodes (12): get_symbol(), main(), module_overview(), MCP server — exposes repo-context tools over stdio.  Launch via:     python -m a, Semantic search over the AlphaForge codebase.      Returns chunks ranked by cosi, Look up a function, class, interface, or type by name.      `kind` may be one of, Summarize a module: nearest CLAUDE.md / PLAN.md / README.md + file listing., Recent git commits — optionally scoped to a path. (+4 more)

### Community 25 - "Relative Strength Features"
Cohesion: 0.26
Nodes (11): clear_index_cache(), compute_all_relative_strength(), compute_relative_strength(), _compute_returns(), _load_index_close(), Phase 2.2 — Relative Strength Features.  Computes stock returns relative to benc, Compute relative strength vs all available benchmarks.      Args:         stock_, Clear the cached index data (e.g., between runs). (+3 more)

### Community 26 - "Feature Importance Reports"
Cohesion: 0.23
Nodes (11): compare_model_importances(), compute_shap_importance(), generate_report(), get_model_importance(), Phase 4.5 — Feature Importance & Selection.  Analyzes feature importance from tr, Select features above a minimum importance threshold.      Args:         importa, Generate a text report of feature importance analysis.      Args:         compar, Load feature importance CSV from a saved model directory. (+3 more)

### Community 27 - "Drift Detection & Retrain"
Cohesion: 0.28
Nodes (11): check_model_drift(), _load_retrain_log(), _log_retrain(), Phase 6.3 — Monthly Model Retraining with Drift Detection.  Automates model retr, Check for model drift by comparing backtest metrics to live performance.      Lo, Load retrain log entries., Retrain model if enough time has passed since last retrain.      Args:         m, Retrain model on latest dataset.      Args:         model_type: 'lightgbm' or 'x (+3 more)

### Community 28 - "OHLCV Download"
Cohesion: 0.27
Nodes (11): download_ohlcv_batch(), fetch_ohlcv(), get_date_range(), load_filtered_universe(), Step 1.2 — Historical OHLCV Download.  Downloads 2 years of daily OHLCV data for, Save OHLCV data to Parquet file. Merges with existing if incremental., Main entry point: download OHLCV for all filtered stocks.      Args:         inc, Load yfinance symbols from the filtered universe CSV. (+3 more)

### Community 29 - "Universe Fetcher"
Cohesion: 0.27
Nodes (11): apply_volume_filter(), fetch_nse_equity_list(), fetch_universe(), filter_eq_series(), map_to_yfinance_symbols(), Step 1.1 — Stock Universe Fetcher.  Fetches all NSE-listed equities, filters to, Main entry point: fetch, filter, and save stock universe.      Returns (full_uni, Fetch the full list of NSE-listed equities via nselib. (+3 more)

### Community 30 - "Dark Theme Landing Page"
Cohesion: 0.18
Nodes (13): Solar Terminal Landing Page (Dark Theme), Solar Terminal Dark Theme, Amber/Orange Accent Token, Dark Background Token, Allocation Card, Alpha Brief Panel, Left Icon Rail, Net Worth Card (+5 more)

### Community 31 - "Auth Routes"
Cohesion: 0.36
Nodes (8): login(), LoginRequest, Authentication endpoints — register, login, token refresh., # TODO: persist user to DB, hash password, return token, # TODO: verify credentials, return token, register(), RegisterRequest, TokenResponse

### Community 32 - "Light Theme Landing Page"
Cohesion: 0.2
Nodes (10): Solar Terminal Landing Page (Light Theme), Solar Terminal Light Theme Tokens, Allocation Card (Light), Alpha Brief Panel (Light), Net Worth Card (Light), Risk Analysis Panel (Light), Central Solar Orb (Light), Top Navigation Bar (Light) (+2 more)

### Community 33 - "Backend Logging"
Cohesion: 0.38
Nodes (5): get_logger(), Centralized logging configuration for AlphaForge backend.  Thin wrapper around t, Configure and return the application root logger., Return a child logger under the ``alphaforge`` namespace., setup_logging()

### Community 34 - "Security & JWT"
Cohesion: 0.48
Nodes (5): create_access_token(), decode_access_token(), hash_password(), Security utilities — password hashing, JWT tokens., verify_password()

### Community 35 - "Loading Screen"
Cohesion: 0.33
Nodes (7): Light Solar Terminal Theme, Centered Logo Card, AlphaForge Loading Screen, Loading Progress Bar, App Boot/Splash Purpose, Terminal Metadata Corners, ALPHA FORGE Wordmark

### Community 36 - "Initial pgvector Migration"
Cohesion: 0.6
Nodes (3): downgrade(), initial schema with pgvector memory  Revision ID: 640eee61bc50 Revises:  Create, upgrade()

### Community 37 - "Portfolio Cards UI"
Cohesion: 0.67
Nodes (2): Allocation(), NetWorth()

### Community 38 - "Health Endpoint"
Cohesion: 0.67
Nodes (2): health_check(), Health check endpoints.

### Community 39 - "Health Tests"
Cohesion: 0.67
Nodes (2): Backend test: health check., test_health_check()

### Community 40 - "Root Layout"
Cohesion: 0.67
Nodes (1): RootLayout()

### Community 41 - "Home Page"
Cohesion: 0.67
Nodes (1): Home()

### Community 42 - "Header Component"
Cohesion: 0.67
Nodes (1): Header()

### Community 43 - "Sidebar Component"
Cohesion: 0.67
Nodes (1): Sidebar()

### Community 44 - "Risk Analysis UI"
Cohesion: 0.67
Nodes (1): RiskAnalysis()

### Community 45 - "Screener Picks UI"
Cohesion: 0.67
Nodes (1): ProbabilityBar()

### Community 46 - "Alpha Brief UI"
Cohesion: 0.67
Nodes (1): AlphaBrief()

### Community 47 - "Solar Orb Animation"
Cohesion: 0.67
Nodes (1): SolarOrb()

### Community 48 - "Market Overview UI"
Cohesion: 0.67
Nodes (1): MarketOverview()

### Community 49 - "AI Chat UI"
Cohesion: 0.67
Nodes (1): handleSend()

### Community 50 - "Query Providers"
Cohesion: 0.67
Nodes (1): QueryProvider()

### Community 51 - "AI Prompt Templates"
Cohesion: 0.67
Nodes (1): Domain-specific prompt templates for financial analysis.

### Community 52 - "tsup Build Config"
Cohesion: 0.67
Nodes (1): onSuccess()

### Community 53 - "Card Primitive"
Cohesion: 0.67
Nodes (1): Card()

### Community 54 - "Icon Primitive"
Cohesion: 0.67
Nodes (1): Icon()

### Community 55 - "Divider Primitive"
Cohesion: 0.67
Nodes (1): Divider()

### Community 56 - "Chip Primitive"
Cohesion: 0.67
Nodes (1): Chip()

### Community 57 - "Badge Primitive"
Cohesion: 0.67
Nodes (1): Badge()

### Community 58 - "Input Primitive"
Cohesion: 0.67
Nodes (1): twMerge()

### Community 59 - "Frontend Logo Asset"
Cohesion: 0.67
Nodes (3): AlphaForge Brand Identity, AlphaForge Logo (frontend/public/logo.png), Frontend Public Static Assets Folder

### Community 60 - "Solar Orb Tokens & README"
Cohesion: 1.0
Nodes (2): Solar Terminal Design Tokens, @alphaforge/solar-orb-ui README

## Knowledge Gaps
- **239 isolated node(s):** `Compute the N-day forward return from Adjusted Close prices.      Forward return`, `Convert forward return to binary classification label.      1 = stock returned >`, `Compute all labels for a single stock's OHLCV DataFrame.      Args:         df:`, `Compute labels for a single stock by loading its OHLCV parquet.      Args:`, `Get symbols that have OHLCV parquet files downloaded.` (+234 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Portfolio Cards UI`** (4 nodes): `PortfolioCards.tsx`, `Allocation()`, `NetWorth()`, `PortfolioCards.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Health Endpoint`** (4 nodes): `health.py`, `health_check()`, `Health check endpoints.`, `health.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Health Tests`** (4 nodes): `test_health.py`, `Backend test: health check.`, `test_health_check()`, `test_health.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Root Layout`** (3 nodes): `layout.tsx`, `RootLayout()`, `layout.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Home Page`** (3 nodes): `page.tsx`, `Home()`, `page.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Header Component`** (3 nodes): `Header.tsx`, `Header()`, `Header.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Sidebar Component`** (3 nodes): `Sidebar.tsx`, `Sidebar()`, `Sidebar.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Risk Analysis UI`** (3 nodes): `RiskAnalysis.tsx`, `RiskAnalysis()`, `RiskAnalysis.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Screener Picks UI`** (3 nodes): `ScreenerPicks.tsx`, `ProbabilityBar()`, `ScreenerPicks.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Alpha Brief UI`** (3 nodes): `AlphaBrief()`, `AlphaBrief.tsx`, `AlphaBrief.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Solar Orb Animation`** (3 nodes): `SolarOrb.tsx`, `SolarOrb()`, `SolarOrb.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Market Overview UI`** (3 nodes): `MarketOverview.tsx`, `MarketOverview()`, `MarketOverview.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `AI Chat UI`** (3 nodes): `handleSend()`, `AIChat.tsx`, `AIChat.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Query Providers`** (3 nodes): `providers.tsx`, `QueryProvider()`, `providers.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `AI Prompt Templates`** (3 nodes): `prompts.py`, `Domain-specific prompt templates for financial analysis.`, `prompts.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `tsup Build Config`** (3 nodes): `tsup.config.ts`, `onSuccess()`, `tsup.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Card Primitive`** (3 nodes): `Card()`, `Card.tsx`, `Card.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Icon Primitive`** (3 nodes): `Icon()`, `Icon.tsx`, `Icon.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Divider Primitive`** (3 nodes): `Divider()`, `Divider.tsx`, `Divider.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Chip Primitive`** (3 nodes): `Chip()`, `Chip.tsx`, `Chip.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Badge Primitive`** (3 nodes): `Badge()`, `Badge.tsx`, `Badge.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Input Primitive`** (3 nodes): `twMerge()`, `Input.tsx`, `Input.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Solar Orb Tokens & README`** (2 nodes): `Solar Terminal Design Tokens`, `@alphaforge/solar-orb-ui README`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `LLMProvider` connect `LLM Provider Adapters` to `LLM CLI & Routes`, `Trade & Logger Packages`, `Config & Env Settings`?**
  _High betweenness centrality (0.123) - this node is a cross-community bridge._
- **Why does `evaluate_walk_forward()` connect `Backtest Engine` to `Trade & Logger Packages`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Are the 84 inferred relationships involving `LLMProvider` (e.g. with `LLMGateway` and `LLMGateway — main entry point that ties providers, router, rate limiter, and cos`) actually correct?**
  _`LLMProvider` has 84 INFERRED edges - model-reasoned connections that need verification._
- **Are the 52 inferred relationships involving `QueryType` (e.g. with `LLMGateway` and `LLMGateway — main entry point that ties providers, router, rate limiter, and cos`) actually correct?**
  _`QueryType` has 52 INFERRED edges - model-reasoned connections that need verification._
- **Are the 48 inferred relationships involving `LLMResponse` (e.g. with `LLMGateway` and `LLMGateway — main entry point that ties providers, router, rate limiter, and cos`) actually correct?**
  _`LLMResponse` has 48 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `MemoryService` (e.g. with `ChatMessage` and `ChatRequest`) actually correct?**
  _`MemoryService` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 37 inferred relationships involving `RateLimits` (e.g. with `_BucketState` and `RateLimiter`) actually correct?**
  _`RateLimits` has 37 INFERRED edges - model-reasoned connections that need verification._