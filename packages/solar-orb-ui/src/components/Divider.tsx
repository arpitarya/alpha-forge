import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export interface DividerProps {
  orientation?: "horizontal" | "vertical";
  className?: string;
}

export function Divider({ orientation = "horizontal", className }: DividerProps) {
  return (
    <div
      className={twMerge(
        clsx(
          "bg-outline/15",
          orientation === "horizontal" && "h-px w-full",
          orientation === "vertical" && "w-px h-full",
          className,
        ),
      )}
      role="separator"
      aria-orientation={orientation}
    />
  );
}
