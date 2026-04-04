import { clsx } from "clsx";
import type { HTMLAttributes, ReactNode } from "react";
import { twMerge } from "tailwind-merge";

type CardVariant = "surface" | "glass" | "elevated";

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  variant?: CardVariant;
  hover?: boolean;
}

const variantStyles: Record<CardVariant, string> = {
  surface: "bg-surface-container",
  glass: "bg-white/[0.03] backdrop-blur-[40px] border border-white/5",
  elevated: "bg-surface-bright",
};

export function Card({
  children,
  className,
  variant = "surface",
  hover = false,
  ...props
}: CardProps) {
  return (
    <div
      className={twMerge(
        clsx(
          "p-6",
          variantStyles[variant],
          hover && "hover:bg-surface-bright transition-colors duration-700",
          className,
        ),
      )}
      {...props}
    >
      {children}
    </div>
  );
}
