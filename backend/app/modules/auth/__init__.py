"""auth module — public API surface."""

from __future__ import annotations

from app.modules.auth.auth_routes import router

__all__ = ["router"]
