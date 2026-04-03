export function Header() {
  return (
    <header className="flex h-12 items-center justify-between border-b border-subtle bg-card px-4">
      <div className="flex items-center gap-3">
        <h1 className="text-lg font-bold tracking-tight">
          <span className="text-[var(--af-accent-cyan)]">Alpha</span>
          <span className="text-[var(--af-accent-blue)]">Forge</span>
        </h1>
        <span className="text-muted text-xs">v0.1.0</span>
      </div>

      <nav className="flex items-center gap-6 text-sm">
        <NavItem label="Dashboard" active />
        <NavItem label="Markets" />
        <NavItem label="Portfolio" />
        <NavItem label="Trade" />
        <NavItem label="AI Analysis" />
      </nav>

      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5 text-xs">
          <span className="h-2 w-2 rounded-full bg-[var(--af-green)]" />
          <span className="text-muted">NSE Open</span>
        </div>
        <button className="rounded bg-[var(--af-accent-blue)] px-3 py-1 text-xs font-medium text-white hover:bg-blue-600">
          Connect Broker
        </button>
      </div>
    </header>
  );
}

function NavItem({ label, active = false }: { label: string; active?: boolean }) {
  return (
    <button
      className={`transition-colors ${
        active ? "text-[var(--af-accent-cyan)]" : "text-muted hover:text-[var(--af-text-primary)]"
      }`}
    >
      {label}
    </button>
  );
}
