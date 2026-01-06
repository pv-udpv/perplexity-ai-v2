"""
Main Perplexity AI client (synchronous)
"""

from __future__ import annotations

from typing import Dict, Iterator, List, Optional

from perplexity_ai.auth import PerplexityAuth
from perplexity_ai.endpoints.ask import AskEndpoint
from perplexity_ai.models.request import Mode, Model, Source
from perplexity_ai.models.response import AskResponse
from perplexity_ai.session import PerplexitySession
from perplexity_ai.stealth import HeaderGenerator


class Client:
    """Perplexity AI synchronous client

    Features:
    - Full API endpoint coverage
    - curl-cffi for Cloudflare bypass
    - iOS Safari fingerprinting
    - SSE streaming support
    - Type-safe with Pydantic models

    Example:
        >>> client = Client()
        >>> response = client.ask("What is quantum computing?")
        >>> print(response.text)
    """

    def __init__(
        self,
        auth: Optional[PerplexityAuth] = None,
        language: str = "ru-RU",
        timezone: str = "Europe/Moscow",
        device_id: Optional[str] = None,
    ):
        """Initialize Perplexity AI client

        Args:
            auth: Authentication credentials (optional)
            language: Accept-Language header value
            timezone: User timezone
            device_id: Device ID (will generate if None)
        """
        self.auth = auth or PerplexityAuth()
        self.language = language
        self.timezone = timezone
        self.header_gen = HeaderGenerator(device_id=device_id, language=language)

        # Initialize session
        cookies = self.auth.to_cookies()
        self.session = PerplexitySession(cookies=cookies)

        # Initialize endpoints
        self._ask_endpoint = AskEndpoint(
            session=self.session,
            header_gen=self.header_gen,
            auth=self.auth,
            language=language,
            timezone=timezone,
        )

    def ask(
        self,
        query: str,
        *,
        mode: Mode | str = Mode.CONCISE,
        model: Optional[Model | str] = None,
        sources: Optional[List[Source | str]] = None,
        follow_up: Optional[AskResponse] = None,
        files: Optional[Dict[str, bytes]] = None,
        stream: bool = False,
        incognito: bool = False,
    ) -> AskResponse | Iterator[AskResponse]:
        """Ask a question to Perplexity AI

        Args:
            query: Question or search query
            mode: Response mode (concise, copilot, research)
            model: AI model to use (requires Pro account)
            sources: Search sources (web, scholar, social)
            follow_up: Previous response for follow-up questions
            files: Files to upload (name -> bytes)
            stream: Enable streaming responses
            incognito: Use incognito mode

        Returns:
            AskResponse or Iterator[AskResponse] if streaming

        Example:
            >>> # Simple query
            >>> response = client.ask("Explain quantum computing")
            >>>
            >>> # Streaming
            >>> for chunk in client.ask("Long explanation", stream=True):
            ...     print(chunk.text, end="", flush=True)
            >>>
            >>> # Pro model
            >>> response = client.ask(
            ...     "Deep analysis",
            ...     mode="research",
            ...     model="claude37sonnetthinking"
            ... )
        """
        return self._ask_endpoint.ask(
            query=query,
            mode=mode,
            model=model,
            sources=sources,
            follow_up=follow_up,
            files=files,
            stream=stream,
            incognito=incognito,
        )

    def close(self) -> None:
        """Close HTTP session"""
        self.session.close()

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *args) -> None:
        self.close()
