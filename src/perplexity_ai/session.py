"""
HTTP Session management with curl-cffi
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional
from curl_cffi import requests
from curl_cffi.requests import Response, Session


class PerplexitySession:
    """HTTP Session wrapper using curl-cffi for Cloudflare bypass"""

    BASE_URL = "https://www.perplexity.ai"
    IMPERSONATE = "chrome120"  # Browser to impersonate

    def __init__(self, cookies: Optional[Dict[str, str]] = None):
        self.session = Session(impersonate=self.IMPERSONATE)
        if cookies:
            self.session.cookies.update(cookies)

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[bytes] = None,
        timeout: int = 30,
        stream: bool = False,
    ) -> Response:
        """Make HTTP request with curl-cffi

        Args:
            method: HTTP method
            url: Full URL or path (will be prefixed with BASE_URL)
            headers: Request headers
            params: Query parameters
            json_data: JSON body
            data: Binary data
            timeout: Request timeout in seconds
            stream: Whether to stream response

        Returns:
            curl-cffi Response object
        """
        if not url.startswith("http"):
            url = f"{self.BASE_URL}{url}"

        return self.session.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_data,
            data=data,
            timeout=timeout,
            stream=stream,
        )

    def get(self, url: str, **kwargs: Any) -> Response:
        """GET request"""
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> Response:
        """POST request"""
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> Response:
        """PUT request"""
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> Response:
        """DELETE request"""
        return self.request("DELETE", url, **kwargs)

    def close(self) -> None:
        """Close session"""
        self.session.close()

    def __enter__(self) -> PerplexitySession:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
