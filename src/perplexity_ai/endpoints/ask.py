"""
Implementation of /rest/sse/perplexity_ask endpoint
"""

from __future__ import annotations

from typing import Dict, Iterator, List, Optional

from perplexity_ai.auth import PerplexityAuth
from perplexity_ai.models.request import AskParams, AskRequest, Mode, Model, Source
from perplexity_ai.models.response import AskResponse, SSEMessage
from perplexity_ai.session import PerplexitySession
from perplexity_ai.stealth import HeaderGenerator
from perplexity_ai.utils import SSEParser


class AskEndpoint:
    """Handler for /rest/sse/perplexity_ask endpoint"""

    ENDPOINT = "/rest/sse/perplexity_ask"

    def __init__(
        self,
        session: PerplexitySession,
        header_gen: HeaderGenerator,
        auth: PerplexityAuth,
        language: str,
        timezone: str,
    ):
        self.session = session
        self.header_gen = header_gen
        self.auth = auth
        self.language = language
        self.timezone = timezone

    def _build_request(
        self,
        query: str,
        mode: Mode | str,
        model: Optional[Model | str],
        sources: Optional[List[Source | str]],
        follow_up: Optional[AskResponse],
        incognito: bool,
    ) -> AskRequest:
        """Build AskRequest from parameters"""
        # Convert string enums
        if isinstance(mode, str):
            mode = Mode(mode)
        if model and isinstance(model, str):
            model = Model(model)

        sources_list = [Source.WEB]
        if sources:
            sources_list = [
                Source(s) if isinstance(s, str) else s for s in sources
            ]

        # Build params
        params = AskParams(
            language=self.language,
            timezone=self.timezone,
            sources=sources_list,
            is_incognito=incognito,
        )

        # Set model preference
        if model:
            params.model_preference = model
        elif mode == Mode.RESEARCH:
            params.model_preference = Model.PPLX_PRO

        # Add follow-up context
        if follow_up:
            params.last_backend_uuid = follow_up.backend_uuid

        # Add user auth
        if self.auth.user_nextauth_id:
            params.user_nextauth_id = self.auth.user_nextauth_id

        return AskRequest(query_str=query, params=params)

    def _parse_sse_response(self, response_text: str) -> AskResponse:
        """Parse SSE response into AskResponse"""
        text_parts = []
        last_message: Optional[SSEMessage] = None

        for event_data in SSEParser.parse_stream(response_text):
            try:
                message = SSEMessage(**event_data)
                last_message = message

                # Accumulate text
                if message.text:
                    text_parts.append(message.text)

            except Exception:
                continue

        if not last_message:
            return AskResponse(text="")

        return AskResponse(
            text="".join(text_parts) or last_message.text,
            thread_uuid=last_message.uuid,
            backend_uuid=last_message.backend_uuid,
            context_uuid=last_message.context_uuid,
            thread_url_slug=last_message.thread_url_slug,
            mode=last_message.mode,
            model=last_message.display_model,
        )

    def _stream_sse_response(
        self, response_text: str
    ) -> Iterator[AskResponse]:
        """Stream SSE response as iterator"""
        accumulated_text = ""

        for event_data in SSEParser.parse_stream(response_text):
            try:
                message = SSEMessage(**event_data)

                # Check for new text
                if message.text and message.text != accumulated_text:
                    new_text = message.text[len(accumulated_text):]
                    accumulated_text = message.text

                    yield AskResponse(
                        text=new_text,
                        thread_uuid=message.uuid,
                        backend_uuid=message.backend_uuid,
                        context_uuid=message.context_uuid,
                        thread_url_slug=message.thread_url_slug,
                        mode=message.mode,
                        model=message.display_model,
                    )

            except Exception:
                continue

    def ask(
        self,
        query: str,
        mode: Mode | str,
        model: Optional[Model | str],
        sources: Optional[List[Source | str]],
        follow_up: Optional[AskResponse],
        files: Optional[Dict[str, bytes]],
        stream: bool,
        incognito: bool,
    ) -> AskResponse | Iterator[AskResponse]:
        """Execute perplexity_ask request"""
        # Build request
        request = self._build_request(
            query=query,
            mode=mode,
            model=model,
            sources=sources,
            follow_up=follow_up,
            incognito=incognito,
        )

        # Generate headers
        headers = self.header_gen.request_headers(sse=True)
        headers.update(self.auth.to_headers())

        # Make request
        response = self.session.post(
            self.ENDPOINT,
            headers=headers,
            json_data=request.model_dump(mode="json", exclude_none=True),
            timeout=60,
        )

        response.raise_for_status()

        # Parse response
        if stream:
            return self._stream_sse_response(response.text)
        else:
            return self._parse_sse_response(response.text)
