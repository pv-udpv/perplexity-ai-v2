"""
Server-Sent Events (SSE) stream parser
"""

from __future__ import annotations

import json
from typing import Dict, Iterator, Optional


class SSEParser:
    """Parse SSE event stream

    SSE format:
    event: message
    data: {json}

    event: message
    data: {json}
    """

    def __init__(self):
        self.event: Optional[str] = None
        self.data: str = ""

    @staticmethod
    def parse_stream(content: bytes | str) -> Iterator[Dict]:
        """Parse SSE stream into events

        Args:
            content: Raw SSE stream content

        Yields:
            Parsed event data as dictionary
        """
        if isinstance(content, bytes):
            content = content.decode("utf-8")

        lines = content.split("\n")
        event_type: Optional[str] = None
        data_lines: list[str] = []

        for line in lines:
            line = line.strip()

            if not line:
                # Empty line = end of event
                if data_lines:
                    data = "\n".join(data_lines)
                    try:
                        yield json.loads(data)
                    except json.JSONDecodeError:
                        pass
                    data_lines = []
                    event_type = None
                continue

            if line.startswith("event:"):
                event_type = line[6:].strip()
            elif line.startswith("data:"):
                data_lines.append(line[5:].strip())

        # Handle remaining data
        if data_lines:
            data = "\n".join(data_lines)
            try:
                yield json.loads(data)
            except json.JSONDecodeError:
                pass

    @staticmethod
    def parse_line(line: str) -> Optional[Dict]:
        """Parse single SSE line

        Args:
            line: Single line from SSE stream

        Returns:
            Parsed data if complete event, None otherwise
        """
        line = line.strip()
        if not line:
            return None

        if line.startswith("data:"):
            data = line[5:].strip()
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return None

        return None
