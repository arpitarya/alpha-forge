import { useState } from "react";
import {
  useResetSource,
  useStartLogin,
  useSubmitOtp,
  useSyncSource,
  useUploadCsv,
} from "./portfolio.query";
import { readErr } from "./sources.utils";

export function useSourceRow(slug: string, onAfter: () => void) {
  const upload = useUploadCsv();
  const sync = useSyncSource();
  const reset = useResetSource();
  const startLogin = useStartLogin();
  const submitOtp = useSubmitOtp();

  const [error, setError] = useState<string | null>(null);
  const [otpVisible, setOtpVisible] = useState(false);
  const [otpCode, setOtpCode] = useState("");
  const [otpStatus, setOtpStatus] = useState<string | null>(null);

  async function handleUpload(file: File) {
    setError(null);
    try {
      await upload.mutateAsync({ slug, file });
      onAfter();
    } catch (e) {
      setError(readErr(e));
    }
  }

  async function handleSync() {
    setError(null);
    try {
      await sync.mutateAsync(slug);
      onAfter();
    } catch (e) {
      setError(readErr(e));
    }
  }

  async function handleStartLogin() {
    setError(null);
    setOtpStatus(null);
    try {
      const r = (await startLogin.mutateAsync(slug)) as { sent?: boolean; channel?: string };
      setOtpStatus(`OTP sent via ${r.channel ?? "sms"} — enter code below`);
      setOtpVisible(true);
    } catch (e) {
      setError(readErr(e));
    }
  }

  async function handleSubmitOtp() {
    setError(null);
    if (!otpCode.trim()) return setError("Enter the OTP code");
    try {
      await submitOtp.mutateAsync({ slug, code: otpCode.trim() });
      setOtpStatus("Verified — syncing holdings");
      setOtpCode("");
      setOtpVisible(false);
      await sync.mutateAsync(slug);
      onAfter();
    } catch (e) {
      setError(readErr(e));
    }
  }

  async function handleReset() {
    await reset.mutateAsync(slug);
    onAfter();
  }

  return {
    upload, sync, reset, startLogin, submitOtp,
    error, otpVisible, otpCode, otpStatus,
    setOtpCode, setOtpVisible, setOtpStatus,
    handleUpload, handleSync, handleStartLogin, handleSubmitOtp, handleReset,
  };
}
