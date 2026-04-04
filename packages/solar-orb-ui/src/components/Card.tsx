import { clsx } from "clsx";
import type { ReactNode } from "react";
import { twMerge } from "tailwind-merge";

export interface CardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
}

export function Card({ children, className, hover = false }: CardProps) {
  return (
    <div
      className={twMerge(
        clsx(
          "floating-shard rounded-[2.5rem] p-8",
          hover && "hover:scale-105 transition-all duration-700",
          className,
        ),
      )}
    >
      {children}
    </div>
  );
}
