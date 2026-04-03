import { create } from "zustand";

interface AppState {
  // Current symbol in focus
  activeSymbol: string | null;
  setActiveSymbol: (symbol: string) => void;

  // Sidebar / navigation
  activePage: string;
  setActivePage: (page: string) => void;

  // Broker connection
  brokerConnected: boolean;
  brokerName: string | null;
  setBrokerConnection: (connected: boolean, name?: string) => void;

  // Theme
  theme: "dark" | "light";
  toggleTheme: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeSymbol: null,
  setActiveSymbol: (symbol) => set({ activeSymbol: symbol }),

  activePage: "dashboard",
  setActivePage: (page) => set({ activePage: page }),

  brokerConnected: false,
  brokerName: null,
  setBrokerConnection: (connected, name) =>
    set({ brokerConnected: connected, brokerName: name ?? null }),

  theme: "dark",
  toggleTheme: () => set((s) => ({ theme: s.theme === "dark" ? "light" : "dark" })),
}));
