/**
 * Solar Terminal — Design Tokens (TypeScript)
 *
 * Single source of truth consumed by components, Storybook, and tooling.
 * The CSS tokens in theme.css are generated from these values.
 *
 * Usage:
 *   import { tokens } from "@alphaforge/solar-orb-ui/tokens";
 */

// ── Colors ──────────────────────────────────────────────────

export const color = {
  primary: "#ff8f00",
  primaryLight: "#ffa44f",
  primaryDark: "#cc7200",

  surface: {
    lowest: "#000000",
    low: "#0e0e0e",
    DEFAULT: "#131313",
    container: "#1a1a1a",
    containerHigh: "#222222",
    containerHighest: "#282828",
    bright: "#2c2c2c",
    overlay: "rgba(0, 0, 0, 0.6)",
  },

  onSurface: {
    DEFAULT: "#ffffff",
    variant: "#adaaaa",
    muted: "#666666",
    faint: "rgba(255, 255, 255, 0.3)",
  },

  outline: {
    DEFAULT: "#484847",
    subtle: "rgba(255, 255, 255, 0.05)",
    focus: "#ff8f00",
  },

  green: "#34d399",
  red: "#f87171",
  orange: "#f59e0b",
  purple: "#a855f7",
  blue: "#3b82f6",

  glass: {
    bg: "rgba(255, 255, 255, 0.03)",
    border: "rgba(255, 255, 255, 0.05)",
  },
} as const;

// ── Typography ──────────────────────────────────────────────

export const font = {
  family: {
    headline: "'Space Grotesk', sans-serif",
    body: "'Space Grotesk', sans-serif",
    mono: "'JetBrains Mono', 'SF Mono', 'Fira Code', ui-monospace, monospace",
  },
  weight: {
    light: 300,
    regular: 400,
    medium: 500,
    bold: 700,
  },
  size: {
    displayLg: "3.5rem",
    display: "2.25rem",
    headline: "0.875rem",
    title: "1.25rem",
    body: "0.875rem",
    bodySm: "0.75rem",
    label: "0.625rem",
    labelSm: "0.6875rem",
    caption: "0.625rem",
    monoData: "0.8125rem",
  },
  lineHeight: {
    tight: "1.1",
    normal: "1.5",
    relaxed: "1.7",
  },
  letterSpacing: {
    tighter: "-0.05em",
    tight: "-0.04em",
    normal: "0em",
    terminal: "0.1em",
    wide: "0.15em",
    wider: "0.2em",
    widest: "0.3em",
  },
} as const;

// ── Spacing ─────────────────────────────────────────────────

export const spacing = {
  0: "0px",
  1: "4px",
  2: "8px",
  3: "12px",
  4: "16px",
  5: "20px",
  6: "24px",
  8: "32px",
  10: "40px",
  12: "48px",
  16: "64px",
  20: "80px",
  24: "96px",
} as const;

// ── Border Radius ───────────────────────────────────────────

export const radius = {
  none: "0px",
  sm: "0px",
  md: "0px",
  lg: "0px",
  xl: "0px",
  "2xl": "0px",
  full: "0px",
} as const;

// ── Shadows ─────────────────────────────────────────────────

export const shadow = {
  none: "none",
  sm: "0 1px 2px rgba(0, 0, 0, 0.5)",
  md: "0 4px 12px rgba(0, 0, 0, 0.4)",
  lg: "0 8px 24px rgba(0, 0, 0, 0.5)",
  glowPrimary: "0 0 40px rgba(255, 143, 0, 0.15)",
  glowPrimaryLg: "0 0 120px rgba(255, 143, 0, 0.4)",
  glowGreen: "0 0 12px rgba(52, 211, 153, 0.2)",
  glowRed: "0 0 12px rgba(248, 113, 113, 0.2)",
} as const;

// ── Blur ────────────────────────────────────────────────────

export const blur = {
  glass: "40px",
  orb: "2px",
} as const;

// ── Animation ───────────────────────────────────────────────

export const animation = {
  duration: {
    instant: "0ms",
    fast: "150ms",
    normal: "300ms",
    slow: "700ms",
    pulse: "8s",
  },
  easing: {
    default: "ease",
    inOut: "ease-in-out",
    spring: "cubic-bezier(0.34, 1.56, 0.64, 1)",
  },
} as const;

// ── Layout ──────────────────────────────────────────────────

export const layout = {
  sidebar: { collapsed: "56px", expanded: "200px" },
  header: { height: "48px" },
  contentGap: "4px",
  breakpoint: {
    sm: "640px",
    md: "768px",
    lg: "1024px",
    xl: "1280px",
    "2xl": "1536px",
  },
} as const;

// ── Z-Index ─────────────────────────────────────────────────

export const zIndex = {
  base: 0,
  dropdown: 10,
  sticky: 20,
  header: 30,
  sidebar: 40,
  modal: 50,
  tooltip: 60,
  toast: 70,
} as const;

// ── Aggregate Export ────────────────────────────────────────

export const tokens = {
  color,
  font,
  spacing,
  radius,
  shadow,
  blur,
  animation,
  layout,
  zIndex,
} as const;

export type Tokens = typeof tokens;
