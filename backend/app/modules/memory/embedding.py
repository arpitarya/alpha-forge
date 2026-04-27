"""Gemini embedding service for vector memory."""

from __future__ import annotations

import asyncio
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger("services.embedding")

_EMBED_URL = (
    "https://generativelanguage.googleapis.com/v1beta"
    "/models/{model}:embedContent?key={key}"
)


class EmbeddingService:
    """Generates float32[768] embeddings via Gemini text-embedding-004 (free tier).

    Falls back to a zero-vector mock when GEMINI_API_KEY is absent (dev mode).
    """

    def __init__(self) -> None:
        self._api_key = settings.gemini_api_key
        self._model = settings.embedding_model
        self._dims = settings.embedding_dimensions
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def embed_text(self, text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
        """Embed a single text string. task_type should be RETRIEVAL_QUERY for queries."""
        if not self._api_key:
            logger.warning("GEMINI_API_KEY not set — returning zero-vector mock embedding")
            return [0.0] * self._dims

        client = await self._get_client()
        url = _EMBED_URL.format(model=self._model, key=self._api_key)
        payload = {
            "model": f"models/{self._model}",
            "content": {"parts": [{"text": text}]},
            "taskType": task_type,
        }
        try:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()["embedding"]["values"]
        except httpx.HTTPStatusError as e:
            logger.error("Gemini embedding failed (status=%d): %s", e.response.status_code, e)
            return [0.0] * self._dims
        except Exception as e:
            logger.error("Gemini embedding error: %s", e)
            return [0.0] * self._dims

    async def embed_batch(
        self, texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT"
    ) -> list[list[float]]:
        """Embed a list of texts. Enforces 1.1s between calls (Gemini free tier: 1 RPM)."""
        results: list[list[float]] = []
        for i, text in enumerate(texts):
            vec = await self.embed_text(text, task_type=task_type)
            results.append(vec)
            if i < len(texts) - 1:
                await asyncio.sleep(1.1)
        return results

    def build_pick_explanation_text(self, pick: dict) -> str:
        """Build a rich, embeddable text description of a screener pick."""
        symbol = pick.get("symbol", pick.get("SYMBOL", "UNKNOWN"))
        date = pick.get("scan_date", pick.get("DATE", ""))
        model = pick.get("model_type", "ml")
        prob = pick.get("probability", pick.get("PROBABILITY", 0.0))
        rank = pick.get("rank", pick.get("RANK", ""))
        rsi = pick.get("rsi_14", pick.get("RSI_14", ""))
        vol = pick.get("vol_sma_ratio", pick.get("VOL_SMA_RATIO", ""))
        macd = pick.get("macd_hist", pick.get("MACD_HIST", ""))
        adx = pick.get("adx_14", pick.get("ADX_14", ""))
        dist_52w = pick.get("dist_52w_high_pct", pick.get("DIST_52W_HIGH_PCT", ""))
        roc = pick.get("roc_5", pick.get("ROC_5", ""))

        parts = [f"{symbol} screener pick"]
        if date:
            parts.append(date)
        parts.append(f"{model}: probability={float(prob):.3f}")
        if rank:
            parts.append(f"rank={rank}")
        if rsi != "":
            parts.append(f"RSI={float(rsi):.1f}")
        if vol != "":
            parts.append(f"volume ratio={float(vol):.2f}x average")
        if macd != "":
            sign = "+" if float(macd) >= 0 else ""
            parts.append(f"MACD histogram={sign}{float(macd):.2f}")
        if adx != "":
            parts.append(f"ADX={float(adx):.1f} (trend strength)")
        if dist_52w != "":
            parts.append(f"distance from 52-week high={float(dist_52w):.1f}%")
        if roc != "":
            sign = "+" if float(roc) >= 0 else ""
            parts.append(f"5-day ROC={sign}{float(roc):.2f}%")

        return ", ".join(parts)

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()


_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
