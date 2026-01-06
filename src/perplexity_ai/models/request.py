"""
Request models for Perplexity AI API
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from uuid import uuid4


class Mode(str, Enum):
    """Query mode"""

    CONCISE = "concise"
    COPILOT = "copilot"
    RESEARCH = "research"


class Model(str, Enum):
    """AI Model selection"""

    PPLX_PRO = "pplx_pro"
    CLAUDE_SONNET = "claude37sonnetthinking"
    GPT_4O = "gpt-4o"
    GPT_45 = "gpt-4.5"
    O3_MINI = "o3-mini"
    R1 = "r1"
    SONAR = "sonar"
    GEMINI = "gemini 2.0 flash"
    GROK = "grok-2"


class Source(str, Enum):
    """Search source"""

    WEB = "web"
    SCHOLAR = "scholar"
    SOCIAL = "social"


class AskParams(BaseModel):
    """Parameters for perplexity_ask request"""

    read_write_token: Optional[str] = None
    is_voice_to_voice: bool = False
    model_preference: Model = Model.PPLX_PRO
    supported_block_use_cases: List[str] = Field(
        default_factory=lambda: [
            "answer_modes",
            "media_items",
            "knowledge_cards",
            "place_widgets",
            "shopping_widgets",
            "sports_widgets",
            "finance_widgets",
            "jobs_widgets",
            "placeholder_cards",
            "maps_preview",
            "search_result_widgets",
            "diff_blocks",
            "inline_images",
            "inline_assets",
            "inline_entity_cards",
            "inline_finance_widgets",
        ]
    )
    query_source: str = "home"
    is_related_query: bool = False
    frontend_uuid: str = Field(default_factory=lambda: str(uuid4()))
    language: str = "ru-RU"
    timezone: str = "Europe/Moscow"
    user_nextauth_id: Optional[str] = None
    frontend_context_uuid: str = Field(default_factory=lambda: str(uuid4()))
    sources: List[Source] = Field(default_factory=lambda: [Source.WEB])
    use_schematized_api: bool = True
    is_incognito: bool = False
    last_backend_uuid: Optional[str] = None


class AskRequest(BaseModel):
    """Request to /rest/sse/perplexity_ask"""

    query_str: str = Field(..., description="Search query")
    params: AskParams = Field(default_factory=AskParams)

    class Config:
        use_enum_values = True
