"use client";

import {
  Badge,
  Button,
  Card,
  Icon,
  Text,
} from "@alphaforge/solar-orb-ui";
import { useQueryClient } from "@tanstack/react-query";
import { useRef, useState } from "react";
import {
  type SourceInfoDTO,
  useResetSource,
  useSources,
  useSyncSource,
  useUploadCsv,
} from "@/lib/queries";

function formatTime(iso: string | null): string {
  if (!iso) return "never";
  const dt = new Date(iso);
  const diffMs = Date.now() - dt.getTime();
  const min = Math.floor(diffMs / 60000);
  if (min < 1) return "just now";
  if (min < 60) return `${min}m ago`;
  const hrs = Math.floor(min / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

function statusVariant(status: SourceInfoDTO["status"]) {
  switch (status) {
    case "ready":
      return "success" as const;
    case "syncing":
      return "warning" as const;
    case "error":
      return "danger" as const;
    default:
      return "default" as const;
  }
}

function SourceRow({ src, onAfter }: { src: SourceInfoDTO; onAfter: () => void }) {
  const fileRef = useRef<HTMLInputElement>(null);
  const upload = useUploadCsv();
  const sync = useSyncSource();
  const reset = useResetSource();
  const [error, setError] = useState<string | null>(null);

  async function handleUpload(file: File) {
    setError(null);
    try {
      await upload.mutateAsync({ slug: src.slug, file });
      onAfter();
    } catch (e) {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg ?? (e as Error).message);
    }
  }

  return (
    <div className="flex flex-col gap-2 rounded-[var(--radius-sm)] border border-[color:var(--line)] p-3">
      <div className="flex items-center justify-between">
        <div className="flex flex-col">
          <Text className="font-bold">{src.label}</Text>
          <Text variant="caption" tone="subtle">
            {src.kind.toUpperCase()} · {formatTime(src.last_synced_at)}
            {src.holdings_count > 0 && ` · ${src.holdings_count} holdings`}
          </Text>
        </div>
        <Badge variant={statusVariant(src.status)}>{src.status}</Badge>
      </div>

      {src.notes && (
        <Text variant="caption" tone="subtle">
          {src.notes}
        </Text>
      )}

      <div className="flex flex-wrap gap-2">
        {src.kind === "csv" && (
          <>
            <input
              ref={fileRef}
              type="file"
              accept=".csv"
              hidden
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) handleUpload(f);
                e.target.value = "";
              }}
            />
            <Button
              size="sm"
              variant="secondary"
              onClick={() => fileRef.current?.click()}
              disabled={upload.isPending}
            >
              <Icon name="upload" size="sm" className="mr-1" />
              {upload.isPending ? "Uploading…" : "Upload CSV"}
            </Button>
          </>
        )}
        {src.kind === "api" && (
          <Button
            size="sm"
            variant="secondary"
            disabled={sync.isPending}
            onClick={async () => {
              setError(null);
              try {
                await sync.mutateAsync(src.slug);
                onAfter();
              } catch (e) {
                const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
                setError(msg ?? (e as Error).message);
              }
            }}
          >
            <Icon name="sync" size="sm" className="mr-1" />
            {sync.isPending ? "Syncing…" : "Sync now"}
          </Button>
        )}
        {src.holdings_count > 0 && (
          <Button
            size="sm"
            variant="ghost"
            disabled={reset.isPending}
            onClick={async () => {
              await reset.mutateAsync(src.slug);
              onAfter();
            }}
          >
            Reset
          </Button>
        )}
      </div>

      {(error || src.error_message) && (
        <Text variant="caption" tone="dn">
          {error ?? src.error_message}
        </Text>
      )}
    </div>
  );
}

export function SourcesPanel() {
  const { data } = useSources();
  const qc = useQueryClient();
  const sources = data?.sources ?? [];

  const onAfter = () => {
    qc.invalidateQueries({ queryKey: ["portfolio"] });
  };

  return (
    <Card glow className="flex h-full flex-col gap-3 overflow-auto">
      <Card.Header
        title={
          <span className="flex items-center gap-2">
            <Icon name="hub" size="sm" className="text-[color:var(--accent)]" />
            Sources
          </span>
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
