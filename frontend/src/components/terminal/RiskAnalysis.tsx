export function RiskAnalysis() {
  return (
    <section className="floating-shard rounded-[2.5rem] p-8 flex flex-col gap-6">
      <h2 className="text-[10px] font-bold tracking-[0.3em] uppercase text-white/40">
        Risk Analysis
      </h2>
      <div className="flex-1 flex items-end gap-2 px-2">
        <div className="flex-1 h-[30%] bg-white/5 rounded-full transition-all duration-1000 hover:h-[50%] hover:bg-primary/20" />
        <div className="flex-1 h-[60%] bg-white/5 rounded-full transition-all duration-1000 hover:h-[80%] hover:bg-primary/20" />
        <div className="flex-1 h-[90%] bg-primary/40 rounded-full" />
        <div className="flex-1 h-[40%] bg-white/5 rounded-full transition-all duration-1000 hover:h-[60%] hover:bg-primary/20" />
        <div className="flex-1 h-[70%] bg-white/5 rounded-full transition-all duration-1000 hover:h-[85%] hover:bg-primary/20" />
      </div>
      <div className="flex justify-between items-center text-[10px] font-bold uppercase tracking-widest text-primary/80">
        <span>Confidence</span>
        <span>88.4%</span>
      </div>
    </section>
  );
}
