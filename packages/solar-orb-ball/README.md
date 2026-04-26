# @alphaforge/solar-orb-ball

> Standalone, animated **Solar Orb** — extracted from the AlphaForge design system into its own iterable package.

A glowing, breathing AI presence indicator. Renders entirely from CSS gradients + DOM nodes (no canvas/SVG), so it scales infinitely and re-tints by passing a single `accent` prop.

## Why a separate package?

The orb is the visual hero of the AlphaForge terminal and gets iterated frequently — animations, glow shapes, color presets, motion timing. Pulling it out of `@alphaforge/solar-orb-ui` lets you:

- run a focused **dev playground** (sliders for size/pulse/stars, accent swatches, custom backgrounds) on its own Vite server
- ship it independently to other apps that just want the orb without the full design system
- iterate without rebuilding the larger UI library

## Install

```bash
pnpm add @alphaforge/solar-orb-ball
```

## Usage

```tsx
import { SolarOrb } from "@alphaforge/solar-orb-ball";
import "@alphaforge/solar-orb-ball/styles";

<SolarOrb
  size={260}
  accent="#ff8f00"
  accentSoft="#ffb455"
  accentDim="#c36a00"
  hud
  rings
  starPreset="constellation"
  caption={{ eyebrow: "· READY ·", text: "What's moving my portfolio today?" }}
/>
```

### Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `size` | `number` | `260` | Orb diameter in px (the wrap is sized 1.6×). |
| `accent` | `string` | `#ff8f00` | Primary color (any CSS color). |
| `accentSoft` | `string` | `#ffb455` | Lighter shade for the inner highlight. |
| `accentDim` | `string` | `#c36a00` | Darker shade for the inner shadow rim. |
| `hud` | `boolean` | `true` | Render the 4 corner brackets + horizontal scanline. |
| `rings` | `boolean` | `true` | Render the two outward pulse rings. |
| `starPreset` | `"constellation" \| "minimal" \| "none"` | `"constellation"` | Star pattern around the orb. |
| `pulseSeconds` | `number` | `3.4` | Pulse cycle duration. `0` disables animation. |
| `caption` | `{ eyebrow?, text? }` | — | Optional caption below the orb. |

## Development

```bash
cd packages/solar-orb-ball
pnpm install
pnpm dev          # http://localhost:5180/playground/
pnpm build        # → dist/ (esm + cjs + d.ts + css)
pnpm build:demo   # → dist-demo/ (static playground site)
```

The playground (in `playground/`) is a thin Vite app that mounts the orb with sliders for every prop — drop straight into the dev loop without standing up the full Next.js frontend.

## License

MIT
