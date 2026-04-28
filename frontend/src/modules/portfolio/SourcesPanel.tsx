"use client";

import { Button, Card, Icon, Text } from "@alphaforge/solar-orb-ui";
import { useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useSources, useSyncAll } from "./portfolio.query";
import { SourceRow } from "./SourceRow";
import { readErr } from "./sources.utils";

export function SourcesPanel() {
  const { data } = useSources();
  const syncAll = useSyncAll();
  const qc = useQueryClient();
  const [syncSummary, setSyncSummary] = useState<string | null>(null);
  const sources = data?.sources ?? [];

  const onAfter = () => qc.invalidateQueries({ queryKey: ["portfolio"] });

  async function handleSyncAll() {
    setSyncSummary(null);
    try {
      const r = await syncAll.mutateAsync();
      const ok = Object.values(r.results).filter((v) => v.ok).length;
      const failed = Object.values(r.results).filter((v) => !v.ok).length;
      const total = ok + failed;
      setSyncSummary(failed ? `${ok}/${total} synced, ${failed} failed` : `All ${ok} sources synced`);
      onAfter();
    } catch (e) {
      setSyncSummary(readErr(e));
    }
  }

  return (
    <Card glow className="flex h-full flex-col gap-3 overflow-auto">
      <Card.Header
        title={
          <span className="flex items-center gap-2">
            <Icon name="hub" size="sm" className="text-[color:var(--accent)]" />
            Sources
          </span>
        }
        right={
          <div className="flex items-center gap-2">
            {syncSummary && (
              <Text variant="caption" tone="subtle">
                {syncSummary}
              </Text>
            )}
            <Button
              size="sm"
              variant="secondary"
              disabled={syncAll.isPending}
              onClick={handleSyncAll}
            >
              <Icon name="sync" size="sm" className="mr-1" />
              {syncAll.isPending ? "Syncing…" : "Sync all"}
            </Button>
          </div>
        }
      />
      <div className="flex flex-col gap-2">
        {sources.map((s) => (
          <SourceRow key={s.slug} src={s} onAfter={onAfter} />
        ))}
      </div>
    </Card>
  );
}
