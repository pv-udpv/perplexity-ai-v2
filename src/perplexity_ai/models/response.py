"""
Response models for Perplexity AI API
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class StepType(str, Enum):
    """Type of search step"""

    INITIAL_QUERY = "INITIAL_QUERY"
    SEARCH = "SEARCH"
    ANALYSIS = "ANALYSIS"
    SUMMARY = "SUMMARY"


class SearchStep(BaseModel):
    """Single step in search plan"""

    uuid: str = ""
    step_type: StepType
    initial_query_content: Optional[Dict[str, str]] = None


class PlanBlock(BaseModel):
    """Search plan with steps"""

    progress: str = "IN_PROGRESS"
    goals: List[str] = Field(default_factory=list)
    steps: List[SearchStep] = Field(default_factory=list)
    final: bool = False


class Block(BaseModel):
    """Response block"""

    intended_usage: str
    plan_block: Optional[PlanBlock] = None


class SSEMessage(BaseModel):
    """SSE event message"""

    backend_uuid: str
    context_uuid: str
    uuid: str
    frontend_context_uuid: str
    display_model: str
    mode: str
    search_focus: str
    source: str
    thread_url_slug: str
    expect_search_results: str
    gpt4: bool
    text_completed: bool
    blocks: List[Block] = Field(default_factory=list)
    message_mode: str = "STREAMING"
    answer_modes: List[str] = Field(default_factory=list)
    reconnectable: bool = True
    image_completions: List[str] = Field(default_factory=list)
    cursor: Optional[str] = None
    status: str = "PENDING"
    final_sse_message: bool = False
    text: str = ""  # Accumulated text


class AskResponse(BaseModel):
    """Final response from perplexity_ask"""

    text: str = Field(..., description="Answer text")
    sources: List[Dict[str, Any]] = Field(
        default_factory=list, description="Source citations"
    )
    thread_uuid: Optional[str] = Field(None, description="Thread UUID for follow-ups")
    backend_uuid: Optional[str] = Field(None, description="Backend UUID")
    context_uuid: Optional[str] = Field(None, description="Context UUID")
    thread_url_slug: Optional[str] = Field(None, description="Thread URL slug")
    mode: Optional[str] = Field(None, description="Response mode")
    model: Optional[str] = Field(None, description="Model used")
