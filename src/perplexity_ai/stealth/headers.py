"""
Stealth header generation for iOS Safari emulation
"""

from __future__ import annotations

import secrets
from typing import Dict
from uuid import uuid4


class HeaderGenerator:
    """Generate browser-like headers for Perplexity AI requests"""

    # iOS Safari constants
    USER_AGENT = (
        "Ask/2.250911.0/16709 (iOS; iPhone; 18.7.0) isiOSOnMac/false"
    )
    APP_VERSION = "2.250911.0"
    API_VERSION = "2.18"
    CLIENT_NAME = "Perplexity-iOS"
    CLIENT_ENV = "production"

    def __init__(self, device_id: str | None = None, language: str = "ru-RU"):
        """Initialize header generator

        Args:
            device_id: Device ID (will generate if None)
            language: Accept-Language value
        """
        self.device_id = device_id or f"ios:{uuid4()}"
        self.language = language

    def base_headers(self) -> Dict[str, str]:
        """Generate base headers for all requests

        Returns:
            Dictionary of base headers
        """
        return {
            "User-Agent": self.USER_AGENT,
            "Accept": "*/*",
            "Accept-Language": self.language,
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        }

    def api_headers(self) -> Dict[str, str]:
        """Generate headers for API requests

        Returns:
            Dictionary of API headers
        """
        headers = self.base_headers()
        headers.update({
            "X-Client-Name": self.CLIENT_NAME,
            "X-App-ApiClient": "ios",
            "X-Device-ID": self.device_id,
            "X-App-Version": self.APP_VERSION,
            "X-Client-Env": self.CLIENT_ENV,
            "X-App-ApiVersion": self.API_VERSION,
            "Content-Type": "application/json",
        })
        return headers

    def sse_headers(self) -> Dict[str, str]:
        """Generate headers for SSE requests

        Returns:
            Dictionary of SSE-specific headers
        """
        headers = self.api_headers()
        headers["Accept"] = "text/event-stream"
        return headers

    def sentry_headers(self) -> Dict[str, str]:
        """Generate Sentry tracing headers

        Returns:
            Dictionary of Sentry headers
        """
        trace_id = uuid4().hex
        span_id = secrets.token_hex(8)
        return {
            "sentry-trace": f"{trace_id}-{span_id}-0",
            "baggage": (
                f"sentry-environment={self.CLIENT_ENV},"
                "sentry-public_key=f77046e48c26a58c0318fb447f540d47,"
                f"sentry-release=ai.perplexity.app%40{self.APP_VERSION}%2B16709,"
                f"sentry-trace_id={trace_id}"
            ),
        }

    def request_headers(
        self, sse: bool = False, with_sentry: bool = True
    ) -> Dict[str, str]:
        """Generate complete request headers

        Args:
            sse: Whether this is an SSE request
            with_sentry: Whether to include Sentry headers

        Returns:
            Complete headers dictionary
        """
        if sse:
            headers = self.sse_headers()
        else:
            headers = self.api_headers()

        if with_sentry:
            headers.update(self.sentry_headers())

        return headers
