# AlphaForge — Design System

> For designers (Gemini Stitch), AI design tools, and frontend developers.
> This file defines the visual language of AlphaForge.

## Brand Identity

- **Name**: AlphaForge
- **Tagline**: AI-Powered Trading Terminal for Indian Markets
- **Personality**: Professional, data-dense, trustworthy, fast, intelligent
- **Aesthetic**: Bloomberg Terminal meets modern dark UI — information-rich without clutter

## Color Palette

### Core Colors (Dark Theme — Primary)

| Token | Hex | Usage |
|-------|-----|-------|
| `--af-bg-primary` | `#0a0e17` | App background |
| `--af-bg-secondary` | `#111827` | Secondary background |
| `--af-bg-tertiary` | `#1a2332` | Cards hover, input backgrounds |
| `--af-bg-card` | `#151d2b` | Card/panel backgrounds |
| `--af-border` | `#1e293b` | Borders, dividers |
| `--af-text-primary` | `#e2e8f0` | Primary text |
| `--af-text-secondary` | `#94a3b8` | Secondary text, labels |
| `--af-text-muted` | `#64748b` | Muted text, placeholders |

### Accent Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `--af-accent-blue` | `#3b82f6` | Primary actions, links, focus rings |
| `--af-accent-cyan` | `#06b6d4` | Brand accent, "Alpha" in logo |
| `--af-green` | `#22c55e` | Positive change, profit, buy signals |
| `--af-red` | `#ef4444` | Negative change, loss, sell signals |
| `--af-orange` | `#f59e0b` | Warnings, neutral signals |
| `--af-purple` | `#a855f7` | AI-related UI elements |

### Semantic Usage

- **Price up / Profit**: `--af-green`
- **Price down / Loss**: `--af-red`
- **Neutral / Warning**: `--af-orange`
- **AI / Smart features**: `--af-purple`
- **Interactive / CTA**: `--af-accent-blue`

## Typography

### Font Stack
```
Primary: "JetBrains Mono", "SF Mono", "Fira Code", ui-monospace, monospace
Fallback: system-ui, -apple-system, sans-serif (only for long-form content)
```

### Scale
| Token | Size | Weight | Usage |
|-------|------|--------|-------|
| `heading-lg` | 18px | 700 | Page titles |
| `heading-sm` | 12px | 600 | Section headers (uppercase + tracking-wider) |
| `body` | 14px | 400 | Default text |
| `body-sm` | 12px | 400 | Table data, chat messages |
| `caption` | 11px | 400 | Timestamps, footnotes |
| `mono-data` | 13px | 500 | Financial numbers, prices |

### Rules
- **Financial numbers**: Always monospace, right-aligned
- **Section headers**: Uppercase, letter-spacing: 0.05em, muted color
- **Positive numbers**: Green, prefix with `+`
- **Negative numbers**: Red, prefix with `-`

## Spacing & Layout

### Grid
- **Sidebar**: Fixed 56px (icon-only, expandable to 200px)
- **Header**: Fixed 48px height
- **Content**: Flexible, gap: 4px between panels
- **Panel padding**: 12px (compact) or 16px (standard)

### Spacing Scale
```
4px  — tight (within components)
8px  — compact (between related items)
12px — standard (panel padding)
16px — comfortable (section spacing)
24px — spacious (between major sections)
```

### Border Radius
```
Buttons, inputs: 6px
Cards, panels: 8px
Tooltips, dropdowns: 6px
Avatars, status dots: 50% (circle)
```

## Component Patterns

### Cards / Panels
```
Background: var(--af-bg-card)
Border: 1px solid var(--af-border)
Border-radius: 8px
Padding: 12px
```

### Buttons
| Type | Background | Text | Border |
|------|-----------|------|--------|
| Primary | `--af-accent-blue` | white | none |
| Secondary | transparent | `--af-text-secondary` | 1px `--af-border` |
| Danger | transparent | `--af-red` | 1px `--af-red` |
| Ghost | transparent | `--af-text-muted` | none |

### Inputs
```
Background: var(--af-bg-tertiary)
Border: none (focus: 1px ring var(--af-accent-blue))
Text: var(--af-text-primary)
Placeholder: var(--af-text-muted)
Height: 32px
Font-size: 12px
Padding: 0 12px
```

### Stock Ticker Row
```
Layout: flex, justify-between
Left: Symbol (font-weight: 500)
Right: Price + Change (green/red, right-aligned)
Hover: background var(--af-bg-tertiary)
Height: 36px
Padding: 0 8px
```

### Market Index Card
```
Layout: vertical stack in grid (4 columns)
Background: var(--af-bg-tertiary)
Content: Name (muted, 12px), Value (14px, semibold), Change (12px, green/red)
Padding: 8px
```

## Page Layouts

### Dashboard (Main View)
```
┌─────────────────────────────────────────────────┐
│ Header: Logo | Nav tabs | Market status | CTA   │
├──┬──────────────────────────────────────┬───────┤
│S │  Market Indices (4-col grid cards)   │ Watch │
│I │                                      │ list  │
│D ├──────────────────────────────────────┤       │
│E │                                      ├───────┤
│B │  Chart Area (Lightweight Charts)     │  AI   │
│A │                                      │ Chat  │
│R │                                      │       │
└──┴──────────────────────────────────────┴───────┘
```

### Key Screens (to design)
1. **Dashboard** — Market overview + chart + watchlist + AI chat
2. **Stock Detail** — Full analysis page with chart, fundamentals, news, AI insights
3. **Portfolio** — Holdings, positions, P&L, allocation pie chart
4. **Trade** — Order form, order book, position tracker
5. **AI Analysis** — Full-page AI chat with expanded context panels
6. **Screener** — Filterable table of AI-picked stocks
7. **Settings** — Broker connections, API keys, preferences

## Iconography
- Library: Lucide React (`lucide-react`)
- Size: 16px (inline), 20px (nav), 24px (empty states)
- Color: Inherits text color

## Motion
- Transitions: 150ms ease (hover states, focus rings)
- Tab switches: instant (no page transition animation)
- Data loading: Skeleton shimmer (pulse animation on bg-tertiary)
- Number updates: No animation (instant update, like a real terminal)

## Accessibility
- Contrast ratio: Minimum 4.5:1 for body text, 3:1 for large text
- Focus rings: 2px solid `--af-accent-blue` with 2px offset
- All interactive elements keyboard-navigable
- Screen reader support for price changes (aria-live regions)

## Gemini Stitch Setup Notes
- Define all color tokens as CSS custom properties and feed them into Gemini Stitch prompts
- Use structured prompts with component variant descriptions: Default, Hover, Active, Disabled
- Include realistic Indian stock data context (RELIANCE, TCS, INFY, HDFCBANK, etc.) in generation prompts
- Use the monospace font for all financial data
- See `design/GEMINI_STITCH.md` for detailed MCP/extension workflow
