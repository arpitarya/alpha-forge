import { clsx } from "clsx";
import { type ButtonHTMLAttributes, forwardRef } from "react";
import { twMerge } from "tailwind-merge";

type ButtonVariant = "primary" | "secondary" | "ghost" | "deploy";
type ButtonSize = "sm" | "md" | "lg";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
}

const variantStyles: Record<ButtonVariant, string> = {
  primary:
    "bg-gradient-to-br from-primary-light to-primary text-black font-bold active:scale-95",
  secondary:
    "bg-transparent border border-[color:var(--line-hi)] text-[color:var(--accent)] hover:bg-white/5 active:scale-95",
  ghost: "bg-transparent text-[color:var(--fg-2)] hover:text-[color:var(--fg)]",
  // Hi-Fi `.deploy` — gradient accent CTA used in the voice footer + rebalance rail.
  deploy:
    "bg-[linear-gradient(45deg,var(--accent),var(--accent-soft))] text-[color:var(--on-accent)] font-mono font-bold shadow-[0_0_32px_var(--glow)] hover:-translate-y-px active:translate-y-0",
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: "text-[10px] px-4 py-2 tracking-[0.15em]",
  md: "text-xs px-6 py-2.5 tracking-[0.2em]",
  lg: "text-xs px-8 py-3 tracking-[0.24em]",
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
