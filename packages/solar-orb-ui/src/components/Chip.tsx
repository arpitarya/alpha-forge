import { clsx } from "clsx";
import type { ReactNode } from "react";
import { twMerge } from "tailwind-merge";

export interface ChipProps {
  children: ReactNode;
  icon?: string;
  variant?: "default" | "active";
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
          "inline-flex items-center gap-1.5 px-3 py-1.5 text-[10px] font-bold uppercase tracking-[0.15em] transition-colors",
          variant === "default" && "bg-surface-container text-on-surface-variant",
          variant === "active" && "bg-primary/10 text-primary",
          isInteractive && "cursor-pointer hover:bg-surface-bright",
          !isInteractive && "cursor-default",
          className,
        ),
      )}
      onClick={onClick}
      tabIndex={isInteractive ? 0 : -1}
    >
      {icon && (
        <span className="material-symbols-outlined text-xs">{icon}</span>
      )}
      {children}
    </button>
  );
}
