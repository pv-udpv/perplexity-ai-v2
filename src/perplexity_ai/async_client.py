"""
Async Perplexity AI client (placeholder)
"""

from __future__ import annotations

from typing import Optional

from perplexity_ai.auth import PerplexityAuth


class AsyncClient:
    """Perplexity AI asynchronous client

    TODO: Implement async variant with httpx or async curl-cffi
    """

    def __init__(
        self,
        auth: Optional[PerplexityAuth] = None,
        language: str = "ru-RU",
        timezone: str = "Europe/Moscow",
        device_id: Optional[str] = None,
    ):
        raise NotImplementedError(
            "Async client not yet implemented. Use Client instead."
        )
