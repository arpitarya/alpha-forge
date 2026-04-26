# solar-orb-ui — Component Library Plan

> Design system for AlphaForge. Single source of truth: `design/project/Alpha Forge Hi-Fi.html`.
> Goal: every visual atom or repeated molecule from the Hi-Fi mock lives here, so `frontend/` only composes screens.

## Design principles

1. **Token-driven.** Colors/spacing/radius/typography come from `theme.css` + `tokens/index.ts`. Never inline hex.
2. **Theme-agnostic.** Components must work under `data-theme="dark|light"` and `data-accent="amber|ion|signal|violet"` (Hi-Fi defines all four). Use semantic tokens (`--bg`, `--surface`, `--accent`, `--fg`, …), not raw `--color-primary`.
3. **Server-friendly.** Default to RSC; only mark `"use client"` when interactive (Input, Chip with onClick, ThemeSwitcher, Ticker).
4. **Composable, not configurable.** Prefer `<Card.Header/>` + `<Card.Body/>` slots over a 12-prop monolith.
5. **One atom = one file.** No nested mega-components inside a single `.tsx`.

## Token gaps to close (theme.css)

The Hi-Fi uses semantic CSS vars our `theme.css` doesn't yet expose. Add:

| New token | Purpose | Hi-Fi equivalent |
|---|---|---|
| `--color-accent` / `-soft` / `-dim` / `-on` | Themable accent (amber/ion/signal/violet) | `--accent`, `--accent-soft`, `--accent-dim`, `--on-accent` |
| `--color-glow` | Accent shadow tint | `--glow` |
| `--color-fg` / `-2` / `-3` / `-4` | 4-step text ramp | `--fg`, `--fg-2`, `--fg-3`, `--fg-4` |
| `--color-line` / `-hi` | Hairline borders | `--line`, `--line-hi` |
| Light-mode overrides | Keyed off `html[data-theme="light"]` | already in Hi-Fi |
| Accent overrides | Keyed off `html[data-accent="…"]` | already in Hi-Fi |

Plus a `Space Mono` font face (`fonts.css`) — Hi-Fi uses it everywhere for tags, prices, and labels.

## Component inventory

Status legend: ✅ exists · 🔧 exists but needs upgrade · 🆕 new

### Atoms

| Component | Status | Notes |
|---|---|---|
| `Text` | 🔧 | Add `mono` variant (Space Mono); add `tag` variant (uppercase 10px / 0.22em — used everywhere as a section eyebrow) |
| `Icon` | ✅ | Already wraps Material Symbols |
| `Badge` | ✅ | Add `outline` variant (border-only, used for ticker chips) |
| `Chip` | 🔧 | Add `bordered` variant (rebalance rail chips: 1px outline, hover → accent) |
| `Button` | 🔧 | Add `deploy` variant (gradient `accent→accent-soft`, glow shadow — voice-footer CTA) |
| `Divider` | ✅ | Add `dashed` orientation (used between watchlist rows) |
| `ProgressBar` | 🔧 | Add `bidirectional` mode (drift bars: fill grows from center; +/− on either side) |
| `Logo` | ✅ | Already done |
| `Kbd` | 🆕 | `⌘K` chip in top bar |
| `LiveDot` | 🆕 | Pulsing green dot ("LIVE · NSE") — extracted because it appears in 3+ places |
| `HudCorners` | 🆕 | 4 absolutely-positioned corner brackets — wraps any container; drives the "scanner frame" feel of the orb wrap, treemap, boot screen |
| `Sparkline` | 🆕 | SVG mini-chart; props `points: number[]`, `tone: 'up'\|'dn'\|'accent'`, `fill: boolean`. Used in stat cards, ledger, treemap |
| `CountUp` | 🆕 | Client-only animated number; `value`, `format: 'inr'\|'usd'\|'pct'\|'plain'`, `decimals` |

### Molecules

| Component | Status | Notes |
|---|---|---|
| `Card` | 🔧 | Add `glow` prop → renders the gradient hairline border via `::after` (Hi-Fi `.card::after`); add `Card.Header` slot taking `title` + `right` (the `<h3>` + tag pattern repeats on every card) |
| `Stat` | 🆕 | Label · Value · Delta (up/dn) · optional Sparkline · optional `corner` decoration. Used in terminal stats row + portfolio header |
| `WatchRow` | 🆕 | Icon · Symbol+sub · Price · Change. Click handler. Hover row tint |
| `RiskBars` | 🆕 | 5-bar mini-histogram with one `active` bar that glows. Animated jitter optional |
| `SegmentedControl` | 🆕 | Theme switcher / portfolio Treemap↔Ledger toggle |
| `Swatches` | 🆕 | Accent picker (4 colored circles, outlined-active) |
| `Ticker` | 🆕 | Horizontal marquee; `items: TickerItem[]`. Pure CSS animation, pauses on hover |
| `MicIndicator` | 🆕 | Circular mic with double ping ring (voice footer) |
| `Waveform` | 🆕 | 8-bar audio meter, animated heights |
| `BootStep` | 🆕 | One row of the boot list (state: queued/now/ok, icon, label, status text) |
| `TreemapCell` | 🆕 | Absolute-positioned cell with sym/sub/value/change + optional sparkline. Tone-tinted bg |

### Layout shells (in solar-orb-ui because they're brand-defining chrome)

| Component | Status | Notes |
|---|---|---|
| `AppShell` | 🆕 | `header` / `aside` / `main` / `footer` slots. Provides the `radial-gradient(glow)` background and theme attribute hookup |
| `TopBar` | 🆕 | Brand · nav · status. Takes `nav: NavItem[]`, `status: ReactNode`, `right: ReactNode` |
| `IconRail` | 🆕 | Vertical sidebar (52px wide); `items: IconRailItem[]`, `active`, `onSelect` |
| `VoiceDock` | 🆕 | Footer dock; slots: `mic`, `centerText`, `cta`. Composed from MicIndicator + Waveform + Button |

### Charts (separate sub-package later; stub here)

`Sparkline` ships in v0. `Treemap` (squarified layout), `DonutAllocation`, `AreaChart` are future — designs have static mocks today.

## Frontend composition

Once the library above is in place, `frontend/src/components/` collapses dramatically:

```
frontend/src/components/
  layout/
    AppLayout.tsx       wraps <AppShell>, <TopBar>, <IconRail>, <VoiceDock>
  terminal/
    AlphaBriefCard.tsx  data + composes <Card> + <Text variant="tag"> blocks
    StatStrip.tsx       3 × <Stat> with live data
    Watchlist.tsx       <Card> + <WatchRow> list
    RiskMeter.tsx       <Card> + <RiskBars>
    OrbStage.tsx        <HudCorners> + <SolarOrb> + rotating caption
    ScreenerPanel.tsx   <Card> + ranked rows (already close — refactor to <WatchRow>)
  portfolio/
    Treemap.tsx         layout calc + <TreemapCell> grid
    Ledger.tsx          table + <Sparkline> + <Button variant="ghost">
    RebalanceRail.tsx   <Card> + <Chip variant="bordered"> + <ProgressBar bidirectional>
  boot/
    BootScreen.tsx      <HudCorners> + <BootStep> list + <ProgressBar>
```

Routing (Next App Router):

```
src/app/
  layout.tsx          AppLayout (header + rail + voice dock around children)
  page.tsx            redirect to /terminal
  terminal/page.tsx   server-renders the 4-quadrant terminal grid
  portfolio/page.tsx  server-renders portfolio (treemap default, ledger toggle is client)
  boot/page.tsx       loading screen (also reachable as Suspense fallback)
```

Page-level grids stay in `frontend/`; **all visual primitives ship from `@alphaforge/solar-orb-ui`**.

## Phases

**Phase 1 — Token + atom expansion (closes the gap to render Hi-Fi terminal screen accurately)**
1. Extend `theme.css` with semantic tokens + light/accent variants; add Space Mono to `fonts.css`.
2. Upgrade `Text` (mono, tag), `Card` (glow + Header slot), `Chip` (bordered), `Button` (deploy).
3. New atoms: `Kbd`, `LiveDot`, `HudCorners`, `Sparkline`, `CountUp`.

**Phase 2 — Molecules for terminal screen**
4. `Stat`, `WatchRow`, `RiskBars`, `Ticker`, `MicIndicator`, `Waveform`.
5. Layout shells: `AppShell`, `TopBar`, `IconRail`, `VoiceDock`.
6. Refactor `frontend/src/app/page.tsx` + terminal components onto the new primitives. Delete duplicated styles.

**Phase 3 — Portfolio + boot**
7. `SegmentedControl`, `Swatches`, `BootStep`, `TreemapCell`.
8. Build `/portfolio` and `/boot` routes against the same primitives.

**Phase 4 — Theming runtime**
9. `ThemeProvider` (sets `data-theme`/`data-accent` on `<html>`, persists to localStorage). Surface the segmented control + swatches in a settings popover.

## Out of scope (for now)

- Real-time websocket wiring (separate concern, lives in `frontend/src/lib`)
- Charting library beyond `Sparkline` (defer until designs need richer charts)
- Mobile / responsive < 1200px (Hi-Fi targets a fixed 1440×900 stage)
- Storybook (revisit after Phase 2 stabilizes the API)
