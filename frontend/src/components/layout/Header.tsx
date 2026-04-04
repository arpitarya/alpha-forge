import { Logo } from "@/components/solar-orb";

export function Header() {
  return (
    <header className="fixed top-6 left-1/2 -translate-x-1/2 w-[calc(100%-48px)] max-w-7xl z-50 flex justify-between items-center px-10 py-4 floating-shard rounded-full">
      <Logo variant="full" size="sm" theme="dark" />
      <nav className="hidden md:flex gap-10 text-xs font-bold tracking-[0.2em] uppercase">
        <button type="button" className="text-primary">
          Terminal
        </button>
        <button type="button" className="text-neutral-500 hover:text-white transition-colors">
          Portfolio
        </button>
        <button type="button" className="text-neutral-500 hover:text-white transition-colors">
          Markets
        </button>
      </nav>
      <div className="flex items-center gap-6">
        <span className="material-symbols-outlined text-neutral-400 cursor-pointer hover:text-primary transition-colors">
          notifications
        </span>
        <div className="w-8 h-8 rounded-full border border-white/10 bg-surface-container flex items-center justify-center">
          <span className="material-symbols-outlined text-sm text-white/60">person</span>
        </div>
      </div>
    </header>
  );
}
