"use client";

import { Badge, Text } from "@alphaforge/solar-orb-ui";
import { useRef } from "react";
import type { SourceInfoDTO } from "./portfolio.types";
import { SourceActions } from "./SourceActions";
import { SourceOtpDialog } from "./SourceOtpDialog";
import { formatTime, statusVariant } from "./sources.utils";
import { useSourceRow } from "./useSourceRow.hook";

export function SourceRow({ src, onAfter }: { src: SourceInfoDTO; onAfter: () => void }) {
  const fileRef = useRef<HTMLInputElement>(null);
  const r = useSourceRow(src.slug, onAfter);

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

      <SourceActions src={src} fileRef={fileRef} r={r} />

      {r.otpVisible && (
        <SourceOtpDialog
          code={r.otpCode}
          pending={r.submitOtp.isPending}
          onChange={r.setOtpCode}
          onSubmit={r.handleSubmitOtp}
          onCancel={() => {
            r.setOtpVisible(false);
            r.setOtpCode("");
            r.setOtpStatus(null);
          }}
        />
      )}

      {r.otpStatus && !r.error && (
        <Text variant="caption" tone="subtle">
          {r.otpStatus}
        </Text>
      )}

      {(r.error || src.error_message) && (
        <Text variant="caption" tone="dn">
          {r.error ?? src.error_message}
        </Text>
      )}
    </div>
  );
}
