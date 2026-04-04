export function SolarOrb() {
  return (
    <div className="relative group cursor-pointer">
      <div className="w-72 h-72 solar-orb rounded-full" />
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="w-56 h-56 rounded-full bg-white/5 backdrop-blur-3xl border border-white/5 flex items-center justify-center overflow-hidden transition-transform duration-1000 group-hover:scale-110">
          <span className="material-symbols-outlined text-7xl text-white/20 select-none">
            stream
          </span>
        </div>
      </div>
    </div>
  );
}
