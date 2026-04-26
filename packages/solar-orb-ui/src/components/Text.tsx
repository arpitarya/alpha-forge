import { clsx } from "clsx";
import type { ReactNode } from "react";
import { twMerge } from "tailwind-merge";

type TextVariant =
  | "display-lg"
  | "display"
  | "headline"
  | "title"
  | "body"
  | "body-sm"
  | "label"
  | "label-sm"
  | "caption"
  | "tag"
  | "mono";

type TextTone = "default" | "muted" | "subtle" | "accent" | "up" | "dn";

export interface TextProps {
  variant?: TextVariant;
  tone?: TextTone;
  children: ReactNode;
  className?: string;
  as?: keyof HTMLElementTagNameMap;
}

const variantStyles: Record<TextVariant, string> = {
  "display-lg": "text-[3.5rem] font-medium tracking-[-0.04em] leading-tight",
  display: "text-4xl font-medium tracking-tighter",
  headline: "text-sm font-bold tracking-[0.3em] uppercase",
  title: "text-xl font-medium tracking-tight",
  body: "text-sm font-light leading-relaxed",
  "body-sm": "text-xs font-light leading-relaxed",
  label: "text-[10px] font-bold uppercase tracking-[0.2em]",
  "label-sm": "text-[0.6875rem] font-bold uppercase tracking-[0.1em]",
  caption: "text-[10px] uppercase tracking-tighter",
  // Hi-Fi `.tag` — Space Mono, 10px, wide tracking, uppercase. Used as section eyebrow.
  tag: "font-mono text-[10px] uppercase tracking-[0.22em]",
  // Hi-Fi `.mono` — Space Mono with subtle tracking. Used for prices, deltas, numerics.
  mono: "font-mono text-sm tracking-[0.02em] tabular-nums",
};

const toneStyles: Record<TextTone, string> = {
  default: "text-[color:var(--fg)]",
  muted: "text-[color:var(--fg-2)]",
  subtle: "text-[color:var(--fg-3)]",
  accent: "text-[color:var(--accent)]",
  up: "text-[color:var(--green)]",
  dn: "text-[color:var(--red)]",
};

export function Text({
  variant = "body",
  tone = "default",
  children,
  className,
  as: Tag = "span",
}: TextProps) {
  return (
    <Tag className={twMerge(clsx(variantStyles[variant], toneStyles[tone], className))}>
      {children}
    </Tag>
  );
}
