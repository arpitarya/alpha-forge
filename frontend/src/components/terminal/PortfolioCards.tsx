export function NetWorth() {
  return (
    <div className="floating-shard px-10 py-8 rounded-[2.5rem] flex flex-col items-center gap-2 hover:scale-105 transition-all duration-700">
      <p className="text-[10px] font-bold text-white/30 uppercase tracking-[0.4em]">Net Worth</p>
      <p className="text-4xl font-bold text-white tracking-tighter">$1,284,500</p>
      <div className="flex items-center gap-2 text-emerald-400/80 font-bold">
        <span className="material-symbols-outlined text-xs">trending_up</span>
        <span className="text-[10px]">1.2% TODAY</span>
      </div>
    </div>
  );
}

export function Allocation() {
  return (
    <div className="floating-shard px-10 py-8 rounded-[2.5rem] flex flex-col items-center gap-4 hover:scale-105 transition-all duration-700">
      <p className="text-[10px] font-bold text-white/30 uppercase tracking-[0.4em]">Allocation</p>
      <div className="flex gap-6">
        <div className="flex flex-col items-center gap-1">
          <div className="w-1.5 h-10 bg-primary rounded-full" />
          <p className="text-[10px] font-bold">45%</p>
        </div>
        <div className="flex flex-col items-center gap-1">
          <div className="w-1.5 h-6 bg-white/20 rounded-full" />
          <p className="text-[10px] font-bold">30%</p>
        </div>
        <div className="flex flex-col items-center gap-1">
          <div className="w-1.5 h-4 bg-white/10 rounded-full" />
          <p className="text-[10px] font-bold">25%</p>
        </div>
      </div>
    </div>
  );
}
