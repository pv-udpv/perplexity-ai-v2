"""curl_cffi session wrapper with fingerprint support."""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Optional

try:
    from curl_cffi import requests
except ImportError:
    raise ImportError(
        "curl_cffi is required for session management.\n"
        "Install with: pip install curl-cffi>=0.7.0"
    )

from .stealth.fingerprint import BrowserFingerprint


class PerplexitySession:
    """Perplexity API session with curl_cffi and fingerprint support.
    
    Automatically handles:
    - Browser fingerprinting (from daemon or generated)
    - curl_cffi impersonation
    - Header generation
    - Cookie management
    
    Example:
        >>> # Auto-load from daemon
        >>> session = PerplexitySession()
        >>> 
        >>> # Use custom fingerprint
        >>> fp = BrowserFingerprint.generate_realistic()
        >>> session = PerplexitySession(fingerprint=fp)
    """
    
    DEFAULT_ARTIFACT_PATH = 'artifacts/browser-fingerprint.json'
    
    def __init__(
        self,
        fingerprint: Optional[BrowserFingerprint] = None,
        cookies: Optional[dict[str, str]] = None,
        auto_load_fingerprint: bool = True,
    ):
        """Initialize session.
        
        Args:
            fingerprint: Custom fingerprint (optional)
            cookies: Initial cookies dict
            auto_load_fingerprint: Auto-load from daemon artifact if exists
        """
        self.cookies = cookies or {}
        
        # Load or generate fingerprint
        if fingerprint is None:
            fingerprint = self._load_or_generate_fingerprint(auto_load_fingerprint)
        
        self.fingerprint = fingerprint
        self._session = self._create_curl_session()
    
    def _load_or_generate_fingerprint(self, auto_load: bool) -> BrowserFingerprint:
        """Load fingerprint from daemon or generate."""
        if auto_load:
            artifact_path = Path(self.DEFAULT_ARTIFACT_PATH)
            
            if artifact_path.exists():
                try:
                    return BrowserFingerprint.from_daemon_artifact(artifact_path)
                except (ValueError, KeyError) as e:
                    warnings.warn(
                        f"Failed to load daemon fingerprint: {e}. "
                        "Generating new one.",
                        UserWarning
                    )
        
        # Generate fallback
        return BrowserFingerprint.generate_realistic()
    
    def _create_curl_session(self) -> requests.Session:
        """Create curl_cffi session with fingerprint."""
        headers = {
            **self.fingerprint.to_headers(),
            'Accept': 'text/event-stream',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Origin': 'https://www.perplexity.ai',
            'Referer': 'https://www.perplexity.ai/',
        }
        
        return requests.Session(
            headers=headers,
            cookies=self.cookies,
            impersonate=self.fingerprint.impersonate_profile
        )
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """POST request."""
        return self._session.post(url, **kwargs)
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """GET request."""
        return self._session.get(url, **kwargs)
    
    def update_cookies(self, cookies: dict[str, str]):
        """Update session cookies."""
        self.cookies.update(cookies)
        self._session.cookies.update(cookies)
    
    def get_info(self) -> dict:
        """Get session info."""
        return {
            'impersonate': self.fingerprint.impersonate_profile,
            'chrome_version': self.fingerprint.chrome_version,
            'platform': self.fingerprint.platform,
            'canvas_hash': self.fingerprint.canvas_hash,
            'cookies_count': len(self.cookies),
            'fingerprint_source': self.fingerprint.source,
            'fingerprint_age_hours': (
                (datetime.now() - self.fingerprint.timestamp).total_seconds() / 3600
            ),
        }
    
    def close(self):
        """Close session."""
        if hasattr(self._session, 'close'):
            self._session.close()


from datetime import datetime
