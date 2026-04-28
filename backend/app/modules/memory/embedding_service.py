"""Gemini embedding service for vector memory."""

from __future__ import annotations

import asyncio
import logging

import httpx

from app.core.config import settings
from app.modules.memory.embedding_utils import build_pick_explanation_text

logger = logging.getLogger("services.embedding")

_EMBED_URL = (
    "https://generativelanguage.googleapis.com/v1beta"
    "/models/{model}:embedContent?key={key}"
)


class EmbeddingService:
    """float32[768] embeddings via Gemini text-embedding-004 (free tier).

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
        except Exception as e:
            logger.error("Gemini embedding error: %s", e)
        return [0.0] * self._dims

    async def embed_batch(
        self, texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT"
    ) -> list[list[float]]:
        results: list[list[float]] = []
        for i, text in enumerate(texts):
            results.append(await self.embed_text(text, task_type=task_type))
            if i < len(texts) - 1:
                await asyncio.sleep(1.1)  # Gemini free tier: 1 RPM
        return results

    def build_pick_explanation_text(self, pick: dict) -> str:
        return build_pick_explanation_text(pick)

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()


_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    global _embedding_service  # noqa: PLW0603
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
