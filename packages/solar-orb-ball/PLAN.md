# solar-orb-ball — Plan

> Standalone Solar Orb component, broken out of `@alphaforge/solar-orb-ui` so it can iterate on its own dev server.

## Why this exists

The orb is the visual signature of AlphaForge — and the piece most likely to keep evolving (motion, glow shape, color presets, accessibility states). Coupling it to the larger UI library means a slow rebuild loop and pollution of the shared `theme.css` with orb-only knobs. As a standalone package:

- Designers + developers iterate against an isolated Vite playground (sliders for size, pulse, stars, color, background) with HMR.
- The orb ships with a clean API surface (one component, ~10 props) that any AlphaForge surface — terminal, marketing site, mobile shell — can consume without pulling the full design system.
- All custom properties (`--orb-*`) are scoped to `.solar-orb-ball`, so multiple orbs with different accents can coexist on the same page.

## Design principles

1. **One component.** No DS, no tokens module, no theming context. Everything is props.
2. **Self-scoped vars.** Component reads only `--orb-*` vars set on its own root element. Zero global side-effects.
3. **No external deps beyond React + clsx.** Animation is pure CSS keyframes.
4. **DOM, not canvas.** Stays crisp at any zoom and inherits OS accessibility settings.
5. **Playground = first-class.** Vite serves `playground/` for development. Same Vite config builds the lib (`vite build`) or the demo as a static site (`vite build --mode demo`).

## API surface

```ts
<SolarOrb
  size={260}
  accent="#ff8f00"
  accentSoft="#ffb455"
  accentDim="#c36a00"
  hud
  rings
  starPreset="constellation" | "minimal" | "none"
  pulseSeconds={3.4}
  caption={{ eyebrow: "...", text: "..." }}
/>
```

## Layout

```
packages/solar-orb-ball/
  package.json          ESM + CJS exports, vite scripts
  tsconfig.json         dev (noEmit)
  tsconfig.build.json   declarations only → dist/
  vite.config.ts        dual mode: lib build (default) | demo build (--mode demo)
  README.md             usage + props table
  PLAN.md               this file
  src/
    index.ts            barrel
    SolarOrb.tsx        the component
    SolarOrb.css        scoped styles + keyframes
  playground/
    index.html          dev server entry
    main.tsx            mounts <Playground/>
    Playground.tsx      sliders + swatches + toggles
    playground.css      panel/stage layout
```

## Phases

**Phase 1 — Standalone component + playground ✅ DONE**
- Component, scoped CSS, props API.
- Vite playground with size/pulse/stars/HUD/rings/caption/background controls + 4 accent presets.
- `pnpm dev` boots the playground, `pnpm build` produces lib (esm + cjs + d.ts + css), `pnpm build:demo` produces a static site.

**Phase 2 — Visual variants** (next)
- Star "field" preset (denser, slower drift).
- Idle vs Listening vs Thinking states (different pulse rhythms / colors).
- Reduced-motion mode (respect `prefers-reduced-motion`).

**Phase 3 — Interaction**
- Click → soft burst animation.
- Hover → magnetic highlight follow.

**Phase 4 — Embeddable**
- Web component wrapper (`<solar-orb-ball>`) so non-React surfaces can drop it in.

## Out of scope

- Real-time audio reactivity (separate package, would tap WebAudio).
- 3D / WebGL rendering — explicitly stays DOM-only.
- Theme switching at the component level — consumers handle palette by passing `accent`/`accentSoft`/`accentDim` props.
