"use client";

import { Card, Icon, Text } from "@alphaforge/solar-orb-ui";
import { useDashboardBrief } from "@/lib/queries";

export function AlphaBriefCard() {
  const { data, isLoading } = useDashboardBrief();
  const blocks = data?.blocks ?? [];

  return (
    <Card glow className="flex h-full flex-col overflow-auto">
      <Card.Header
        title={
          <span className="flex items-center gap-2">
            <Icon name="bolt" size="sm" className="text-[color:var(--accent)]" />
            Alpha Brief
          </span>
        }
        right={<Text variant="tag" tone="subtle">· LIVE</Text>}
      />

      {isLoading && <Text variant="body-sm" tone="subtle">Loading…</Text>}

      <div className="flex flex-col gap-5 mt-2">
        {blocks.map((b, i) => (
          <div key={`${b.title}-${i}`} className="flex flex-col gap-2">
            <Text variant="tag" tone={b.accent ? "accent" : "subtle"}>
              {b.title}
            </Text>
            <Text variant="body" tone="muted">
              {b.body}
            </Text>
            <button
              type="button"
              className="self-start font-mono text-[10px] uppercase tracking-[0.18em] text-[color:var(--accent)] transition-transform hover:translate-x-0.5"
            >
              {b.cta} →
            </button>
          </div>
        ))}
      </div>

      {data?.disclaimer && (
        <Text variant="caption" tone="subtle" className="mt-auto pt-4 text-center">
          {data.disclaimer}
        </Text>
      )}
    </Card>
  );
}
