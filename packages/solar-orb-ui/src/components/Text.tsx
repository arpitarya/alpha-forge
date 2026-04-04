import { clsx } from "clsx";
import type { ReactNode } from "react";
import { twMerge } from "tailwind-merge";

type TextVariant = "display" | "headline" | "title" | "body" | "label" | "caption";

export interface TextProps {
  variant?: TextVariant;
  children: ReactNode;
  className?: string;
  as?: keyof HTMLElementTagNameMap;
}

const variantStyles: Record<TextVariant, string> = {
  display: "text-4xl font-bold tracking-tighter text-on-surface",
  headline: "text-sm font-bold tracking-[0.3em] uppercase text-white/90",
  title: "text-xl font-bold tracking-tighter text-on-surface",
  body: "text-sm text-white/70 font-light leading-relaxed",
  label: "text-[10px] font-bold uppercase tracking-[0.2em] text-white/40",
  caption: "text-[10px] text-white/30 uppercase tracking-tighter",
};

export function Text({ variant = "body", children, className, as: Tag = "span" }: TextProps) {
  return <Tag className={twMerge(clsx(variantStyles[variant], className))}>{children}</Tag>;
}
