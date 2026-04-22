"""Gemini embeddings client.

Standalone rewrite of `backend/app/services/embedding.py` — duplicated
rather than imported to keep `repo-context-mcp` deployable without the
backend on `PYTHONPATH`.
"""

from __future__ import annotations

import asyncio
import logging

import httpx

from alphaforge_repo_context.config import get_settings

logger = logging.getLogger("repo_context.embeddings")

_EMBED_URL = (
    "https://generativelanguage.googleapis.com/v1beta"
    "/models/{model}:embedContent?key={key}"
)


class EmbeddingClient:
    """Single-text + batch embedding with free-tier pacing."""

    def __init__(self) -> None:
        s = get_settings()
        self._api_key = s.gemini_api_key
        self._model = s.embedding_model
        self._dims = s.embedding_dimensions
        self._pace = s.embed_batch_sleep_seconds
        self._client: httpx.AsyncClient | None = None

    async def _http(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    def _zero(self) -> list[float]:
        return [0.0] * self._dims

    async def embed(self, text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
        if not self._api_key:
            logger.warning("GEMINI_API_KEY not set — returning zero vector")
            return self._zero()
        client = await self._http()
        url = _EMBED_URL.format(model=self._model, key=self._api_key)
        payload = {
            "model": f"models/{self._model}",
            "content": {"parts": [{"text": text}]},
            "taskType": task_type,
        }
        try:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            return r.json()["embedding"]["values"]
        except httpx.HTTPStatusError as e:
            logger.error("Gemini embed failed (status=%d): %s", e.response.status_code, e)
            return self._zero()
        except Exception as e:  # noqa: BLE001
            logger.error("Gemini embed error: %s", e)
            return self._zero()

    async def embed_batch(
        self, texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT"
    ) -> list[list[float]]:
        out: list[list[float]] = []
        for i, t in enumerate(texts):
            out.append(await self.embed(t, task_type=task_type))
            if i < len(texts) - 1:
                await asyncio.sleep(self._pace)
        return out

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
