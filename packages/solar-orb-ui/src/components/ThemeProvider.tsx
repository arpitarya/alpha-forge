"use client";

import {
  type ReactNode,
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import type { AccentName } from "./Swatches";

export type ThemeName = "dark" | "light";

export interface ThemeState {
  theme: ThemeName;
  accent: AccentName;
  setTheme: (next: ThemeName) => void;
  setAccent: (next: AccentName) => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeState | null>(null);

const STORAGE_KEY = "solar-orb-theme";

interface PersistShape {
  theme?: ThemeName;
  accent?: AccentName;
}

function readPersisted(): PersistShape {
  if (typeof window === "undefined") return {};
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as PersistShape) : {};
  } catch {
    return {};
  }
}

function writePersisted(state: PersistShape): void {
  if (typeof window === "undefined") return;
  try {
    const prev = readPersisted();
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify({ ...prev, ...state }));
  } catch {
    // localStorage unavailable (Safari private mode, etc.) — silent.
  }
}

export interface ThemeProviderProps {
  children: ReactNode;
  defaultTheme?: ThemeName;
  defaultAccent?: AccentName;
  /** When true, skip writing to localStorage. Useful for SSR-only renders. */
  ephemeral?: boolean;
}

/**
 * Sets `data-theme` and `data-accent` on `<html>` so the semantic CSS-var
 * layer in theme.css re-skins everything. Persists to localStorage.
 *
 * Usage in a Next.js root layout:
 *   <html lang="en"><body>
 *     <ThemeProvider><App /></ThemeProvider>
 *   </body></html>
 *
 * (The provider mutates `document.documentElement` after mount; for
 * flash-free SSR add a tiny inline script that reads localStorage and sets
 * the attrs before hydration.)
 */
export function ThemeProvider({
  children,
  defaultTheme = "dark",
  defaultAccent = "amber",
  ephemeral = false,
}: ThemeProviderProps) {
  const [theme, setThemeState] = useState<ThemeName>(defaultTheme);
  const [accent, setAccentState] = useState<AccentName>(defaultAccent);

  // Hydrate from localStorage once on mount.
  useEffect(() => {
    const persisted = readPersisted();
    if (persisted.theme) setThemeState(persisted.theme);
    if (persisted.accent) setAccentState(persisted.accent);
  }, []);

  // Apply attributes to <html>.
  useEffect(() => {
    if (typeof document === "undefined") return;
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  useEffect(() => {
    if (typeof document === "undefined") return;
    document.documentElement.dataset.accent = accent;
  }, [accent]);

  const setTheme = useCallback(
    (next: ThemeName) => {
      setThemeState(next);
      if (!ephemeral) writePersisted({ theme: next });
    },
    [ephemeral],
  );

  const setAccent = useCallback(
    (next: AccentName) => {
      setAccentState(next);
      if (!ephemeral) writePersisted({ accent: next });
    },
    [ephemeral],
  );

  const toggleTheme = useCallback(() => {
    setTheme(theme === "dark" ? "light" : "dark");
  }, [theme, setTheme]);

  return (
    <ThemeContext.Provider value={{ theme, accent, setTheme, setAccent, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme(): ThemeState {
  const ctx = useContext(ThemeContext);
  if (!ctx) {
    throw new Error("useTheme must be used inside a <ThemeProvider/>.");
  }
  return ctx;
}
