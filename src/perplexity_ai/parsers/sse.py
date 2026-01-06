"""SSE (Server-Sent Events) parser with double JSON decode fix."""

from __future__ import annotations

import json
from typing import Any, Generator, Optional


class SSEEvent:
    """Single SSE event."""
    
    def __init__(self, event: str, data: dict[str, Any]):
        self.event = event
        self.data = data
        self.step_type = data.get('step_type')
    
    def is_final(self) -> bool:
        """Check if this is the FINAL step with answer."""
        return self.step_type == 'FINAL'
    
    def __repr__(self) -> str:
        return f"SSEEvent(event='{self.event}', step_type='{self.step_type}')"


class SSEParser:
    """Streaming SSE parser with buffer support.
    
    Handles Perplexity's SSE format:
    - Multiple events per response
    - Nested JSON in 'answer' field (CRITICAL!)
    - List or dict data formats
    """
    
    def __init__(self):
        self.buffer = ""
        self.events: list[SSEEvent] = []
    
    def feed(self, chunk: str) -> Generator[SSEEvent, None, None]:
        """Feed chunk of data and yield parsed events.
        
        Args:
            chunk: Raw SSE text chunk
            
        Yields:
            Parsed SSEEvent objects
        """
        self.buffer += chunk
        
        while '\n' in self.buffer:
            line, self.buffer = self.buffer.split('\n', 1)
            
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                    
                    # Support both list and dict
                    events_data = data if isinstance(data, list) else [data]
                    
                    for event_data in events_data:
                        event = SSEEvent('message', event_data)
                        self.events.append(event)
                        yield event
                        
                except json.JSONDecodeError:
                    continue
    
    def parse_complete(self, text: str) -> list[SSEEvent]:
        """Parse complete SSE response (non-streaming).
        
        Args:
            text: Complete SSE response text
            
        Returns:
            List of parsed events
        """
        events = []
        
        for line in text.split('\n'):
            if not line.startswith('data: '):
                continue
            
            try:
                data = json.loads(line[6:])
                
                events_data = data if isinstance(data, list) else [data]
                
                for event_data in events_data:
                    events.append(SSEEvent('message', event_data))
                    
            except json.JSONDecodeError:
                continue
        
        return events
    
    def extract_answer(self, events: Optional[list[SSEEvent]] = None) -> dict[str, Any]:
        """Extract final answer from events.
        
        CRITICAL: Perplexity returns nested JSON!
        step['content']['answer'] is a JSON STRING, not object.
        Must decode twice: json.loads(json.loads(...))
        
        Args:
            events: List of events (uses self.events if None)
            
        Returns:
            Dict with:
                - text: Final answer text
                - web_results: List of sources
                - structured_answer: Structured data (if any)
        """
        events = events or self.events
        
        for event in events:
            if event.is_final():
                content = event.data.get('content', {})
                answer_str = content.get('answer', '')
                
                if answer_str:
                    try:
                        # CRITICAL: Double JSON decode!
                        # answer_str is a JSON string containing the real answer
                        answer_obj = json.loads(answer_str)
                        
                        return {
                            'text': answer_obj.get('answer', ''),
                            'web_results': answer_obj.get('web_results', []),
                            'structured_answer': answer_obj.get('structured_answer'),
                        }
                    except json.JSONDecodeError:
                        # Fallback: return raw string
                        return {
                            'text': answer_str,
                            'web_results': [],
                            'structured_answer': None,
                        }
        
        return {
            'text': '',
            'web_results': [],
            'structured_answer': None,
        }
    
    def reset(self):
        """Reset parser state."""
        self.buffer = ""
        self.events = []
