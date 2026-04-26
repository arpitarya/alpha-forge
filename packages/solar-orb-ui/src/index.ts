/**
 * @alphaforge/solar-orb-ui
 *
 * Solar Terminal design system — UI components, design tokens, and fonts.
 *
 * Components:
 *   import { Button, Input, Card, Badge, Icon, Text } from "@alphaforge/solar-orb-ui";
 *
 * Design tokens (JS/TS):
 *   import { tokens, color, font, spacing } from "@alphaforge/solar-orb-ui/tokens";
 *
 * Styles (import in your CSS):
 *   @import "@alphaforge/solar-orb-ui/styles";
 *
 * Theme tokens only (for Tailwind v4):
 *   @import "@alphaforge/solar-orb-ui/theme";
 */

// Atoms
export { Badge } from "./components/Badge";
export { Button } from "./components/Button";
export { Card } from "./components/Card";
export { Chip } from "./components/Chip";
export { CountUp } from "./components/CountUp";
export { Divider } from "./components/Divider";
export { HudCorners } from "./components/HudCorners";
export { Icon } from "./components/Icon";
export { Input } from "./components/Input";
export { Kbd } from "./components/Kbd";
export { LiveDot } from "./components/LiveDot";
export { Logo } from "./components/Logo";
export { ProgressBar } from "./components/ProgressBar";
export { Sparkline } from "./components/Sparkline";
export { Text } from "./components/Text";

// Molecules
export { BootStep } from "./components/BootStep";
export { MicIndicator } from "./components/MicIndicator";
export { RiskBars } from "./components/RiskBars";
export { SegmentedControl } from "./components/SegmentedControl";
export { Stat } from "./components/Stat";
export { Swatches } from "./components/Swatches";
export { Ticker } from "./components/Ticker";
export { TreemapCell } from "./components/TreemapCell";
export { WatchRow } from "./components/WatchRow";
export { Waveform } from "./components/Waveform";

// Layout shells
export { AppShell } from "./components/AppShell";
export { IconRail } from "./components/IconRail";
export { TopBar } from "./components/TopBar";
export { VoiceDock } from "./components/VoiceDock";

// Theming
export { ThemeProvider, useTheme } from "./components/ThemeProvider";

// Types — atoms
export type { BadgeProps } from "./components/Badge";
export type { ButtonProps } from "./components/Button";
export type { CardHeaderProps, CardProps } from "./components/Card";
export type { ChipProps } from "./components/Chip";
export type { CountUpProps } from "./components/CountUp";
export type { DividerProps } from "./components/Divider";
export type { HudCornersProps } from "./components/HudCorners";
export type { IconProps } from "./components/Icon";
export type { InputProps } from "./components/Input";
export type { KbdProps } from "./components/Kbd";
export type { LiveDotProps } from "./components/LiveDot";
export type { LogoProps } from "./components/Logo";
export type { ProgressBarProps } from "./components/ProgressBar";
export type { SparklineProps } from "./components/Sparkline";
export type { TextProps } from "./components/Text";

// Types — molecules
export type { BootStepProps, BootStepState } from "./components/BootStep";
export type { MicIndicatorProps } from "./components/MicIndicator";
export type { RiskBarsProps } from "./components/RiskBars";
export type {
  SegmentedControlProps,
  SegmentedOption,
} from "./components/SegmentedControl";
export type { StatProps } from "./components/Stat";
export type { AccentName, SwatchesProps } from "./components/Swatches";
export type { TickerItem, TickerProps } from "./components/Ticker";
export type { TreemapCellProps } from "./components/TreemapCell";
export type { WatchRowProps } from "./components/WatchRow";
export type { WaveformProps } from "./components/Waveform";

// Types — shells
export type { AppShellProps } from "./components/AppShell";
export type { IconRailItem, IconRailProps } from "./components/IconRail";
export type { TopBarNavItem, TopBarProps } from "./components/TopBar";
export type { VoiceDockProps } from "./components/VoiceDock";

// Types — theming
export type { ThemeName, ThemeProviderProps, ThemeState } from "./components/ThemeProvider";

// Design tokens
export {
  animation,
  blur,
  color,
  font,
  layout,
  radius,
  shadow,
  spacing,
  tokens,
  zIndex,
} from "./tokens";
export type { Tokens } from "./tokens";
