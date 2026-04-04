const sidebarItems = [
  { icon: "terminal", label: "Terminal", active: true },
  { icon: "account_balance_wallet", label: "Portfolio", active: false },
  { icon: "monitoring", label: "Markets", active: false },
];

export function Sidebar() {
  return (
    <aside className="fixed left-6 top-32 z-40 flex flex-col gap-6 py-8 px-4 floating-shard rounded-[3.5rem] w-20 hover:w-56 transition-all duration-700 ease-in-out group overflow-hidden">
      <div className="flex flex-col gap-4">
        {sidebarItems.map(({ icon, label, active }) => (
          <div
            key={label}
            className={`flex items-center gap-4 rounded-full p-4 cursor-pointer transition-all ${
              active
                ? "bg-primary/10 text-primary"
                : "text-neutral-500 hover:text-white hover:bg-white/5"
            }`}
          >
            <span className="material-symbols-outlined">{icon}</span>
            <span className="opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap font-bold text-sm tracking-widest uppercase">
              {label}
            </span>
          </div>
        ))}
      </div>
    </aside>
  );
}
