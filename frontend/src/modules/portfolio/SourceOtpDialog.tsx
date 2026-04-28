"use client";

import { Button, Input } from "@alphaforge/solar-orb-ui";

interface Props {
  code: string;
  pending: boolean;
  onChange: (code: string) => void;
  onSubmit: () => void;
  onCancel: () => void;
}

export function SourceOtpDialog({ code, pending, onChange, onSubmit, onCancel }: Props) {
  return (
    <div className="flex items-center gap-2 pt-1">
      <Input
        value={code}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Enter OTP"
        inputMode="numeric"
        maxLength={8}
        className="max-w-[140px]"
      />
      <Button size="sm" disabled={pending} onClick={onSubmit}>
        {pending ? "Verifying…" : "Verify"}
      </Button>
      <Button size="sm" variant="ghost" onClick={onCancel}>
        Cancel
      </Button>
    </div>
  );
}
