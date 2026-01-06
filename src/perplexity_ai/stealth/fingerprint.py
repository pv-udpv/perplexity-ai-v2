"""Browser fingerprint models for stealth mode."""

from __future__ import annotations

import hashlib
import json
import random
import re
import warnings
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class ScreenInfo(BaseModel):
    """Screen information."""
    width: int = Field(ge=800, le=7680)
    height: int = Field(ge=600, le=4320)
    colorDepth: int = Field(default=24, ge=8, le=32)


class WebGLInfo(BaseModel):
    """WebGL information."""
    vendor: Optional[str] = None
    renderer: Optional[str] = None


class BrowserFingerprint(BaseModel):
    """Unified browser fingerprint for Cloudflare bypass.
    
    Can be loaded from browser_daemon artifacts or generated.
    """
    
    timestamp: datetime
    user_agent: str = Field(min_length=10)
    platform: Literal["Windows", "macOS", "Linux", "Win32", "MacIntel", "Linux x86_64"]
    language: str = Field(default="en-US", pattern=r"^[a-z]{2}-[A-Z]{2}$")
    screen: ScreenInfo
    timezone: str = Field(default="America/New_York")
    hardware_concurrency: int = Field(ge=1, le=128)
    device_memory: Optional[int] = Field(default=None, ge=1, le=32)
    canvas_hash: str = Field(min_length=16, max_length=32)
    webgl: Optional[WebGLInfo] = None
    cookies_count: int = Field(default=0, ge=0)
    
    # Metadata
    source: Literal["daemon", "manual", "generated"] = "generated"
    
    @field_validator('timestamp')
    @classmethod
    def validate_freshness(cls, v: datetime) -> datetime:
        """Warn if fingerprint is stale."""
        age = datetime.now() - v
        if age > timedelta(days=7):
            warnings.warn(
                f"Fingerprint is {age.days} days old. "
                "Consider refreshing with browser_daemon.",
                UserWarning
            )
        return v
    
    @property
    def chrome_version(self) -> int:
        """Extract Chrome version from user agent."""
        match = re.search(r'Chrome/(\d+)', self.user_agent)
        return int(match.group(1)) if match else 120
    
    @property
    def impersonate_profile(self) -> str:
        """Select curl_cffi impersonate profile based on Chrome version."""
        v = self.chrome_version
        if v >= 126:
            return "chrome126"
        if v >= 120:
            return "chrome120"
        if v >= 110:
            return "chrome110"
        return "chrome101"
    
    @property
    def platform_name(self) -> str:
        """Get platform display name for Sec-CH-UA-Platform header."""
        mapping = {
            "Win32": "Windows",
            "Windows": "Windows",
            "MacIntel": "macOS",
            "macOS": "macOS",
            "Linux x86_64": "Linux",
            "Linux": "Linux",
        }
        return mapping.get(self.platform, "Unknown")
    
    def generate_sec_ch_ua(self) -> str:
        """Generate Sec-CH-UA header."""
        v = self.chrome_version
        return f'"Not;A=Brand";v="24", "Chromium";v="{v}"'
    
    def to_headers(self) -> dict[str, str]:
        """Generate HTTP headers from fingerprint."""
        return {
            'User-Agent': self.user_agent,
            'Accept-Language': f"{self.language},en;q=0.9",
            'Sec-Ch-Ua': self.generate_sec_ch_ua(),
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': f'"{self.platform_name}"',
        }
    
    @classmethod
    def from_daemon_artifact(cls, path: str | Path) -> BrowserFingerprint:
        """Load fingerprint from browser_daemon.py output.
        
        Args:
            path: Path to browser-fingerprint.json
            
        Returns:
            BrowserFingerprint instance
            
        Raises:
            FileNotFoundError: If artifact file doesn't exist
            ValueError: If artifact format is invalid
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(
                f"Fingerprint artifact not found: {path}\n"
                "Run: python tools/browser_daemon.py start"
            )
        
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {path}: {e}")
        
        return cls(
            timestamp=datetime.fromisoformat(data['timestamp']),
            user_agent=data['user_agent'],
            platform=data['platform'],
            language=data['language'],
            screen=ScreenInfo(**data['screen']),
            timezone=data['timezone'],
            hardware_concurrency=data['hardware_concurrency'],
            device_memory=data.get('device_memory'),
            canvas_hash=data['canvas_hash'],
            webgl=WebGLInfo(
                vendor=data.get('webgl_vendor'),
                renderer=data.get('webgl_renderer')
            ) if data.get('webgl_vendor') or data.get('webgl_renderer') else None,
            cookies_count=data['cookies_count'],
            source="daemon"
        )
    
    @classmethod
    def generate_realistic(cls, platform: Optional[str] = None) -> BrowserFingerprint:
        """Generate realistic fingerprint for testing.
        
        Args:
            platform: Force specific platform (Windows/macOS/Linux)
            
        Returns:
            Generated BrowserFinprint
        """
        chrome_v = random.choice([120, 121, 122, 123, 124, 125, 126])
        
        platforms_map = {
            "Windows": ("Win32", "Windows NT 10.0; Win64; x64"),
            "macOS": ("MacIntel", "Macintosh; Intel Mac OS X 10_15_7"),
            "Linux": ("Linux x86_64", "X11; Linux x86_64"),
        }
        
        if platform and platform in platforms_map:
            os_name = platform
        else:
            os_name = random.choice(list(platforms_map.keys()))
        
        platform_internal, ua_os = platforms_map[os_name]
        
        user_agent = (
            f"Mozilla/5.0 ({ua_os}) AppleWebKit/537.36 "
            f"(KHTML, like Gecko) Chrome/{chrome_v}.0.0.0 Safari/537.36"
        )
        
        # Realistic screen resolutions
        resolutions = [
            (1920, 1080), (2560, 1440), (3840, 2160),
            (1366, 768), (1440, 900), (2880, 1800)
        ]
        width, height = random.choice(resolutions)
        
        # Generate semi-consistent canvas hash
        canvas_seed = f"{user_agent}{width}{height}{random.random()}"
        canvas_hash = hashlib.md5(canvas_seed.encode()).hexdigest()[:16]
        
        # WebGL renderers
        webgl_configs = [
            ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080)"),
            ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) UHD Graphics 630)"),
            ("Google Inc. (AMD)", "ANGLE (AMD, AMD Radeon RX 6800 XT)"),
        ]
        webgl_vendor, webgl_renderer = random.choice(webgl_configs)
        
        return cls(
            timestamp=datetime.now(),
            user_agent=user_agent,
            platform=platform_internal,
            language="en-US",
            screen=ScreenInfo(
                width=width,
                height=height,
                colorDepth=24
            ),
            timezone="America/New_York",
            hardware_concurrency=random.choice([8, 12, 16]),
            device_memory=random.choice([8, 16, 32]),
            canvas_hash=canvas_hash,
            webgl=WebGLInfo(
                vendor=webgl_vendor,
                renderer=webgl_renderer
            ),
            cookies_count=0,
            source="generated"
        )
    
    model_config = {
        'json_schema_extra': {
            'examples': [
                {
                    'timestamp': '2026-01-06T05:00:00',
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
                    'platform': 'Win32',
                    'language': 'en-US',
                    'screen': {'width': 1920, 'height': 1080, 'colorDepth': 24},
                    'timezone': 'America/New_York',
                    'hardware_concurrency': 8,
                    'device_memory': 8,
                    'canvas_hash': 'a1b2c3d4e5f6g7h8',
                    'webgl': {
                        'vendor': 'Google Inc. (NVIDIA)',
                        'renderer': 'ANGLE (NVIDIA, NVIDIA GeForce RTX 3080)'
                    },
                    'cookies_count': 12,
                    'source': 'daemon'
                }
            ]
        }
    }
