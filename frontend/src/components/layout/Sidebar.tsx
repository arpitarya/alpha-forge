const sidebarItems = [
  { icon: "📊", label: "Dashboard", path: "/" },
  { icon: "📈", label: "Markets", path: "/markets" },
  { icon: "💼", label: "Portfolio", path: "/portfolio" },
  { icon: "⚡", label: "Trade", path: "/trade" },
  { icon: "🤖", label: "AI Chat", path: "/ai" },
  { icon: "🔍", label: "Screener", path: "/screener" },
  { icon: "📰", label: "News", path: "/news" },
  { icon: "⚙️", label: "Settings", path: "/settings" },
];

export function Sidebar() {
  return (
    <aside className="flex w-14 flex-col items-center gap-1 border-r border-subtle bg-card py-2">
      {sidebarItems.map(({ icon, label }) => (
        <button
          key={label}
          title={label}
          className="flex h-10 w-10 items-center justify-center rounded text-lg transition-colors hover:bg-[var(--af-bg-tertiary)]"
        >
          {icon}
        </button>
      ))}
    </aside>
  );
}
