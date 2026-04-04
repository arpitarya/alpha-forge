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

// Components
export { Button } from "./components/Button";
export { Input } from "./components/Input";
export { Card } from "./components/Card";
export { Badge } from "./components/Badge";
export { Icon } from "./components/Icon";
export { Text } from "./components/Text";
export { Logo } from "./components/Logo";

// Types
export type { ButtonProps } from "./components/Button";
export type { InputProps } from "./components/Input";
export type { CardProps } from "./components/Card";
export type { BadgeProps } from "./components/Badge";
export type { IconProps } from "./components/Icon";
export type { TextProps } from "./components/Text";
export type { LogoProps } from "./components/Logo";

// Design tokens
export { tokens, color, font, spacing, radius, shadow, blur, animation, layout, zIndex } from "./tokens";
export type { Tokens } from "./tokens";
