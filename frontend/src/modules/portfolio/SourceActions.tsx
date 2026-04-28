"use client";

import { Button, Icon } from "@alphaforge/solar-orb-ui";
import type { RefObject } from "react";
import type { SourceInfoDTO } from "./portfolio.types";
import { OTP_SLUGS } from "./sources.utils";
import type { useSourceRow } from "./useSourceRow.hook";

interface Props {
  src: SourceInfoDTO;
  fileRef: RefObject<HTMLInputElement | null>;
  r: ReturnType<typeof useSourceRow>;
}

export function SourceActions({ src, fileRef, r }: Props) {
  const isOtp = OTP_SLUGS.has(src.slug);
  const showSync = (src.kind === "api" && !isOtp) || (isOtp && src.status === "ready");
  const showSendOtp = isOtp && src.status !== "ready";

  return (
    <div className="flex flex-wrap gap-2">
      {showSync && (
        <Button size="sm" variant="secondary" disabled={r.sync.isPending} onClick={r.handleSync}>
          <Icon name="sync" size="sm" className="mr-1" />
          {r.sync.isPending ? "Syncing…" : "Sync now"}
        </Button>
      )}
      {showSendOtp && (
        <Button
          size="sm"
          variant="secondary"
          disabled={r.startLogin.isPending}
          onClick={r.handleStartLogin}
        >
          <Icon name="key" size="sm" className="mr-1" />
          {r.startLogin.isPending ? "Sending OTP…" : "Send OTP"}
        </Button>
      )}
      <input
        ref={fileRef}
        type="file"
        accept=".csv"
        hidden
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) r.handleUpload(f);
          e.target.value = "";
        }}
      />
      <Button
        size="sm"
        variant="ghost"
        onClick={() => fileRef.current?.click()}
        disabled={r.upload.isPending}
      >
        <Icon name="upload" size="sm" className="mr-1" />
        {r.upload.isPending ? "Uploading…" : src.kind === "csv" ? "Upload CSV" : "CSV fallback"}
      </Button>
      {src.holdings_count > 0 && (
        <Button size="sm" variant="ghost" disabled={r.reset.isPending} onClick={r.handleReset}>
          Reset
        </Button>
      )}
    </div>
  );
}
