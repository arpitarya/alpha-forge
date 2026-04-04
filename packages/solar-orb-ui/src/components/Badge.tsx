import { clsx } from "clsx";
import type { ReactNode } from "react";
import { twMerge } from "tailwind-merge";

export interface BadgeProps {
  children: ReactNode;
  variant?: "default" | "success" | "danger" | "warning";
  className?: string;
}

const variantStyles: Record<string, string> = {
  default: "bg-white/5 text-on-surface-variant",
  success: "bg-af-green/10 text-af-green",
  danger: "bg-af-red/10 text-af-red",
  warning: "bg-primary/10 text-primary",
};

export function Badge({ children, variant = "default", className }: BadgeProps) {
  return (
    <span
      className={twMerge(
        clsx(
          "inline-flex items-center gap-1 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.15em]",
          variantStyles[variant],
          className,
        ),
      )}
    >
      {children}
    </span>
  );
}
