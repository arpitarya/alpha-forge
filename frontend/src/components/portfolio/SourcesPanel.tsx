"use client";

import {
  Badge,
  Button,
  Card,
  Icon,
  Input,
  Text,
} from "@alphaforge/solar-orb-ui";
import { useQueryClient } from "@tanstack/react-query";
import { useRef, useState } from "react";
import {
  type SourceInfoDTO,
  useResetSource,
  useSources,
  useStartLogin,
  useSubmitOtp,
  useSyncAll,
  useSyncSource,
  useUploadCsv,
} from "@/lib/queries";

const OTP_SLUGS = new Set(["wint-wealth"]);

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

function readErr(e: unknown): string {
  const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
  return detail ?? (e as Error).message;
}

function SourceRow({ src, onAfter }: { src: SourceInfoDTO; onAfter: () => void }) {
  const fileRef = useRef<HTMLInputElement>(null);
  const upload = useUploadCsv();
  const sync = useSyncSource();
  const reset = useResetSource();
  const startLogin = useStartLogin();
  const submitOtp = useSubmitOtp();
  const [error, setError] = useState<string | null>(null);
  const [otpVisible, setOtpVisible] = useState(false);
  const [otpCode, setOtpCode] = useState("");
  const [otpStatus, setOtpStatus] = useState<string | null>(null);

  const isOtpSource = OTP_SLUGS.has(src.slug);

  async function handleUpload(file: File) {
    setError(null);
    try {
      await upload.mutateAsync({ slug: src.slug, file });
      onAfter();
    } catch (e) {
      setError(readErr(e));
    }
  }

  async function handleSync() {
    setError(null);
    try {
      await sync.mutateAsync(src.slug);
      onAfter();
    } catch (e) {
      setError(readErr(e));
    }
  }

  async function handleStartLogin() {
    setError(null);
    setOtpStatus(null);
    try {
      const r = (await startLogin.mutateAsync(src.slug)) as {
        sent?: boolean;
        channel?: string;
      };
      setOtpStatus(`OTP sent via ${r.channel ?? "sms"} — enter code below`);
      setOtpVisible(true);
    } catch (e) {
      setError(readErr(e));
    }
  }

  async function handleSubmitOtp() {
    setError(null);
    if (!otpCode.trim()) {
      setError("Enter the OTP code");
      return;
    }
    try {
      await submitOtp.mutateAsync({ slug: src.slug, code: otpCode.trim() });
      setOtpStatus("Verified — syncing holdings");
      setOtpCode("");
      setOtpVisible(false);
      await sync.mutateAsync(src.slug);
      onAfter();
    } catch (e) {
      setError(readErr(e));
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
        {src.kind === "api" && !isOtpSource && (
          <Button
            size="sm"
            variant="secondary"
            disabled={sync.isPending}
            onClick={handleSync}
          >
            <Icon name="sync" size="sm" className="mr-1" />
            {sync.isPending ? "Syncing…" : "Sync now"}
          </Button>
        )}

        {isOtpSource && src.status !== "ready" && (
          <Button
            size="sm"
            variant="secondary"
            disabled={startLogin.isPending}
            onClick={handleStartLogin}
          >
            <Icon name="key" size="sm" className="mr-1" />
            {startLogin.isPending ? "Sending OTP…" : "Send OTP"}
          </Button>
        )}

        {isOtpSource && src.status === "ready" && (
          <Button
            size="sm"
            variant="secondary"
            disabled={sync.isPending}
            onClick={handleSync}
          >
            <Icon name="sync" size="sm" className="mr-1" />
            {sync.isPending ? "Syncing…" : "Sync now"}
          </Button>
        )}

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
          variant="ghost"
          onClick={() => fileRef.current?.click()}
          disabled={upload.isPending}
        >
          <Icon name="upload" size="sm" className="mr-1" />
          {upload.isPending ? "Uploading…" : src.kind === "csv" ? "Upload CSV" : "CSV fallback"}
        </Button>

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

      {otpVisible && (
        <div className="flex items-center gap-2 pt-1">
          <Input
            value={otpCode}
            onChange={(e) => setOtpCode(e.target.value)}
            placeholder="Enter OTP"
            inputMode="numeric"
            maxLength={8}
            className="max-w-[140px]"
          />
          <Button
            size="sm"
            disabled={submitOtp.isPending}
            onClick={handleSubmitOtp}
          >
            {submitOtp.isPending ? "Verifying…" : "Verify"}
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => {
              setOtpVisible(false);
              setOtpCode("");
              setOtpStatus(null);
            }}
          >
            Cancel
          </Button>
        </div>
      )}

      {otpStatus && !error && (
        <Text variant="caption" tone="subtle">
          {otpStatus}
        </Text>
      )}

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
  const syncAll = useSyncAll();
  const qc = useQueryClient();
  const [syncAllSummary, setSyncAllSummary] = useState<string | null>(null);
  const sources = data?.sources ?? [];

  const onAfter = () => {
    qc.invalidateQueries({ queryKey: ["portfolio"] });
  };

  async function handleSyncAll() {
    setSyncAllSummary(null);
    try {
      const r = await syncAll.mutateAsync();
      const ok = Object.entries(r.results).filter(([, v]) => v.ok).length;
      const failed = Object.entries(r.results).filter(([, v]) => !v.ok).length;
      const total = Object.keys(r.results).length;
      setSyncAllSummary(
        failed
          ? `${ok}/${total} synced, ${failed} failed`
          : `All ${ok} sources synced`,
      );
      onAfter();
    } catch (e) {
      setSyncAllSummary(readErr(e));
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
            {syncAllSummary && (
              <Text variant="caption" tone="subtle">
                {syncAllSummary}
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
