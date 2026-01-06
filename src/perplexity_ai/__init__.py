"""
Perplexity AI v2 - Comprehensive API Client
"""

from perplexity_ai.client import Client
from perplexity_ai.async_client import AsyncClient
from perplexity_ai.auth import PerplexityAuth

__version__ = "2.0.0"
__all__ = ["Client", "AsyncClient", "PerplexityAuth"]
