"""Source-management endpoints — list/sync/upload. Mounted under /sources/*."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, UploadFile, status

from app.core.logging import get_logger
from app.modules.brokers import SOURCES, SourceKind, get_source
from app.modules.portfolio.sources_helper import apply_uploaded, sync_all

router = APIRouter()
logger = get_logger("routes.portfolio.sources")


@router.get("")
async def list_sources():
    return {"sources": [s.info().model_dump(mode="json") for s in SOURCES.values()]}


@router.get("/{slug}")
async def get_source_info(slug: str):
    if slug not in SOURCES:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Unknown source: {slug}")
    return SOURCES[slug].info().model_dump(mode="json")


@router.post("/{slug}/upload")
async def upload_csv(slug: str, file: UploadFile):
    try:
        src = get_source(slug)
    except KeyError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e)) from e
    try:
        holdings = src.parse(file.file, filename=file.filename)
        apply_uploaded(src, holdings)
    except NotImplementedError as e:
        raise HTTPException(400, f"{slug} does not support CSV upload.") from e
    except Exception as e:  # noqa: BLE001
        logger.exception("CSV ingest failed for %s", slug)
        raise HTTPException(400, f"Ingest failed: {e}") from e
    logger.info("Ingested %d holdings from %s (%s)", len(holdings), slug, file.filename)
    return {
        "source": slug, "filename": file.filename,
        "holdings_count": len(holdings),
        "info": src.info().model_dump(mode="json"),
    }


@router.post("/{slug}/sync")
async def sync_source(slug: str):
    try:
        src = get_source(slug)
    except KeyError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e)) from e
    if src.kind != SourceKind.API:
        raise HTTPException(400, f"{slug} is a CSV source — use /sources/{slug}/upload instead.")
    try:
        holdings = await src.sync()
    except Exception as e:  # noqa: BLE001
        logger.exception("Sync failed for %s", slug)
        raise HTTPException(400, f"Sync failed: {e}") from e
    return {
        "source": slug, "holdings_count": len(holdings),
        "info": src.info().model_dump(mode="json"),
    }


@router.post("/sync-all")
async def sync_all_sources():
    return await sync_all()
