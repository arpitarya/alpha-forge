import { clsx } from "clsx";
import { type ButtonHTMLAttributes, forwardRef } from "react";
import { twMerge } from "tailwind-merge";

type ButtonVariant = "primary" | "secondary" | "ghost";
type ButtonSize = "sm" | "md" | "lg";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
}

const variantStyles: Record<ButtonVariant, string> = {
  primary:
    "bg-gradient-to-br from-primary-light to-primary text-black font-bold active:scale-95",
  secondary:
    "bg-transparent border border-outline/20 text-primary hover:bg-white/5 active:scale-95",
  ghost: "bg-transparent text-on-surface-variant hover:text-on-surface",
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: "text-[10px] px-4 py-2 tracking-[0.15em]",
  md: "text-xs px-6 py-2.5 tracking-[0.2em]",
  lg: "text-xs px-8 py-3 tracking-[0.2em]",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = "primary", size = "md", className, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={twMerge(
          clsx(
            "inline-flex items-center justify-center font-bold uppercase transition-transform",
            variantStyles[variant],
            sizeStyles[size],
            className,
          ),
        )}
        {...props}
      >
        {children}
      </button>
    );
  },
);

Button.displayName = "Button";
