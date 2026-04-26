# Frontend — Variable Conventions

> One file per concept (component / service / transformer / hook). One name shape per concept.
> The discipline below is what keeps a multi-thousand-file Next.js app readable five months in.

---

## 1. Universal rules

1. **Names should describe intent, not type.** `holdings` not `data`, `selectedSourceSlug` not `value`. The reader should be able to guess the type without seeing it.
2. **`const` only.** Never `let`, never `var`. If you need to reassign, restructure. (For loop counters and reducer accumulators, prefer functional methods — `map` / `reduce` / `flatMap`.)
3. **No abbreviations** unless they're industry-standard: `idx`, `i`, `id`, `url`, `dto`, `pnl`, `fx`, `rsi`. Anything else, write it out.
4. **No noise prefixes/suffixes.** `IUser` (Hungarian), `UserClass`, `holdingsList` are banned — the type system already tells you they're interface/class/array.
5. **Boolean names start with a question word.** `is*`, `has*`, `should*`, `can*`, `did*`, `will*`. A bare `disabled` or `active` is ambiguous on a multi-arg call site; `isDisabled` is not.
6. **Never use `any`** without a comment explaining why. Prefer `unknown` + a narrowing function.
7. **Avoid stringly-typed APIs.** Prefer `as const` objects over inline string unions when the value is referenced from multiple files.
8. **Mutations get verbs, queries get nouns.** `setHoldings`, `clearCache`, `holdings`, `totalValue`. Never `getHoldings()` for a synchronous computed value (use `totalValue`).

---

## 2. Casing matrix

| Kind | Casing | Example |
|------|--------|---------|
| Local variable | `camelCase` | `selectedSourceSlug`, `totalInvested` |
| Function | `camelCase` | `transformHolding`, `handleRefresh` |
| Component | `PascalCase` | `Dashboard`, `PortfolioHeader` |
| Type / interface | `PascalCase` | `HoldingDTO`, `DashboardProps` |
| React hook | `useCamelCase` | `usePortfolioHoldings`, `useTheme` |
| Constants (module-level, immutable) | `UPPER_SNAKE_CASE` | `DEFAULT_TIMEOUT_MS`, `STALE_TIMES` |
| Enum members | `UPPER_SNAKE_CASE` | `OrderStatus.PENDING` |
| File (component) | `PascalCase.tsx` | `Dashboard.tsx` |
| File (everything else) | `kebab-or-dot.ext` | `portfolio.service.ts`, `dashboard.const.ts` |
| CSS class | `kebab-case` (when not Tailwind) | `solar-orb`, `card-glow` |
| URL / route segment | `kebab-case` | `/portfolio/risk-meter` |
| API path / query param | `snake_case` (matches backend) | `/portfolio/sources/{slug}/upload`, `?source=zerodha` |
| JSON field over the wire | `snake_case` (raw DTO only) | `current_value`, `pnl_pct` |
| JSON field after transformer | `camelCase` (domain DTO) | `currentValue`, `pnlPct` |

> **The transformer layer is where snake_case dies.** Components must never see `current_value`.

---

## 3. Variable name templates

### Numeric quantities

Pattern: `{adjective}{Noun}` or `{Noun}{Metric}`. Always include the unit when it isn't obvious.

```ts
const totalInvested = 0;          // currency, in user base ccy (₹)
const totalInvestedInr = 0;       // explicit when mixed-ccy is in scope
const avgPrice = 0;
const maxDrawdownPct = 0;         // % — append Pct
const refreshIntervalMs = 5_000;  // ms — append Ms
const refreshIntervalSec = 5;     // s  — append Sec
const fontSizePx = 14;
const ttlSeconds = 60;
```

❌ `time = 5000` — units? seconds? ms?  
❌ `value = 1234` — value of what?

### Booleans

Always start with `is`, `has`, `should`, `can`, `did`, `will`. Pair them in opposites instead of negating:

```ts
const isOpen = true;     // not !isClosed
const isLoading = true;
const isDisabled = false;
const hasError = false;
const hasMounted = true;
const shouldShowModal = true;
const canEdit = true;
const didFetch = false;
const willExpireSoon = false;
```

For state toggles, mirror the boolean name:

```ts
const [isOpen, setIsOpen] = useState(false);
const open = () => setIsOpen(true);   // not setOpen(true) — the name is wrong
const close = () => setIsOpen(false);
```

### Counts and indices

```ts
const holdingsCount = holdings.length;   // not holdingsLength
const selectedIndex = 0;
const activeIdx = 2;                     // idx is OK in tight scopes (loops)
```

### Arrays

Plural noun, no `List`/`Array` suffix.

```ts
const holdings: HoldingDTO[] = [];
const sources: SourceInfoDTO[] = [];
// ❌ holdingsList, holdingsArray
```

### Maps / records

`{Key}By{Discriminator}` for lookup tables; plain noun for grouped data.

```ts
const holdingBySymbol: Record<string, HoldingDTO> = {};
const holdingsByAssetClass: Record<AssetClass, HoldingDTO[]> = {};
```

### Identifiers

Always suffix `Id` (lowercase `d`) when the value is a foreign key.

```ts
const userId: string = "u_123";
const orderId: string = "o_456";
const sourceSlug: string = "zerodha";  // slug, not id, when human-readable
```

### Refs

Always end React refs in `Ref`:

```ts
const fileInputRef = useRef<HTMLInputElement>(null);
const chartContainerRef = useRef<HTMLDivElement>(null);
```

### Async / loading state

Mirror React Query's vocabulary so consumers get a consistent surface:

```ts
// Local async
const [isLoading, setIsLoading] = useState(false);
const [isSubmitting, setIsSubmitting] = useState(false);
const [error, setError] = useState<Error | null>(null);

// React Query (don't re-alias)
const { data, isLoading, isError, error, isPending, isFetching } = useHoldings();

// ❌ never: const { data, loading, hasError, errMsg }
```

### Errors

```ts
type PortfolioError = Error;
const [error, setError] = useState<PortfolioError | null>(null);

// Throwing
throw new Error(`Unknown source: ${slug}`);

// Re-throwing with cause
} catch (cause) {
  throw new Error("Failed to upload CSV", { cause });
}
```

---

## 4. Function names

### Verbs by category

| Category | Verbs | Example |
|----------|-------|---------|
| Side-effect (state) | `set`, `clear`, `reset`, `add`, `remove`, `toggle` | `setHoldings`, `clearCache` |
| Side-effect (network) | `fetch`, `create`, `update`, `delete`, `upload`, `sync` | `fetchHoldings`, `uploadCsv` |
| Pure computation | `calculate`, `compute`, `derive`, `format`, `parse`, `normalize`, `enrich`, `groupBy` | `calculateMetrics`, `formatCurrency` |
| Boolean check | `is`, `has`, `should`, `can` | `isValidEmail`, `hasPosition` |
| Lookup / selector | `get`, `find`, `select` | `getHoldingBySymbol`, `selectActiveSource` |
| Event handler | `handle` | `handleSubmit`, `handleRowClick` |
| Lifecycle / on-event callback | `on` | `onSelect`, `onUploadComplete` |
| Transformer | `transform`, `mapTo`, `from*`, `to*` | `transformHolding`, `toApiPayload` |

> `handle*` lives inside a component (it knows about local state). `on*` lives on a prop signature (the parent passes it in).

```tsx
function PortfolioRow({ onSelect }: { onSelect: (id: string) => void }) {
  const handleClick = () => onSelect(row.id);
  return <button onClick={handleClick}>…</button>;
}
```

### Async functions

If it returns a `Promise`, prefer `async`/`await` over `.then()` chains, and pick a verb that implies asynchrony when it isn't obvious:

```ts
export async function fetchHoldings(source?: string): Promise<HoldingsResponseDTO> { … }
export async function uploadCsv(slug: string, file: File): Promise<UploadResult> { … }

// ❌ getHoldings() that hits the network — call it fetchHoldings()
```

---

## 5. Type / interface naming

| Suffix | Purpose | Example |
|--------|---------|---------|
| `DTO` | Domain transfer object — what flows through the app **after** transformation | `HoldingDTO`, `PortfolioDTO` |
| `Raw` / `RawDTO` | Wire shape **before** transformation (snake_case fields) | `HoldingRawDTO` |
| `Props` | Component props | `DashboardProps` |
| `Params` | Function params (when complex enough to need an interface) | `GetHoldingsParams` |
| `Options` | Optional behaviour knobs | `QueryOptions` |
| `Request` | API request body | `CreateOrderRequest` |
| `Response` | API response body | `HoldingsResponse` |
| `State` | Zustand / reducer state | `PortfolioState` |
| `Action` | Discriminated union member for reducers | `SetHoldingsAction` |
| `Event` | Domain event | `OrderFilledEvent` |
| `Config` | Configuration object | `ChartConfig` |
| `Error` | Error subclass | `ValidationError` |
| `Slug` | URL-safe identifier | `SourceSlug` |

Never combine suffixes (`HoldingDTOResponse` ❌). The shape is one or the other.

---

## 6. Constants

Module-level, frozen, `as const`:

```ts
// portfolio.const.ts
export const STALE_TIMES = {
  HOLDINGS: 10_000,
  POSITIONS: 5_000,
  TREEMAP: 10_000,
} as const;

export const DEFAULT_TARGETS_PCT = {
  EQUITY: 60,
  MUTUAL_FUND: 15,
  BOND: 15,
  GOLD: 5,
  CRYPTO: 3,
  CASH: 2,
} as const;
```

Numeric literals get **underscore separators** when they exceed 4 digits:

```ts
const REQUEST_TIMEOUT_MS = 30_000;
const MAX_PORTFOLIO_VALUE_INR = 10_000_000;
```

---

## 7. Generics

Single uppercase letters when there's no semantic meaning, `PascalCase` words when there is:

```ts
function pick<T, K extends keyof T>(obj: T, key: K): T[K] { … }

function transformList<Raw, Domain>(
  items: Raw[],
  fn: (raw: Raw) => Domain,
): Domain[] { … }
```

---

## 8. Discriminated unions

Use a `kind` (or `type`) field with `PascalCase` discriminator values. One union member per file when they have meaningful logic:

```ts
export type SyncResult =
  | { kind: "Success"; holdings: HoldingDTO[] }
  | { kind: "Empty" }
  | { kind: "Error"; error: Error };

function describe(r: SyncResult): string {
  switch (r.kind) {
    case "Success": return `${r.holdings.length} holdings`;
    case "Empty":   return "No holdings yet";
    case "Error":   return r.error.message;
  }
}
```

---

## 9. CSS-in-Tailwind variable references

When binding a runtime value into a Tailwind utility, use the `[color:var(--…)]` arbitrary syntax — never inline hex codes:

```tsx
<div className="bg-[color:var(--surface)] text-[color:var(--fg)]" />
```

CSS custom properties follow this scheme:

| Prefix | Purpose | Example |
|--------|---------|---------|
| `--bg`, `--fg`, `--line`, `--surface*` | Theme-switchable semantic tokens | `--surface-hi` |
| `--accent*` | Runtime accent palette | `--accent-soft` |
| `--orb-*` | Component-scoped (solar-orb-ball) | `--orb-glow` |
| `--af-*` | Legacy app-prefixed tokens (do not extend) | `--af-bg-card` |

---

## 10. Anti-patterns to refactor on sight

```ts
// ❌ Hungarian / type in name
const sHoldings: string[] = [];
const arrHoldings: Holding[] = [];

// ❌ Negated booleans
const notLoading = !isLoading;     // just use !isLoading at the call site

// ❌ Ambiguous units
setTimeout(refresh, 5000);          // 5 seconds? 5 ms? read the docs to find out
setTimeout(refresh, 5_000 /* ms */);  // ✓ until you have REFRESH_INTERVAL_MS

// ❌ Mutable accumulators outside reducers
let total = 0;
for (const h of holdings) total += h.currentValue;
const total = holdings.reduce((sum, h) => sum + h.currentValue, 0); // ✓

// ❌ Stringly-typed paths
queryClient.invalidateQueries({ queryKey: ["portfolio", "holdings", "all"] });
queryClient.invalidateQueries({ queryKey: PORTFOLIO_QUERY_KEYS.bySource("all") }); // ✓

// ❌ any escape hatches
function pick(obj: any, key: any): any { … }
function pick<T, K extends keyof T>(obj: T, key: K): T[K] { … } // ✓
```

---

## 11. Quick reference card

```
Components       PascalCase.tsx          Dashboard.tsx
Hooks            useCamelCase.ts         usePortfolioHoldings.ts
Types            PascalCase + suffix     HoldingDTO, DashboardProps
Functions        camelCase verb-first    transformHolding, fetchHoldings
Booleans         is/has/should/can…      isLoading, hasError
Constants        UPPER_SNAKE_CASE        STALE_TIMES, DEFAULT_TIMEOUT_MS
Files (svc)      kebab.dot.case          portfolio.service.ts
URLs             /kebab-case             /portfolio/risk-meter
API params       snake_case              ?source=zerodha
DTO fields       camelCase               currentValue
Raw DTO fields   snake_case              current_value (transformer-only)
Numeric literals 10_000                  underscore-grouped
```
