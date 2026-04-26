import { clsx } from "clsx";
import type { HTMLAttributes, ReactNode } from "react";
import { twMerge } from "tailwind-merge";

type CardVariant = "surface" | "glass" | "elevated";

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  variant?: CardVariant;
  hover?: boolean;
  /**
   * Render the Hi-Fi gradient hairline border (a 1px accent-tinted rim drawn
   * via mask-composite). Adds a subtle "scanner" feel to terminal cards.
   */
  glow?: boolean;
}

const variantStyles: Record<CardVariant, string> = {
  surface:
    "bg-[color:color-mix(in_srgb,var(--surface)_88%,transparent)] border border-[color:var(--line)]",
  glass:
    "bg-white/[0.03] backdrop-blur-[40px] border border-[color:var(--line)]",
  elevated: "bg-[color:var(--surface-hi)] border border-[color:var(--line-hi)]",
};

export function Card({
  children,
  className,
  variant = "surface",
  hover = false,
  glow = false,
  ...props
}: CardProps) {
  return (
    <div
      className={twMerge(
        clsx(
          "relative overflow-hidden rounded-[var(--radius-md)] p-5",
          variantStyles[variant],
          hover && "transition-colors duration-300 hover:bg-[color:var(--surface-hi)]",
          glow && "card-glow",
          className,
        ),
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export interface CardHeaderProps {
  title: ReactNode;
  right?: ReactNode;
  className?: string;
}

/**
 * Standard card header used across the Hi-Fi: title (uppercase, mono-tag style)
 * on the left, optional right slot (a tag, count, or "+ ADD" affordance).
 */
function CardHeader({ title, right, className }: CardHeaderProps) {
  return (
    <div
      className={twMerge(
        clsx("flex items-center justify-between mb-3", className),
      )}
    >
      <h3 className="font-mono text-[11px] font-bold uppercase tracking-[0.24em] text-[color:var(--fg-2)]">
        {title}
      </h3>
      {right && <div className="flex items-center gap-2">{right}</div>}
    </div>
  );
}

Card.Header = CardHeader;
