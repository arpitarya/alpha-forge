# Backend — Variable Conventions (Python 3.14)

> Names earn their keep at 3am during an incident. Spell them out.
> All async-first, all type-hinted, all ruff-clean.

---

## 1. Universal rules

1. **Type hint every signature.** No untyped public function or method. `mypy --strict` (or `pyright`) is the bar.
2. **Async by default.** Names of coroutines describe the action — no `async_` prefix. The signature already says it.
3. **No mutable defaults.** Use `field(default_factory=...)` or `None` + setup inside the body.
4. **Prefer dataclasses or Pydantic over plain dicts** for any data that crosses a function boundary more than once.
5. **No bare `except:`.** Catch the narrowest type that's correct. Re-raise with `raise NewError(...) from e` to preserve cause chains.
6. **No `print()`.** Use `get_logger(__name__).info(...)`.
7. **`from __future__ import annotations`** at the top of every module. This makes all annotations strings, removes runtime cost, and lets `X | None` work on older Pythons.
8. **One ORM class per file** in `app/models/`. Cross-class relationships use forward strings (`Mapped["User"]`).

---

## 2. Casing matrix

| Kind | Casing | Example |
|------|--------|---------|
| Module / package | `snake_case` | `portfolio_service.py`, `brokers/` |
| Class | `PascalCase` | `BrokerSource`, `HoldingRepository` |
| Function / method / variable | `snake_case` | `fetch_holdings`, `total_invested` |
| Constant (module-level) | `UPPER_SNAKE_CASE` | `DEFAULT_TIMEOUT_SEC`, `DISCLAIMER` |
| Type alias | `PascalCase` | `HoldingId = int` |
| TypeVar / Generic | single capital letter | `T`, `K`, `V` |
| Pydantic model | `PascalCase` + suffix | `CreateHoldingRequest`, `HoldingResponse` |
| Enum | `PascalCase` (class) + `UPPER_SNAKE_CASE` (members) | `AssetClass.MUTUAL_FUND` |
| Private / internal | `_leading_underscore` | `_squarify`, `_cached_holdings` |
| Test class / function | `Test*` / `test_*` | `class TestZerodhaParser`, `def test_parses_console_export` |
| URL path | `kebab-case` | `/portfolio/risk-meter` |
| Path / query param | `snake_case` | `scan_date`, `source_slug` |
| JSON field over the wire | `snake_case` | `current_value`, `pnl_pct` |
| Env var | `UPPER_SNAKE_CASE`, namespace-prefixed | `ANGEL_ONE_API_KEY` |

---

## 3. Pydantic model naming

| Suffix | Purpose | Example |
|--------|---------|---------|
| `Request` | Inbound API body | `CreateHoldingRequest` |
| `Response` | Outbound API body | `HoldingsResponse` |
| `DTO` | Internal data contract (rare in Python; prefer dataclasses) | `HoldingDTO` |
| `Params` | Query / path params bundled as one model | `ListHoldingsParams` |
| `Filter` | Read-only filter object | `HoldingsFilter` |
| `Settings` | pydantic-settings only — exactly one in the codebase | `Settings` |

```python
class CreateHoldingRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=32)
    quantity: float = Field(..., gt=0)
    avg_price: float = Field(..., gt=0)


class HoldingResponse(BaseModel):
    id: int
    symbol: str
    quantity: float
    avg_price: float
    pnl: float
    pnl_pct: float
```

---

## 4. Variable name templates

### Numeric quantities

Always include the unit when ambiguous:

```python
total_invested = 0.0           # currency, base ccy (₹)
total_invested_inr = 0.0       # explicit when mixed-ccy in scope
avg_price = 0.0
pnl_pct = 0.0                  # percent — append _pct
refresh_interval_sec = 5
refresh_interval_ms = 5_000    # explicit unit suffix
ttl_seconds = 60
batch_size = 100
max_concurrency = 8
```

❌ `time = 5` (seconds? days?)  
❌ `value = 1234` (of what?)

### Booleans

Always start with `is_`, `has_`, `should_`, `can_`, `did_`:

```python
is_authenticated = True
is_disabled = False
has_holdings = bool(rows)
should_retry = True
can_modify = user.role == "admin"
did_sync = False
```

### Counts and indices

```python
holdings_count = len(holdings)   # not len_holdings
selected_index = 0
batch_idx = 0                    # idx OK in tight scopes
```

### Collections

Plural nouns; no `_list`/`_array` suffix:

```python
holdings: list[Holding] = []
sources: dict[str, BrokerSource] = {}
holding_by_symbol: dict[str, Holding] = {}
holdings_by_asset_class: dict[AssetClass, list[Holding]] = {}
```

### Identifiers

Suffix with `_id` for foreign keys, `_slug` for human-readable IDs, `_uuid` when type-ambiguity matters:

```python
user_id: int
order_id: int
source_slug: str = "zerodha"
session_uuid: UUID
```

---

## 5. Function names

### Verbs by category

| Category | Verbs | Example |
|----------|-------|---------|
| Pure compute | `calculate_*`, `compute_*`, `derive_*`, `format_*`, `parse_*`, `normalize_*` | `calculate_metrics`, `parse_holding` |
| Data access (read) | `get_*`, `list_*`, `find_*`, `count_*`, `exists_*` | `get_holding`, `list_for_user` |
| Data access (write) | `create_*`, `update_*`, `delete_*`, `upsert_*` | `create_holding`, `delete_user` |
| Network / I/O | `fetch_*`, `sync_*`, `upload_*`, `download_*` | `fetch_holdings`, `sync` |
| Boolean check | `is_*`, `has_*`, `should_*`, `can_*` | `is_valid_isin`, `has_active_session` |
| Side-effect | `set_*`, `reset_*`, `clear_*`, `register_*` | `set_default_targets`, `register_source` |
| Translation | `to_*`, `from_*`, `as_*` | `to_dict`, `from_csv_row` |
| Lifecycle | `start_*`, `stop_*`, `close`, `dispose` | `start_listener`, `close` |

### Async / sync distinction

If the function does I/O, it's `async def` with the same name — no `_async` suffix:

```python
async def fetch_holdings() -> list[Holding]: ...
async def upload_csv(stream: IO[bytes]) -> int: ...

# Sync helpers in the same module
def parse_csv_row(row: dict[str, str]) -> Holding: ...
```

❌ `def fetch_holdings_async()` — the `async def` already says it.

---

## 6. Class naming

### Service / repository / client

| Pattern | Example |
|---------|---------|
| `*Service` | `PortfolioService`, `AIService` |
| `*Repository` | `HoldingRepository`, `UserRepository` |
| `*Client` | `KiteClient`, `LLMClient` |
| `*Source` (plug-ins) | `ZerodhaCSVSource`, `AngelOneSource` |
| `*Aggregator` | `HoldingsAggregator` |
| `*Factory` | `EngineFactory` (rare; prefer functions) |

### Exceptions

End in `Error`:

```python
class BrokerError(Exception): ...
class CSVParseError(BrokerError): ...
class AngelOneAuthError(BrokerError): ...
```

### Enums

```python
class AssetClass(str, Enum):
    EQUITY = "equity"
    MUTUAL_FUND = "mutual_fund"
    ETF = "etf"
```

Use `str, Enum` (or `IntEnum`) when the value is serialized — it's JSON-friendly and sorts predictably.

---

## 7. Module-level constants

```python
DEFAULT_TIMEOUT_SEC = 30
MAX_BATCH_SIZE = 100
DISCLAIMER = "Not SEBI registered investment advice."

DEFAULT_TARGETS_PCT: dict[AssetClass, float] = {
    AssetClass.EQUITY: 60.0,
    AssetClass.MUTUAL_FUND: 15.0,
}
```

Underscore separators on numeric literals over 4 digits:

```python
REQUEST_TIMEOUT_MS = 30_000
MAX_PORTFOLIO_VALUE_INR = 10_000_000
```

---

## 8. Type hints

### Built-in generics (3.9+)

Use lowercase built-ins, never `typing.List`/`Dict`:

```python
holdings: list[Holding]
by_symbol: dict[str, Holding]
maybe: str | None             # never Optional[str]
either: int | str
```

### Aliases

```python
# app/types.py
HoldingId = int
SourceSlug = str
Cents = int
```

### Generics

```python
from typing import TypeVar

T = TypeVar("T")
K = TypeVar("K")

async def fetch_one(model: type[T], pk: K) -> T | None: ...
```

### Protocols (for duck typing)

```python
class Closable(Protocol):
    async def close(self) -> None: ...
```

---

## 9. Async patterns

### Naming awaitables

A coroutine result and its variable should both be nouns describing the value, not the act:

```python
holdings = await fetch_holdings()
session = await create_session()

# ❌ holdings_future = await fetch_holdings()
```

### Concurrency

```python
results = await asyncio.gather(*(fetch_one(s) for s in sources))
async with asyncio.TaskGroup() as tg:
    tg.create_task(sync_one("zerodha"))
    tg.create_task(sync_one("groww"))
```

### Context managers

Pair `async with` for I/O resources:

```python
async with httpx.AsyncClient(base_url=BASE) as client:
    r = await client.get("/holdings")
```

---

## 10. Error handling

```python
try:
    raw = await client.fetch_holdings()
except httpx.HTTPStatusError as e:
    raise BrokerError(f"upstream returned {e.response.status_code}") from e

# Routes translate, services raise plain exceptions
@router.post("/sources/{slug}/sync")
async def sync_source(slug: str):
    try:
        await get_source(slug).sync()
    except BrokerError as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(e)) from e
```

Rules:
- Always `from e` to preserve the cause chain.
- Catch the narrowest exception that's correct.
- Don't catch `Exception` unless you re-raise (logging only doesn't count).
- `# noqa: BLE001` on broad excepts only when the broadness is the point (e.g. lifecycle handlers that must survive any failure).

---

## 11. Logging

```python
from app.core.logging import get_logger

logger = get_logger(__name__)   # always __name__, never a string literal

logger.info("Sync complete: %d holdings", len(holdings))
logger.warning("Source %s degraded: %s", slug, exc)
logger.exception("Unexpected error in sync")   # in except block — auto-includes traceback
```

- Always use `%s`-style formatting (deferred — saves cycles when log level filters).
- Lowercase first word, no trailing period.
- Include the relevant identifier (`slug`, `user_id`, …) by name, not just by value.

---

## 12. SQLAlchemy 2.0 conventions

```python
class Holding(Base):
    __tablename__ = "holdings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    quantity: Mapped[float]
    avg_price: Mapped[float]

    user: Mapped["User"] = relationship(back_populates="holdings")
```

- `Mapped[...]` for every column — never bare `Column(...)`.
- Index every column you'll filter on. Composite indexes via `Index()` in `__table_args__`.
- Repositories own all `select()` calls; services orchestrate.

---

## 13. Pydantic v2 conventions

```python
class HoldingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)   # equivalent of orm_mode

    id: int
    symbol: str
    quantity: float
```

- `from_attributes=True` to read directly from ORM objects.
- `Field(..., gt=0)` for cheap validation. Don't reinvent.
- Custom validators via `@field_validator("symbol")`.

---

## 14. Configuration

`app/core/config.py` holds **the only** `Settings` class. Anything env-driven flows through it.

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", ".env.cred"), extra="ignore")

    angel_one_api_key: str = ""
    request_timeout_sec: int = 30
```

Env vars are namespace-prefixed (`ANGEL_ONE_*`, `KITE_*`) so a casual `printenv` is grouped sensibly.

---

## 15. Quick reference card

```
Module             snake_case.py            portfolio_service.py
Package            snake_case/              brokers/
Class              PascalCase               BrokerSource, HoldingRepository
Function           snake_case               fetch_holdings, transform_row
Variable           snake_case               total_invested, holdings_count
Constant           UPPER_SNAKE_CASE         DEFAULT_TIMEOUT_SEC, DISCLAIMER
Boolean            is_/has_/should_/can_    is_authenticated, has_active_session
Pydantic models    PascalCase + suffix      CreateHoldingRequest, HoldingResponse
Enum               PascalCase + UPPER       AssetClass.MUTUAL_FUND
Exception          *Error                   CSVParseError, BrokerError
TypeVar            single capital           T, K, V
Private            _leading_underscore      _squarify, _cached_holdings
URL path           kebab-case               /portfolio/risk-meter
JSON field         snake_case               current_value
Env var            UPPER_SNAKE w/ prefix    ANGEL_ONE_API_KEY
Numeric literal    underscore-grouped       10_000
```
