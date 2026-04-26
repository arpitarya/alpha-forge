# Frontend Application Structure

> **Core Principle**: 1 file = 1 component, Single Responsibility Principle throughout all layers
> max lines: 50 lines for utils, types, service, transformer. 100 lines for components.

## File Organization Overview

### Components Layer (`.types.ts`, `.const.ts`, `.tsx`)
- `Component.tsx` - React functional component only
- `component.types.ts` - Component props interfaces, enums, custom types
- `component.const.ts` - Constants, magic strings, default values, UI text

**Example**:
```
src/components/Dashboard/
├── Dashboard.tsx
├── dashboard.types.ts (DashboardProps interface)
└── dashboard.const.ts (DEFAULT_REFRESH_INTERVAL, CHART_COLORS)
```

### State Management (`.store.ts`)
- `domain.store.ts` - Zustand store for domain-specific state (auth, portfolio, screener)
- Use Zustand for global state; avoid Context for large shared state
- Colocate with feature folder

**Example**:
```
src/lib/store.ts - Central store exports
  → authStore (user, token, permissions)
  → portfolioStore (holdings, positions, allocation)
  → screenerStore (selectedPicks, filterCriteria)
```

---

## Services Layer (API Integration)

The service layer is **the single point of contact with the backend API**.

### 1. Service Definition (`*.service.ts`)
- Raw HTTP requests using axios client
- GET and POST functions; no business logic
- Handles HTTP verbs, endpoints, error responses

```typescript
// portfolio.service.ts
export async function getPortfolioHoldings(source?: string) {
  return apiClient.get("/portfolio/holdings", { params: { source } });
}

export async function uploadCsv(slug: string, file: File) {
  const formData = new FormData();
  formData.append("file", file);
  return apiClient.post(`/portfolio/sources/${slug}/upload`, formData);
}
```

### 2. Service Types (`*.service.types.ts`)
- Request parameter interfaces
- Response body interfaces
- Error response shapes

```typescript
// portfolio.service.types.ts
export interface GetHoldingsParams {
  source?: string;
}

export interface UploadCsvParams {
  slug: string;
  file: File;
}

export interface HoldingRawDTO {
  symbol: string;
  quantity: number;
  avg_price: number;
  // ... (upstream API format)
}
```

### 3. Service Constants (`*.service.const.ts`)
- Endpoint paths
- Default query parameters
- Retry policies
- Request timeout values

```typescript
// portfolio.service.const.ts
export const PORTFOLIO_ENDPOINTS = {
  HOLDINGS: "/portfolio/holdings",
  UPLOAD: "/portfolio/sources/:slug/upload",
  SYNC: "/portfolio/sources/:slug/sync",
};

export const PORTFOLIO_DEFAULTS = {
  HOLDINGS_FETCH_TIMEOUT: 5000,
  MAX_FILE_SIZE_MB: 50,
};
```

### 4. Service Empty States (`*.service.empty.ts`)
- Default/empty responses for error handling
- Skeleton data for loading states
- Fallback values

```typescript
// portfolio.service.empty.ts
export const EMPTY_HOLDINGS: HoldingRawDTO[] = [];

export const EMPTY_PORTFOLIO_RESPONSE = {
  totals: { invested: 0, current_value: 0, pnl: 0, pnl_pct: 0, count: 0 },
  holdings: [],
  allocation: [],
};
```

---

## Transformer Layer (`*.transformer.*`)

**Purpose**: Convert raw API responses → domain models.  
Maps uppercase/snake_case API fields → camelCase domain entities.

### 1. Transformer Function (`*.transformer.ts`)
- Pure functions transforming service responses
- Normalizes data structure
- Type-safe conversion

```typescript
// portfolio.transformer.ts
export function transformHolding(raw: HoldingRawDTO): HoldingDTO {
  return {
    symbol: raw.symbol,
    quantity: raw.quantity,
    avgPrice: raw.avg_price,
    currentValue: raw.quantity * raw.last_price,
    gainLoss: (raw.quantity * raw.last_price) - (raw.quantity * raw.avg_price),
  };
}

export function transformPortfolioResponse(raw: PortfolioRawResponse): PortfolioDTO {
  return {
    ...raw,
    holdings: raw.holdings.map(transformHolding),
    totalPnl: raw.holdings.reduce((sum, h) => sum + (h.pnl || 0), 0),
  };
}
```

### 2. Transformer Types (`*.transformer.types.ts`)
- Output domain model interfaces (DTO)
- Transformed response shapes

```typescript
// portfolio.transformer.types.ts
export interface HoldingDTO {
  symbol: string;
  quantity: number;
  avgPrice: number;
  currentValue: number;
  gainLoss: number;
  gainLossPct: number;
}

export interface PortfolioDTO {
  holdings: HoldingDTO[];
  totalPnl: number;
  allocation: Record<string, number>;
}
```

### 3. Transformer Constants (`*.transformer.const.ts`)
- Mapping tables
- Threshold values
- Color/tone assignments

```typescript
// portfolio.transformer.const.ts
export const GAIN_LOSS_TONE = (pnl: number) => 
  pnl > 0 ? "up" : pnl < 0 ? "dn" : "neutral";

export const ASSET_CLASS_LABELS = {
  equity: "Stocks",
  mutual_fund: "Mutual Funds",
  etf: "ETFs",
};
```

### 4. Transformer Empty (`*.transformer.empty.ts`)
- Default transformed models for errors
- Skeleton domain DTOs

```typescript
// portfolio.transformer.empty.ts
export const EMPTY_HOLDING_DTO: HoldingDTO = {
  symbol: "",
  quantity: 0,
  avgPrice: 0,
  currentValue: 0,
  gainLoss: 0,
  gainLossPct: 0,
};
```

---

## Query Layer (React Query Integration)

**Purpose**: Bridge between components and services—handle fetching, caching, mutations.

### 1. Query Hooks (`*.query.ts`)
- TanStack React Query `useQuery` and `useMutation` hooks
- Integrates transformers automatically
- Handles errors, loading states, caching

```typescript
// portfolio.query.ts
export function usePortfolioHoldings(source?: string, options?: Partial<UseQueryOptions>) {
  return useQuery({
    queryKey: ["portfolio", "holdings", source ?? "all"],
    queryFn: async () => {
      const raw = await portfolioService.getHoldings(source);
      return transformPortfolioResponse(raw.data);
    },
    staleTime: 10_000,
    ...options,
  });
}

export function useUploadCsv() {
  return useMutation({
    mutationFn: async (params: { slug: string; file: File }) =>
      portfolioService.uploadCsv(params.slug, params.file),
  });
}
```

### 2. Query Types (`*.query.types.ts`)
- Query parameter interfaces
- Mutation input types
- Hook return overrides

```typescript
// portfolio.query.types.ts
export interface UsePortfolioHoldingsParams {
  source?: string;
  enabled?: boolean;
}
```

### 3. Query Constants (`*.query.const.ts`)
- Query key factories
- Stale times
- Cache invalidation triggers

```typescript
// portfolio.query.const.ts
export const PORTFOLIO_QUERY_KEYS = {
  all: ["portfolio"],
  holdings: ["portfolio", "holdings"],
  bySource: (source: string) => ["portfolio", "holdings", source],
};

export const STALE_TIMES = {
  HOLDINGS: 10_000,
  POSITIONS: 5_000,
  TREEMAP: 10_000,
};
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────┐
│         React Component (.tsx)                   │
│  - Renders UI                                    │
│  - Calls usePortfolioHoldings()                  │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│    Query Hook (*.query.ts)                       │
│  - usePortfolioHoldings()                        │
│  - Manages caching & fetching                    │
│  - Calls transformer on success                  │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│   Transformer (*.transformer.ts)                 │
│  - transformPortfolioResponse()                  │
│  - Raw API → Domain Model (DTO)                 │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│    Service Layer (*.service.ts)                  │
│  - portfolioService.getHoldings()                │
│  - Makes HTTP request via apiClient              │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │   Backend API       │
         │  (FastAPI/Python)   │
         └─────────────────────┘
```

---

## Import/Export Patterns

### Component File Imports
```typescript
// Dashboard.tsx
import { usePortfolioHoldings } from "@/lib/queries";
import { portfolioStore } from "@/lib/store";
import { DASHBOARD_CONFIG } from "./dashboard.const";
import type { DashboardProps } from "./dashboard.types";
```

### Barrel Exports
Create `index.ts` in each feature folder:
```typescript
// src/components/Dashboard/index.ts
export { Dashboard } from "./Dashboard";
export { useDashboardStore } from "./dashboard.store";
export type { DashboardProps } from "./dashboard.types";
```

---

## Best Practices

### ✅ Do's
1. **One component per file** – Keep logic separated and testable
2. **Transform at query layer** – Never pass raw API responses to components
3. **Use query keys consistently** – Enables proper cache invalidation
4. **Colocate constants** – Keep magic strings in `.const.ts` files
5. **Type everything** – Strict TypeScript throughout
6. **Store global state in Zustand** – Not Context or Redux
7. **Use axios client** – All HTTP calls through `src/lib/api.ts`

### ❌ Don'ts
1. **Don't mix API calls in components** – Use query hooks instead
2. **Don't mutate raw API responses** – Transform them
3. **Don't create random service files** – Stick to naming conventions
4. **Don't use Context for global state** – Use Zustand stores
5. **Don't spread `options` at end of hooks** – Explicit > implicit
6. **Don't skip types** – No `any` without justification

---

## Directory Structure Example

```
src/
├── app/                          # Next.js pages & layouts
├── components/
│   ├── Dashboard/
│   │   ├── Dashboard.tsx         # Component
│   │   ├── dashboard.types.ts    # Component props
│   │   ├── dashboard.const.ts    # UI constants
│   │   ├── dashboard.store.ts    # Zustand store (if needed)
│   │   └── index.ts              # Barrel export
│   │
│   ├── PortfolioCard/
│   │   ├── PortfolioCard.tsx
│   │   ├── portfolioCard.types.ts
│   │   ├── portfolioCard.const.ts
│   │   └── index.ts
│   │
│   └── terminal/                 # Feature folder
│       ├── SolarOrb.tsx
│       ├── ScreenerPicks.tsx
│       ├── RiskAnalysis.tsx
│       └── index.ts
│
├── lib/
│   ├── api.ts                    # Axios client instance
│   ├── queries.ts                # All TanStack React Query hooks
│   ├── store.ts                  # All Zustand stores
│   └── logger.ts                 # Logger setup
│
└── services/
    ├── portfolio/
    │   ├── portfolio.service.ts
    │   ├── portfolio.service.types.ts
    │   ├── portfolio.service.const.ts
    │   ├── portfolio.service.empty.ts
    │   ├── portfolio.transformer.ts
    │   ├── portfolio.transformer.types.ts
    │   ├── portfolio.transformer.const.ts
    │   ├── portfolio.transformer.empty.ts
    │   └── index.ts              # Barrel export
    │
    ├── screener/
    │   ├── screener.service.ts
    │   ├── screener.transformer.ts
    │   ├── screener.query.ts     # Alternative: put queries here
    │   └── index.ts
    │
    └── market/
        ├── market.service.ts
        ├── market.transformer.ts
        └── index.ts
```

---

---

## Extended Naming Conventions

### Utility Functions (`utils/`)
Prefixed by action/intent:

```typescript
// utils/portfolio.utils.ts
export function calculatePortfolioMetrics(holdings: HoldingDTO[]) { }    // calculate*
export function formatCurrency(value: number) { }                         // format*
export function parseHolding(raw: Record<string, unknown>) { }            // parse*
export function isValidSymbol(symbol: string): boolean { }                // is*
export function hasPosition(symbol: string, holdings: HoldingDTO[]) { }   // has*
export function shouldRebalance(allocation: Record<string, number>) { }   // should*
export function canPlaceOrder(holdings: HoldingDTO[]): boolean { }        // can*
export function getAssetAllocation(holdings: HoldingDTO[]) { }            // get*
export function setDefaultValues<T>(data: Partial<T>): T { }              // set*
export function normalizeSymbol(symbol: string): string { }               // normalize*
export function groupByAssetClass(holdings: HoldingDTO[]) { }             // groupBy*
export function enrichHolding(holding: HoldingDTO) { }                    // enrich*
export function validateOrderParams(order: OrderDTO): ValidationError[] { }  // validate*
```

### Event Handlers (Components)
`handle*` prefix for all event handlers:

```typescript
// Dashboard.tsx
export function Dashboard() {
  const handleSymbolChange = (symbol: string) => { };
  const handleRefresh = async () => { };
  const handleFilterSubmit = (filters: FilterDTO) => { };
  const handleError = (error: Error) => { };
  const handleSuccess = (data: SuccessDTO) => { };
}
```

### Type/Interface Naming

| Suffix | Usage | Example |
|--------|-------|---------|
| `DTO` | Data Transfer Object (from API/transformer) | `HoldingDTO`, `PortfolioDTO` |
| `Props` | Component props interface | `DashboardProps`, `CardProps` |
| `Request` | API request payload | `CreateOrderRequest`, `SyncSourceRequest` |
| `Response` | API response payload | `HoldingsResponse`, `QuoteResponse` |
| `State` | State machine/store state | `PortfolioState`, `AuthState` |
| `Action` | Redux-like action (Zustand) | `SetHoldingsAction`, `ClearCacheAction` |
| `Config` | Configuration object | `ChartConfig`, `ThemeConfig` |
| `Error` | Error type | `ValidationError`, `APIError` |
| `Params` | Function parameters (when complex) | `GetHoldingsParams`, `SearchParams` |
| `Options` | Optional settings | `QueryOptions`, `RequestOptions` |

```typescript
// portfolio.service.types.ts
export interface HoldingDTO { }           // From transformer
export interface DashboardProps { }       // Component props
export interface GetHoldingsRequest { }   // API request
export interface HoldingsResponse { }     // API response raw
export interface PortfolioState { }       // Zustand state

// portfolio.transformer.types.ts
export interface HoldingDTO { }           // Domain model (same name!)
export interface PortfolioError extends Error { }
export interface TransformOptions { currency?: string; }
```

### Boolean Variables & Functions
Always be explicit:

```typescript
// ❌ Bad
let disabled: boolean;
let loading: boolean;

// ✅ Good - State variables
const isLoading = true;
const isDisabled = true;
const hasError = false;
const shouldShowModal = true;
const willFetch = false;
const canEdit = true;

// ✅ Good - Function names
export function isValidEmail(email: string): boolean { }
export function hasPermission(user: User, action: string): boolean { }
export function shouldRebalance(portfolio: Portfolio): boolean { }
export function canDeleteOrder(order: Order): boolean { }
export function willExpire(date: Date): boolean { }
```

### Query/Selector Naming (Zustand)

```typescript
// src/lib/store.ts
export const portfolioStore = create<PortfolioState>((set, get) => ({
  // State
  holdings: [],
  isLoading: false,
  
  // Selectors (prefix with 'get')
  getHoldingBySymbol: (symbol: string) => 
    get().holdings.find(h => h.symbol === symbol),
  
  getTotalValue: () =>
    get().holdings.reduce((sum, h) => sum + h.currentValue, 0),
  
  hasPosition: (symbol: string) =>
    get().holdings.some(h => h.symbol === symbol),
  
  // Actions (imperative verbs)
  setHoldings: (holdings) => set({ holdings }),
  addHolding: (holding) => set(state => ({
    holdings: [...state.holdings, holding]
  })),
  removeHolding: (symbol) => set(state => ({
    holdings: state.holdings.filter(h => h.symbol !== symbol)
  })),
  clearCache: () => set({ holdings: [], isLoading: false }),
  startLoading: () => set({ isLoading: true }),
  stopLoading: () => set({ isLoading: false }),
}));
```

### API Client Methods

```typescript
// src/lib/api.ts
export const apiClient = {
  // Query methods
  get: <T>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> => { },
  getList: <T>(url: string, params?: Record<string, any>) => { },   // For paginated lists
  
  // Mutation methods
  post: <T>(url: string, data?: any) => { },
  put: <T>(url: string, data?: any) => { },      // Full replacement
  patch: <T>(url: string, data?: any) => { },    // Partial update
  delete: <T>(url: string) => { },
  
  // Batch operations
  postMany: <T>(url: string, items: any[]) => { },
  deleteMany: <T>(url: string, ids: string[]) => { },
};

// Usage
await apiClient.get<HoldingsResponse>("/portfolio/holdings");
await apiClient.post<Order>("/orders", orderData);
await apiClient.patch<Holding>(`/holdings/${id}`, updates);
```

### Modal/Dialog Naming

```typescript
// Zustand modal store
export const modalStore = create<ModalState>((set) => ({
  modals: {
    editHolding: { isOpen: false, data: null },
    confirmDelete: { isOpen: false, data: null },
    placeOrder: { isOpen: false, data: null },
  },
  
  openModal: (modalName: string, data?: any) => set(state => ({
    modals: {
      ...state.modals,
      [modalName]: { isOpen: true, data }
    }
  })),
  
  closeModal: (modalName: string) => set(state => ({
    modals: {
      ...state.modals,
      [modalName]: { isOpen: false, data: null }
    }
  })),
}));

// Component file naming
// src/components/modals/
├── EditHoldingModal.tsx      // Closes on cancel/save
├── ConfirmDeleteModal.tsx    // Asks for confirmation
└── PlaceOrderModal.tsx       // Multi-step form
```

### Error & Loading States

```typescript
// *.query.ts - Naming in hooks
export function usePortfolioHoldings() {
  return useQuery({
    // Returns: data, isLoading, isError, error, isPending, isFetching
  });
}

// Component usage
const { data, isLoading, isError, error } = usePortfolioHoldings();

// ❌ Avoid
const { data, loading, hasError }

// State variable naming
const [isLoading, setIsLoading] = useState(false);
const [error, setError] = useState<Error | null>(null);
const [isSubmitting, setIsSubmitting] = useState(false);
const [didFetch, setDidFetch] = useState(false);
```

### Route/Page Naming

```
src/app/
├── page.tsx                    // Home / landing
├── portfolio/
│   ├── page.tsx                // /portfolio
│   ├── [id]/
│   │   └── page.tsx            // /portfolio/[id]
│   └── analytics/
│       └── page.tsx            // /portfolio/analytics
├── screener/
│   ├── page.tsx                // /screener
│   └── [strategyId]/
│       └── page.tsx            // /screener/[strategyId]
└── settings/
    └── page.tsx                // /settings

// Route constants
export const ROUTES = {
  HOME: "/",
  PORTFOLIO: "/portfolio",
  PORTFOLIO_DETAIL: (id: string) => `/portfolio/${id}`,
  PORTFOLIO_ANALYTICS: "/portfolio/analytics",
  SCREENER: "/screener",
  SCREENER_STRATEGY: (id: string) => `/screener/${id}`,
  SETTINGS: "/settings",
} as const;
```

### Component Variant Naming

```typescript
// button.types.ts
export type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";
export type ButtonSize = "sm" | "md" | "lg";
export type ButtonState = "idle" | "loading" | "disabled" | "error";

// button.const.ts
export const BUTTON_VARIANTS = {
  PRIMARY: "primary",
  SECONDARY: "secondary",
  GHOST: "ghost",
  DANGER: "danger",
} as const;

export const BUTTON_SIZES = {
  SMALL: "sm",
  MEDIUM: "md",
  LARGE: "lg",
} as const;
```

### Testing File Naming

```
src/
├── components/
│   └── Dashboard/
│       ├── Dashboard.tsx
│       ├── Dashboard.test.tsx         # Unit test for component
│       ├── Dashboard.spec.tsx         # Integration test
│       └── dashboard.utils.test.ts    # Utils test
├── lib/
│   ├── api.ts
│   └── api.test.ts
└── utils/
    ├── portfolio.utils.ts
    └── portfolio.utils.test.ts

// Test file naming pattern
describe("Dashboard", () => {
  describe("renderPortfolioCards", () => {
    it("should display correct holdings count", () => { });
    it("should handle empty holdings gracefully", () => { });
  });
  
  describe("event handlers", () => {
    it("handleRefresh should trigger data refetch", () => { });
  });
});
```

### Enum Naming

```typescript
// ✅ Good - CONSTANT_CASE for string unions that act like enums
export const ASSET_CLASSES = {
  EQUITY: "equity",
  MUTUAL_FUND: "mutual_fund",
  ETF: "etf",
  BOND: "bond",
  GOLD: "gold",
  CRYPTO: "crypto",
  CASH: "cash",
} as const;

export type AssetClass = (typeof ASSET_CLASSES)[keyof typeof ASSET_CLASSES];

// ✅ Alternative - TypeScript Enum (when ordered matters)
export enum OrderStatus {
  PENDING = "PENDING",
  EXECUTING = "EXECUTING",
  FILLED = "FILLED",
  CANCELLED = "CANCELLED",
  REJECTED = "REJECTED",
}

// ✅ Good - PascalCase for type discriminators
export type PortfolioAction = 
  | { type: "SetHoldings"; payload: HoldingDTO[] }
  | { type: "AddHolding"; payload: HoldingDTO }
  | { type: "RemoveHolding"; payload: string };
```

### Mock/Stub/Fixture Naming

```
src/
├── __tests__/
│   ├── fixtures/
│   │   ├── mockHoldings.ts         # Mock data
│   │   ├── mockResponses.ts        # Mock API responses
│   │   └── testHelpers.ts          # Utility functions
│   └── mocks/
│       ├── mockApi.ts              # Mock axios client
│       └── mockStore.ts            # Mock Zustand store
└── services/
    └── __mocks__/
        └── portfolio.service.ts    # Jest auto-mock

// File content example
// mockHoldings.ts
export const mockHolding: HoldingDTO = {
  symbol: "INFY",
  quantity: 100,
  avgPrice: 1500,
  currentValue: 160000,
};

export const mockHoldings: HoldingDTO[] = [
  { ...mockHolding },
  { ...mockHolding, symbol: "TCS", quantity: 50 },
];

// mockResponses.ts
export const mockHoldingsResponse: PortfolioDTO = {
  holdings: mockHoldings,
  totalPnl: 10000,
  allocation: { equity: 0.8, cash: 0.2 },
};
```

### Cache/Optimization Naming

```typescript
// Cache key builders
export const CACHE_KEYS = {
  HOLDINGS: "holdings",
  HOLDINGS_DETAIL: (symbol: string) => `holdings:${symbol}`,
  POSITIONS: "positions",
  POSITIONS_REALTIME: "positions:rt",
  SCREENER_PICKS: (date?: string) => `screener:picks:${date || "latest"}`,
} as const;

// Memoization
export const memoizedCalculateMetrics = useMemo(
  () => calculatePortfolioMetrics(holdings),
  [holdings]
);

// Callbacks
const memoizedHandleRefresh = useCallback(() => {
  refetch();
}, [refetch]);
```

### Async/Promise Naming

```typescript
// Service methods
export async function fetchPortfolioHoldings(source?: string) { }  // fetch*
export async function createOrder(order: OrderDTO) { }             // create*, post*
export async function updateHolding(id: string, data: Partial<HoldingDTO>) { }  // update*, put*, patch*
export async function deleteHolding(id: string) { }                // delete*, remove*

// Async state
const [isPending, setIsPending] = useState(false);
const [didComplete, setDidComplete] = useState(false);
const [isFetching, setIsFetching] = useState(false);
```

### Computed/Derived Values

```typescript
// Within components or hooks
const totalInvested = useMemo(
  () => holdings.reduce((sum, h) => sum + h.invested, 0),
  [holdings]
);

const portfolioMetrics = useMemo(
  () => calculateMetrics(holdings),
  [holdings]
);

const gainLossPercentage = useMemo(
  () => ((totalCurrent - totalInvested) / totalInvested) * 100,
  [totalCurrent, totalInvested]
);

// Naming pattern: {adjective}{Noun} or {Noun}{Metric}
// Examples:
const totalValue = 0;
const avgPrice = 0;
const maxGainLoss = 0;
const minPosition = 0;
```

---

## Full Naming Reference Table

| Pattern | Example | File Location |
|---------|---------|----------------|
| Component | `Dashboard.tsx` | `components/Dashboard/` |
| Component Props | `DashboardProps` | `dashboard.types.ts` |
| Component Constants | `DASHBOARD_CONFIG` | `dashboard.const.ts` |
| Service | `portfolioService.getHoldings()` | `services/portfolio/portfolio.service.ts` |
| Service Types | `GetHoldingsParams` | `portfolio.service.types.ts` |
| Transformer | `transformHolding()` | `portfolio.transformer.ts` |
| Query Hook | `usePortfolioHoldings()` | `lib/queries.ts` |
| Store | `portfolioStore` | `lib/store.ts` |
| Selector | `portfolioStore.getHoldingBySymbol()` | `lib/store.ts` |
| Utility | `calculatePortfolioMetrics()` | `utils/portfolio.utils.ts` |
| Event Handler | `handleRefresh()` | `components/*/Component.tsx` |
| Boolean Value | `isLoading`, `hasError` | Any scope |
| Boolean Function | `canEdit()`, `isValid()` | `utils/`, services |
| Route | `ROUTES.PORTFOLIO` | `lib/routes.ts` |
| Enum/Const | `ASSET_CLASSES.EQUITY` | `*.const.ts` |
| Mock Data | `mockHoldings` | `__tests__/fixtures/` |
| Test File | `Component.test.tsx` | Same dir as component |

---

## Implementation Tips

1. **Be Consistent** – Apply the same pattern across the entire codebase
2. **Use TypeScript Strict Mode** – Catch naming inconsistencies at compile time
3. **Enforce with ESLint** – Add rules for naming conventions (e.g., `@typescript-eslint/naming-convention`)
4. **Document Domain Models** – Keep a shared glossary of DTOs and domain terms
5. **Review & Refactor** – Rename aggressively when patterns emerge
6. **Prefix/Suffix Standardization** – Use `is*`, `has*`, `should*`, `can*` consistently for booleans