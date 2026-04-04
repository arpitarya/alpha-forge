import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export interface IconProps {
  name: string;
  size?: "sm" | "md" | "lg";
  filled?: boolean;
  className?: string;
}

const sizeStyles: Record<string, string> = {
  sm: "text-sm",
  md: "text-xl",
  lg: "text-4xl",
};

export function Icon({ name, size = "md", filled = false, className }: IconProps) {
  return (
    <span
      className={twMerge(
        clsx("material-symbols-outlined select-none", sizeStyles[size], className),
      )}
      style={filled ? { fontVariationSettings: "'FILL' 1" } : undefined}
    >
      {name}
    </span>
  );
}
