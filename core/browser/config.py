"""
Browser configuration classes.

Provides dataclass-based configuration for browser initialization.
"""

from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


@dataclass
class ProxyConfig:
    """Proxy configuration for browser connections."""
    
    enabled: bool = False
    type: str = "http"  # http, socks5, tor
    address: str = "127.0.0.1:8080"
    username: Optional[str] = None
    password: Optional[str] = None


@dataclass
class StealthConfig:
    """Stealth mode configuration to avoid bot detection."""
    
    enabled: bool = False
    languages: list = field(default_factory=lambda: ["en-US", "en"])
    vendor: str = "Google Inc."
    platform: str = "Win32"
    webgl_vendor: str = "Intel Inc."
    renderer: str = "Intel Iris OpenGL Engine"
    fix_hairline: bool = True


@dataclass
class BrowserConfig:
    """Complete browser configuration."""
    
    headless: bool = False
    user_agent: Optional[str] = None  # None = auto-generate, "auto" = random
    stealth: Optional[StealthConfig] = None
    proxy: Optional[ProxyConfig] = None
    window_size: tuple[int, int] = (1920, 1080)
    cache_dir: Optional[Path] = None
    user_data_dir: Optional[Path] = None
    timeout: int = 30
    page_load_strategy: str = "normal"  # normal, eager, none
