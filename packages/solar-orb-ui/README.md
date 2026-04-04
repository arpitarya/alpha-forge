# @alphaforge/solar-orb-ui

> Solar Terminal design system — UI primitives, design tokens, and fonts for AlphaForge.

A publishable React component library following the **Solar Terminal** design spec: Space Grotesk typography, amber/obsidian palette, glassmorphic floating shards, and Material Symbols icons.

## Install

```bash
pnpm add @alphaforge/solar-orb-ui
```

## Usage

### Components

```tsx
import { Button, Input, Card, Badge, Icon, Text } from "@alphaforge/solar-orb-ui";

function Example() {
  return (
    <Card hover>
      <Text variant="headline">Portfolio</Text>
      <Input label="Symbol" icon="search" placeholder="Search stocks..." />
      <Badge variant="success">+2.4%</Badge>
      <Button variant="primary" size="md">Deploy</Button>
    </Card>
  );
}
```

### Styles

Import the combined stylesheet (fonts + theme tokens + base utilities) in your app's CSS:

```css
/* globals.css */
@import "@alphaforge/solar-orb-ui/styles";
@import "tailwindcss";
```

Or import pieces individually:

```css
@import "@alphaforge/solar-orb-ui/theme";   /* Tailwind v4 @theme tokens only */
```

### Design Tokens

The theme provides these Tailwind v4 color tokens:

| Token | Value | Usage |
|-------|-------|-------|
| `primary` | `#ff8f00` | Amber accent, CTAs |
| `primary-light` | `#ffa44f` | Hover states |
| `surface` | `#0e0e0e` | Base background |
| `surface-lowest` | `#000000` | Deep-set areas |
| `surface-low` | `#131313` | Card backgrounds |
| `surface-container` | `#1a1a1a` | Interactive layers |
| `surface-bright` | `#2c2c2c` | Active states |
| `on-surface` | `#ffffff` | Primary text |
| `on-surface-variant` | `#adaaaa` | Secondary text |
| `af-green` | `#34d399` | Positive changes |
| `af-red` | `#f87171` | Negative changes |

### CSS Classes

| Class | Description |
|-------|-------------|
| `.solar-orb` | Glowing amber orb with pulse animation |
| `.floating-shard` | Glassmorphic card with blur + border |
| `.no-scrollbar` | Hides scrollbar (webkit + firefox) |
| `.solar-scrollbar` | Minimal dark scrollbar |

## Development

```bash
cd packages/solar-orb-ui
pnpm install
pnpm dev     # Watch mode
pnpm build   # Production build → dist/
```

## License

MIT
