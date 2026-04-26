import { clsx } from "clsx";
import type { ReactNode } from "react";
import { twMerge } from "tailwind-merge";

type ChipVariant = "default" | "active" | "bordered";

export interface ChipProps {
  children: ReactNode;
  icon?: string;
  variant?: ChipVariant;
  className?: string;
  onClick?: () => void;
}

export function Chip({
  children,
  icon,
  variant = "default",
  className,
  onClick,
}: ChipProps) {
  const isInteractive = !!onClick;

  return (
    <button
      type="button"
      className={twMerge(
        clsx(
          "inline-flex items-center gap-1.5 px-3 py-1.5 font-mono text-[10px] uppercase tracking-[0.16em] transition-colors",
          variant === "default" &&
            "bg-[color:var(--surface-hi)] text-[color:var(--fg-2)]",
          variant === "active" &&
            "bg-[color:color-mix(in_srgb,var(--accent)_10%,transparent)] text-[color:var(--accent)]",
          variant === "bordered" &&
            "border border-[color:var(--line-hi)] text-[color:var(--fg-2)] hover:border-[color:var(--accent)] hover:text-[color:var(--accent)]",
          isInteractive && "cursor-pointer",
          !isInteractive && "cursor-default",
          className,
        ),
      )}
      onClick={onClick}
      tabIndex={isInteractive ? 0 : -1}
    >
      {icon && <span className="material-symbols-outlined text-xs">{icon}</span>}
      {children}
    </button>
  );
}
