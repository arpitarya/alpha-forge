export function AlphaBrief() {
  return (
    <section className="floating-shard rounded-[2.5rem] p-10 flex flex-col gap-8">
      <div className="flex items-center gap-3">
        <span className="material-symbols-outlined text-primary text-xl">bolt</span>
        <h2 className="text-sm font-bold tracking-[0.3em] uppercase text-white/90">Alpha Brief</h2>
      </div>
      <div className="space-y-10">
        <div className="space-y-3">
          <p className="text-[10px] text-primary/80 font-bold uppercase tracking-[0.2em]">
            Market Sentiment
          </p>
          <p className="text-sm text-white/70 font-light leading-relaxed">
            System detects bullish pivot in AI infrastructure tokens. Volume up 22% in APAC.
          </p>
        </div>
        <div className="space-y-3">
          <p className="text-[10px] text-white/40 font-bold uppercase tracking-[0.2em]">
            Risk Alert
          </p>
          <p className="text-sm text-white/50 font-light leading-relaxed">
            Global Equities hedge position is over-extended. System recommends rebalancing.
          </p>
        </div>
      </div>
    </section>
  );
}
