"use client";

import { clsx } from "clsx";
import { type InputHTMLAttributes, forwardRef, useState } from "react";
import { twMerge } from "tailwind-merge";

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, icon, className, ...props }, ref) => {
    const [focused, setFocused] = useState(false);

    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label className="text-[10px] font-bold uppercase tracking-[0.2em] text-white/40">
            {label}
          </label>
        )}
        <div className="relative">
          {icon && (
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-sm text-white/30">
              {icon}
            </span>
          )}
          <input
            ref={ref}
            onFocus={(e) => {
              setFocused(true);
              props.onFocus?.(e);
            }}
            onBlur={(e) => {
              setFocused(false);
              props.onBlur?.(e);
            }}
            className={twMerge(
              clsx(
                "w-full bg-surface-container text-sm text-on-surface placeholder:text-white/30 outline-none transition-all",
                "px-4 py-3",
                icon && "pl-10",
                focused && "border-b-2 border-b-primary",
                !focused && "border-b-2 border-b-transparent",
                error && "border-b-2 border-b-af-red",
                className,
              ),
            )}
            {...props}
          />
        </div>
        {error && <span className="text-[10px] font-bold text-af-red">{error}</span>}
      </div>
    );
  },
);

Input.displayName = "Input";
