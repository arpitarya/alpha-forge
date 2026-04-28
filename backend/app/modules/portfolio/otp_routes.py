"""OTP-bound login endpoints — used by Wint Wealth and any future OTP source."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.core.logging import get_logger
from app.modules.brokers import SOURCES, get_source
from app.modules.portfolio.sources_routes import OTPSubmit

router = APIRouter()
logger = get_logger("routes.portfolio.otp")


@router.post("/{slug}/start-login")
async def start_login(slug: str):
    try:
        src = get_source(slug)
    except KeyError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e)) from e
    fn = getattr(src, "start_login", None)
    if not callable(fn):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"{slug} does not use OTP login.")
    try:
        return await fn()
    except Exception as e:  # noqa: BLE001
        logger.exception("start-login failed for %s", slug)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"start-login failed: {e}") from e


@router.post("/{slug}/otp")
async def submit_otp(slug: str, body: OTPSubmit):
    try:
        src = get_source(slug)
    except KeyError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e)) from e
    fn = getattr(src, "submit_otp", None)
    if not callable(fn):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"{slug} does not use OTP login.")
    try:
        return await fn(body.code)
    except Exception as e:  # noqa: BLE001
        logger.exception("submit-otp failed for %s", slug)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"submit-otp failed: {e}") from e


@router.post("/{slug}/reset")
async def reset_source(slug: str):
    if slug not in SOURCES:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Unknown source: {slug}")
    SOURCES[slug].reset()
    return {"source": slug, "info": SOURCES[slug].info().model_dump(mode="json")}
