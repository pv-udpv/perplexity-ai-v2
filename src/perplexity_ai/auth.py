"""
Authentication management for Perplexity AI
"""

from __future__ import annotations

from typing import Dict, Optional
from pydantic import BaseModel, Field


class PerplexityAuth(BaseModel):
    """Authentication credentials for Perplexity AI

    Attributes:
        bearer_token: JWT Bearer token from Authorization header
        session_token: NextAuth session token (__Secure-next-auth.session-token)
        csrf_token: CSRF token (next-auth.csrf-token)
        cf_clearance: Cloudflare clearance cookie
        user_nextauth_id: User NextAuth ID
        device_id: Device identifier (iOS format)
    """

    bearer_token: Optional[str] = Field(default=None, description="JWT Bearer token")
    session_token: Optional[str] = Field(
        default=None, description="NextAuth session token"
    )
    csrf_token: Optional[str] = Field(default=None, description="CSRF token")
    cf_clearance: Optional[str] = Field(
        default=None, description="Cloudflare clearance"
    )
    user_nextauth_id: Optional[str] = Field(
        default=None, description="User NextAuth ID"
    )
    device_id: Optional[str] = Field(
        default=None, description="Device ID (iOS format)"
    )

    @classmethod
    def from_cookies(cls, cookies: Dict[str, str]) -> PerplexityAuth:
        """Create auth from cookie dictionary

        Args:
            cookies: Dictionary of cookies from browser

        Returns:
            PerplexityAuth instance
        """
        return cls(
            session_token=cookies.get("__Secure-next-auth.session-token"),
            csrf_token=cookies.get("next-auth.csrf-token"),
            cf_clearance=cookies.get("cf_clearance"),
        )

    def to_cookies(self) -> Dict[str, str]:
        """Convert to cookie dictionary

        Returns:
            Cookie dictionary
        """
        cookies = {}
        if self.session_token:
            cookies["__Secure-next-auth.session-token"] = self.session_token
        if self.csrf_token:
            cookies["next-auth.csrf-token"] = self.csrf_token
        if self.cf_clearance:
            cookies["cf_clearance"] = self.cf_clearance
        return cookies

    def to_headers(self) -> Dict[str, str]:
        """Convert to request headers

        Returns:
            Headers dictionary
        """
        headers = {}
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        return headers

    def is_authenticated(self) -> bool:
        """Check if authentication is valid

        Returns:
            True if authenticated
        """
        return bool(self.session_token or self.bearer_token)
