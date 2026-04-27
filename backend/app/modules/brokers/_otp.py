"""TOTP helper shared by broker sources that auth with a time-based OTP."""

from __future__ import annotations


def generate_totp(secret: str) -> str:
    try:
        import pyotp  # type: ignore[import-not-found]
    except ImportError as e:  # pragma: no cover
        raise RuntimeError(
            "pyotp not installed — run `pdm add pyotp` to enable TOTP auth"
        ) from e
    return pyotp.TOTP(secret).now()
